#!/usr/bin/env python3
"""
WiX MSI Generator for pyMediaManager
Generates Windows Installer (MSI) packages using WiX Toolset v4
"""

import hashlib
import logging
from pathlib import Path
import subprocess
import sys
from typing import Any
import uuid

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("Error: jinja2 is required for MSI generation. Run: uv sync --all-extras")
    sys.exit(1)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("wix_generator")

# Fixed UpgradeCode GUID for all versions (enables major upgrades)
UPGRADE_CODE_GUID = "B8F9A3D2-7E6C-4F1B-9A5D-8C2E4B7F3A1D"

# Icon path (relative to project root)
ICON_FILENAME = "app/ui/assets/logo.png"  # Will need conversion or use default


def generate_stable_guid(seed: str) -> str:
    """Generate stable GUID from seed string for component IDs."""
    # Use SHA256 hash of seed to generate deterministic UUID (first 16 bytes)
    hash_bytes = hashlib.sha256(seed.encode()).digest()[:16]
    return str(uuid.UUID(bytes=hash_bytes))


def sanitize_id(path: str) -> str:
    """Sanitize file path to valid WiX ID (alphanumeric + underscore + period).

    WiX ID requirements:
    - Only ASCII A-Z, a-z, digits, underscores (_), periods (.)
    - Must start with letter or underscore
    - Recommended max length: 72 characters

    To ensure uniqueness when truncating long paths, a hash suffix is appended
    based on the original full path. This prevents collisions when different
    paths would produce the same truncated ID.

    Args:
        path: File path string to sanitize

    Returns:
        Sanitized ID string suitable for WiX
    """
    # Replace path separators and invalid characters with underscores
    sanitized = (
        path.replace("/", "_")
        .replace("\\", "_")
        .replace("-", "_")
        .replace("+", "_")
        .replace(" ", "_")
        .replace("(", "_")
        .replace(")", "_")
        .replace("[", "_")
        .replace("]", "_")
        .replace("{", "_")
        .replace("}", "_")
        .replace("@", "_")
        .replace("#", "_")
        .replace("$", "_")
        .replace("%", "_")
        .replace("&", "_")
        .replace("*", "_")
        .replace("=", "_")
        .replace("!", "_")
        .replace("~", "_")
        .replace("`", "_")
        .replace("'", "_")
        .replace('"', "_")
        .replace(",", "_")
        .replace(";", "_")
        .replace(":", "_")
        .replace("?", "_")
        .replace("<", "_")
        .replace(">", "_")
        .replace("|", "_")
    )

    # Ensure it starts with letter or underscore
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"

    # If too long, truncate and add hash suffix to ensure uniqueness
    if len(sanitized) > 72:
        # Generate 8-character hex hash of original path for uniqueness
        path_hash = hashlib.sha256(path.encode()).hexdigest()[:8]
        # Keep first 63 chars + underscore + 8 char hash = 72 chars max
        sanitized = f"{sanitized[:63]}_{path_hash}"

    return sanitized


def collect_files_recursive(directory: Path) -> list[Path]:
    """Recursively collect all files in directory."""
    if not directory.exists():
        logger.warning(f"Directory does not exist: {directory}")
        return []

    # Use list comprehension instead of append
    return sorted([item for item in directory.rglob("*") if item.is_file()])


def generate_short_name(file_path: Path, directory_counters: dict[str, int]) -> str:
    """Generate a unique 8.3 short filename.

    Args:
        file_path: Path to the file
        directory_counters: Dictionary tracking counters per directory

    Returns:
        8.3 format short filename (e.g., FILE_1.TXT or FILE001.TXT)
    """
    stem = file_path.stem
    ext = file_path.suffix

    # Get directory key for tracking
    dir_key = str(file_path.parent)

    # Get and increment counter for this directory
    counter = directory_counters.get(dir_key, 0) + 1
    directory_counters[dir_key] = counter

    # Truncate extension to 3 chars (standard 8.3 format)
    short_ext = ext[:4] if ext else ""  # Include the dot

    # If filename is already 8.3 compliant and unique, use it
    if len(stem) <= 8 and not any(c for c in stem if not c.isalnum() and c != "_"):
        # Check if we need to make it unique by appending counter
        if counter == 1:
            short_name = f"{stem}{short_ext}".upper()
        else:
            # Append counter with underscore to avoid tilde ambiguity
            base_len = min(len(stem), 8 - len(str(counter)) - 1)
            short_name = f"{stem[:base_len]}_{counter}{short_ext}".upper()
    else:
        # Create base name from first chars + counter with underscore
        # Use underscore instead of tilde to avoid WIX1044 ambiguity warnings
        max_base = 8 - len(str(counter)) - 1  # Leave room for _N
        short_base = stem[:max_base].upper()
        # Clean invalid characters for 8.3 format
        short_base = "".join(c if c.isalnum() else "_" for c in short_base)
        short_name = f"{short_base}_{counter}{short_ext}".upper()

    return short_name


