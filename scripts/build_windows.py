#!/usr/bin/env python3
"""
Build Portable Distribution
Automates the creation of a portable Windows distribution.
"""

import argparse
import logging
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import urllib.request
import zipfile

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("builder")

# Python Embeddable Distributions
# Structure: version -> arch -> config
PYTHON_VERSIONS = {
    "3.12": {
        "amd64": {
            "url": "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip",
            "dir_name": "python312",
            "lib_dir": "lib-py312",
        },
        "arm64": {
            "url": "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-arm64.zip",
            "dir_name": "python312-arm64",
            "lib_dir": "lib-py312-arm64",
        },
    },
    "3.13": {
        "amd64": {
            "url": "https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip",
            "dir_name": "python313",
            "lib_dir": "lib-py313",
        },
        "arm64": {
            "url": "https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-arm64.zip",
            "dir_name": "python313-arm64",
            "lib_dir": "lib-py313-arm64",
        },
    },
    "3.14": {
        "amd64": {
            "url": "https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-amd64.zip",
            "dir_name": "python314",
            "lib_dir": "lib-py314",
        },
        "arm64": {
            "url": "https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-arm64.zip",
            "dir_name": "python314-arm64",
            "lib_dir": "lib-py314-arm64",
        },
    },
}

ROOT_DIR = Path(__file__).parent.parent.resolve()


def get_app_version() -> str:
    """Get application version from hatch-vcs generated file or git tags.

    Returns:
        Version string (e.g., "0.2.0" or "0.0.0-dev" on failure)
    """
    # Try reading hatch-vcs generated _version.py first (fastest)
    try:
        version_file = ROOT_DIR / "app" / "_version.py"
        if version_file.exists():
            namespace: dict[str, str] = {}
            exec(version_file.read_text(), namespace)  # noqa: S102
            version = namespace.get("__version__", "")
            if version:
                logger.info(f"Detected version from _version.py: {version}")
                return version
    except Exception as e:
        logger.debug(f"Could not read _version.py: {e}")

    # Try reading from git tags (development)
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            check=False,
            cwd=ROOT_DIR,
        )
        if result.returncode == 0:
            version = result.stdout.strip().lstrip("v")
            if version:
                logger.info(f"Detected version from git tags: {version}")
                return version
    except Exception as e:
        logger.debug(f"Could not get version from git: {e}")
    return "0.0.0-dev"


def download_file(url: str, dest: Path) -> None:
    """Download a file from a URL to a destination path.

    Args:
        url: The URL to download from.
        dest: The destination path to save the file.
    """
    if dest.exists():
        logger.info(f"Using cached {dest.name}")
        return
    logger.info(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest)  # noqa: S310
    except Exception:
        logger.exception(f"Failed to download {url}")
        sys.exit(1)


