"""Tests for ConfigService."""

from pathlib import Path

import pytest
import yaml

from app import __commit_id__, __version__
from app.core.services.config_service import (
    AppConfig,
    ConfigService,
    LoggingConfig,
    LogLevel,
    UIConfig,
)


class TestAppConfig:
    """Test suite for AppConfig model."""

    def test_default_config(self):
        """Test default configuration values."""
        config = AppConfig()

        assert config.app_name == "pyMediaManager"
        assert config.app_version == __version__
        assert config.app_commit == __commit_id__
        assert config.paths.projects_dir == "pyMM.Projects"
        assert config.logging.level == LogLevel.INFO
        assert config.ui.show_first_run is True

    def test_config_with_overrides(self):
        """Test configuration with custom values."""
        config = AppConfig(
            app_name="CustomApp",
            logging=LoggingConfig(level=LogLevel.DEBUG),
            ui=UIConfig(theme="dark", window_width=1600),
        )

        assert config.app_name == "CustomApp"
        assert config.logging.level == LogLevel.DEBUG
        assert config.ui.theme == "dark"
        assert config.ui.window_width == 1600

    def test_to_dict_without_redaction(self):
        """Test converting config to dict without redaction."""
        config = AppConfig()
        data = config.to_dict(redact_sensitive=False)

        assert isinstance(data, dict)
        assert data["app_name"] == "pyMediaManager"
        assert "paths" in data
        assert "logging" in data

    def test_to_dict_with_redaction(self):
        """Test sensitive data redaction."""
        config = AppConfig()
        # Manually add a sensitive field for testing
        config_dict = config.model_dump()
        config_dict["api_key"] = "secret-key-123"
        config_dict["password"] = "secret-password"

        # Create new config with sensitive data
        test_config = AppConfig(**config_dict)
        redacted = test_config.to_dict(redact_sensitive=True)

        assert redacted["api_key"] == "[REDACTED]"
        assert redacted["password"] == "[REDACTED]"


class TestConfigService:
    """Test suite for ConfigService."""

    @pytest.fixture
    def service(self, app_root):
        """Create ConfigService instance."""
        # Use explicit config_dir for tests to avoid platform-specific locations
        config_dir = app_root / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return ConfigService(app_root=app_root, config_dir=config_dir)

    def test_init(self, service, app_root):
        """Test service initialization."""
        assert service.app_root == app_root
        assert service.config_dir == app_root / "config"

    def test_load_default_config(self, service):
        """Test loading default configuration when no files exist."""
        config = service.load()

        assert isinstance(config, AppConfig)
        assert config.app_name == "pyMediaManager"

    def test_load_with_default_file(self, service, app_root):
        """Test loading configuration from default file."""
        # Create default config file
        default_config = {
            "app_name": "TestApp",
            "logging": {"level": "DEBUG"},
        }

        config_dir = app_root / "config"
        config_dir.mkdir(exist_ok=True)

        with open(config_dir / "app.yaml", "w") as f:
            yaml.dump(default_config, f)

        config = service.load()

        assert config.app_name == "TestApp"
        assert config.logging.level == LogLevel.DEBUG

    def test_load_with_user_override(self, service, app_root):
        """Test user configuration overrides default."""
        # Create default config
        default_config = {
            "app_name": "DefaultApp",
            "ui": {"theme": "light"},
        }

        # Create user config
        user_config = {
            "app_name": "UserApp",
            "ui": {"theme": "dark"},
        }

        config_dir = app_root / "config"
        config_dir.mkdir(exist_ok=True)

        with open(config_dir / "app.yaml", "w") as f:
            yaml.dump(default_config, f)

        with open(config_dir / "user.yaml", "w") as f:
            yaml.dump(user_config, f)

        config = service.load()

        # User config should override defaults
        assert config.app_name == "UserApp"
        assert config.ui.theme == "dark"

    def test_save_user_config(self, service, app_root):
        """Test saving user configuration."""
        config = AppConfig(app_name="SavedApp", ui=UIConfig(theme="dark"))

        service.save_user_config(config)

        user_file = app_root / "config" / "user.yaml"
        assert user_file.exists()

        # Verify saved content
        with open(user_file) as f:
            data = yaml.safe_load(f)

        assert data["app_name"] == "SavedApp"
        assert data["ui"]["theme"] == "dark"

    def test_get_config_lazy_load(self, service):
        """Test lazy loading of configuration."""
        # Config should be None initially
        assert service._config is None

        config = service.get_config()

        # Should load and cache
        assert isinstance(config, AppConfig)
        assert service._config is config

        # Second call should return cached
        config2 = service.get_config()
        assert config2 is config

    def test_update_config(self, service, app_root):
        """Test updating configuration values."""
        # Initial load
        service.load()

        # Update config
        updated = service.update_config(ui=UIConfig(theme="dark", window_width=1920))

        assert updated.ui.theme == "dark"
        assert updated.ui.window_width == 1920

        # Verify saved to user config
        user_file = app_root / "config" / "user.yaml"
        assert user_file.exists()

    def test_reset_to_defaults(self, service, app_root):
        """Test resetting configuration to defaults."""
        # Create user config
        user_file = app_root / "config" / "user.yaml"
        user_file.parent.mkdir(exist_ok=True)
        user_file.write_text("app_name: CustomApp")

        assert user_file.exists()

        # Reset
        config = service.reset_to_defaults()

        assert not user_file.exists()
        assert config.app_name == "pyMediaManager"  # Default value

    def test_export_config(self, service, app_root):
        """Test exporting configuration to file."""
        config = service.load()

        export_path = app_root / "export" / "config.yaml"
        service.export_config(export_path, redact_sensitive=False)

        assert export_path.exists()

        with open(export_path) as f:
            data = yaml.safe_load(f)

        assert data["app_name"] == config.app_name

    def test_export_config_with_redaction(self, service, app_root):
        """Test exporting with sensitive data redacted."""
        service.load()

        export_path = app_root / "export" / "config_redacted.yaml"
        service.export_config(export_path, redact_sensitive=True)

        assert export_path.exists()

    def test_merge_dicts_simple(self, service):
        """Test simple dictionary merging."""
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}

        result = service._merge_dicts(base, override)

        assert result == {"a": 1, "b": 3, "c": 4}

    def test_merge_dicts_nested(self, service):
        """Test nested dictionary merging."""
        base = {"level1": {"a": 1, "b": 2}, "other": "value"}
        override = {"level1": {"b": 3, "c": 4}}

        result = service._merge_dicts(base, override)

        assert result["level1"] == {"a": 1, "b": 3, "c": 4}
        assert result["other"] == "value"


