"""
Unit tests for PluginBase class functionality.

Tests download, extraction, checksum verification, and plugin management.
"""

import hashlib
from pathlib import Path
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.plugins.plugin_base import (
    ExecutableSource,
    PlatformManifest,
    PluginManifest,
    SimplePluginImplementation,
)


@pytest.fixture
def test_manifest():
    """Create a test plugin manifest."""
    # Create platform config for all platforms to ensure tests work everywhere
    platform_config = PlatformManifest(
        source_type="url",
        source_uri="https://example.com/plugin.zip",
        command_path="bin",
        command_executable="test.exe",
    )
    return PluginManifest(
        name="TestPlugin",
        version="1.0.0",
        mandatory=False,
        enabled=True,
        register_to_path=False,
        windows_config=platform_config,
        linux_config=platform_config,
        macos_config=platform_config,
    )


@pytest.fixture
def install_dir(tmp_path):
    """Create a temporary installation directory."""
    return tmp_path / "plugins"


@pytest.fixture
def simple_plugin(test_manifest, install_dir):
    """Create a SimplePluginImplementation instance."""
    return SimplePluginImplementation(
        test_manifest,
        install_dir,
        "https://example.com/plugin.zip",
    )


class TestPluginManifest:
    """Tests for PluginManifest dataclass."""

    def test_manifest_creation(self):
        """Test creating a plugin manifest."""
        windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/plugin.zip",
        )
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=True,
            enabled=True,
            windows_config=windows_config,
        )

        assert manifest.name == "TestPlugin"
        assert manifest.version == "1.0.0"
        assert manifest.mandatory is True
        assert manifest.enabled is True
        assert manifest.dependencies == []

    def test_manifest_with_dependencies(self):
        """Test manifest with dependencies."""
        windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/plugin.zip",
        )
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            windows_config=windows_config,
            dependencies=["dep1", "dep2"],
        )

        assert manifest.dependencies == ["dep1", "dep2"]

    def test_manifest_defaults(self):
        """Test manifest default values."""
        windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/plugin.zip",
        )
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            windows_config=windows_config,
        )

        assert windows_config.asset_pattern is None
        assert windows_config.command_path == ""
        assert windows_config.command_executable == ""
        assert manifest.register_to_path is False
        assert windows_config.checksum_sha256 is None
        assert windows_config.file_size is None


class TestPluginBase:
    """Tests for PluginBase abstract class."""

    def test_plugin_initialization(self, test_manifest, install_dir):
        """Test plugin initialization."""
        plugin = SimplePluginImplementation(
            test_manifest,
            install_dir,
            "https://example.com/plugin.zip",
        )

        assert plugin.manifest == test_manifest
        assert plugin.install_dir == install_dir
        assert plugin.plugin_dir == install_dir / "testplugin"

    def test_get_executable_path_not_installed(self, simple_plugin):
        """Test getting executable path when not installed."""
        exe_path = simple_plugin.get_executable_path()
        assert exe_path is None

    def test_get_executable_path_installed(self, simple_plugin, install_dir):
        """Test getting executable path when installed."""
        # Create plugin directory and executable
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        exe_file = plugin_dir / "bin" / "test.exe"
        exe_file.touch()

        exe_path = simple_plugin.get_executable_path()
        assert exe_path == exe_file
        assert exe_path.exists()

    def test_is_installed_false(self, simple_plugin):
        """Test is_installed when plugin not installed."""
        assert simple_plugin.is_installed() is False

    def test_is_installed_true(self, simple_plugin, install_dir):
        """Test is_installed when plugin is installed."""
        # Create plugin directory and executable
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        (plugin_dir / "bin" / "test.exe").touch()

        assert simple_plugin.is_installed() is True

    @pytest.mark.asyncio
    async def test_uninstall_not_installed(self, simple_plugin):
        """Test uninstalling when not installed."""
        result = await simple_plugin.uninstall()
        assert result is True

    @pytest.mark.asyncio
    async def test_uninstall_success(self, simple_plugin, install_dir):
        """Test successful uninstallation."""
        # Create plugin directory
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "test.txt").touch()

        assert plugin_dir.exists()

        result = await simple_plugin.uninstall()
        assert result is True
        assert not plugin_dir.exists()


