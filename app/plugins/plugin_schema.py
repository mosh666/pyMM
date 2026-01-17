"""Pydantic schema models for plugin YAML validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


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
        if v is not None and v != "":
            if len(v) != 64:
                raise ValueError(f"SHA-256 checksum must be exactly 64 characters, got {len(v)}")
            if not all(c in "0123456789ABCDEFabcdef" for c in v):
                raise ValueError("SHA-256 checksum must contain only hexadecimal characters")
        # Convert empty string to None
        return v if v else None

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
    """

    # Schema version (v2 required)
    schema_version: Literal[2] = Field(
        default=2, description="Manifest schema version (only v2 supported)"
    )

    # Required fields
    name: str = Field(..., description="Display name of the plugin")
    version: str = Field(..., description="Version of the plugin/tool")
    mandatory: bool = Field(..., description="Whether plugin is required for pyMM to function")
    enabled: bool = Field(..., description="Whether plugin is active")

    # Platform-specific configuration (v2)
    platforms: dict[str, PlatformConfig] = Field(
        ...,
        description="Platform-specific configurations keyed by 'windows', 'linux', 'macos'",
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
    category: (
        Literal[
            "Version Control",
            "Media Processing",
            "Image Processing",
            "Database",
            "Development Tools",
            "Other",
        ]
        | None
    ) = Field(
        None,
        description=(
            "Optional category for organizing plugins in documentation. "
            "If not specified, plugins are categorized based on hardcoded mapping "
            "for backward compatibility. Available categories: Version Control, "
            "Media Processing, Image Processing, Database, Development Tools, Other."
        ),
    )

    @field_validator("platforms")
    @classmethod
    def validate_platforms(cls, v: dict[str, PlatformConfig]) -> dict[str, PlatformConfig]:
        """Validate platforms contains at least one valid platform."""
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
        "str_strip_whitespace": True,  # Strip whitespace from strings
        "validate_assignment": True,  # Validate on attribute assignment
    }