class TestPlatformDirectories:
    """Test suite for platform-specific directory functions."""

    def test_get_platform_config_dir_windows(self, monkeypatch):
        """Test getting config dir on Windows."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_config_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.WINDOWS
        )
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")

        config_dir = get_platform_config_dir("TestApp")

        # Compare string paths to avoid platform-specific path separators
        assert str(config_dir).replace("/", "\\") == "C:\\Users\\Test\\AppData\\Roaming\\TestApp"

    def test_get_platform_config_dir_linux(self, monkeypatch):
        """Test getting config dir on Linux with XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_config_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.setenv("XDG_CONFIG_HOME", "/home/test/.config")

        config_dir = get_platform_config_dir("TestApp")

        assert config_dir == Path("/home/test/.config/testapp")

    def test_get_platform_config_dir_linux_no_xdg(self, monkeypatch):
        """Test getting config dir on Linux without XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_config_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)

        config_dir = get_platform_config_dir("TestApp")

        # Check it's in .config directory with lowercased app name
        assert ".config" in str(config_dir)
        assert "testapp" in str(config_dir)

    def test_get_platform_config_dir_macos(self, monkeypatch):
        """Test getting config dir on macOS."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_config_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.MACOS
        )

        config_dir = get_platform_config_dir("TestApp")

        # Check it's in Library/Application Support
        assert "Library" in str(config_dir)
        assert "Application Support" in str(config_dir)
        assert "TestApp" in str(config_dir)

    def test_get_platform_data_dir_windows(self, monkeypatch):
        """Test getting data dir on Windows."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_data_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.WINDOWS
        )
        monkeypatch.setenv("APPDATA", "C:\\Users\\Test\\AppData\\Roaming")

        data_dir = get_platform_data_dir("TestApp")

        # Compare string paths to avoid platform-specific path separators
        assert str(data_dir).replace("/", "\\") == "C:\\Users\\Test\\AppData\\Roaming\\TestApp"

    def test_get_platform_data_dir_linux(self, monkeypatch):
        """Test getting data dir on Linux with XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_data_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.setenv("XDG_DATA_HOME", "/home/test/.local/share")

        data_dir = get_platform_data_dir("TestApp")

        assert data_dir == Path("/home/test/.local/share/testapp")

    def test_get_platform_data_dir_linux_no_xdg(self, monkeypatch):
        """Test getting data dir on Linux without XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_data_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)

        data_dir = get_platform_data_dir("TestApp")

        # Check it's in .local/share with lowercased app name
        assert ".local" in str(data_dir)
        assert "share" in str(data_dir)
        assert "testapp" in str(data_dir)

    def test_get_platform_data_dir_macos(self, monkeypatch):
        """Test getting data dir on macOS."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_data_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.MACOS
        )

        data_dir = get_platform_data_dir("TestApp")

        # Check it's in Library/Application Support
        assert "Library" in str(data_dir)
        assert "Application Support" in str(data_dir)
        assert "TestApp" in str(data_dir)

    def test_get_platform_cache_dir_windows(self, monkeypatch):
        """Test getting cache dir on Windows."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_cache_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.WINDOWS
        )
        monkeypatch.setenv("LOCALAPPDATA", "C:\\Users\\Test\\AppData\\Local")

        cache_dir = get_platform_cache_dir("TestApp")

        # Compare string paths to avoid platform-specific path separators
        assert (
            str(cache_dir).replace("/", "\\") == "C:\\Users\\Test\\AppData\\Local\\TestApp\\Cache"
        )

    def test_get_platform_cache_dir_linux(self, monkeypatch):
        """Test getting cache dir on Linux with XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_cache_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.setenv("XDG_CACHE_HOME", "/home/test/.cache")

        cache_dir = get_platform_cache_dir("TestApp")

        assert cache_dir == Path("/home/test/.cache/testapp")

    def test_get_platform_cache_dir_linux_no_xdg(self, monkeypatch):
        """Test getting cache dir on Linux without XDG."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_cache_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.LINUX
        )
        monkeypatch.delenv("XDG_CACHE_HOME", raising=False)

        cache_dir = get_platform_cache_dir("TestApp")

        # Check it's in .cache with lowercased app name
        assert ".cache" in str(cache_dir)
        assert "testapp" in str(cache_dir)

    def test_get_platform_cache_dir_macos(self, monkeypatch):
        """Test getting cache dir on macOS."""
        from app.core.platform import Platform
        from app.core.services.config_service import get_platform_cache_dir

        monkeypatch.setattr(
            "app.core.services.config_service.current_platform", lambda: Platform.MACOS
        )

        cache_dir = get_platform_cache_dir("TestApp")

        # Check it's in Library/Caches
        assert "Library" in str(cache_dir)
        assert "Caches" in str(cache_dir)
        assert "TestApp" in str(cache_dir)
