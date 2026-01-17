"""
Plugin manager for discovering, installing, and managing plugins.
"""

from __future__ import annotations

from collections.abc import Callable
import logging
from pathlib import Path
from typing import Any

from pydantic import ValidationError
import yaml

from app.plugins.plugin_base import PluginBase, PluginManifest, SimplePluginImplementation
from app.plugins.plugin_schema import PluginManifestSchema


class PluginManager:
    """Manager for application plugins."""

    def __init__(
        self,
        plugins_dir: Path,
        manifests_dir: Path,
    ):
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
        manifest_files = list(self.manifests_dir.rglob("plugin.yaml"))

        for manifest_file in manifest_files:
            try:
                manifest = self._load_manifest(manifest_file)
                if manifest:
                    self.manifests[manifest.name] = manifest
                    # Create plugin instance
                    plugin = self._create_plugin_instance(manifest)
                    if plugin:
                        self.plugins[manifest.name] = plugin
            except ValidationError:
                # Log validation errors but continue with other plugins
                self.logger.exception("Plugin manifest validation failed: %s", manifest_file)
            except Exception:
                # Log errors but continue with other plugins
                self.logger.exception("Error loading manifest %s", manifest_file)

        return len(self.plugins)

    def _load_manifest(self, manifest_file: Path) -> PluginManifest | None:
        """
        Load plugin manifest from YAML file with strict schema validation.

        Args:
            manifest_file: Path to plugin.yaml file

        Returns:
            PluginManifest object or None if loading fails

        Raises:
            ValidationError: If manifest fails schema validation (fails fast)
        """
        try:
            with open(manifest_file, encoding="utf-8") as f:
                data = yaml.safe_load(f)

            def raise_empty_manifest() -> None:
                """Raise error for empty manifest file.

                Raises:
                    ValueError: Always raised with descriptive message.
                """
                msg = f"Empty manifest file: {manifest_file}"
                self.logger.error(msg)
                raise ValueError(msg)

            if not data:
                raise_empty_manifest()

            # Validate against Pydantic schema (fails fast on validation errors)
            try:
                validated_data = PluginManifestSchema(**data)
            except ValidationError:
                self.logger.exception(f"Schema validation failed for {manifest_file}")
                raise

            # Import platform manifest
            from app.plugins.plugin_base import PlatformManifest

            # Extract platform-specific configurations
            platforms = validated_data.platforms

            def _extract_platform_config(platform_key: str) -> PlatformManifest | None:
                """Extract platform configuration from validated data."""
                if platforms is None or platform_key not in platforms:
                    return None

                pc = platforms[platform_key]
                return PlatformManifest(
                    source_type=pc.source.type if pc.source else None,
                    source_uri=pc.source.base_uri if pc.source else None,
                    asset_pattern=pc.source.asset_pattern if pc.source else None,
                    checksum_sha256=pc.source.checksum_sha256 if pc.source else None,
                    file_size=pc.source.file_size if pc.source else None,
                    command_path=pc.command.path,
                    command_executable=pc.command.executable,
                    system_package=pc.system_package,
                    version_constraint=pc.version_constraint,
                )

            return PluginManifest(
                name=validated_data.name,
                version=validated_data.version,
                mandatory=validated_data.mandatory,
                enabled=validated_data.enabled,
                prefer_system=validated_data.prefer_system,
                register_to_path=validated_data.register_to_path,
                dependencies=validated_data.dependencies or [],
                windows_config=_extract_platform_config("windows"),
                linux_config=_extract_platform_config("linux"),
                macos_config=_extract_platform_config("macos"),
            )

        except ValidationError:
            # Re-raise validation errors to fail fast
            raise
        except Exception:
            self.logger.exception(f"Error parsing manifest {manifest_file}")
            raise

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

        # Check if manifest has platform config with source
        platform_config = manifest.get_current_platform_config()
        if platform_config and platform_config.source_type == "url" and platform_config.source_uri:
            return SimplePluginImplementation(
                manifest, self.plugins_dir, platform_config.source_uri
            )

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
        except Exception:
            self.logger.exception(f"Exception during installation of {name}")
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
