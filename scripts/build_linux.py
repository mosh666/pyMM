#!/usr/bin/env python3
"""
Linux Build Script (Helper)
Assists with Flatpak generation or clean-up.
"""

from pathlib import Path
import shutil
import sys


def main() -> None:
    print("🐧 Linux Build Helper")

    root_dir = Path(__file__).parent.parent.resolve()
    flatpak_dir = root_dir / "dist" / "flatpak"
    manifest = flatpak_dir / "org.pymmediamanager.yaml"

    if not manifest.exists():
        print(f"❌ Flatpak manifest not found at {manifest}")
        sys.exit(1)

    print(f"✅ Flatpak manifest located at: {manifest.relative_to(root_dir)}")

    # Check for flatpak-builder
    if not shutil.which("flatpak-builder"):
        print("⚠️  'flatpak-builder' is not installed or not in PATH.")
        print("   Please install it (e.g., 'sudo apt install flatpak-builder').")
        sys.exit(1)

    print("\nTo build and install the Flatpak, you can run:")
    print(f"flatpak-builder --user --install build-dir {manifest} --force-clean")

    # Optional: We could actually run it if the user passed a flag like --run-builder
    # But usually builds are better explicit on Linux.


if __name__ == "__main__":
    main()
