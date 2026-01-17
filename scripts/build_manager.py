#!/usr/bin/env python3
"""Build manager entry point for pyMediaManager.

Routes build requests to the appropriate platform-specific builder.
Supports Windows, Linux, and macOS with configurable Python versions
and architectures.
"""

import argparse
from pathlib import Path
import platform
import subprocess
import sys


def main() -> None:  # noqa: C901, PLR0912, PLR0915
    """Build portable distributions for pyMediaManager across platforms."""
    parser = argparse.ArgumentParser(description="Build portable distributions for pyMediaManager")
    parser.add_argument(
        "--version",
        default="3.13",
        help="Python version to build for (e.g., 3.12, 3.13, 3.14)",
    )
    parser.add_argument(
        "--arch",
        default=None,
        help="Target architecture (e.g., amd64, arm64, x86_64). Auto-detected if not specified.",
    )
    parser.add_argument(
        "--format",
        default=None,
        help="Output format (Windows: zip/msi/both, macOS: dmg, Linux: appimage). "
        "Platform-specific defaults apply if not specified.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parameters without creating build artifacts",
    )

    args = parser.parse_args()

    system = platform.system()
    script_dir = Path(__file__).parent.resolve()

    print(f"[BUILD] Build Manager: Detected platform '{system}'")

    # Build command-line arguments for platform-specific builders
    builder_args = ["--version", args.version]

    if args.arch:
        builder_args.extend(["--arch", args.arch])

    if args.format:
        builder_args.extend(["--format", args.format])

    if args.dry_run:
        builder_args.append("--dry-run")
        print("[INFO] Dry-run mode enabled - no files will be created")

    print(f"[INFO] Build parameters: Python {args.version}", end="")
    if args.arch:
        print(f", arch={args.arch}", end="")
    if args.format:
        print(f", format={args.format}", end="")
    print()

    if system == "Windows":
        script = script_dir / "build_windows.py"
        if not script.exists():
            print(f"[ERROR] {script.name} not found!")
            sys.exit(1)

        cmd = [sys.executable, str(script), *builder_args]
        print("[INFO] Launching Windows build...")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    elif system == "Linux":
        script = script_dir / "build_linux_appimage.py"
        if not script.exists():
            print(f"[ERROR] {script.name} not found!")
            sys.exit(1)

        cmd = [sys.executable, str(script), *builder_args]
        print("[INFO] Launching Linux AppImage build...")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    elif system == "Darwin":
        script = script_dir / "build_macos.py"
        if not script.exists():
            print(f"[ERROR] {script.name} not found!")
            sys.exit(1)

        cmd = [sys.executable, str(script), *builder_args]
        print("[INFO] Launching macOS build...")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)

    else:
        print(f"[WARNING] Unsupported platform for automated build: {system}")
        sys.exit(1)


if __name__ == "__main__":
    main()