def download_uv_executable(arch: str = "amd64") -> Path:
    """Download the latest UV executable for Windows.

    Args:
        arch: Target architecture ('amd64' or 'arm64').

    Returns:
        Path to the downloaded uv.exe file.
    """
    # Map our arch names to UV's architecture naming
    arch_map = {
        "amd64": "x86_64",
        "arm64": "aarch64",
    }
    uv_arch = arch_map.get(arch, "x86_64")

    # Download UV zip archive for Windows
    uv_url = (
        f"https://github.com/astral-sh/uv/releases/latest/download/uv-{uv_arch}-pc-windows-msvc.zip"
    )
    uv_zip = ROOT_DIR / "bin" / f"uv-{uv_arch}.zip"
    uv_zip.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading UV executable for {arch}...")
    download_file(uv_url, uv_zip)

    # Extract uv.exe from the zip
    uv_dest = ROOT_DIR / "bin" / "uv.exe"
    with zipfile.ZipFile(uv_zip, "r") as zip_ref:
        # Find and extract uv.exe
        for member in zip_ref.namelist():
            if member.endswith("uv.exe") or member == "uv.exe":
                # Extract with just the filename (no subdirectories)
                with zip_ref.open(member) as source, uv_dest.open("wb") as target:
                    target.write(source.read())
                break

    # Clean up the zip file
    uv_zip.unlink()

    return uv_dest


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    """Extract a ZIP file to a destination directory.

    Args:
        zip_path: Path to the ZIP file to extract.
        dest_dir: Destination directory for extracted files.
    """
    logger.info(f"Extracting {zip_path.name} to {dest_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)


def configure_python(version: str, config: dict[str, str]) -> None:
    """Configure Python embeddable distribution for portable use.

    Args:
        version: Python version string (e.g., '3.12').
        config: Configuration dictionary with dir_name and lib_dir keys.
    """
    python_dir = ROOT_DIR / config["dir_name"]
    lib_dir_name = config["lib_dir"]

    # 1. Modify ._pth file
    # The file is named like python312._pth
    pth_file = python_dir / f"python{version.replace('.', '')}._pth"
    if not pth_file.exists():
        logger.error(f"Error: Could not find {pth_file}")
        sys.exit(1)

    logger.info(f"Configuring {pth_file.name}...")
    with pth_file.open("r") as f:
        lines = f.read().splitlines()

    # Add necessary paths if not present
    # We need to add ..\lib-pyXXX and import site

    # Check if lines already exist to avoid duplication on re-run

    # Normalized search target
    # In ._pth, lines are just paths.
    # Current workflow usage: "../${{ matrix.lib-dir }}"
    target_lib_line = f"../{lib_dir_name}"

    # Add win32 and win32com directories for pywin32 modules
    win32_line = f"../{lib_dir_name}/win32"
    win32com_line = f"../{lib_dir_name}/win32com"

    # We want to ensure 'import site' is active (uncommented)
    # The default file has '#import site'

    final_lines = []
    has_lib = False
    has_active_site = False

    for line in lines:
        stripped = line.strip()

        # Check if this line enables site
        if stripped == "import site":
            has_active_site = True
            final_lines.append(line)
        # Check if this is the commented out line
        elif stripped == "#import site":
            # Uncomment it
            final_lines.append("import site")
            has_active_site = True
        else:
            final_lines.append(line)

        # Check for lib dir
        if target_lib_line in line:
            has_lib = True

    if not has_lib:
        final_lines.append(target_lib_line)

    # Add win32 and win32com paths for pywin32
    if win32_line not in final_lines:
        final_lines.append(win32_line)
    if win32com_line not in final_lines:
        final_lines.append(win32com_line)

    # Fallback if we somehow didn't find the commented line or an active line
    if not has_active_site:
        final_lines.append("import site")

    with pth_file.open("w") as f:
        # Filter out empty strings that might result from splitlines
        f.write("\n".join(filter(None, final_lines)) + "\n")


def generate_version_file() -> None:
    """Pre-generate _version.py using hatch-vcs before installing to embedded Python.

    This is necessary because embeddable Python lacks _socket module needed by hatch-vcs.
    """
    logger.info("Pre-generating version file with hatch-vcs...")
    version_file = ROOT_DIR / "app" / "_version.py"

    # If _version.py already exists and is recent, skip regeneration
    if version_file.exists():
        logger.info("  Using existing _version.py")
        return

    try:
        # Use uv run to generate version with development Python
        subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                "from hatchling.metadata.core import ProjectMetadata; "
                "import pathlib; "
                "pm = ProjectMetadata(str(pathlib.Path.cwd()), None); "
                "version = pm.version; "
                "pathlib.Path('app/_version.py').write_text(f'__version__ = \"{version}\"\\n')",
            ],
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,
            check=True,
        )
        logger.info("  Generated _version.py successfully")
    except subprocess.CalledProcessError as e:
        logger.warning(f"  Failed to generate _version.py: {e.stderr}")
        logger.warning("  Continuing with fallback version detection...")


