#!/usr/bin/env python3
"""
Test Portable Build Script
Validates portable distributions by extracting, verifying structure, and testing critical imports.
"""

import argparse
import logging
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import zipfile

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("test_portable")


def test_windows_portable(version: str, root_dir: Path) -> bool:  # noqa: C901, PLR0912, PLR0915
    """Test Windows portable ZIP distribution.

    Args:
        version: Python version (e.g., "3.13")
        root_dir: Root directory of the project

    Returns:
        True if all tests pass, False otherwise
    """
    py_nodot = version.replace(".", "")
    archive_name = f"pyMM-*-py{version}-win-amd64.zip"

    # Find the archive in dist directory
    dist_dir = root_dir / "dist"
    archives = list(dist_dir.glob(archive_name)) if dist_dir.exists() else []

    # Fallback to root directory for backward compatibility
    if not archives:
        archives = list(root_dir.glob(archive_name))

    if not archives:
        logger.error(f"Archive not found: {archive_name}")
        return False

    archive_path = archives[0]
    logger.info(f"Testing archive: {archive_path.name}")

    # Extract to temporary directory
    test_dir = root_dir / "test_portable_extract"
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()

    try:
        logger.info("Extracting portable distribution...")
        with zipfile.ZipFile(archive_path, "r") as zip_ref:
            zip_ref.extractall(test_dir)

        # Verify directory structure
        python_dir = test_dir / f"python{py_nodot}"
        lib_dir = test_dir / f"lib-py{py_nodot}"
        required_dirs = [
            python_dir,
            lib_dir,
            test_dir / "app",
            test_dir / "plugins",
            test_dir / "config",
            test_dir / "bin",
        ]

        logger.info("Verifying directory structure...")
        for req_dir in required_dirs:
            if not req_dir.exists():
                logger.error(f"Missing required directory: {req_dir.name}")
                return False
            logger.info(f"  ✓ {req_dir.name}")

        # Verify UV executable
        uv_exe = test_dir / "bin" / "uv.exe"
        if not uv_exe.exists():
            logger.error("UV executable not found")
            return False
        logger.info("  ✓ UV executable found")

        # Test UV version
        try:
            result = subprocess.run(
                [str(uv_exe), "--version"], capture_output=True, text=True, timeout=5, check=False
            )
            if result.returncode == 0:
                logger.info(f"  ✓ UV version: {result.stdout.strip()}")
        except Exception as e:
            logger.warning(f"  ⚠ UV version check failed: {e}")

        # Test launcher
        python_exe = python_dir / "python.exe"
        launcher_py = test_dir / "launcher.py"

        if not python_exe.exists() or not launcher_py.exists():
            logger.error("Python executable or launcher not found")
            return False

        logger.info("Testing launcher --version...")
        try:
            result = subprocess.run(
                [str(python_exe), str(launcher_py), "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                logger.info(f"  ✓ Launcher version: {result.stdout.strip()}")
            else:
                logger.warning(f"  ⚠ Launcher returned non-zero exit code: {result.returncode}")
        except Exception as e:
            logger.warning(f"  ⚠ Launcher test failed: {e}")

        # Test critical imports
        logger.info("Validating critical imports...")
        test_imports = ["PySide6.QtWidgets", "qfluentwidgets", "pydantic", "yaml", "git", "wmi"]
        failed_imports = []

        for module in test_imports:
            try:
                result = subprocess.run(
                    [str(python_exe), "-c", f"import {module}; print('OK')"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
                if result.returncode == 0 and "OK" in result.stdout:
                    logger.info(f"  ✓ {module}")
                else:
                    logger.error(f"  ✗ {module}")
                    failed_imports.append(module)
            except Exception:
                logger.exception(f"  ✗ {module}")
                failed_imports.append(module)

        if failed_imports:
            logger.error(f"Failed imports: {', '.join(failed_imports)}")
            return False

        logger.info("✓ All tests passed!")
        return True

    finally:
        # Cleanup
        if test_dir.exists():
            shutil.rmtree(test_dir, ignore_errors=True)


def test_linux_portable(version: str, root_dir: Path) -> bool:
    """Test Linux AppImage distribution.

    Args:
        version: Python version (e.g., "3.13")
        root_dir: Root directory of the project

    Returns:
        True if all tests pass, False otherwise
    """
    appimage_name = f"pyMM-*-py{version}-linux-x86_64.AppImage"
    dist_dir = root_dir / "dist"

    # Find the AppImage
    appimages = list(dist_dir.glob(appimage_name))
    if not appimages:
        logger.error(f"AppImage not found: {appimage_name}")
        return False

    appimage_path = appimages[0]
    logger.info(f"Testing AppImage: {appimage_path.name}")

    # Verify file exists and size
    size = appimage_path.stat().st_size
    if size < 10_000_000:  # 10MB minimum
        logger.error(f"AppImage too small: {size} bytes")
        return False

    logger.info(f"  ✓ AppImage size: {size / 1024 / 1024:.2f}MB")

    # Make executable
    appimage_path.chmod(0o755)

    # Test --version (may fail in headless environment)
    try:
        result = subprocess.run(
            [str(appimage_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0:
            logger.info(f"  ✓ Version: {result.stdout.strip()}")
    except Exception as e:
        logger.warning(f"  ⚠ --version test failed (expected in CI): {e}")

    logger.info("✓ Basic AppImage tests passed!")
    return True


def test_macos_portable(version: str, root_dir: Path) -> bool:
    """Test macOS DMG distribution.

    Args:
        version: Python version (e.g., "3.13")
        root_dir: Root directory of the project

    Returns:
        True if all tests pass, False otherwise
    """
    dmg_name = f"pyMM-*-py{version}-macos-*.dmg"
    dist_dir = root_dir / "dist"

    # Find the DMG
    dmgs = list(dist_dir.glob(dmg_name))
    if not dmgs:
        logger.error(f"DMG not found: {dmg_name}")
        return False

    dmg_path = dmgs[0]
    logger.info(f"Testing DMG: {dmg_path.name}")

    # Verify file exists and size
    size = dmg_path.stat().st_size
    if size < 10_000_000:  # 10MB minimum
        logger.error(f"DMG too small: {size} bytes")
        return False

    logger.info(f"  ✓ DMG size: {size / 1024 / 1024:.2f}MB")
    logger.info("✓ Basic DMG tests passed!")
    return True


def main() -> None:
    """Main entry point for portable build testing."""
    parser = argparse.ArgumentParser(description="Test portable build distributions")
    parser.add_argument("--version", default="3.13", help="Python version to test")
    args = parser.parse_args()

    root_dir = Path(__file__).parent.parent.resolve()
    system = platform.system()

    logger.info(f"Testing portable build for Python {args.version} on {system}")

    success = False
    if system == "Windows":
        success = test_windows_portable(args.version, root_dir)
    elif system == "Linux":
        success = test_linux_portable(args.version, root_dir)
    elif system == "Darwin":
        success = test_macos_portable(args.version, root_dir)
    else:
        logger.error(f"Unsupported platform: {system}")
        sys.exit(1)

    if not success:
        logger.error("Portable build tests failed")
        sys.exit(1)

    logger.info("All portable build tests passed successfully!")


if __name__ == "__main__":
    main()
