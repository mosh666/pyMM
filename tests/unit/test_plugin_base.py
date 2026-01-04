"""
Unit tests for PluginBase class functionality.

Tests download, extraction, checksum verification, and plugin management.
"""

import hashlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.plugins.plugin_base import (
    PluginManifest,
    SimplePluginImplementation,
)


@pytest.fixture
def test_manifest():
    """Create a test plugin manifest."""
    return PluginManifest(
        name="TestPlugin",
        version="1.0.0",
        mandatory=False,
        enabled=True,
        source_type="url",
        source_uri="https://example.com/plugin.zip",
        command_path="bin",
        command_executable="test.exe",
        register_to_path=False,
        checksum_sha256="abc123",
        file_size=1024,
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
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=True,
            enabled=True,
            source_type="url",
            source_uri="https://example.com/plugin.zip",
        )

        assert manifest.name == "TestPlugin"
        assert manifest.version == "1.0.0"
        assert manifest.mandatory is True
        assert manifest.enabled is True
        assert manifest.dependencies == []

    def test_manifest_with_dependencies(self):
        """Test manifest with dependencies."""
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            source_type="url",
            source_uri="https://example.com/plugin.zip",
            dependencies=["dep1", "dep2"],
        )

        assert manifest.dependencies == ["dep1", "dep2"]

    def test_manifest_defaults(self):
        """Test manifest default values."""
        manifest = PluginManifest(
            name="TestPlugin",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            source_type="url",
            source_uri="https://example.com/plugin.zip",
        )

        assert manifest.asset_pattern is None
        assert manifest.command_path == ""
        assert manifest.command_executable == ""
        assert manifest.register_to_path is False
        assert manifest.checksum_sha256 is None
        assert manifest.file_size is None


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
        manifest = PluginManifest(
            name="ExifTool",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            source_type="url",
            source_uri="https://example.com/exiftool.zip",
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
