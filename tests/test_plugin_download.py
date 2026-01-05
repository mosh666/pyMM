"""
Test script for plugin download functionality.
Run this to verify plugin downloads work correctly.
"""

import asyncio
from pathlib import Path
import sys

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.plugins.plugin_manager import PluginManager


async def test_plugin_download():
    """Test downloading a plugin."""
    print("=" * 60)
    print("Plugin Download Test")
    print("=" * 60)

    # Setup paths
    app_root = Path(__file__).parent
    plugins_dir = app_root / "test_plugins"
    manifests_dir = app_root / "plugins"

    # Clean test directory
    if plugins_dir.exists():
        import shutil

        shutil.rmtree(plugins_dir)
    plugins_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nTest directory: {plugins_dir}")
    print(f"Manifests directory: {manifests_dir}")

    # Create plugin manager
    manager = PluginManager(plugins_dir, manifests_dir)

    # Discover plugins
    print("\nDiscovering plugins...")
    manager.discover_plugins()

    all_plugins = manager.get_all_plugins()
    print(f"Found {len(all_plugins)} plugins:")
    for plugin in all_plugins:
        status = "✓ Installed" if plugin.is_installed() else "✗ Not installed"
        print(f"  - {plugin.manifest.name} ({status})")

    # Test with a small plugin (ExifTool or similar)
    print("\n" + "=" * 60)
    print("Testing plugin installation")
    print("=" * 60)

    test_plugin_name = "ExifTool"  # Small and fast to download
    print(f"\nAttempting to install: {test_plugin_name}")

    def progress_callback(current, total):
        """Progress callback."""
        if total > 0:
            percent = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            size_mb = current / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            print(f"\r[{bar}] {percent:.1f}% ({size_mb:.2f}/{total_mb:.2f} MB)", end="", flush=True)

    try:
        print("Starting download from plugin manifest...")
        success = await manager.install_plugin(test_plugin_name, progress_callback)
        print()  # New line after progress

        if success:
            print(f"✓ {test_plugin_name} installed successfully!")

            # Verify installation
            plugin = next(
                p for p in manager.get_all_plugins() if p.manifest.name == test_plugin_name
            )
            if plugin.is_installed():
                print("✓ Installation verified")
                exe_path = plugin.get_executable_path()
                if exe_path and exe_path.exists():
                    print(f"✓ Executable found: {exe_path}")
                version = plugin.get_version()
                if version:
                    print(f"✓ Version: {version}")
            else:
                print("✗ Installation verification failed")
        else:
            print(f"✗ Failed to install {test_plugin_name}")

    except Exception as e:
        print(f"\n✗ Error during installation: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Test complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_plugin_download())
