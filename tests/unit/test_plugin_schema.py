"""Tests for PluginSchema validation.

Tests Pydantic schema validation for plugin manifests.
"""

from __future__ import annotations

from pydantic import ValidationError
import pytest

from app.plugins.plugin_schema import (
    PlatformConfig,
    PluginCommand,
    PluginManifestSchema,
    PluginSource,
)


class TestPluginSource:
    """Test suite for PluginSource model."""

    def test_create_url_source(self):
        """Test creating URL source."""
        source = PluginSource(
            type="url",
            base_uri="https://example.com/tool.zip",
        )

        assert source.type == "url"
        assert source.base_uri == "https://example.com/tool.zip"

    def test_source_with_checksum(self):
        """Test source with SHA-256 checksum."""
        checksum = "A" * 64  # Valid 64-char hex
        source = PluginSource(
            type="url",
            base_uri="https://example.com/tool.zip",
            checksum_sha256=checksum,
        )

        assert source.checksum_sha256 == checksum

    def test_source_with_file_size(self):
        """Test source with file size."""
        source = PluginSource(
            type="url",
            base_uri="https://example.com/tool.zip",
            file_size=1024000,
        )

        assert source.file_size == 1024000

    def test_source_requires_type(self):
        """Test type field is required."""
        with pytest.raises(ValidationError):
            PluginSource(base_uri="https://example.com/tool.zip")

    def test_source_requires_base_uri(self):
        """Test base_uri field is required."""
        with pytest.raises(ValidationError):
            PluginSource(type="url")

    def test_invalid_source_type(self):
        """Test invalid source type is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PluginSource(
                type="invalid",
                base_uri="https://example.com/tool.zip",
            )

        assert "Unsupported source type" in str(exc_info.value)

    def test_invalid_checksum_length(self):
        """Test checksum must be 64 characters."""
        with pytest.raises(ValidationError) as exc_info:
            PluginSource(
                type="url",
                base_uri="https://example.com/tool.zip",
                checksum_sha256="abc123",  # Too short
            )

        assert "64 characters" in str(exc_info.value)

    def test_invalid_checksum_characters(self):
        """Test checksum must be hexadecimal."""
        with pytest.raises(ValidationError) as exc_info:
            PluginSource(
                type="url",
                base_uri="https://example.com/tool.zip",
                checksum_sha256="G" * 64,  # Invalid hex
            )

        assert "hexadecimal" in str(exc_info.value)

    def test_negative_file_size(self):
        """Test file size must be positive."""
        with pytest.raises(ValidationError) as exc_info:
            PluginSource(
                type="url",
                base_uri="https://example.com/tool.zip",
                file_size=-1000,
            )

        assert "positive" in str(exc_info.value)


class TestPluginCommand:
    """Test suite for PluginCommand model."""

    def test_create_basic_command(self):
        """Test creating basic command."""
        cmd = PluginCommand(executable="git.exe")

        assert cmd.executable == "git.exe"
        assert cmd.path == ""

    def test_create_command_with_path(self):
        """Test creating command with path."""
        cmd = PluginCommand(
            path="bin",
            executable="tool.exe",
        )

        assert cmd.path == "bin"
        assert cmd.executable == "tool.exe"

    def test_command_requires_executable(self):
        """Test executable is required."""
        with pytest.raises(ValidationError):
            PluginCommand(path="bin")

    def test_empty_executable_rejected(self):
        """Test empty executable is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PluginCommand(executable="")

        assert "cannot be empty" in str(exc_info.value)

    def test_whitespace_executable_rejected(self):
        """Test whitespace-only executable is rejected."""
        with pytest.raises(ValidationError):
            PluginCommand(executable="   ")


class TestPlatformConfig:
    """Test suite for PlatformConfig model."""

    def test_create_config_with_source(self):
        """Test creating config with download source."""
        source = PluginSource(
            type="url",
            base_uri="https://example.com/tool.zip",
        )
        command = PluginCommand(path="bin", executable="tool.exe")

        config = PlatformConfig(source=source, command=command)

        assert config.source == source
        assert config.command == command

    def test_create_config_with_system_package(self):
        """Test creating config for system package."""
        command = PluginCommand(executable="git")

        config = PlatformConfig(
            command=command,
            system_package="git",
        )

        assert config.system_package == "git"
        assert config.command.executable == "git"
        assert config.source is None

    def test_config_with_version_constraint(self):
        """Test config with version constraint."""
        command = PluginCommand(executable="git")

        config = PlatformConfig(
            command=command,
            system_package="git",
            version_constraint=">=2.40,<4.0",
        )

        assert config.version_constraint == ">=2.40,<4.0"

    def test_invalid_version_constraint(self):
        """Test invalid version constraint is rejected."""
        command = PluginCommand(executable="git")

        with pytest.raises(ValidationError) as exc_info:
            PlatformConfig(
                command=command,
                system_package="git",
                version_constraint="invalid>=2.0",
            )

        assert "Invalid version constraint" in str(exc_info.value)

    def test_config_requires_command(self):
        """Test command field is required."""
        source = PluginSource(
            type="url",
            base_uri="https://example.com/tool.zip",
        )

        with pytest.raises(ValidationError):
            PlatformConfig(source=source)


