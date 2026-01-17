"""
Configuration service for pyMediaManager.
Handles layered configuration (defaults → environment → user) with Pydantic models.
"""

from __future__ import annotations

from enum import Enum
import os
from pathlib import Path
import shutil
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
import yaml

from app import __commit_id__, __version__
from app.core.platform import Platform, current_platform


def get_platform_config_dir(app_name: str = "pyMediaManager") -> Path:
    """Get platform-specific configuration directory.

    Follows platform conventions:
    - Windows: %APPDATA%/pyMediaManager
    - Linux: $XDG_CONFIG_HOME/pymediamanager or ~/.config/pymediamanager
    - macOS: ~/Library/Application Support/pyMediaManager

    Args:
        app_name: Application name for directory

    Returns:
        Path to configuration directory
    """
    match current_platform():
        case Platform.WINDOWS:
            # Windows: %APPDATA%\pyMediaManager
            base_dir = Path(os.getenv("APPDATA", "~")).expanduser()
            return base_dir / app_name
        case Platform.MACOS:
            # macOS: ~/Library/Application Support/pyMediaManager
            return Path.home() / "Library" / "Application Support" / app_name
        case Platform.LINUX:
            # Linux: XDG Base Directory
            xdg_config = os.getenv("XDG_CONFIG_HOME")
            base_dir = Path(xdg_config) if xdg_config else Path.home() / ".config"
            return base_dir / app_name.lower()


def get_platform_data_dir(app_name: str = "pyMediaManager") -> Path:
    """Get platform-specific data directory.

    Follows platform conventions:
    - Windows: %APPDATA%/pyMediaManager
    - Linux: $XDG_DATA_HOME/pymediamanager or ~/.local/share/pymediamanager
    - macOS: ~/Library/Application Support/pyMediaManager

    Args:
        app_name: Application name for directory

    Returns:
        Path to data directory
    """
    match current_platform():
        case Platform.WINDOWS:
            # Windows: %APPDATA%\pyMediaManager
            base_dir = Path(os.getenv("APPDATA", "~")).expanduser()
            return base_dir / app_name
        case Platform.MACOS:
            # macOS: ~/Library/Application Support/pyMediaManager
            return Path.home() / "Library" / "Application Support" / app_name
        case Platform.LINUX:
            # Linux: XDG Base Directory
            xdg_data = os.getenv("XDG_DATA_HOME")
            base_dir = Path(xdg_data) if xdg_data else Path.home() / ".local" / "share"
            return base_dir / app_name.lower()


def get_platform_cache_dir(app_name: str = "pyMediaManager") -> Path:
    """Get platform-specific cache directory.

    Follows platform conventions:
    - Windows: %LOCALAPPDATA%/pyMediaManager/Cache
    - Linux: $XDG_CACHE_HOME/pymediamanager or ~/.cache/pymediamanager
    - macOS: ~/Library/Caches/pyMediaManager

    Args:
        app_name: Application name for directory

    Returns:
        Path to cache directory
    """
    match current_platform():
        case Platform.WINDOWS:
            # Windows: %LOCALAPPDATA%\pyMediaManager\Cache
            base_dir = Path(os.getenv("LOCALAPPDATA", "~")).expanduser()
            return base_dir / app_name / "Cache"
        case Platform.MACOS:
            # macOS: ~/Library/Caches/pyMediaManager
            return Path.home() / "Library" / "Caches" / app_name
        case Platform.LINUX:
            # Linux: XDG Base Directory
            xdg_cache = os.getenv("XDG_CACHE_HOME")
            base_dir = Path(xdg_cache) if xdg_cache else Path.home() / ".cache"
            return base_dir / app_name.lower()


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ExecutionPreference(str, Enum):
    """Plugin execution preference."""

    AUTO = "auto"  # Use plugin's prefer_system setting
    SYSTEM = "system"  # Always prefer system packages
    PORTABLE = "portable"  # Always use portable binaries


class PathConfig(BaseModel):
    """Configuration for application paths.

    Paths can be absolute or relative. Relative paths are resolved against:
    - config_dir: platform-specific config directory (when None, uses platform default)
    - Other paths: user's home directory
    """

    projects_dir: str = Field(
        default="pyMM.Projects", description="Projects directory name (relative to home)"
    )
    logs_dir: str = Field(default="pyMM.Logs", description="Logs directory name (relative to home)")
    plugins_dir: str = Field(
        default="pyMM.Plugins", description="Plugins directory name (relative to home)"
    )
    config_dir: str | None = Field(
        default=None, description="Config directory (None = use platform default)"
    )


