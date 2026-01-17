"""
Platform detection and cross-platform utilities for pyMediaManager.

This module provides a centralized, type-safe way to handle platform detection
throughout the application. All platform-specific code should use these utilities
instead of directly checking sys.platform or platform.system().

Python 3.12+ is required for match statement support.

Example usage:
    from app.core.platform import Platform, current_platform, is_windows

    match current_platform():
        case Platform.WINDOWS:
            # Windows-specific code
        case Platform.LINUX | Platform.MACOS:
            # Unix-like code

    if is_windows():
        # Windows-specific code
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import logging
import sys

__all__ = [
    "Platform",
    "PortableConfig",
    "PortableMode",
    "current_platform",
    "is_linux",
    "is_macos",
    "is_unix",
    "is_windows",
    "platform_name",
]

logger = logging.getLogger(__name__)


class Platform(StrEnum):
    """
    Enumeration of supported platforms.

    Uses StrEnum (Python 3.11+) for easy string comparison and serialization.
    Values match sys.platform for direct comparison when needed.
    """

    WINDOWS = "win32"
    LINUX = "linux"
    MACOS = "darwin"

    @classmethod
    def from_sys_platform(cls, platform_string: str) -> Platform:
        """
        Convert a sys.platform string to Platform enum.

        Args:
            platform_string: Value from sys.platform

        Returns:
            Matching Platform enum value, defaults to LINUX for unknown platforms
        """
        match platform_string:
            case "win32":
                return cls.WINDOWS
            case "darwin":
                return cls.MACOS
            case "linux" | _:
                return cls.LINUX


def current_platform() -> Platform:
    """
    Get the current platform as a Platform enum.

    Returns:
        Platform enum value for the current system
    """
    return Platform.from_sys_platform(sys.platform)


def is_windows() -> bool:
    """Check if running on Windows."""
    return current_platform() == Platform.WINDOWS


def is_linux() -> bool:
    """Check if running on Linux."""
    return current_platform() == Platform.LINUX


def is_macos() -> bool:
    """Check if running on macOS."""
    return current_platform() == Platform.MACOS


def is_unix() -> bool:
    """Check if running on a Unix-like system (Linux or macOS)."""
    return current_platform() in (Platform.LINUX, Platform.MACOS)


def platform_name() -> str:
    """
    Get a human-readable platform name.

    Returns:
        Human-readable platform name (e.g., "Windows", "Linux", "macOS")
    """
    match current_platform():
        case Platform.WINDOWS:
            return "Windows"
        case Platform.LINUX:
            return "Linux"
        case Platform.MACOS:
            return "macOS"


class PortableMode(StrEnum):
    """Source of portable mode configuration."""

    CLI = "cli"  # Set via --portable or --no-portable command line flag
    ENV = "env"  # Set via PYMM_PORTABLE environment variable
    AUTO = "auto"  # Auto-detected from running on removable media
    DEFAULT = "default"  # No explicit configuration, using default behavior


@dataclass(frozen=True, slots=True)
class PortableConfig:
    """
    Configuration for portable mode operation.

    Portable mode affects where the application stores data:
    - Portable: Data stored relative to executable/drive root
    - Non-portable: Data stored in platform-specific directories

    Attributes:
        enabled: Whether portable mode is active
        source: How portable mode was determined
        auto_detected_removable: If AUTO, whether removable media was detected
    """

    enabled: bool
    source: PortableMode
    auto_detected_removable: bool = False

    def __str__(self) -> str:
        """Human-readable representation of portable config."""
        status = "Portable" if self.enabled else "Installed"
        match self.source:
            case PortableMode.CLI:
                source_text = "command line"
            case PortableMode.ENV:
                source_text = "environment variable"
            case PortableMode.AUTO:
                source_text = "auto-detected" + (
                    " (removable media)" if self.auto_detected_removable else ""
                )
            case PortableMode.DEFAULT:
                source_text = "default"
        return f"{status} ({source_text})"

    @property
    def status_icon(self) -> str:
        """Get status icon for UI display."""
        return "📦" if self.enabled else "💻"

    @property
    def status_text(self) -> str:
        """Get short status text for UI display."""
        match self.source:
            case PortableMode.CLI:
                return f"{'Portable' if self.enabled else 'Installed'} (CLI)"
            case PortableMode.ENV:
                return f"{'Portable' if self.enabled else 'Installed'} (ENV)"
            case PortableMode.AUTO:
                return "Portable (auto)" if self.enabled else "Installed"
            case PortableMode.DEFAULT:
                return "Portable" if self.enabled else "Installed"
