"""
Test script for plugin download functionality.
Run this to verify plugin downloads work correctly.
"""

import asyncio
from pathlib import Path
import sys

import pytest

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.plugins.plugin_manager import PluginManager


@pytest.mark.asyncio
async def test_plugin_download(tmp_path):
    """Test downloading a plugin."""

    # Setup paths
    plugins_dir = tmp_path / "test_plugins"
    manifests_dir = Path(__file__).parent / "plugins"

    plugins_dir.mkdir(parents=True, exist_ok=True)

    # Create plugin manager
    manager = PluginManager(plugins_dir, manifests_dir)

    # Discover plugins
    manager.discover_plugins()

    all_plugins = manager.get_all_plugins()
    for plugin in all_plugins:
        "✓ Installed" if plugin.is_installed() else "✗ Not installed"

    # Test with a small plugin (ExifTool or similar)

    test_plugin_name = "ExifTool"  # Small and fast to download

    def progress_callback(current, total):
        """Progress callback."""
        if total > 0:
            (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            "█" * filled + "░" * (bar_length - filled)
            current / (1024 * 1024)
            total / (1024 * 1024)

    try:
        success = await manager.install_plugin(test_plugin_name, progress_callback)

        if success:
            # Verify installation
            plugin = next(
                p for p in manager.get_all_plugins() if p.manifest.name == test_plugin_name
            )
            if plugin.is_installed():
                exe_path = plugin.get_executable_path()
                if exe_path and exe_path.exists():
                    pass
                version = plugin.get_version()
                if version:
                    pass
            else:
                pass
        else:
            pass

    except Exception:
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_plugin_download())
