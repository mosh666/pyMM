"""
Configuration service for pyMediaManager.
Handles layered configuration (defaults → environment → user) with Pydantic models.
"""
from pathlib import Path
from typing import Any, Dict, Optional
from enum import Enum
import yaml
from pydantic import BaseModel, Field, field_validator


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class PathConfig(BaseModel):
    """Configuration for application paths."""

    projects_dir: str = Field(default="pyMM.Projects", description="Projects directory name")
    logs_dir: str = Field(default="pyMM.Logs", description="Logs directory name")
    plugins_dir: str = Field(default="pyMM.Plugins", description="Plugins directory name")
    config_dir: str = Field(default="config", description="Config directory name")


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


class AppConfig(BaseModel):
    """Main application configuration."""

    app_name: str = Field(default="pyMediaManager", description="Application name")
    app_version: str = Field(default="0.0.1", description="Application version")
    paths: PathConfig = Field(default_factory=PathConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    plugins: PluginConfig = Field(default_factory=PluginConfig)

    # Sensitive fields that should be redacted in logs
    _sensitive_fields: set = {"password", "token", "secret", "key", "api_key"}

    def to_dict(self, redact_sensitive: bool = False) -> Dict[str, Any]:
        """
        Convert config to dictionary.

        Args:
            redact_sensitive: If True, replace sensitive values with [REDACTED]

        Returns:
            Dictionary representation of config
        """
        data = self.model_dump()

        if redact_sensitive:
            data = self._redact_sensitive_data(data)

        return data

    def _redact_sensitive_data(self, data: Any) -> Any:
        """Recursively redact sensitive data in configuration."""
        if isinstance(data, dict):
            return {
                key: "[REDACTED]"
                if any(sensitive in key.lower() for sensitive in self._sensitive_fields)
                else self._redact_sensitive_data(value)
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        else:
            return data


class ConfigService:
    """Service for managing layered application configuration."""

    def __init__(self, app_root: Path, config_dir: Optional[Path] = None):
        """
        Initialize configuration service.

        Args:
            app_root: Application root directory
            config_dir: Configuration directory (defaults to app_root/config)
        """
        self.app_root = Path(app_root)
        self.config_dir = Path(config_dir) if config_dir else self.app_root / "config"

        self._config: Optional[AppConfig] = None
        self._user_config_path = self.config_dir / "user.yaml"
        self._default_config_path = self.config_dir / "app.yaml"

    def load(self) -> AppConfig:
        """
        Load configuration from all layers (defaults → file → environment → user).

        Returns:
            Loaded AppConfig object
        """
        # Start with default config
        config_data = {}

        # Layer 1: Load from default config file if exists
        if self._default_config_path.exists():
            with open(self._default_config_path, "r", encoding="utf-8") as f:
                default_data = yaml.safe_load(f) or {}
                config_data.update(default_data)

        # Layer 2: Load from user config file if exists
        if self._user_config_path.exists():
            with open(self._user_config_path, "r", encoding="utf-8") as f:
                user_data = yaml.safe_load(f) or {}
                config_data = self._merge_dicts(config_data, user_data)

        # Layer 3: Override with environment variables (TODO: implement)
        # config_data = self._apply_env_overrides(config_data)

        # Create Pydantic model from merged data
        self._config = AppConfig(**config_data)
        return self._config

    def save_user_config(self, config: AppConfig) -> None:
        """
        Save user configuration to user.yaml.

        Args:
            config: AppConfig object to save
        """
        self.config_dir.mkdir(parents=True, exist_ok=True)

        with open(self._user_config_path, "w", encoding="utf-8") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False, sort_keys=False)

    def get_config(self) -> AppConfig:
        """
        Get current configuration, loading it if not already loaded.

        Returns:
            Current AppConfig object
        """
        if self._config is None:
            self.load()
        return self._config

    def update_config(self, **kwargs) -> AppConfig:
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

    def _merge_dicts(self, base: Dict, override: Dict) -> Dict:
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
