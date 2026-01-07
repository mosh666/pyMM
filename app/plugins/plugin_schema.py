"""Pydantic schema models for plugin YAML validation."""

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class PluginSource(BaseModel):
    """Plugin source configuration for downloading."""

    type: str = Field(..., description="Download method (currently only 'url' supported)")
    base_uri: str = Field(..., description="Download URL for the plugin archive")
    asset_pattern: str | None = Field(
        None, description="Pattern for GitHub release assets (not yet implemented)"
    )
    checksum_sha256: str | None = Field(
        None, description="SHA-256 hash (uppercase hex) for integrity verification"
    )
    file_size: int | None = Field(
        None, description="Expected file size in bytes for progress tracking"
    )

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate that source type is supported."""
        if v not in ("url",):
            raise ValueError(f"Unsupported source type: {v}. Only 'url' is currently supported.")
        return v

    @field_validator("checksum_sha256")
    @classmethod
    def validate_checksum(cls, v: str | None) -> str | None:
        """Validate SHA-256 checksum format."""
        if v is not None:
            if len(v) != 64:
                raise ValueError(f"SHA-256 checksum must be exactly 64 characters, got {len(v)}")
            if not all(c in "0123456789ABCDEFabcdef" for c in v):
                raise ValueError("SHA-256 checksum must contain only hexadecimal characters")
        return v

    @field_validator("file_size")
    @classmethod
    def validate_file_size(cls, v: int | None) -> int | None:
        """Validate file size is positive."""
        if v is not None and v <= 0:
            raise ValueError(f"File size must be positive, got {v}")
        return v


class PluginCommand(BaseModel):
    """Plugin command configuration for executable location."""

    path: str = Field(
        "",
        description="Relative path to executable directory from plugin root (empty string for root)",
    )
    executable: str = Field(..., description="Filename of the executable")

    @field_validator("executable")
    @classmethod
    def validate_executable(cls, v: str) -> str:
        """Validate executable is not empty."""
        if not v or not v.strip():
            raise ValueError("Executable filename cannot be empty")
        return v


class PlatformConfig(BaseModel):
    """Platform-specific plugin configuration.

    Defines how a plugin should be installed and configured on a specific platform
    (Windows, Linux, or macOS).
    """

    source: PluginSource | None = Field(
        None, description="Download source for portable binaries (optional if using system package)"
    )
    command: PluginCommand = Field(..., description="Executable command configuration")
    system_package: str | None = Field(
        None,
        description="System package name (e.g., 'git' for apt/brew) for system-installed tools",
    )
    version_constraint: str | None = Field(
        None, description="Version constraint using packaging specifiers (e.g., '>=2.40,<4.0')"
    )

    @field_validator("version_constraint")
    @classmethod
    def validate_version_constraint(cls, v: str | None) -> str | None:
        """Validate version constraint format."""
        if v is not None:
            try:
                from packaging.specifiers import SpecifierSet

                SpecifierSet(v)
            except Exception as e:
                raise ValueError(f"Invalid version constraint '{v}': {e}") from e
        return v


class PluginManifestSchema(BaseModel):
    """Complete plugin manifest schema for YAML validation.

    This schema validates all fields in plugin.yaml files to ensure
    they meet the requirements for the plugin system.

    Schema version 2 introduces platform-specific configuration allowing
    cross-platform support with system package detection and portable binary fallback.

    For backward compatibility, v1 manifests are automatically detected and converted.
    """

    # Schema version (v2 required, v1 auto-converted)
    schema_version: Literal[1, 2] = Field(
        default=1, description="Manifest schema version (1=legacy, 2=platform-aware)"
    )

    # Required fields
    name: str = Field(..., description="Display name of the plugin")
    version: str = Field(..., description="Version of the plugin/tool")
    mandatory: bool = Field(..., description="Whether plugin is required for pyMM to function")
    enabled: bool = Field(..., description="Whether plugin is active")

    # Platform-specific configuration (v2) or flat config (v1)
    platforms: dict[str, PlatformConfig] | None = Field(
        None,
        description="Platform-specific configurations keyed by 'windows', 'linux', 'macos' (v2 only)",
    )

    # Legacy v1 fields (auto-converted to platforms)
    source: dict[str, Any] | None = Field(
        None, description="Legacy v1 source configuration (converted to platforms.windows.source)"
    )
    command: dict[str, Any] | None = Field(
        None, description="Legacy v1 command configuration (converted to platforms.windows.command)"
    )

    # Hybrid plugin system preferences
    prefer_system: bool = Field(
        True, description="Whether to prefer system-installed tools over portable binaries"
    )

    register_to_path: bool = Field(
        False, description="Whether to add executable directory to PATH (legacy, mostly unused)"
    )

    # Optional fields
    description: str | None = Field(None, description="Human-readable description of the plugin")
    dependencies: list[str] | None = Field(
        None, description="List of plugin names this plugin depends on"
    )

    @model_validator(mode="before")
    @classmethod
    def convert_v1_to_v2(cls, data: Any) -> Any:
        """Auto-convert v1 manifests and flattened v2 manifests to proper v2 format."""
        if not isinstance(data, dict):
            return data

        # Check if platforms exist but have flat structure (schema_version: 2 with flat fields)
        if "platforms" in data and isinstance(data["platforms"], dict):
            platforms = data["platforms"]
            needs_restructure = False

            for platform_key, platform_data in platforms.items():
                if isinstance(platform_data, dict):
                    # Check if it has flat fields like 'source: url', 'command_path', etc.
                    if (
                        "source" in platform_data and isinstance(platform_data.get("source"), str)
                    ) or ("command_path" in platform_data or "download_url" in platform_data):
                        needs_restructure = True
                        break

            if needs_restructure:
                # Restructure flattened v2 format to nested v2 format
                restructured_platforms = {}
                for platform_key, platform_data in platforms.items():
                    if not isinstance(platform_data, dict):
                        continue

                    # Build nested source object
                    source_obj = None
                    if "source" in platform_data or "download_url" in platform_data:
                        source_obj = {
                            "type": platform_data.get("source", "url"),
                            "base_uri": platform_data.get("download_url", ""),
                            "asset_pattern": platform_data.get("asset_pattern"),
                            "checksum_sha256": platform_data.get("checksum_sha256") or None,
                            "file_size": platform_data.get("file_size"),
                        }
                        # Remove None values
                        source_obj = {k: v for k, v in source_obj.items() if v is not None}

                    # Build nested command object
                    command_obj = {
                        "path": platform_data.get("command_path", ""),
                        "executable": platform_data.get("command_executable", ""),
                    }

                    restructured_platforms[platform_key] = {
                        "source": source_obj,
                        "command": command_obj,
                        "system_package": platform_data.get("system_package"),
                        "version_constraint": platform_data.get("version_constraint"),
                    }
                    # Remove None values
                    restructured_platforms[platform_key] = {
                        k: v
                        for k, v in restructured_platforms[platform_key].items()
                        if v is not None
                    }

                data["platforms"] = restructured_platforms
                data["schema_version"] = 2
                return data

        # Check if this is a v1 manifest (has source/command but no platforms)
        schema_version = data.get("schema_version", 1)
        if schema_version == 1 and "platforms" not in data:
            # Convert v1 to v2 format
            if "source" in data and "command" in data:
                source_data = data["source"]
                command_data = data["command"]

                # Build PlatformConfig for Windows (v1 was Windows-only)
                platform_config = {
                    "windows": {
                        "source": {
                            "type": source_data.get("type", "url"),
                            "base_uri": source_data.get("base_uri", ""),
                            "asset_pattern": source_data.get("asset_pattern"),
                            "checksum_sha256": source_data.get("checksum_sha256"),
                            "file_size": source_data.get("file_size"),
                        },
                        "command": {
                            "path": command_data.get("path", ""),
                            "executable": command_data.get("executable", ""),
                        },
                    }
                }

                data["platforms"] = platform_config
                data["schema_version"] = 2

        return data

    @field_validator("platforms")
    @classmethod
    def validate_platforms(
        cls, v: dict[str, PlatformConfig] | None
    ) -> dict[str, PlatformConfig] | None:
        """Validate platforms contains at least one valid platform."""
        if v is None:
            return v

        valid_platforms = {"windows", "linux", "macos"}
        if not v:
            raise ValueError("At least one platform configuration required")

        invalid = set(v.keys()) - valid_platforms
        if invalid:
            raise ValueError(
                f"Invalid platform keys: {invalid}. Valid platforms: {valid_platforms}"
            )

        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate plugin name is not empty."""
        if not v or not v.strip():
            raise ValueError("Plugin name cannot be empty")
        return v

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version string is not empty."""
        if not v or not v.strip():
            raise ValueError("Plugin version cannot be empty")
        return v

    @field_validator("dependencies")
    @classmethod
    def validate_dependencies(cls, v: list[str] | None) -> list[str] | None:
        """Validate dependencies list contains no empty strings."""
        if v is not None and not all(dep and dep.strip() for dep in v):
            raise ValueError("Dependency list cannot contain empty strings")
        return v

    model_config = {
        "extra": "allow",  # Allow extra fields for v1 compatibility
        "str_strip_whitespace": True,  # Strip whitespace from strings
        "validate_assignment": True,  # Validate on attribute assignment
    }