class TestPluginManifestSchema:
    """Test suite for PluginManifestSchema model."""

    @pytest.fixture
    def valid_v2_manifest_dict(self):
        """Valid v2 manifest data dictionary."""
        return {
            "schema_version": 2,
            "name": "TestPlugin",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "prefer_system": False,
            "register_to_path": True,
            "dependencies": ["git"],
            "platforms": {
                "windows": {
                    "source": {
                        "type": "url",
                        "base_uri": "https://example.com/tool-win.zip",
                        "checksum_sha256": "A" * 64,
                    },
                    "command": {
                        "path": "bin",
                        "executable": "tool.exe",
                    },
                },
                "linux": {
                    "system_package": "tool",
                    "command": {
                        "executable": "tool",
                    },
                    "version_constraint": ">=1.0",
                },
            },
        }

    def test_create_valid_v2_manifest(self, valid_v2_manifest_dict):
        """Test creating valid v2 manifest."""
        manifest = PluginManifestSchema(**valid_v2_manifest_dict)

        assert manifest.schema_version == 2
        assert manifest.name == "TestPlugin"
        assert manifest.version == "1.0.0"
        assert manifest.mandatory is False
        assert manifest.enabled is True

    def test_manifest_requires_name(self, valid_v2_manifest_dict):
        """Test name is required."""
        del valid_v2_manifest_dict["name"]

        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(**valid_v2_manifest_dict)

        assert "name" in str(exc_info.value)

    def test_manifest_requires_version(self, valid_v2_manifest_dict):
        """Test version is required."""
        del valid_v2_manifest_dict["version"]

        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(**valid_v2_manifest_dict)

        assert "version" in str(exc_info.value)

    def test_manifest_requires_mandatory_field(self, valid_v2_manifest_dict):
        """Test mandatory field is required."""
        del valid_v2_manifest_dict["mandatory"]

        with pytest.raises(ValidationError):
            PluginManifestSchema(**valid_v2_manifest_dict)

    def test_manifest_requires_enabled_field(self, valid_v2_manifest_dict):
        """Test enabled field is required."""
        del valid_v2_manifest_dict["enabled"]

        with pytest.raises(ValidationError):
            PluginManifestSchema(**valid_v2_manifest_dict)

    def test_manifest_with_all_platforms(self):
        """Test manifest with all supported platforms."""
        manifest_data = {
            "schema_version": 2,
            "name": "CrossPlatformTool",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "platforms": {
                "windows": {
                    "command": {"executable": "tool.exe"},
                    "system_package": "tool",
                },
                "linux": {
                    "command": {"executable": "tool"},
                    "system_package": "tool",
                },
                "macos": {
                    "command": {"executable": "tool"},
                    "system_package": "tool",
                },
            },
        }

        manifest = PluginManifestSchema(**manifest_data)

        assert "windows" in manifest.platforms
        assert "linux" in manifest.platforms
        assert "macos" in manifest.platforms

    def test_manifest_invalid_platform_name(self):
        """Test invalid platform name is rejected."""
        manifest_data = {
            "schema_version": 2,
            "name": "Test",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "platforms": {
                "invalid_os": {
                    "command": {"executable": "tool"},
                },
            },
        }

        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(**manifest_data)

        assert "Invalid platform keys" in str(exc_info.value)

    def test_empty_name_rejected(self):
        """Test empty name is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(
                name="",
                version="1.0.0",
                mandatory=False,
                enabled=True,
            )

        assert "cannot be empty" in str(exc_info.value)

    def test_empty_version_rejected(self):
        """Test empty version is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(
                name="Test",
                version="",
                mandatory=False,
                enabled=True,
            )

        assert "cannot be empty" in str(exc_info.value)

    def test_manifest_with_dependencies(self, valid_v2_manifest_dict):
        """Test manifest with plugin dependencies."""
        manifest = PluginManifestSchema(**valid_v2_manifest_dict)

        assert manifest.dependencies == ["git"]

    def test_manifest_empty_dependency_rejected(self):
        """Test empty dependency string is rejected."""
        manifest_data = {
            "schema_version": 2,
            "name": "Test",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "dependencies": ["git", ""],
            "platforms": {"windows": {"command": {"executable": "test.exe"}}},
        }

        with pytest.raises(ValidationError) as exc_info:
            PluginManifestSchema(**manifest_data)

        assert "empty" in str(exc_info.value).lower()

    def test_manifest_prefer_system_default(self):
        """Test prefer_system has default value."""
        manifest = PluginManifestSchema(
            name="Test",
            version="1.0.0",
            mandatory=False,
            enabled=True,
            platforms={"windows": {"command": {"executable": "test.exe"}}},
        )

        assert isinstance(manifest.prefer_system, bool)
        assert manifest.prefer_system is True  # Default is True

    def test_manifest_to_dict(self, valid_v2_manifest_dict):
        """Test converting manifest to dict."""
        manifest = PluginManifestSchema(**valid_v2_manifest_dict)

        data = manifest.model_dump()

        assert data["name"] == "TestPlugin"
        assert data["version"] == "1.0.0"
        assert "platforms" in data

    def test_manifest_extra_fields_allowed(self, valid_v2_manifest_dict):
        """Test extra fields are allowed for v1 compatibility."""
        valid_v2_manifest_dict["extra_field"] = "extra_value"

        manifest = PluginManifestSchema(**valid_v2_manifest_dict)

        # Extra field should be allowed
        assert manifest.name == "TestPlugin"

    def test_manifest_with_description(self, valid_v2_manifest_dict):
        """Test manifest with optional description."""
        valid_v2_manifest_dict["description"] = "A test plugin"

        manifest = PluginManifestSchema(**valid_v2_manifest_dict)

        assert manifest.description == "A test plugin"