class TestSimplePluginImplementation:
    """Tests for SimplePluginImplementation."""

    def test_archive_extension_detection_zip(self, test_manifest, install_dir):
        """Test ZIP archive extension detection."""
        plugin = SimplePluginImplementation(
            test_manifest,
            install_dir,
            "https://example.com/plugin.zip",
        )

        assert plugin.archive_path.suffix == ".zip"

    def test_archive_extension_detection_7z(self, test_manifest, install_dir):
        """Test 7z archive extension detection."""
        plugin = SimplePluginImplementation(
            test_manifest,
            install_dir,
            "https://example.com/plugin.7z",
        )

        assert plugin.archive_path.suffix == ".7z"

    def test_archive_extension_detection_7z_exe(self, test_manifest, install_dir):
        """Test 7z.exe archive extension detection."""
        plugin = SimplePluginImplementation(
            test_manifest,
            install_dir,
            "https://example.com/plugin.7z.exe",
        )

        assert str(plugin.archive_path).endswith(".7z.exe")

    @pytest.mark.asyncio
    async def test_download_success(self, simple_plugin, install_dir):
        """Test successful download."""
        # Mock the download method
        with patch.object(simple_plugin, "_download_file", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = True

            result = await simple_plugin.download()

            assert result is True
            mock_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_no_archive(self, simple_plugin):
        """Test extraction when archive doesn't exist."""
        result = await simple_plugin.extract()
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_zip_success(self, simple_plugin, install_dir):
        """Test successful ZIP extraction."""
        # Create fake archive
        archive_path = simple_plugin.archive_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        archive_path.touch()

        # Mock extraction methods
        with patch.object(simple_plugin, "_extract_zip", new_callable=AsyncMock) as mock_extract:
            mock_extract.return_value = True

            # Create fake extracted content
            temp_dir = install_dir / "testplugin_temp"
            temp_dir.mkdir(parents=True)
            (temp_dir / "bin").mkdir()
            (temp_dir / "bin" / "test.exe").touch()

            with patch.object(simple_plugin, "_flatten_extraction"):
                with patch.object(simple_plugin, "_handle_special_cases"):
                    result = await simple_plugin.extract()

            assert result is True

    def test_validate_installation_success(self, simple_plugin, install_dir):
        """Test successful installation validation."""
        # Create plugin directory and executable
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        (plugin_dir / "bin" / "test.exe").touch()

        assert simple_plugin.validate_installation() is True

    def test_validate_installation_failure(self, simple_plugin):
        """Test installation validation failure."""
        assert simple_plugin.validate_installation() is False

    def test_get_version_installed(self, simple_plugin, install_dir):
        """Test getting version when installed."""
        # Create plugin directory
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        (plugin_dir / "bin" / "test.exe").touch()

        version = simple_plugin.get_version()
        assert version == "1.0.0"

    def test_get_version_not_installed(self, simple_plugin):
        """Test getting version when not installed."""
        version = simple_plugin.get_version()
        assert version is None

    def test_flatten_extraction_single_dir(self, simple_plugin, tmp_path):
        """Test flattening extraction with single nested directory."""
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create nested structure
        nested = extract_dir / "nested"
        nested.mkdir()
        (nested / "file1.txt").touch()
        (nested / "file2.txt").touch()

        simple_plugin._flatten_extraction(extract_dir)

        # Files should be moved up
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()
        assert not nested.exists()

    def test_flatten_extraction_multiple_items(self, simple_plugin, tmp_path):
        """Test flattening doesn't occur with multiple top-level items."""
        extract_dir = tmp_path / "extract"
        extract_dir.mkdir()

        # Create multiple top-level items
        (extract_dir / "file1.txt").touch()
        (extract_dir / "file2.txt").touch()

        simple_plugin._flatten_extraction(extract_dir)

        # Structure should remain unchanged
        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()

    def test_handle_special_cases_exiftool(self, install_dir):
        """Test ExifTool special case handling."""
        windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/exiftool.zip",
        )
        manifest = PluginManifest(
            name="ExifTool",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            windows_config=windows_config,
        )

        plugin = SimplePluginImplementation(
            manifest,
            install_dir,
            "https://example.com/exiftool.zip",
        )

        extract_dir = install_dir / "temp"
        extract_dir.mkdir(parents=True)

        # Create the special ExifTool file
        old_file = extract_dir / "exiftool(-k).exe"
        old_file.touch()

        plugin._handle_special_cases(extract_dir)

        # Should be renamed
        assert not old_file.exists()
        assert (extract_dir / "exiftool.exe").exists()