def generate_component_group(
    group_name: str, directory: Path, base_path: Path, max_files_per_component: int = 100
) -> list[dict[str, Any]]:
    """
    Generate component group for a directory with all its files.

    Args:
        group_name: Name prefix for components
        directory: Directory to scan
        base_path: Base path for relative path calculation
        max_files_per_component: Maximum files per component (WiX has limits)

    Returns:
        List of component dictionaries with IDs, GUIDs, and file lists
    """
    files = collect_files_recursive(directory)

    if not files:
        logger.warning(f"No files found in {directory}")
        return []

    components = []
    used_ids = set()  # Track used IDs to prevent duplicates
    directory_counters: dict[str, int] = {}  # Track short name counters per directory

    # Split files into chunks (WiX has component size limits)
    for component_index, i in enumerate(range(0, len(files), max_files_per_component), start=1):
        file_chunk = files[i : i + max_files_per_component]

        # Generate component ID and GUID
        component_id = f"{group_name}Component{component_index}"
        component_guid = generate_stable_guid(f"{group_name}_{component_index}")

        # Generate file entries
        file_entries = []
        for file_path in file_chunk:
            relative_path = file_path.relative_to(base_path)
            base_id = sanitize_id(f"{group_name}_{relative_path}")

            # Ensure unique ID by adding counter if duplicate
            file_id = base_id
            counter = 1
            while file_id in used_ids:
                file_id = f"{base_id}_{counter}"
                counter += 1
            used_ids.add(file_id)

            # Generate unique short name for this file
            short_name = generate_short_name(file_path, directory_counters)

            file_entries.append(
                {
                    "id": file_id,
                    "source": str(file_path),
                    "relative": str(relative_path),
                    "short_name": short_name,
                }
            )

        components.append(
            {
                "id": component_id,
                "guid": component_guid,
                "files": file_entries,
            }
        )

    logger.info(f"Generated {len(components)} components for {group_name} ({len(files)} files)")
    return components


def render_wix_manifest(
    version: str,
    arch: str,
    python_dir_name: str,
    lib_dir_name: str,
    root_dir: Path,
    output_path: Path,
) -> None:
    """
    Render WiX manifest from Jinja2 template.

    Args:
        version: Application version (e.g., "1.2.3")
        arch: Architecture (amd64 or arm64)
        python_dir_name: Python directory name (e.g., "python313")
        lib_dir_name: Library directory name (e.g., "lib-py313")
        root_dir: Project root directory
        output_path: Output .wxs file path
    """
    logger.info("Generating WiX manifest...")

    # Setup Jinja2 environment
    template_dir = Path(__file__).parent.resolve()
    # Note: autoescape=False is intentional for WiX XML generation (not HTML)
    env = Environment(loader=FileSystemLoader(str(template_dir)), autoescape=False)  # noqa: S701
    template = env.get_template("wix_template.wxs.j2")

    # Check for icon file
    icon_path = root_dir / ICON_FILENAME
    if not icon_path.exists():
        # Use default or skip
        logger.warning(f"Icon file not found: {icon_path}. Using default.")
        icon_path = root_dir / "README.md"  # Placeholder - WiX can work without icon

    # Check for frozen requirements file
    frozen_req_file = root_dir / f"requirements-frozen-py{version.replace('.', '')}-{arch}.txt"
    frozen_req_path = str(frozen_req_file) if frozen_req_file.exists() else None

    # Generate component groups for each directory
    python_components = generate_component_group(
        "PythonRuntime", root_dir / python_dir_name, root_dir
    )
    lib_components = generate_component_group("PythonLib", root_dir / lib_dir_name, root_dir)
    app_components = generate_component_group("App", root_dir / "app", root_dir)
    plugins_components = generate_component_group("Plugins", root_dir / "plugins", root_dir)
    config_components = generate_component_group("Config", root_dir / "config", root_dir)

    # Generate stable GUIDs for special components
    root_files_guid = generate_stable_guid("RootFiles")
    shortcuts_guid = generate_stable_guid("Shortcuts")

    # Render template
    context = {
        "version": version,
        "arch": arch,
        "upgrade_code": UPGRADE_CODE_GUID,
        "python_dir_name": python_dir_name,
        "lib_dir_name": lib_dir_name,
        "source_dir": str(root_dir),
        "icon_path": str(icon_path),
        "frozen_requirements_file": frozen_req_path,
        "root_files_guid": root_files_guid,
        "shortcuts_guid": shortcuts_guid,
        "python_components": python_components,
        "lib_components": lib_components,
        "app_components": app_components,
        "plugins_components": plugins_components,
        "config_components": config_components,
    }

    manifest_content = template.render(**context)

    # Write manifest file
    output_path.write_text(manifest_content, encoding="utf-8")
    logger.info(f"WiX manifest written to: {output_path}")


