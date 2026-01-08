#!/usr/bin/env python3
"""
Build Manager
Routes build requests to the appropriate platform-specific builder.
"""

from pathlib import Path
import platform
import subprocess
import sys


def main() -> None:
    system = platform.system()
    script_dir = Path(__file__).parent.resolve()

    # Pass through arguments (like --version)
    args = sys.argv[1:]

    print(f"[BUILD] Build Manager: Detected platform '{system}'")

    if system == "Windows":
        script = script_dir / "build_windows.py"
        if not script.exists():
            print(f"[ERROR] {script.name} not found!")
            sys.exit(1)

        cmd = [sys.executable, str(script), *args]
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

        cmd = [sys.executable, str(script), *args]
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

        cmd = [sys.executable, str(script), *args]
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