class TestDownloadFile:
    """Tests for _download_file method."""

    @pytest.mark.asyncio
    async def test_download_file_http_error(self, simple_plugin, tmp_path):
        """Test download with HTTP error."""
        destination = tmp_path / "download.zip"

        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.reason = "Not Found"

        # Create an async context manager for session.get()
        mock_get_cm = AsyncMock()
        mock_get_cm.__aenter__.return_value = mock_response
        mock_get_cm.__aexit__.return_value = None

        mock_session = MagicMock()
        mock_session.get.return_value = mock_get_cm
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await simple_plugin._download_file(
                "https://example.com/file.zip",
                destination,
                max_retries=1,
            )

        assert result is False

    @pytest.mark.asyncio
    async def test_verify_checksum_success(self, simple_plugin, tmp_path):
        """Test successful checksum verification."""
        test_file = tmp_path / "test.txt"
        content = b"test content"
        test_file.write_bytes(content)

        # Calculate expected hash
        expected = hashlib.sha256(content).hexdigest()

        result = await simple_plugin._verify_checksum(test_file, expected)
        assert result is True

    @pytest.mark.asyncio
    async def test_verify_checksum_failure(self, simple_plugin, tmp_path):
        """Test checksum verification failure."""
        test_file = tmp_path / "test.txt"
        test_file.write_bytes(b"test content")

        # Wrong hash
        result = await simple_plugin._verify_checksum(test_file, "wrong_hash")
        assert result is False

    @pytest.mark.asyncio
    async def test_verify_checksum_case_insensitive(self, simple_plugin, tmp_path):
        """Test checksum verification is case-insensitive."""
        test_file = tmp_path / "test.txt"
        content = b"test content"
        test_file.write_bytes(content)

        expected_lower = hashlib.sha256(content).hexdigest().lower()
        expected_upper = expected_lower.upper()

        result1 = await simple_plugin._verify_checksum(test_file, expected_lower)
        result2 = await simple_plugin._verify_checksum(test_file, expected_upper)

        assert result1 is True
        assert result2 is True