def build_msi(wxs_path: Path, msi_path: Path, arch: str) -> None:
    """
    Build MSI installer using WiX Toolset.

    Args:
        wxs_path: Path to .wxs manifest file
        msi_path: Output MSI file path
        arch: Architecture (amd64 or arm64)
    """
    logger.info("Building MSI installer with WiX Toolset...")

    # Check if WiX is installed
    try:
        result = subprocess.run(
            ["wix", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(f"WiX version: {result.stdout.strip()}")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        logger.exception("WiX Toolset not found. Install with: dotnet tool install --global wix")
        raise RuntimeError("WiX Toolset v4 is required for MSI generation") from e

    # Build MSI
    wix_arch = "x64" if arch == "amd64" else "arm64"
    cmd = [
        "wix",
        "build",
        "-arch",
        wix_arch,
        "-out",
        str(msi_path),
        str(wxs_path),
    ]

    logger.info(f"Running: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True, cwd=wxs_path.parent)
        logger.info(f"MSI installer created: {msi_path}")
    except subprocess.CalledProcessError:
        logger.exception("Failed to build MSI")
        raise


def _get_application_version(root_dir: Path) -> str:
    """Get application version from hatch-vcs or git tags.

    Args:
        root_dir: Project root directory

    Returns:
        Application version string (X.Y.Z format)
    """
    # Try reading hatch-vcs generated _version.py first (fastest)
    try:
        version_file = root_dir / "app" / "_version.py"
        if version_file.exists():
            namespace: dict[str, str] = {}
            exec(version_file.read_text(), namespace)  # noqa: S102
            version = namespace.get("__version__", "")
            if version:
                # Clean version for MSI (must be X.Y.Z format)
                version_parts = version.split(".")
                if len(version_parts) > 3:
                    # Remove any pre-release/dev suffixes
                    version = ".".join(version_parts[:3])
                logger.info("Application version from _version.py: %s", version)
                return version
    except Exception as e:
        logger.debug("Could not read _version.py: %s", e)

    # Try reading from git tags (development)
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
            cwd=root_dir,
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip("v")
            if version:
                # Clean version for MSI (must be X.Y.Z format)
                version_parts = version.split(".")
                if len(version_parts) > 3:
                    version = ".".join(version_parts[:3])
                logger.info("Application version from git tags: %s", version)
                return version
    except Exception as e:
        logger.debug("Could not get version from git: %s", e)
    return "0.0.0"


def create_msi_installer(
    python_version: str, arch: str, root_dir: Path, output_dir: Path | None = None
) -> Path:
    """
    Main entry point for MSI generation.

    Args:
        python_version: Python version (e.g., "3.13")
        arch: Architecture (amd64 or arm64)
        root_dir: Project root directory
        output_dir: Output directory for MSI (defaults to root_dir)

    Returns:
        Path to generated MSI file
    """
    if output_dir is None:
        output_dir = root_dir

    # Get application version
    app_version = _get_application_version(root_dir)

    # Determine directory names
    python_dir_name = f"python{python_version.replace('.', '')}"
    if arch == "arm64":
        python_dir_name += "-arm64"
        lib_dir_name = f"lib-py{python_version.replace('.', '')}-arm64"
    else:
        lib_dir_name = f"lib-py{python_version.replace('.', '')}"

    # Generate WiX manifest
    wxs_path = output_dir / "pyMM_installer.wxs"
    render_wix_manifest(python_version, arch, python_dir_name, lib_dir_name, root_dir, wxs_path)

    # Build MSI
    msi_filename = f"pyMM-v{app_version}-py{python_version}-win-{arch}.msi"
    msi_path = output_dir / msi_filename

    build_msi(wxs_path, msi_path, arch)

    # Calculate SHA256 checksum
    logger.info("Calculating SHA256 checksum...")
    sha256_hash = hashlib.sha256()
    with msi_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)

    checksum = sha256_hash.hexdigest()
    checksum_path = output_dir / f"{msi_filename}.sha256"
    checksum_path.write_text(checksum, encoding="utf-8")
    logger.info(f"SHA256: {checksum}")
    logger.info(f"Checksum written to: {checksum_path}")

    return msi_path


if __name__ == "__main__":
    # For testing: python wix_generator.py
    import argparse

    parser = argparse.ArgumentParser(description="Generate MSI installer for pyMediaManager")
    parser.add_argument("--version", default="3.13", help="Python version")
    parser.add_argument("--arch", default="amd64", choices=["amd64", "arm64"], help="Architecture")
    args = parser.parse_args()

    root = Path(__file__).parent.parent.resolve()
    msi_path = create_msi_installer(args.version, args.arch, root)
    print(f"\nMSI installer created successfully: {msi_path}")
