#!/usr/bin/env python3
"""
Setup Git Hooks
Cross-platform script to set up git hooks using pre-commit.
"""

import shutil
import subprocess
import sys


def main() -> None:
    print("🎣 Setting up Git hooks...")

    # Check if pre-commit is installed
    if not shutil.which("pre-commit"):
        print("⚠️  pre-commit not found. Installing via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pre-commit"])
        except subprocess.CalledProcessError:
            print("❌ Failed to install pre-commit package.")
            sys.exit(1)

    # Run pre-commit install
    print("running 'pre-commit install'...")
    try:
        subprocess.check_call(["pre-commit", "install"])
        print("✅ Git hooks installed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to run pre-commit install.")
        sys.exit(1)
    except FileNotFoundError:
        # Fallback if shutil.which said yes but subprocess failed finding it (e.g. not in PATH yet)
        try:
            subprocess.check_call([sys.executable, "-m", "pre_commit", "install"])
            print("✅ Git hooks installed successfully (via module).")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install hooks: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