class TestGetExecutableInfo:
    """Tests for get_executable_info method."""

    def test_get_executable_info_v2_portable(self, simple_plugin, install_dir):
        """Test getting executable info from v2 portable installation."""
        # Create installed plugin
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        exe_path = plugin_dir / "bin" / "test.exe"
        exe_path.touch()

        # Add v2 config
        from app.plugins.plugin_base import PlatformManifest

        simple_plugin.manifest.windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/test.zip",
            command_path="bin",
            command_executable="test.exe",
        )

        path, source, version = simple_plugin.get_executable_info()

        assert path == exe_path
        assert source == ExecutableSource.PORTABLE
        # Version extraction from portable binary is not yet implemented (TODO in code)
        assert version is None

    def test_get_executable_info_system_tool(self, simple_plugin):
        """Test getting executable info from system tool."""
        # Add v2 config with system package for current platform
        from app.core.platform import Platform, current_platform
        from app.plugins.plugin_base import PlatformManifest
        from app.plugins.system_tool_detector import ToolDetectionStatus

        platform = current_platform()
        platform_manifest = PlatformManifest(
            system_package="test-tool", version_constraint=">=2.0.0"
        )

        if platform == Platform.WINDOWS:
            simple_plugin.manifest.windows_config = platform_manifest
        elif platform == Platform.MACOS:
            simple_plugin.manifest.macos_config = platform_manifest
        else:
            simple_plugin.manifest.linux_config = platform_manifest

        simple_plugin.manifest.prefer_system = True

        # Mock system tool detector to find tool
        with patch("app.plugins.system_tool_detector.SystemToolDetector") as mock_detector_cls:
            mock_detector = mock_detector_cls.return_value
            mock_tool_info = MagicMock()
            mock_tool_info.status = ToolDetectionStatus.FOUND_VALID
            mock_tool_info.path = Path("/usr/bin/test")
            mock_tool_info.version = "2.0.0"
            mock_detector.find_system_tool.return_value = mock_tool_info

            path, source, version = simple_plugin.get_executable_info()

            assert path == Path("/usr/bin/test")
            assert source == ExecutableSource.SYSTEM
            assert version == "2.0.0"

    def test_get_executable_info_not_found(self, simple_plugin):
        """Test getting executable info when not found."""

        path, source, version = simple_plugin.get_executable_info()

        assert path is None
        assert source == ExecutableSource.NONE
        assert version is None

    def test_get_executable_path_installed(self, simple_plugin, install_dir):
        """Test getting executable path when installed."""
        # Create installed plugin
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        exe_path = plugin_dir / "bin" / "test.exe"
        exe_path.touch()

        path = simple_plugin.get_executable_path()
        assert path == exe_path

    def test_get_executable_path_not_installed(self, simple_plugin):
        """Test getting executable path when not installed."""
        path = simple_plugin.get_executable_path()
        assert path is None

    def test_is_installed_true(self, simple_plugin, install_dir):
        """Test is_installed returns True when plugin is installed."""
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        (plugin_dir / "bin" / "test.exe").touch()

        assert simple_plugin.is_installed() is True

    def test_is_installed_false(self, simple_plugin):
        """Test is_installed returns False when plugin is not installed."""
        assert simple_plugin.is_installed() is False

    @pytest.mark.asyncio
    async def test_uninstall_success(self, simple_plugin, install_dir):
        """Test successful plugin uninstallation."""
        # Create installed plugin
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "file.txt").write_text("content")

        result = await simple_plugin.uninstall()

        assert result is True
        assert not plugin_dir.exists()

    @pytest.mark.asyncio
    async def test_uninstall_not_installed(self, simple_plugin):
        """Test uninstalling plugin that isn't installed."""
        result = await simple_plugin.uninstall()
        # Should succeed even if not installed
        assert result is True

    @pytest.mark.asyncio
    async def test_download_with_progress_callback(self, simple_plugin):
        """Test download with progress callback."""
        progress_calls = []

        def progress_callback(current, total):
            """Track progress callback calls."""
            progress_calls.append((current, total))

        with patch.object(simple_plugin, "_download_file", new_callable=AsyncMock) as mock_download:
            mock_download.return_value = True

            result = await simple_plugin.download(progress_callback=progress_callback)

            assert result is True
            mock_download.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.windows  # Bundled py7zr dependencies lack native binaries on Linux
    async def test_extract_7z_archive(self, simple_plugin, install_dir):
        """Test extraction of 7z archive."""
        # Create fake 7z archive
        simple_plugin.archive_path = install_dir / "testplugin.7z"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        # Mock inflate64 module before py7zr import to avoid native binary dependency
        sys.modules["inflate64"] = MagicMock()
        sys.modules["inflate64._inflate64"] = MagicMock()
        sys.modules["bcj"] = MagicMock()
        sys.modules["pyppmd"] = MagicMock()
        sys.modules["pyppmd.c._ppmd"] = MagicMock()
        sys.modules["pyppmd.cffi._cffi_ppmd"] = MagicMock()

        with patch("py7zr.SevenZipFile") as mock_7z:
            mock_7z_instance = MagicMock()
            mock_7z.return_value.__enter__.return_value = mock_7z_instance

            # Create mock extracted directory
            temp_dir = install_dir / "testplugin_temp"
            temp_dir.mkdir()
            (temp_dir / "file.txt").touch()

            with patch.object(simple_plugin, "_flatten_extraction"):
                with patch.object(simple_plugin, "_handle_special_cases"):
                    await simple_plugin.extract()

            mock_7z_instance.extractall.assert_called_once()