def install_dependencies(python_dir: Path, lib_dir: Path) -> None:
    """Install Python dependencies into the lib directory.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the target lib directory for dependencies.
    """
    # Determine python executable
    python_exe = python_dir / "python.exe"
    if not python_exe.exists():
        logger.error(f"Error: Python executable not found at {python_exe}")
        sys.exit(1)

    # 2. Install dependencies
    logger.info(f"Installing dependencies into {lib_dir}...")

    # Install build tools first (needed for --no-build-isolation)
    logger.info("Installing build tools (hatchling, hatch-vcs)...")
    build_tools_cmd = [
        "uv",
        "pip",
        "install",
        "hatchling",
        "hatch-vcs",
        "wheel",
        "--target",
        str(lib_dir),
        "--python",
        str(python_exe),
    ]
    subprocess.check_call(build_tools_cmd, cwd=ROOT_DIR)

    # Build wheel with development Python (has all modules needed by hatch-vcs)
    logger.info("Building application wheel with development Python...")
    dist_dir = ROOT_DIR / "dist"
    dist_dir.mkdir(exist_ok=True)

    # Clean old wheels
    for wheel in dist_dir.glob("pymediamanager-*.whl"):
        wheel.unlink()

    build_wheel_cmd = [
        "uv",
        "build",
        "--wheel",
        "--out-dir",
        str(dist_dir),
    ]
    subprocess.check_call(build_wheel_cmd, cwd=ROOT_DIR)

    # Find the built wheel
    wheels = list(dist_dir.glob("pymediamanager-*.whl"))
    if not wheels:
        logger.error("Failed to build wheel")
        sys.exit(1)

    wheel_path = wheels[0]
    logger.info(f"Built wheel: {wheel_path.name}")

    # Install the wheel into embedded Python (with all dependencies)
    logger.info("Installing application wheel with all dependencies into embedded Python...")
    wheel_install_cmd = [
        "uv",
        "pip",
        "install",
        str(wheel_path),
        "--reinstall-package",
        "pymediamanager",
        "--target",
        str(lib_dir),
        "--python",
        str(python_exe),
    ]
    logger.info(f"Running: {' '.join(wheel_install_cmd)}")
    subprocess.check_call(wheel_install_cmd, cwd=ROOT_DIR)

    # 3.5. Set up pywin32
    setup_pywin32(python_dir, lib_dir)

    # 4. Generate _version.py if possible
    # (Disabled: _version.py is generated by hatch-vcs during installation into lib/app)


def setup_pywin32(python_dir: Path, lib_dir: Path) -> None:
    """Set up pywin32 DLLs and modules after installation.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the lib directory containing installed packages.
    """
    logger.info("Running pywin32 post-install setup...")
    try:
        _copy_pywin32_dlls(python_dir, lib_dir)
        _copy_pywin32_modules(python_dir, lib_dir)
        logger.info("pywin32 setup completed successfully")
    except Exception as e:
        logger.warning(f"Warning: pywin32 post-install failed: {e}")
        logger.warning("This may cause issues with Windows-specific functionality")


def _copy_pywin32_dlls(python_dir: Path, lib_dir: Path) -> None:
    """Copy pywin32 DLLs to Python directory.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the lib directory containing installed packages.
    """
    pywin32_system32 = lib_dir / "pywin32_system32"
    if pywin32_system32.exists():
        logger.info("Copying pywin32 DLLs to Python directory...")
        for dll in pywin32_system32.glob("*.dll"):
            dest = python_dir / dll.name
            if not dest.exists():
                shutil.copy2(dll, dest)
                logger.info(f"  Copied {dll.name}")


def _copy_pywin32_py_files(python_dir: Path, lib_dir: Path) -> None:
    """Copy pywin32 .py files from lib and win32/lib to Python directory.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the lib directory containing installed packages.
    """
    pywin32_py_files = [
        "win32con.py",
        "win32api.py",
        "win32event.py",
        "win32evtlog.py",
        "win32file.py",
        "win32gui.py",
        "win32pipe.py",
        "win32print.py",
        "win32process.py",
        "win32security.py",
        "win32service.py",
        "win32timezone.py",
        "winerror.py",  # Required by wmi module
        "pywintypes.py",
        "pythoncom.py",
    ]

    logger.info("Copying pywin32 .py files to Python directory...")
    copied_py = 0

    # Check both lib root and win32/lib subdirectory
    search_paths = [lib_dir, lib_dir / "win32" / "lib"]

    for py_file in pywin32_py_files:
        for search_path in search_paths:
            src = search_path / py_file
            if src.exists():
                dest = python_dir / py_file
                shutil.copy2(src, dest)
                logger.info(f"  Copied {py_file} from {search_path.name}")
                copied_py += 1
                break  # Found it, don't check other paths

    if copied_py == 0:
        logger.warning("  No pywin32 .py files found in lib root or win32/lib")


def _copy_pywin32_pyd_files(python_dir: Path, lib_dir: Path) -> None:
    """Copy pywin32 .pyd files from win32/ to Python directory.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the lib directory containing installed packages.
    """
    win32_dir = lib_dir / "win32"
    if not win32_dir.exists():
        logger.warning(f"  win32 directory not found: {win32_dir}")
        return

    logger.info(f"Copying pywin32 .pyd modules from {win32_dir}...")
    pyd_files = list(win32_dir.glob("*.pyd"))

    if pyd_files:
        for pyd in pyd_files:
            dest = python_dir / pyd.name
            if not dest.exists():
                shutil.copy2(pyd, dest)
                logger.info(f"  Copied {pyd.name}")
    else:
        logger.warning(f"  No .pyd files found in {win32_dir}")

    logger.info("win32/ directory will be accessible via Python path")


