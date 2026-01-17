#!/usr/bin/env python3
"""List all available plugins in pyMediaManager.

This example demonstrates:
- Initializing the PluginManager
- Discovering available plugins
- Checking installation status
- Accessing plugin metadata
"""

import logging
from pathlib import Path

from app.plugins.plugin_manager import PluginManager

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """List all plugins with their installation status."""
    # Initialize plugin manager
    # In a real app, this would come from dependency injection
    plugins_dir = Path("plugins")

    if not plugins_dir.exists():
        logger.error(f"Plugins directory not found: {plugins_dir}")
        return

    plugin_manager = PluginManager(plugins_dir=plugins_dir)

    # Get all available plugins
    plugins = plugin_manager.discover_plugins()

    for plugin in plugins:
        # Check if plugin is installed
        "Installed" if plugin_manager.is_installed(plugin.name) else "Available"

        # Truncate long descriptions
        (plugin.description[:40] + "..." if len(plugin.description) > 40 else plugin.description)

    # Show installed plugins separately
    [p for p in plugins if plugin_manager.is_installed(p.name)]


if __name__ == "__main__":
    main()
