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

try:
    from setuptools_scm import get_version
except ImportError:
    get_version = None  # type: ignore[assignment]

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("builder")

# Python Embeddable Distributions
PYTHON_VERSIONS = {
    "3.12": {
        "url": "https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip",
        "dir_name": "python312",
        "lib_dir": "lib-py312",
    },
    "3.13": {
        "url": "https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip",
        "dir_name": "python313",
        "lib_dir": "lib-py313",
    },
    "3.14": {
        "url": "https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-amd64.zip",
        "dir_name": "python314",
        "lib_dir": "lib-py314",
    },
}

ROOT_DIR = Path(__file__).parent.parent.resolve()


def download_file(url: str, dest: Path) -> None:
    if dest.exists():
        logger.info(f"Using cached {dest.name}")
        return
    logger.info(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest)  # noqa: S310
    except Exception:
        logger.exception(f"Failed to download {url}")
        sys.exit(1)


def extract_zip(zip_path: Path, dest_dir: Path) -> None:
    logger.info(f"Extracting {zip_path.name} to {dest_dir}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(dest_dir)


def configure_python(version: str, config: dict[str, str]) -> None:
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

    # Fallback if we somehow didn't find the commented line or an active line
    if not has_active_site:
        final_lines.append("import site")

    with pth_file.open("w") as f:
        # Filter out empty strings that might result from splitlines
        f.write("\n".join(filter(None, final_lines)) + "\n")


def install_dependencies(python_dir: Path, lib_dir: Path) -> None:
    # Determine python executable
    python_exe = python_dir / "python.exe"
    if not python_exe.exists():
        logger.error(f"Error: Python executable not found at {python_exe}")
        sys.exit(1)

    # 1. Install pip
    logger.info("Installing pip...")
    get_pip_path = ROOT_DIR / "get-pip.py"
    if not get_pip_path.exists():
        download_file("https://bootstrap.pypa.io/get-pip.py", get_pip_path)

    subprocess.check_call(
        [str(python_exe), str(get_pip_path), "--no-warn-script-location"], cwd=ROOT_DIR
    )

    # 2. Install dependencies
    logger.info(f"Installing dependencies into {lib_dir}...")

    # Install build tools first (needed for --no-build-isolation)
    logger.info("Installing build tools (setuptools, wheel)...")
    build_tools_cmd = [
        str(python_exe),
        "-m",
        "pip",
        "install",
        "setuptools>=61.0",
        "wheel",
        "setuptools_scm",
        "--target",
        str(lib_dir),
        "--no-warn-script-location",
    ]
    subprocess.check_call(build_tools_cmd, cwd=ROOT_DIR)

    # Check for requirements.lock
    lockfile = ROOT_DIR / "requirements.lock"

    if lockfile.exists():
        logger.info(f"Using lockfile: {lockfile}")
        # Install from lockfile
        install_cmd = [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "-r",
            str(lockfile),
            "--target",
            str(lib_dir),
            "--no-warn-script-location",
        ]
        logger.info(f"Running: {' '.join(install_cmd)}")
        subprocess.check_call(install_cmd, cwd=ROOT_DIR)

        # Install the app package itself (without deps since they are in lockfile)
        logger.info("Installing application package...")
        app_install_cmd = [
            str(python_exe),
            "-m",
            "pip",
            "install",
            ".",
            "--no-deps",
            "--no-build-isolation",
            "--target",
            str(lib_dir),
            "--no-warn-script-location",
        ]
        logger.info(f"Running: {' '.join(app_install_cmd)}")
        subprocess.check_call(app_install_cmd, cwd=ROOT_DIR)

    else:
        logger.info("No requirements.lock found. Installing from pyproject.toml...")
        # We must ensure build-system requirements are met if we install from source.
        # However, for an embeddable python, we might get away with pip's default behavior.
        # We pass '.' to install the current project (and thus its dependencies)
        install_cmd = [
            str(python_exe),
            "-m",
            "pip",
            "install",
            ".",
            "--target",
            str(lib_dir),
            "--no-warn-script-location",
        ]

        logger.info(f"Running: {' '.join(install_cmd)}")
        subprocess.check_call(install_cmd, cwd=ROOT_DIR)

    # 3. Cleanup: Remove the 'app' package if it got installed into lib
    app_in_lib = lib_dir / "app"
    if app_in_lib.exists():
        logger.info(f"Removing {app_in_lib} to prefer source directory usage...")
        shutil.rmtree(app_in_lib)

    # 4. Generate _version.py if possible
    try:
        if get_version is None:
            raise ImportError("setuptools_scm not installed")  # noqa: TRY301

        version = get_version(root=ROOT_DIR, version_scheme="post-release")
        version_file = ROOT_DIR / "app" / "_version.py"
        logger.info(f"Generating {version_file} with version {version}...")
        with version_file.open("w") as f:
            f.write(
                f"# file generated by setuptools_scm\n# don't change, don't track in version control\n__version__ = version = \"{version}\"\n__version_tuple__ = version_tuple = {tuple(version.split('.'))}\n"
            )
    except ImportError:
        logger.warning("Warning: setuptools_scm not installed. Skipping _version.py generation.")
    except Exception as e:
        logger.warning(f"Warning: Failed to generate _version.py: {e}")


def build(version: str) -> None:
    if version not in PYTHON_VERSIONS:
        logger.error(f"Unsupported version: {version}")
        logger.info(f"Available versions: {', '.join(PYTHON_VERSIONS.keys())}")
        sys.exit(1)

    config = PYTHON_VERSIONS[version]
    logger.info(f"Building for Python {version}...")

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

    configure_python(version, config)
    install_dependencies(python_dir, lib_dir)
    logger.info(f"Build complete for Python {version}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Portable Distribution")
    parser.add_argument(
        "--version",
        choices=PYTHON_VERSIONS.keys(),
        default="3.12",
        help="Python version to build for",
    )
    args = parser.parse_args()

    if platform.system() != "Windows":
        logger.warning(
            "Warning: This script is designed to run on Windows to build Windows embedded distributions."
        )
        logger.warning("Cross-platform building is not strictly supported by this script yet.")
        # Proceeding anyway just in case the user knows what they are doing (e.g. Wine)

    build(args.version)


if __name__ == "__main__":
    main()