def _copy_pywin32_modules(python_dir: Path, lib_dir: Path) -> None:
    """Copy pywin32 .pyd extension modules to Python directory.

    Args:
        python_dir: Path to the Python installation directory.
        lib_dir: Path to the lib directory containing installed packages.
    """
    _copy_pywin32_py_files(python_dir, lib_dir)
    _copy_pywin32_pyd_files(python_dir, lib_dir)

    # Copy top-level .pyd files (pythoncom, pywintypes)
    logger.info("Copying pywin32 core modules to Python directory...")
    found_core = False
    for pyd_pattern in ["pythoncom*.pyd", "pywintypes*.pyd"]:
        for pyd in lib_dir.glob(pyd_pattern):
            found_core = True
            dest = python_dir / pyd.name
            if not dest.exists():
                shutil.copy2(pyd, dest)
                logger.info(f"  Copied {pyd.name}")

    if not found_core:
        logger.warning(f"  No pythoncom/pywintypes .pyd files found in {lib_dir}")


def cleanup_dependencies(lib_dir: Path) -> None:
    """Remove unnecessary files from dependencies to reduce distribution size."""
    logger.info(f"Cleaning up dependencies in {lib_dir}...")

    # Packages that should not have their docs folders removed
    # qfluentwidgets needs its qfluentwidgets/components/widgets/docs folder
    protected_packages = ["qfluentwidgets"]

    patterns_to_remove = [
        "**/tests",
        "**/test",
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/examples",
        "**/*.dist-info/RECORD",
        # NOTE: Keep METADATA files - some packages (like APScheduler) need them at runtime
        # "**/*.dist-info/METADATA",
        "**/*.dist-info/WHEEL",
        "**/LICENSE*",
        "**/README*",
    ]

    removed_count = 0
    removed_size = 0

    for pattern in patterns_to_remove:
        for path in lib_dir.rglob(pattern):
            try:
                if path.is_dir():
                    # Calculate size before removal
                    dir_size = sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
                    shutil.rmtree(path)
                    removed_size += dir_size
                    removed_count += 1
                elif path.is_file():
                    file_size = path.stat().st_size
                    path.unlink()
                    removed_size += file_size
                    removed_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove {path}: {e}")

    # Separately handle docs folders, but skip protected packages
    for docs_path in lib_dir.rglob("**/docs"):
        if docs_path.is_dir():
            # Check if this docs folder belongs to a protected package
            is_protected = any(pkg in str(docs_path) for pkg in protected_packages)
            if is_protected:
                logger.info(f"Protecting docs folder: {docs_path}")
                continue

            try:
                dir_size = sum(f.stat().st_size for f in docs_path.rglob("*") if f.is_file())
                shutil.rmtree(docs_path)
                removed_size += dir_size
                removed_count += 1
            except Exception as e:
                logger.warning(f"Failed to remove {docs_path}: {e}")

    logger.info(
        f"Cleanup complete: removed {removed_count} items, freed {removed_size / 1024 / 1024:.2f} MB"
    )


def verify_critical_imports(python_dir: Path, lib_dir: Path) -> None:
    """Verify that critical dependencies can be imported after cleanup."""
    logger.info("Verifying critical imports...")

    python_exe = python_dir / "python.exe"
    if not python_exe.exists():
        logger.error(f"Python executable not found at {python_exe}")
        sys.exit(1)

    critical_imports = [
        "PySide6.QtWidgets",
        "PySide6.QtCore",
        "qfluentwidgets",
        "pydantic",
        "yaml",
        "git",  # GitPython package is imported as 'git'
    ]

    for module in critical_imports:
        try:
            # Note: We need to add lib_dir, win32/, and win32com/ for pywin32 modules
            # The ._pth file handles this in normal operation, but explicit sys.path tests need it
            # Insert lib_dir LAST so it's checked FIRST (insert(0) puts items at beginning)
            # Order: lib_dir (checked first), then win32/, then win32com/
            win32_path = lib_dir / "win32"
            win32com_path = lib_dir / "win32com"
            test_cmd = [
                str(python_exe),
                "-c",
                f"import sys; sys.path.insert(0, r'{win32com_path}'); sys.path.insert(0, r'{win32_path}'); sys.path.insert(0, r'{lib_dir}'); import {module}; print('OK')",
            ]
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=10,
                check=False,  # Don't raise on error
                cwd=ROOT_DIR,
            )
            if result.returncode == 0 and "OK" in result.stdout:
                logger.info(f"  ✓ {module}")
            else:
                logger.error(f"  ✗ {module} - Import failed")
                if result.stderr:
                    logger.error(f"    Error output: {result.stderr.strip()}")
                if result.stdout:
                    logger.error(f"    Standard output: {result.stdout.strip()}")
                sys.exit(1)
        except subprocess.TimeoutExpired:
            logger.exception(f"  ✗ {module} - Import timeout")
            sys.exit(1)

    logger.info("All critical imports verified successfully!")