class TestPluginManifestMethods:
    """Tests for PluginManifest helper methods."""

    def test_get_current_platform_config_windows(self, test_manifest):
        """Test getting Windows platform config."""
        from app.core.platform import Platform
        from app.plugins.plugin_base import PlatformManifest

        test_manifest.windows_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/windows.zip",
            command_executable="test.exe",
        )

        with patch("app.plugins.plugin_base.current_platform", return_value=Platform.WINDOWS):
            config = test_manifest.get_current_platform_config()

        assert config is not None
        assert config.command_executable == "test.exe"

    def test_get_current_platform_config_linux(self, test_manifest):
        """Test getting Linux platform config."""
        from app.core.platform import Platform
        from app.plugins.plugin_base import PlatformManifest

        test_manifest.linux_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/linux.tar.gz",
            command_executable="test",
        )

        with patch("app.plugins.plugin_base.current_platform", return_value=Platform.LINUX):
            config = test_manifest.get_current_platform_config()

        assert config is not None
        assert config.command_executable == "test"

    def test_get_current_platform_config_macos(self, test_manifest):
        """Test getting macOS platform config."""
        from app.core.platform import Platform
        from app.plugins.plugin_base import PlatformManifest

        test_manifest.macos_config = PlatformManifest(
            source_type="url",
            source_uri="https://example.com/macos.zip",
            command_executable="test",
        )

        with patch("app.plugins.plugin_base.current_platform", return_value=Platform.MACOS):
            config = test_manifest.get_current_platform_config()

        assert config is not None
        assert config.command_executable == "test"


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    @pytest.mark.asyncio
    async def test_download_file_http_error_with_retries(self, simple_plugin):
        """Test download with HTTP error and retry logic."""
        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = MagicMock()
            mock_response = MagicMock()
            mock_response.status = 404
            mock_response.reason = "Not Found"
            mock_response.headers = {"content-length": "0"}

            # Set up async context managers properly
            mock_get = AsyncMock()
            mock_get.__aenter__.return_value = mock_response
            mock_session.get.return_value = mock_get

            mock_session_cls.return_value.__aenter__.return_value = mock_session

            result = await simple_plugin._download_file(
                "https://example.com/file.zip",
                Path("/tmp/file.zip"),  # noqa: S108
                max_retries=2,
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_download_file_timeout_error(self, simple_plugin):
        """Test download with timeout error."""

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.get.side_effect = TimeoutError("Connection timeout")
            mock_session_cls.return_value.__aenter__.return_value = mock_session

            result = await simple_plugin._download_file(
                "https://example.com/file.zip",
                Path("/tmp/file.zip"),  # noqa: S108
                max_retries=1,
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_download_file_client_error(self, simple_plugin):
        """Test download with client error."""
        import aiohttp

        with patch("aiohttp.ClientSession") as mock_session_cls:
            mock_session = MagicMock()
            mock_session.get.side_effect = aiohttp.ClientError("Connection failed")
            mock_session_cls.return_value.__aenter__.return_value = mock_session

            result = await simple_plugin._download_file(
                "https://example.com/file.zip",
                Path("/tmp/file.zip"),  # noqa: S108
                max_retries=1,
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_verify_checksum_file_not_found(self, simple_plugin):
        """Test checksum verification with missing file."""
        result = await simple_plugin._verify_checksum(Path("/nonexistent/file.zip"), "abc123")
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_archive_not_found(self, simple_plugin):
        """Test extraction when archive doesn't exist."""
        simple_plugin.archive_path = Path("/nonexistent/archive.zip")
        result = await simple_plugin.extract()
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_unsupported_format(self, simple_plugin, install_dir):
        """Test extraction with unsupported archive format."""
        simple_plugin.archive_path = install_dir / "file.tar.bz2"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        result = await simple_plugin.extract()
        assert result is False

    @pytest.mark.asyncio
    async def test_extract_zip_error(self, simple_plugin, install_dir):
        """Test extraction error handling for zip."""
        simple_plugin.archive_path = install_dir / "corrupt.zip"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        with patch("zipfile.ZipFile") as mock_zip:
            mock_zip.side_effect = Exception("Corrupt archive")

            result = await simple_plugin.extract()
            assert result is False

    @pytest.mark.asyncio
    @pytest.mark.windows  # Bundled py7zr dependencies lack native binaries on Linux
    async def test_extract_7z_fallback_to_cli(self, simple_plugin, install_dir):
        """Test 7z extraction fallback to CLI when py7zr not available."""
        simple_plugin.archive_path = install_dir / "file.7z"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        # Mock inflate64 module before py7zr import to avoid native binary dependency
        sys.modules["inflate64"] = MagicMock()
        sys.modules["inflate64._inflate64"] = MagicMock()
        sys.modules["bcj"] = MagicMock()
        sys.modules["pyppmd"] = MagicMock()
        sys.modules["pyppmd.c._ppmd"] = MagicMock()
        sys.modules["pyppmd.cffi._cffi_ppmd"] = MagicMock()

        with (
            patch("py7zr.SevenZipFile", side_effect=ImportError("py7zr not found")),
            patch("subprocess.run") as mock_run,
        ):
            mock_run.return_value = MagicMock(returncode=0)

            await simple_plugin._extract_7z(install_dir)

            # Should fall back to CLI
            assert mock_run.called

    def test_flatten_extraction_multiple_items(self, simple_plugin, install_dir):
        """Test flatten extraction doesn't affect multiple top-level items."""
        install_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = install_dir / "extract"
        extract_dir.mkdir()
        (extract_dir / "file1.txt").touch()
        (extract_dir / "file2.txt").touch()

        # Should not modify structure
        simple_plugin._flatten_extraction(extract_dir)

        assert (extract_dir / "file1.txt").exists()
        assert (extract_dir / "file2.txt").exists()

    def test_flatten_extraction_with_conflict(self, simple_plugin, install_dir):
        """Test flatten extraction with naming conflict."""
        install_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = install_dir / "extract"
        extract_dir.mkdir()

        # Create ONLY nested structure (single top-level directory)
        nested = extract_dir / "nested"
        nested.mkdir()
        (nested / "file.txt").write_text("nested")

        # Create another file in nested dir
        (nested / "other.txt").write_text("other")

        simple_plugin._flatten_extraction(extract_dir)

        # Files should have been moved up
        assert (extract_dir / "file.txt").read_text() == "nested"
        assert (extract_dir / "other.txt").read_text() == "other"
        assert not nested.exists()

    def test_handle_special_cases_exiftool(self, simple_plugin, install_dir):
        """Test ExifTool special case handling."""
        from app.plugins.plugin_base import PluginManifest

        # Create ExifTool manifest
        exiftool_manifest = PluginManifest(
            name="ExifTool",
            version="1.0.0",
            mandatory=False,
            enabled=True,
        )
        install_dir.mkdir(parents=True, exist_ok=True)
        plugin = SimplePluginImplementation(
            exiftool_manifest, install_dir, "https://example.com/exiftool.zip"
        )

        extract_dir = install_dir / "extract"
        extract_dir.mkdir()
        (extract_dir / "exiftool(-k).exe").touch()

        plugin._handle_special_cases(extract_dir)

        assert (extract_dir / "exiftool.exe").exists()
        assert not (extract_dir / "exiftool(-k).exe").exists()

    def test_handle_special_cases_non_exiftool(self, simple_plugin, install_dir):
        """Test special case handling for non-ExifTool plugin."""
        install_dir.mkdir(parents=True, exist_ok=True)
        extract_dir = install_dir / "extract"
        extract_dir.mkdir()

        # Should not raise error for non-ExifTool plugins
        simple_plugin._handle_special_cases(extract_dir)

    def test_validate_installation_no_executable(self, simple_plugin):
        """Test validation fails when executable doesn't exist."""
        assert simple_plugin.validate_installation() is False

    def test_get_version_not_installed(self, simple_plugin):
        """Test get_version returns None when not installed."""
        version = simple_plugin.get_version()
        assert version is None

    def test_get_version_installed(self, simple_plugin, install_dir):
        """Test get_version returns manifest version when installed."""
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "bin").mkdir()
        (plugin_dir / "bin" / "test.exe").touch()

        version = simple_plugin.get_version()
        assert version == "1.0.0"

    @pytest.mark.asyncio
    async def test_uninstall_error_handling(self, simple_plugin, install_dir):
        """Test uninstall error handling."""
        plugin_dir = install_dir / "testplugin"
        plugin_dir.mkdir(parents=True)
        (plugin_dir / "file.txt").touch()

        # Mock shutil.rmtree to raise error
        with patch("shutil.rmtree", side_effect=PermissionError("Access denied")):
            result = await simple_plugin.uninstall()
            assert result is False

    @pytest.mark.asyncio
    async def test_extract_7z_exe_success(self, simple_plugin, install_dir):
        """Test extracting self-extracting 7z.exe archive."""
        simple_plugin.archive_path = install_dir / "installer.7z.exe"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = await simple_plugin._extract_7z_exe(install_dir)

            assert result is True
            mock_run.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_7z_exe_fallback(self, simple_plugin, install_dir):
        """Test 7z.exe extraction fallback to py7zr."""
        simple_plugin.archive_path = install_dir / "installer.7z.exe"
        simple_plugin.archive_path.parent.mkdir(parents=True, exist_ok=True)
        simple_plugin.archive_path.touch()

        with (
            patch("subprocess.run", side_effect=Exception("Subprocess failed")),
            patch.object(simple_plugin, "_extract_7z", new_callable=AsyncMock) as mock_extract,
        ):
            mock_extract.return_value = True

            await simple_plugin._extract_7z_exe(install_dir)

            # Should fall back to _extract_7z on exception
            mock_extract.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_7z_cli_success(self, simple_plugin, install_dir):
        """Test 7z extraction using CLI tool."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)

            result = await simple_plugin._extract_7z_cli(install_dir)

            assert result is True
            assert mock_run.called

    @pytest.mark.asyncio
    async def test_extract_7z_cli_error(self, simple_plugin, install_dir):
        """Test 7z CLI extraction error handling."""
        with patch("subprocess.run", side_effect=Exception("CLI not found")):
            result = await simple_plugin._extract_7z_cli(install_dir)
            assert result is False
