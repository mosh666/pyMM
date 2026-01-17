"""Tests for platform utilities."""

from unittest.mock import patch

from app.core.platform import (
    Platform,
    PortableConfig,
    PortableMode,
    current_platform,
    is_linux,
    is_macos,
    is_unix,
    is_windows,
    platform_name,
)


class TestPlatformChecks:
    """Test platform detection utilities."""

    def test_from_sys_platform(self):
        """Test Platform.from_sys_platform() with various platform strings."""
        assert Platform.from_sys_platform("win32") == Platform.WINDOWS
        assert Platform.from_sys_platform("darwin") == Platform.MACOS
        assert Platform.from_sys_platform("linux") == Platform.LINUX
        assert Platform.from_sys_platform("freebsd") == Platform.LINUX
        assert Platform.from_sys_platform("unknown") == Platform.LINUX

    def test_windows_detection(self):
        """Test Windows platform detection and helper functions."""
        with patch("sys.platform", "win32"):
            assert current_platform() == Platform.WINDOWS
            assert is_windows()
            assert not is_linux()
            assert not is_macos()
            assert not is_unix()
            assert platform_name() == "Windows"

    def test_linux_detection(self):
        """Test Linux platform detection and helper functions."""
        with patch("sys.platform", "linux"):
            assert current_platform() == Platform.LINUX
            assert is_linux()
            assert not is_windows()
            assert not is_macos()
            assert is_unix()
            assert platform_name() == "Linux"

    def test_macos_detection(self):
        """Test macOS platform detection and helper functions."""
        with patch("sys.platform", "darwin"):
            assert current_platform() == Platform.MACOS
            assert is_macos()
            assert not is_windows()
            assert not is_linux()
            assert is_unix()
            assert platform_name() == "macOS"


class TestPortableConfigProperties:
    """Test PortableConfig string representations and properties."""

    def test_str_representation(self):
        """Test PortableConfig.__str__() for various configurations."""
        assert "command line" in str(PortableConfig(True, PortableMode.CLI))
        assert "environment variable" in str(PortableConfig(True, PortableMode.ENV))
        assert "auto-detected" in str(PortableConfig(True, PortableMode.AUTO))
        assert "removable media" in str(PortableConfig(True, PortableMode.AUTO, True))
        assert "default" in str(PortableConfig(True, PortableMode.DEFAULT))

        assert "Installed" in str(PortableConfig(False, PortableMode.CLI))

    def test_status_icon(self):
        """Test PortableConfig.status_icon property."""
        assert PortableConfig(True, PortableMode.DEFAULT).status_icon == "📦"
        assert PortableConfig(False, PortableMode.DEFAULT).status_icon == "💻"

    def test_status_text(self):
        """Test PortableConfig.status_text property."""
        assert "CLI" in PortableConfig(True, PortableMode.CLI).status_text
        assert "ENV" in PortableConfig(True, PortableMode.ENV).status_text
        assert PortableConfig(True, PortableMode.AUTO).status_text == "Portable (auto)"
        assert PortableConfig(True, PortableMode.DEFAULT).status_text == "Portable"
        assert PortableConfig(False, PortableMode.DEFAULT).status_text == "Installed"