def build(  # noqa: C901, PLR0915, PLR0912
    version: str, arch: str = "amd64", build_format: str = "zip", dry_run: bool = False
) -> None:
    """Build a portable Windows distribution for the specified Python version and architecture.

    Args:
        version: Python version to build for (e.g., '3.12').
        arch: Target architecture ('amd64' or 'arm64').
        build_format: Distribution format ('zip', 'msi', or 'both').
        dry_run: If True, validate parameters without creating files.
    """
    if version not in PYTHON_VERSIONS:
        logger.error(f"Unsupported version: {version}")
        logger.info(f"Available versions: {', '.join(PYTHON_VERSIONS.keys())}")
        sys.exit(1)

    if arch not in PYTHON_VERSIONS[version]:
        logger.error(f"Unsupported architecture: {arch}")
        logger.info(f"Available architectures: {', '.join(PYTHON_VERSIONS[version].keys())}")
        sys.exit(1)

    config = PYTHON_VERSIONS[version][arch]
    logger.info(f"Building for Python {version} ({arch})...")

    if dry_run:
        logger.info("[DRY-RUN] Validation complete - no files would be created")
        logger.info(f"[DRY-RUN] Would download: {config['url']}")
        logger.info(f"[DRY-RUN] Would create: {config['dir_name']}")
        logger.info(f"[DRY-RUN] Would create: {config['lib_dir']}")
        logger.info(f"[DRY-RUN] Build format: {build_format}")
        if build_format in ("msi", "both"):
            if version == "3.13":
                logger.info("[DRY-RUN] Would generate MSI installer (Python 3.13)")
            else:
                logger.warning(
                    f"[DRY-RUN] MSI generation only supported for Python 3.13, not {version}"
                )
        return

    # Output dirs
    python_dir_name = config["dir_name"]
    lib_dir_name = config["lib_dir"]

    python_dir = ROOT_DIR / python_dir_name
    lib_dir = ROOT_DIR / lib_dir_name

    if python_dir.exists():
        logger.info(f"Python directory {python_dir} already exists. Skipping download/extract.")
    else:
        python_dir.mkdir(parents=True, exist_ok=True)
        zip_path = ROOT_DIR / f"python-{version}-embed.zip"
        download_file(config["url"], zip_path)
        extract_zip(zip_path, python_dir)

    if not lib_dir.exists():
        lib_dir.mkdir(parents=True, exist_ok=True)

    # Pre-generate version file before installing (embeddable Python lacks _socket module)
    generate_version_file()

    configure_python(version, config)
    install_dependencies(python_dir, lib_dir)

    # Download and bundle UV executable
    uv_exe = download_uv_executable(arch)
    if not uv_exe.exists():
        logger.error("UV executable not found at %s", uv_exe)
        logger.error("UV is required for portable distribution")
        sys.exit(1)
    logger.info(f"UV executable bundled at: {uv_exe.relative_to(ROOT_DIR)}")

    # Cleanup dependencies to reduce size
    cleanup_dependencies(lib_dir)

    # Verify critical imports after cleanup
    verify_critical_imports(python_dir, lib_dir)

    logger.info(f"Build complete for Python {version}.")

    # Create ZIP archive if requested
    if build_format in ("zip", "both"):
        # Verify bin directory exists before creating archive
        bin_dir = ROOT_DIR / "bin"
        if not bin_dir.exists():
            logger.error("bin directory not found at %s", bin_dir)
            sys.exit(1)
        if not (bin_dir / "uv.exe").exists():
            logger.error("uv.exe not found in bin directory")
            logger.error("bin directory contents: %s", list(bin_dir.iterdir()))
            sys.exit(1)
        logger.info("Verified bin/uv.exe exists for archiving")
        _create_zip_archive(version, arch, python_dir, lib_dir)

    # Generate MSI installer if requested
    if build_format in ("msi", "both"):
        _generate_msi_installer(version, arch)


