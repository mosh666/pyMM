"""Tests for platform portable configuration."""

from app.core.platform import PortableConfig, PortableMode


class TestPortableMode:
    """Test suite for PortableMode enum."""

    def test_portable_mode_values(self):
        """Test PortableMode enum values."""
        assert PortableMode.CLI.value == "cli"
        assert PortableMode.ENV.value == "env"
        assert PortableMode.AUTO.value == "auto"
        assert PortableMode.DEFAULT.value == "default"

    def test_portable_mode_members(self):
        """Test all PortableMode members exist."""
        modes = list(PortableMode)
        assert len(modes) == 4
        assert PortableMode.CLI in modes
        assert PortableMode.ENV in modes
        assert PortableMode.AUTO in modes
        assert PortableMode.DEFAULT in modes


class TestPortableConfig:
    """Test suite for PortableConfig dataclass."""

    def test_create_portable_config_cli(self):
        """Test creating portable config from CLI."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
            auto_detected_removable=False,
        )

        assert config.enabled is True
        assert config.source == PortableMode.CLI
        assert config.auto_detected_removable is False

    def test_create_portable_config_env(self):
        """Test creating portable config from environment."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.ENV,
        )

        assert config.enabled is True
        assert config.source == PortableMode.ENV
        assert config.auto_detected_removable is False  # Default value

    def test_create_portable_config_auto_removable(self):
        """Test creating portable config with auto-detected removable."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.AUTO,
            auto_detected_removable=True,
        )

        assert config.enabled is True
        assert config.source == PortableMode.AUTO
        assert config.auto_detected_removable is True

    def test_create_non_portable_config(self):
        """Test creating non-portable config."""
        config = PortableConfig(
            enabled=False,
            source=PortableMode.DEFAULT,
        )

        assert config.enabled is False
        assert config.source == PortableMode.DEFAULT
        assert config.auto_detected_removable is False

    def test_portable_config_string_representation_cli(self):
        """Test string representation for CLI source."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        result = str(config)

        assert "Portable" in result
        assert "command line" in result

    def test_portable_config_string_representation_env(self):
        """Test string representation for ENV source."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.ENV,
        )

        result = str(config)

        assert "Portable" in result
        assert "environment variable" in result

    def test_portable_config_string_representation_auto(self):
        """Test string representation for AUTO source."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.AUTO,
            auto_detected_removable=False,
        )

        result = str(config)

        assert "Portable" in result
        assert "auto-detected" in result

    def test_portable_config_string_representation_auto_removable(self):
        """Test string representation for AUTO source with removable media."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.AUTO,
            auto_detected_removable=True,
        )

        result = str(config)

        assert "Portable" in result
        assert "auto-detected" in result
        assert "removable media" in result

    def test_portable_config_string_representation_default(self):
        """Test string representation for DEFAULT source."""
        config = PortableConfig(
            enabled=False,
            source=PortableMode.DEFAULT,
        )

        result = str(config)

        assert "Installed" in result

    def test_portable_config_installed_mode(self):
        """Test config representing installed (non-portable) mode."""
        config = PortableConfig(
            enabled=False,
            source=PortableMode.DEFAULT,
        )

        assert config.enabled is False
        assert "Installed" in str(config)

    def test_portable_config_equality(self):
        """Test portable config equality comparison."""
        config1 = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        config2 = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        # Dataclasses should be equal if all fields match
        assert config1.enabled == config2.enabled
        assert config1.source == config2.source
        assert config1.auto_detected_removable == config2.auto_detected_removable

    def test_portable_config_inequality(self):
        """Test portable config inequality."""
        config1 = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        config2 = PortableConfig(
            enabled=False,
            source=PortableMode.ENV,
        )

        assert config1.enabled != config2.enabled
        assert config1.source != config2.source

    def test_portable_config_with_all_sources(self):
        """Test creating config with each possible source."""
        sources = [
            PortableMode.CLI,
            PortableMode.ENV,
            PortableMode.AUTO,
            PortableMode.DEFAULT,
        ]

        for source in sources:
            config = PortableConfig(
                enabled=True,
                source=source,
            )

            assert config.source == source
            assert isinstance(str(config), str)

    def test_portable_config_default_auto_detected_removable(self):
        """Test default value of auto_detected_removable is False."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        assert config.auto_detected_removable is False

    def test_portable_config_boolean_enabled(self):
        """Test that enabled field is strictly boolean."""
        config_enabled = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        config_disabled = PortableConfig(
            enabled=False,
            source=PortableMode.DEFAULT,
        )

        assert isinstance(config_enabled.enabled, bool)
        assert isinstance(config_disabled.enabled, bool)
        assert config_enabled.enabled is True
        assert config_disabled.enabled is False

    def test_portable_config_source_type(self):
        """Test that source is a PortableMode enum."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.CLI,
        )

        assert isinstance(config.source, PortableMode)
        assert config.source in PortableMode

    def test_portable_config_removable_type(self):
        """Test that auto_detected_removable is boolean."""
        config = PortableConfig(
            enabled=True,
            source=PortableMode.AUTO,
            auto_detected_removable=True,
        )

        assert isinstance(config.auto_detected_removable, bool)
        assert config.auto_detected_removable is True


class TestPlatformHelpers:
    """Test suite for platform helper functions."""

    def test_current_platform_windows(self, monkeypatch):
        """Test current_platform returns Windows on win32."""
        from app.core.platform import Platform, current_platform

        monkeypatch.setattr("sys.platform", "win32")
        assert current_platform() == Platform.WINDOWS

    def test_current_platform_linux(self, monkeypatch):
        """Test current_platform returns Linux."""
        from app.core.platform import Platform, current_platform

        monkeypatch.setattr("sys.platform", "linux")
        assert current_platform() == Platform.LINUX

    def test_current_platform_macos(self, monkeypatch):
        """Test current_platform returns macOS on darwin."""
        from app.core.platform import Platform, current_platform

        monkeypatch.setattr("sys.platform", "darwin")
        assert current_platform() == Platform.MACOS

    def test_is_windows_true(self, monkeypatch):
        """Test is_windows returns True on Windows."""
        from app.core.platform import is_windows

        monkeypatch.setattr("sys.platform", "win32")
        assert is_windows() is True

    def test_is_windows_false(self, monkeypatch):
        """Test is_windows returns False on non-Windows."""
        from app.core.platform import is_windows

        monkeypatch.setattr("sys.platform", "linux")
        assert is_windows() is False

    def test_is_linux_true(self, monkeypatch):
        """Test is_linux returns True on Linux."""
        from app.core.platform import is_linux

        monkeypatch.setattr("sys.platform", "linux")
        assert is_linux() is True

    def test_is_linux_false(self, monkeypatch):
        """Test is_linux returns False on non-Linux."""
        from app.core.platform import is_linux

        monkeypatch.setattr("sys.platform", "win32")
        assert is_linux() is False

    def test_is_macos_true(self, monkeypatch):
        """Test is_macos returns True on macOS."""
        from app.core.platform import is_macos

        monkeypatch.setattr("sys.platform", "darwin")
        assert is_macos() is True

    def test_is_macos_false(self, monkeypatch):
        """Test is_macos returns False on non-macOS."""
        from app.core.platform import is_macos

        monkeypatch.setattr("sys.platform", "win32")
        assert is_macos() is False

    def test_is_unix_true_linux(self, monkeypatch):
        """Test is_unix returns True on Linux."""
        from app.core.platform import is_unix

        monkeypatch.setattr("sys.platform", "linux")
        assert is_unix() is True

    def test_is_unix_true_macos(self, monkeypatch):
        """Test is_unix returns True on macOS."""
        from app.core.platform import is_unix

        monkeypatch.setattr("sys.platform", "darwin")
        assert is_unix() is True

    def test_is_unix_false_windows(self, monkeypatch):
        """Test is_unix returns False on Windows."""
        from app.core.platform import is_unix

        monkeypatch.setattr("sys.platform", "win32")
        assert is_unix() is False

    def test_platform_name_windows(self, monkeypatch):
        """Test platform_name returns Windows string."""
        from app.core.platform import platform_name

        monkeypatch.setattr("sys.platform", "win32")
        assert platform_name() == "Windows"

    def test_platform_name_linux(self, monkeypatch):
        """Test platform_name returns Linux string."""
        from app.core.platform import platform_name

        monkeypatch.setattr("sys.platform", "linux")
        assert platform_name() == "Linux"

    def test_platform_name_macos(self, monkeypatch):
        """Test platform_name returns macOS string."""
        from app.core.platform import platform_name

        monkeypatch.setattr("sys.platform", "darwin")
        assert platform_name() == "macOS"
