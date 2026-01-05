"""
Plugin manager for discovering, installing, and managing plugins.
"""

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from app.plugins.plugin_base import PluginBase, PluginManifest, SimplePluginImplementation


class PluginManager:
    """Manager for application plugins."""

    def __init__(self, plugins_dir: Path, manifests_dir: Path):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory where plugins are installed (e.g., D:\\pyMM.Plugins)
            manifests_dir: Directory containing plugin manifest YAML files
        """
        self.logger = logging.getLogger(__name__)
        self.plugins_dir = Path(plugins_dir)
        self.manifests_dir = Path(manifests_dir)
        self.plugins: dict[str, PluginBase] = {}
        self.manifests: dict[str, PluginManifest] = {}

    def discover_plugins(self) -> int:
        """
        Discover plugins from manifest files.

        Returns:
            Number of plugins discovered
        """
        self.manifests.clear()
        self.plugins.clear()

        if not self.manifests_dir.exists():
            return 0

        # Find all plugin.yaml files in subdirectories
        manifest_files = self.manifests_dir.rglob("plugin.yaml")

        for manifest_file in manifest_files:
            try:
                manifest = self._load_manifest(manifest_file)
                if manifest:
                    self.manifests[manifest.name] = manifest
                    # Create plugin instance
                    plugin = self._create_plugin_instance(manifest)
                    if plugin:
                        self.plugins[manifest.name] = plugin
            except Exception as e:
                # Log error but continue discovering
                self.logger.warning(f"Error loading manifest {manifest_file}: {e}")

        return len(self.plugins)

    def _load_manifest(self, manifest_file: Path) -> PluginManifest | None:
        """
        Load plugin manifest from YAML file.

        Args:
            manifest_file: Path to plugin.yaml file

        Returns:
            PluginManifest object or None if loading fails
        """
        try:
            with open(manifest_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                return None

            # Extract source configuration
            source = data.get("source", {})

            manifest = PluginManifest(
                name=data["name"],
                version=data.get("version", "unknown"),
                mandatory=data.get("mandatory", False),
                enabled=data.get("enabled", True),
                source_type=source.get("type", "url"),
                source_uri=source.get("base_uri", ""),
                asset_pattern=source.get("asset_pattern"),
                checksum_sha256=source.get("checksum_sha256"),
                file_size=source.get("file_size"),
                command_path=data.get("command", {}).get("path", ""),
                command_executable=data.get("command", {}).get("executable", ""),
                register_to_path=data.get("register_to_path", False),
                dependencies=data.get("dependencies", []),
            )

            return manifest
        except Exception as e:
            self.logger.error(f"Error parsing manifest: {e}")
            return None

    def _create_plugin_instance(self, manifest: PluginManifest) -> PluginBase | None:
        """
        Create plugin instance from manifest.

        Args:
            manifest: Plugin manifest

        Returns:
            Plugin instance or None
        """
        # For now, use SimplePluginImplementation
        # In future, could load custom plugin classes via entry points

        if manifest.source_type == "url" and manifest.source_uri:
            # Construct download URL (simplified for now)
            download_url = manifest.source_uri
            return SimplePluginImplementation(manifest, self.plugins_dir, download_url)

        return None

    def get_plugin(self, name: str) -> PluginBase | None:
        """
        Get plugin by name.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self.plugins.get(name)

    def get_all_plugins(self) -> list[PluginBase]:
        """
        Get all discovered plugins.

        Returns:
            List of plugin instances
        """
        return list(self.plugins.values())

    def get_mandatory_plugins(self) -> list[PluginBase]:
        """
        Get mandatory plugins only.

        Returns:
            List of mandatory plugin instances
        """
        return [p for p in self.plugins.values() if p.manifest.mandatory]

    def get_optional_plugins(self) -> list[PluginBase]:
        """
        Get optional plugins only.

        Returns:
            List of optional plugin instances
        """
        return [p for p in self.plugins.values() if not p.manifest.mandatory]

    def get_enabled_plugins(self) -> list[PluginBase]:
        """
        Get enabled plugins only.

        Returns:
            List of enabled plugin instances
        """
        return [p for p in self.plugins.values() if p.manifest.enabled]

    def get_installed_plugins(self) -> list[PluginBase]:
        """
        Get plugins that are currently installed.

        Returns:
            List of installed plugin instances
        """
        return [p for p in self.plugins.values() if p.is_installed()]

    async def install_plugin(
        self, name: str, progress_callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """
        Install a plugin by name.

        Args:
            name: Plugin name
            progress_callback: Optional callback for progress updates

        Returns:
            True if installation successful
        """
        plugin = self.get_plugin(name)
        if not plugin:
            self.logger.error(f"Plugin {name} not found in registry")
            return False

        try:
            # Download
            self.logger.info(f"Downloading {name}...")
            download_success = await plugin.download(progress_callback)
            if not download_success:
                self.logger.error(f"Download failed for {name}")
                return False

            # Extract
            self.logger.info(f"Extracting {name}...")
            extract_success = await plugin.extract()
            if not extract_success:
                self.logger.error(f"Extraction failed for {name}")
                return False

            # Validate
            self.logger.info(f"Validating {name}...")
            is_valid = plugin.validate_installation()
            if not is_valid:
                self.logger.error(f"Validation failed for {name}")
            return is_valid
        except Exception as e:
            self.logger.error(f"Exception during installation of {name}: {e}")
            import traceback

            traceback.print_exc()
            return False

    async def uninstall_plugin(self, name: str) -> bool:
        """
        Uninstall a plugin by name.

        Args:
            name: Plugin name

        Returns:
            True if uninstallation successful
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return False

        return await plugin.uninstall()

    async def update_plugin(
        self, name: str, progress_callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """
        Update a plugin to latest version.

        Args:
            name: Plugin name
            progress_callback: Optional callback for progress updates

        Returns:
            True if update successful
        """
        # Uninstall then reinstall
        if not await self.uninstall_plugin(name):
            return False

        return await self.install_plugin(name, progress_callback)

    def get_plugin_status(self, name: str) -> dict[str, Any]:
        """
        Get detailed status of a plugin.

        Args:
            name: Plugin name

        Returns:
            Dictionary with plugin status information
        """
        plugin = self.get_plugin(name)
        if not plugin:
            return {"exists": False}

        return {
            "exists": True,
            "name": plugin.manifest.name,
            "version": plugin.get_version(),
            "installed": plugin.is_installed(),
            "mandatory": plugin.manifest.mandatory,
            "enabled": plugin.manifest.enabled,
            "executable": (
                str(plugin.get_executable_path()) if plugin.get_executable_path() else None
            ),
        }

    def register_plugins_to_path(self) -> list[Path]:
        """
        Get list of plugin paths that should be registered to PATH.

        Returns:
            List of paths to add to PATH environment variable
        """
        paths = []

        for plugin in self.get_enabled_plugins():
            if plugin.manifest.register_to_path and plugin.is_installed():
                exe_path = plugin.get_executable_path()
                if exe_path:
                    # Add the directory containing the executable
                    paths.append(exe_path.parent)

        return paths