class LoggingConfig(BaseModel):
    """Configuration for logging."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Default log level")
    console_enabled: bool = Field(default=True, description="Enable console logging")
    file_enabled: bool = Field(default=True, description="Enable file logging")
    max_file_size: int = Field(default=10485760, description="Max log file size (10MB)")
    backup_count: int = Field(default=5, description="Number of backup log files")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )


class UIConfig(BaseModel):
    """Configuration for UI settings."""

    theme: str = Field(default="auto", description="UI theme (light/dark/auto)")
    show_first_run: bool = Field(default=True, description="Show first-run wizard")
    window_width: int = Field(default=1200, description="Default window width")
    window_height: int = Field(default=800, description="Default window height")


class PluginConfig(BaseModel):
    """Configuration for plugin system."""

    auto_update_check: bool = Field(default=True, description="Check for plugin updates")
    download_timeout: int = Field(default=300, description="Download timeout in seconds")
    parallel_downloads: int = Field(default=3, description="Max parallel downloads")


class PluginPreferences(BaseModel):
    """Per-plugin execution preferences.

    Allows users to override prefer_system setting for individual plugins.
    """

    execution_preference: ExecutionPreference = Field(
        default=ExecutionPreference.AUTO, description="Execution preference (auto/system/portable)"
    )
    enabled: bool = Field(default=True, description="Whether plugin is enabled")
    notes: str = Field(default="", description="User notes about this plugin")


class AppConfig(BaseModel):
    """Main application configuration."""

    model_config = ConfigDict(extra="allow")

    app_name: str = Field(default="pyMediaManager", description="Application name")
    app_version: str = Field(default=__version__, description="Application version")
    app_commit: str | None = Field(default=__commit_id__, description="Git commit hash")
    paths: PathConfig = Field(default_factory=PathConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)
    plugin_preferences: dict[str, PluginPreferences] = Field(
        default_factory=dict,
        description="Per-plugin execution preferences (plugin_id -> PluginPreferences)",
    )

    # Sensitive fields that should be redacted in logs
    _sensitive_fields: set[str] = {"password", "token", "secret", "key", "api_key"}

    def to_dict(self, redact_sensitive: bool = False) -> dict[str, Any]:
        """
        Convert config to dictionary.

        Args:
            redact_sensitive: If True, replace sensitive values with [REDACTED]

        Returns:
            Dictionary representation of config
        """
        data = self.model_dump(mode="json")

        if redact_sensitive:
            data = self._redact_sensitive_data(data)

        return data

    def _redact_sensitive_data(self, data: Any) -> Any:
        """Recursively redact sensitive data in configuration."""
        if isinstance(data, dict):
            return {
                key: (
                    "[REDACTED]"
                    if any(sensitive in key.lower() for sensitive in self._sensitive_fields)
                    else self._redact_sensitive_data(value)
                )
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        return data


class ConfigService:
    """Service for managing layered application configuration."""

    def __init__(self, app_root: Path | str | None = None, config_dir: Path | str | None = None):
        """
        Initialize configuration service.

        Args:
            app_root: Application root directory (for legacy fallback, deprecated)
            config_dir: Configuration directory (defaults to platform-specific location)
        """
        # Use platform-specific directory if not explicitly provided
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            self.config_dir = get_platform_config_dir()

        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Legacy support: app_root for backward compatibility
        self.app_root = Path(app_root) if app_root else self.config_dir.parent

        self._config: AppConfig | None = None
        self._user_config_path = self.config_dir / "user.yaml"
        self._default_config_path = self.config_dir / "app.yaml"
        self._plugin_preferences_path = self.config_dir / "plugins.yaml"

        # Try to migrate old config if exists and new location is empty
        self._migrate_legacy_config()

    def _migrate_legacy_config(self) -> None:
        """Migrate configuration from legacy location if needed.

        Checks for config files in app_root/config and copies them to
        the platform-specific location if it's empty.
        """
        # Skip if user config already exists in new location
        if self._user_config_path.exists():
            return

        # Check for legacy config location (app_root/config)
        if self.app_root != self.config_dir.parent:
            legacy_config_dir = self.app_root / "config"
            if legacy_config_dir.exists():
                legacy_user_config = legacy_config_dir / "user.yaml"
                legacy_default_config = legacy_config_dir / "app.yaml"

                # Copy user config if exists
                if legacy_user_config.exists():
                    shutil.copy2(legacy_user_config, self._user_config_path)

                # Copy default config if exists
                if legacy_default_config.exists():
                    shutil.copy2(legacy_default_config, self._default_config_path)

    def load(self) -> AppConfig:
        """
        Load configuration from all layers (defaults → file → environment → user).

        Returns:
            Loaded AppConfig object
        """
        # Start with default config
        config_data: dict[str, Any] = {}

        # Layer 1: Load from default config file if exists
        if self._default_config_path.exists():
            with open(self._default_config_path, encoding="utf-8") as f:
                default_data = yaml.safe_load(f) or {}
                config_data.update(default_data)

        # Layer 2: Load from user config file if exists
        if self._user_config_path.exists():
            with open(self._user_config_path, encoding="utf-8") as f:
                user_data = yaml.safe_load(f) or {}
                config_data = self._merge_dicts(config_data, user_data)

        # Create Pydantic model from merged data
        self._config = AppConfig(**config_data)

        # Layer 3: Load plugin preferences from separate file
        self._config.plugin_preferences = self.load_plugin_preferences()

        return self._config

    def save_user_config(self, config: AppConfig) -> None:
        """
        Save user configuration to user.yaml.

        Args:
            config: AppConfig object to save
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(self._user_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(mode="json"), f, default_flow_style=False, sort_keys=False)

    def get_config(self) -> AppConfig:
        """
        Get current configuration, loading it if not already loaded.

        Returns:
            Current AppConfig object
        """
        if self._config is None:
            self.load()
        assert self._config is not None
        return self._config

    def update_config(self, **kwargs: Any) -> AppConfig:
        """
        Update configuration values and save to user config.

        Args:
            **kwargs: Configuration values to update

        Returns:
            Updated AppConfig object
        """
        config = self.get_config()

        # Update config with new values
        updated_data = config.model_dump()
        updated_data.update(kwargs)

        # Create new config and save
        new_config = AppConfig(**updated_data)
        self.save_user_config(new_config)
        self._config = new_config

        return new_config

    def reset_to_defaults(self) -> AppConfig:
        """
        Reset configuration to defaults by removing user config.

        Returns:
            Default AppConfig object
        """
        if self._user_config_path.exists():
            self._user_config_path.unlink()

        self._config = None
        return self.load()

    def _merge_dicts(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively merge two dictionaries.

        Args:
            base: Base dictionary
            override: Dictionary with override values

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value

        return result

    def load_plugin_preferences(self) -> dict[str, PluginPreferences]:
        """
        Load plugin preferences from plugins.yaml.

        Returns:
            Dictionary mapping plugin IDs to PluginPreferences
        """
        if not self._plugin_preferences_path.exists():
            return {}

        with open(self._plugin_preferences_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        preferences = {}
        for plugin_id, pref_data in data.items():
            try:
                preferences[plugin_id] = PluginPreferences(**pref_data)
            except (TypeError, ValueError) as e:
                # Log error but continue loading other preferences
                print(f"Warning: Failed to load preferences for plugin {plugin_id}: {e}")  # noqa: T201
                continue

        return preferences

    def save_plugin_preferences(self, preferences: dict[str, PluginPreferences]) -> None:
        """
        Save plugin preferences to plugins.yaml.

        Args:
            preferences: Dictionary mapping plugin IDs to PluginPreferences
        """
        # Convert preferences to dict format
        data = {plugin_id: pref.model_dump(mode="json") for plugin_id, pref in preferences.items()}

        # Ensure config directory exists
        self._plugin_preferences_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to file
        with open(self._plugin_preferences_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def get_plugin_preference(self, plugin_id: str) -> PluginPreferences:
        """
        Get preference for a specific plugin.

        Args:
            plugin_id: Plugin identifier

        Returns:
            PluginPreferences for the plugin (default if not set)
        """
        config = self.get_config()
        return config.plugin_preferences.get(plugin_id, PluginPreferences())

    def set_plugin_preference(
        self, plugin_id: str, preference: PluginPreferences | None = None, **kwargs: Any
    ) -> None:
        """
        Set preference for a specific plugin.

        Args:
            plugin_id: Plugin identifier
            preference: PluginPreferences object (or None to use kwargs)
            **kwargs: Preference fields to update (execution_preference, enabled, notes)
        """
        config = self.get_config()

        # Get existing preference or create new one
        if preference is None:
            current = config.plugin_preferences.get(plugin_id, PluginPreferences())
            # Update with kwargs
            preference = PluginPreferences(
                execution_preference=kwargs.get(
                    "execution_preference", current.execution_preference
                ),
                enabled=kwargs.get("enabled", current.enabled),
                notes=kwargs.get("notes", current.notes),
            )

        # Update in-memory config
        config.plugin_preferences[plugin_id] = preference

        # Save to disk
        self.save_plugin_preferences(config.plugin_preferences)

    def export_config(self, output_path: Path, redact_sensitive: bool = True) -> None:
        """
        Export current configuration to a file.

        Args:
            output_path: Path to output file
            redact_sensitive: If True, redact sensitive values
        """
        config = self.get_config()
        data = config.to_dict(redact_sensitive=redact_sensitive)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
