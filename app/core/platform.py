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

import ast
from dataclasses import dataclass
from enum import StrEnum
import logging
from pathlib import Path
import sys
from typing import TYPE_CHECKING
import warnings

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "Platform",
    "PlatformCheckError",
    "PortableConfig",
    "PortableMode",
    "check_plugin_platform_usage",
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
    CONFIG = "config"  # Set via legacy config file (deprecated, auto-migrated)
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
            case PortableMode.CONFIG:
                source_text = "config file (migrated)"
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
            case PortableMode.CONFIG:
                return f"{'Portable' if self.enabled else 'Installed'} (config)"
            case PortableMode.AUTO:
                return "Portable (auto)" if self.enabled else "Installed"
            case PortableMode.DEFAULT:
                return "Portable" if self.enabled else "Installed"


class PlatformCheckError(Exception):
    """
    Exception raised when strict platform checks are enabled and violations are found.

    This is raised during plugin loading when:
    1. strict_platform_checks is True in app.yaml
    2. A plugin uses direct sys.platform access instead of the Platform API
    """

    def __init__(self, plugin_path: Path, violations: list[tuple[int, str]]) -> None:
        self.plugin_path = plugin_path
        self.violations = violations
        lines = ", ".join(f"line {line}" for line, _ in violations)
        super().__init__(
            f"Plugin {plugin_path.name} uses deprecated direct platform access at {lines}. "
            f"Use app.core.platform.Platform instead of sys.platform."
        )


class _PlatformUsageVisitor(ast.NodeVisitor):
    """AST visitor to find direct platform access patterns."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.violations: list[tuple[int, str]] = []

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Check for sys.platform and os.name access."""
        if not isinstance(node.value, ast.Name):
            self.generic_visit(node)
            return

        # Check for sys.platform
        if node.value.id == "sys" and node.attr == "platform":
            snippet = ast.get_source_segment(self.source, node) or "sys.platform"
            self.violations.append((node.lineno, snippet))

        # Check for os.name
        if node.value.id == "os" and node.attr == "name":
            snippet = ast.get_source_segment(self.source, node) or "os.name"
            self.violations.append((node.lineno, snippet))

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for platform.system() calls."""
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "platform"
            and node.func.attr == "system"
        ):
            snippet = ast.get_source_segment(self.source, node) or "platform.system()"
            self.violations.append((node.lineno, snippet))

        self.generic_visit(node)


def _emit_platform_warning(
    plugin_path: Path,
    violations: list[tuple[int, str]],
    strict: bool,
) -> None:
    """Emit deprecation warning for platform usage violations."""
    warning_msg = (
        f"Plugin {plugin_path.name} uses deprecated direct platform access at "
        f"line(s) {', '.join(str(line) for line, _ in violations)}. "
        f"Use app.core.platform.Platform instead of sys.platform. "
        f"This will become an error in a future version."
    )
    warnings.warn(warning_msg, DeprecationWarning, stacklevel=3)
    logger.warning(warning_msg)

    if strict:
        raise PlatformCheckError(plugin_path, violations)


def check_plugin_platform_usage(
    plugin_path: Path,
    strict: bool = False,
    allowed_modules: Sequence[str] | None = None,
) -> list[tuple[int, str]]:
    """
    Check a Python file for direct sys.platform usage.

    Scans the AST of a Python file to find direct usage of sys.platform,
    platform.system(), or os.name for platform detection. These should be
    replaced with the Platform API from this module.

    Args:
        plugin_path: Path to the Python file to check
        strict: If True, raise PlatformCheckError on violations
        allowed_modules: Module names that are allowed to use direct platform access
                        (e.g., ["app.core.platform"] for the platform module itself)

    Returns:
        List of (line_number, code_snippet) tuples for violations

    Raises:
        PlatformCheckError: If strict=True and violations are found
    """
    if allowed_modules is None:
        allowed_modules = ["app.core.platform", "app/core/platform.py"]

    # Skip checking allowed modules
    path_str = str(plugin_path)
    if any(allowed in path_str for allowed in allowed_modules):
        return []

    try:
        source = Path(plugin_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=path_str)
    except (OSError, SyntaxError) as e:
        logger.warning("Could not parse %s for platform check: %s", plugin_path, e)
        return []

    visitor = _PlatformUsageVisitor(source)
    visitor.visit(tree)

    if visitor.violations:
        _emit_platform_warning(plugin_path, visitor.violations, strict)

    return visitor.violations
