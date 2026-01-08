"""Unit tests for platform-specific directory resolution."""

import os
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

from app.core.services.config_service import (
    get_platform_cache_dir,
    get_platform_config_dir,
    get_platform_data_dir,
)


class TestPlatformDirectories:
    """Test platform-specific directory functions."""

    @pytest.mark.windows
    def test_windows_directories(self):
        """Test Windows directory resolution."""
        config_dir = get_platform_config_dir()
        data_dir = get_platform_data_dir()
        cache_dir = get_platform_cache_dir()

        appdata = os.getenv("APPDATA", "~")
        localappdata = os.getenv("LOCALAPPDATA", "~")

        assert str(config_dir).startswith(appdata) or str(config_dir).startswith(str(Path.home()))
        assert str(data_dir).startswith(appdata) or str(data_dir).startswith(str(Path.home()))
        assert str(cache_dir).startswith(localappdata) or str(cache_dir).startswith(
            str(Path.home())
        )

        assert "pyMediaManager" in str(config_dir)
        assert "pyMediaManager" in str(data_dir)
        assert "pyMediaManager" in str(cache_dir)

    @pytest.mark.macos
    def test_macos_directories(self):
        """Test macOS directory resolution."""
        config_dir = get_platform_config_dir()
        data_dir = get_platform_data_dir()
        cache_dir = get_platform_cache_dir()

        home = Path.home()

        assert config_dir == home / "Library" / "Application Support" / "pyMediaManager"
        assert data_dir == home / "Library" / "Application Support" / "pyMediaManager"
        assert cache_dir == home / "Library" / "Caches" / "pyMediaManager"

    @pytest.mark.linux
    def test_linux_directories_default(self):
        """Test Linux directory resolution with default XDG paths."""
        with patch.dict(os.environ, {}, clear=False):
            # Remove XDG variables to test defaults
            for key in ["XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME"]:
                if key in os.environ:
                    del os.environ[key]

            config_dir = get_platform_config_dir()
            data_dir = get_platform_data_dir()
            cache_dir = get_platform_cache_dir()

            home = Path.home()

            assert config_dir == home / ".config" / "pymediamanager"
            assert data_dir == home / ".local" / "share" / "pymediamanager"
            assert cache_dir == home / ".cache" / "pymediamanager"

    @pytest.mark.linux
    def test_linux_directories_xdg_override(self):
        """Test Linux directory resolution with XDG environment variables."""
        with patch.dict(
            os.environ,
            {
                "XDG_CONFIG_HOME": "/custom/config",
                "XDG_DATA_HOME": "/custom/data",
                "XDG_CACHE_HOME": "/custom/cache",
            },
        ):
            config_dir = get_platform_config_dir()
            data_dir = get_platform_data_dir()
            cache_dir = get_platform_cache_dir()

            assert config_dir == Path("/custom/config/pymediamanager")
            assert data_dir == Path("/custom/data/pymediamanager")
            assert cache_dir == Path("/custom/cache/pymediamanager")

    def test_custom_app_name(self):
        """Test directory resolution with custom app name."""
        custom_name = "CustomApp"

        config_dir = get_platform_config_dir(custom_name)
        data_dir = get_platform_data_dir(custom_name)
        cache_dir = get_platform_cache_dir(custom_name)

        # On Linux, app name is lowercased
        if sys.platform == "linux":
            expected_name = custom_name.lower()
        else:
            expected_name = custom_name

        assert expected_name in str(config_dir)
        assert expected_name in str(data_dir)
        assert expected_name in str(cache_dir)
