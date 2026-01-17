"""List all available plugins and their status.

This example demonstrates querying the plugin manager for all plugins.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.plugins.plugin_manager import PluginManager


def main() -> None:
    """List all plugins with their status."""
    manager = PluginManager()
    plugins = manager.get_all_plugins()

    if not plugins:
        print("No plugins found.")
        return

    print(f"Found {len(plugins)} plugin(s):\n")

    for plugin in plugins:
        status = "\u2705 Enabled" if plugin.enabled else "\u274c Disabled"
        mandatory = " [MANDATORY]" if plugin.mandatory else ""
        print(f"{plugin.name} v{plugin.version} - {status}{mandatory}")
        print(f"  Category: {plugin.category}")
        print(f"  Description: {plugin.description}")
        print(f"  Platforms: {', '.join(plugin.platforms)}")
        if plugin.dependencies:
            print(f"  Dependencies: {', '.join(plugin.dependencies)}")
        print()


if __name__ == "__main__":
    main()