def _create_zip_archive(  # noqa: C901
    version: str, arch: str, python_dir: Path, lib_dir: Path
) -> Path:
    """Create ZIP archive of the portable distribution.

    Args:
        version: Python version (e.g., "3.13")
        arch: Target architecture (e.g., "amd64", "arm64")
        python_dir: Path to Python installation directory
        lib_dir: Path to lib directory with dependencies

    Returns:
        Path to the created ZIP file
    """
    app_version = get_app_version()

    # Map architecture to Windows naming
    arch_mapping = {
        "amd64": "win-amd64",
        "arm64": "win-arm64",
    }
    platform_arch = arch_mapping.get(arch, arch)

    zip_name = f"pyMM-v{app_version}-py{version}-{platform_arch}.zip"

    # Create dist directory
    dist_dir = ROOT_DIR / "dist"
    dist_dir.mkdir(exist_ok=True)

    zip_path = dist_dir / zip_name

    logger.info(f"Creating ZIP archive: {zip_name}...")

    # Create ZIP file
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add python directory
        for file_path in python_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(ROOT_DIR).as_posix()
                zipf.write(file_path, arcname)

        # Add lib directory
        for file_path in lib_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(ROOT_DIR).as_posix()
                zipf.write(file_path, arcname)

        # Add application directories
        app_dirs = [
            ROOT_DIR / "app",
            ROOT_DIR / "plugins",
            ROOT_DIR / "config",
            ROOT_DIR / "templates",
            ROOT_DIR / "bin",
        ]

        for app_dir in app_dirs:
            if app_dir.exists():
                logger.info(f"Adding directory to archive: {app_dir.name}")
                file_count = 0
                for file_path in app_dir.rglob("*"):
                    if file_path.is_file():
                        arcname = file_path.relative_to(ROOT_DIR).as_posix()
                        zipf.write(file_path, arcname)
                        file_count += 1
                logger.info(f"  Added {file_count} files from {app_dir.name}")
            else:
                logger.warning(f"Directory not found, skipping: {app_dir}")

        # Add essential project files
        essential_files = [
            ROOT_DIR / "launcher.py",
            ROOT_DIR / "LICENSE",
            ROOT_DIR / "README.md",
        ]

        for file_path in essential_files:
            if file_path.exists():
                zipf.write(file_path, file_path.name)

    file_size = zip_path.stat().st_size / 1024 / 1024  # Convert to MB
    logger.info(f"✅ ZIP archive created: {zip_path} ({file_size:.2f} MB)")
    return zip_path


def _generate_msi_installer(version: str, arch: str) -> None:
    """Generate MSI installer using wix_generator."""
    logger.info("Generating MSI installer...")
    # Import wix_generator - requires jinja2
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from wix_generator import create_msi_installer  # noqa: PLC0415
    except ImportError:
        logger.exception("Failed to import wix_generator. Run: uv sync --all-extras")
        sys.exit(1)

    try:
        create_msi_installer(version, arch, ROOT_DIR)
        logger.info("MSI installer created successfully")
    except Exception:
        logger.exception("Failed to create MSI installer")
        sys.exit(1)


def main() -> None:
    """Main entry point for the Windows portable distribution builder script."""
    parser = argparse.ArgumentParser(description="Build Portable Distribution")
    parser.add_argument(
        "--version",
        choices=PYTHON_VERSIONS.keys(),
        default="3.12",
        help="Python version to build for",
    )
    parser.add_argument(
        "--arch",
        choices=["amd64", "arm64"],
        default="amd64",
        help="Target architecture (amd64 or arm64)",
    )
    parser.add_argument(
        "--format",
        choices=["zip", "msi", "both"],
        default="zip",
        help="Output format: zip (portable), msi (installer), or both",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parameters without creating build artifacts",
    )
    args = parser.parse_args()

    if platform.system() != "Windows":
        logger.warning(
            "Warning: This script is designed to run on Windows to build Windows embedded distributions."
        )
        logger.warning("Cross-platform building is not strictly supported by this script yet.")
        # Proceeding anyway just in case the user knows what they are doing (e.g. Wine)

    build(args.version, args.arch, args.format, args.dry_run)


if __name__ == "__main__":
    main()
