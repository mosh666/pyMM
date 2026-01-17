"""Check plugin dependencies and display dependency tree.

This example demonstrates dependency resolution in the plugin system.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.plugins.plugin_manager import PluginManager


def print_dependencies(manager: PluginManager, plugin_name: str, level: int = 0) -> None:
    """Recursively print plugin dependencies."""
    indent = "  " * level
    plugin = manager.get_plugin(plugin_name)

    if not plugin:
        print(f"{indent}\u274c {plugin_name} (not found)")
        return

    symbol = "\u2705" if plugin.enabled else "\u274c"
    print(f"{indent}{symbol} {plugin.name} v{plugin.version}")

    if plugin.dependencies:
        for dep in plugin.dependencies:
            print_dependencies(manager, dep, level + 1)


def main() -> None:
    """Display plugin dependency tree."""
    if len(sys.argv) < 2:
        print("Usage: python plugin_dependencies.py <plugin_name>")
        print("\nAvailable plugins:")
        manager = PluginManager()
        for plugin in manager.get_all_plugins():
            print(f"  {plugin.name}")
        sys.exit(1)

    plugin_name = sys.argv[1]
    manager = PluginManager()
    plugin = manager.get_plugin(plugin_name)

    if not plugin:
        print(f"Plugin not found: {plugin_name}")
        sys.exit(1)

    print(f"Dependency tree for: {plugin.name}\n")

    if not plugin.dependencies:
        print("No dependencies.")
    else:
        print_dependencies(manager, plugin_name)


if __name__ == "__main__":
    main()
