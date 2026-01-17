"""Load a specific plugin and display its manifest.

This example demonstrates loading plugin manifests and accessing properties.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.plugins.plugin_manager import PluginManager


def main() -> None:
    """Load and display plugin information."""
    if len(sys.argv) < 2:
        print("Usage: python load_plugin.py <plugin_name>")
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

    print(f"Plugin: {plugin.name}")
    print(f"Version: {plugin.version}")
    print(f"Schema Version: {plugin.schema_version}")
    print(f"Category: {plugin.category}")
    print(f"Description: {plugin.description}")
    print(f"Enabled: {plugin.enabled}")
    print(f"Mandatory: {plugin.mandatory}")
    print(f"Platforms: {', '.join(plugin.platforms)}")

    if plugin.dependencies:
        print("\nDependencies:")
        for dep in plugin.dependencies:
            print(f"  - {dep}")

    if hasattr(plugin, "installation") and plugin.installation:
        print("\nInstallation:")
        for platform, config in plugin.installation.items():
            print(f"  {platform}:")
            if "download_url" in config:
                print(f"    URL: {config['download_url']}")
            if "sha256" in config:
                print(f"    SHA256: {config['sha256']}")


if __name__ == "__main__":
    main()
