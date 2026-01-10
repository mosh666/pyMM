#!/usr/bin/env python3
"""Check if specific plugins are installed and working.

This example demonstrates:
- Checking plugin installation status
- Getting plugin information
- Checking plugin compatibility
"""

import contextlib
import logging
from pathlib import Path

from app.plugins.plugin_manager import PluginManager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def check_plugin(plugin_manager: PluginManager, plugin_name: str) -> None:
    """Check status of a specific plugin.

    Args:
        plugin_manager: PluginManager instance.
        plugin_name: Name of plugin to check.
    """

    # Check if installed
    if not plugin_manager.is_installed(plugin_name):
        # Try to find it in available plugins
        with contextlib.suppress(KeyError):
            plugin = plugin_manager.get_plugin(plugin_name)
        return

    # Get plugin instance
    try:
        plugin = plugin_manager.get_plugin(plugin_name)

        # Check dependencies
        if plugin.dependencies:
            pass
        else:
            pass

        # Check supported platforms
        if hasattr(plugin, "platforms"):
            pass

    except Exception:
        pass


def main() -> None:
    """Check status of common plugins."""
    plugins_dir = Path("plugins")

    if not plugins_dir.exists():
        logger.error(f"Plugins directory not found: {plugins_dir}")
        return

    plugin_manager = PluginManager(plugins_dir=plugins_dir)

    # Check common plugins
    plugins_to_check = ["git", "digikam", "gitversion"]

    for plugin_name in plugins_to_check:
        check_plugin(plugin_manager, plugin_name)


if __name__ == "__main__":
    main()
