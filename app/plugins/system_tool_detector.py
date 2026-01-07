"""System tool detection for hybrid plugin management.

Detects system-installed tools via PATH and validates versions against constraints.
"""

from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path
import re
import shutil
import subprocess
from typing import ClassVar

from packaging.specifiers import SpecifierSet
from packaging.version import InvalidVersion, Version


class ToolDetectionStatus(str, Enum):
    """Status of system tool detection."""

    FOUND_VALID = "found_valid"  # Tool found, version meets constraint
    FOUND_INVALID = "found_invalid"  # Tool found, version fails constraint
    NOT_FOUND = "not_found"  # Tool not found in PATH
    ERROR = "error"  # Error during detection


@dataclass
class SystemToolInfo:
    """Information about a detected system tool."""

    name: str
    path: Path | None
    version: str | None
    status: ToolDetectionStatus
    error_message: str | None = None

    def meets_constraint(self, constraint: str | None) -> bool:
        """Check if tool version meets the given constraint."""
        if constraint is None:
            return True
        if self.version is None:
            return False

        try:
            spec_set = SpecifierSet(constraint)
            return spec_set.contains(Version(self.version))
        except (InvalidVersion, ValueError):
            return False


class SystemToolDetector:
    """Detector for system-installed tools with version validation.

    Uses shutil.which() to find tools in PATH and validates versions
    against packaging specifiers. Results are cached per session.
    """

    # Tool-specific version detection patterns: (flag, regex)
    VERSION_PATTERNS: ClassVar[dict[str, tuple[str, str]]] = {
        "git": ("--version", r"git version (\d+\.\d+\.\d+)"),
        "ffmpeg": ("-version", r"ffmpeg version (\d+\.\d+\.?\d*)"),
        "exiftool": ("-ver", r"(\d+\.\d+)"),
        "magick": ("--version", r"ImageMagick (\d+\.\d+\.\d+-?\d*)"),
        "convert": ("--version", r"ImageMagick (\d+\.\d+\.\d+-?\d*)"),  # Legacy ImageMagick
        "mysql": ("--version", r"mysql\s+Ver\s+(\d+\.\d+\.\d+)"),
        "mkvmerge": ("--version", r"mkvmerge v(\d+\.\d+\.\d+)"),
        "digikam": ("--version", r"digikam (\d+\.\d+\.\d+)"),
        "git-lfs": ("version", r"git-lfs/(\d+\.\d+\.\d+)"),
        "gitversion": ("/version", r"(\d+\.\d+\.\d+)"),
    }

    def __init__(self) -> None:
        """Initialize system tool detector."""
        self.logger = logging.getLogger(__name__)
        self._cache: dict[str, SystemToolInfo] = {}

    def find_system_tool(
        self, name: str, version_constraint: str | None = None
    ) -> SystemToolInfo | None:
        """Find a system-installed tool and validate its version.

        Args:
            name: Tool executable name (e.g., 'git', 'ffmpeg')
            version_constraint: Optional version constraint (e.g., '>=2.40,<4.0')

        Returns:
            SystemToolInfo if tool found, None otherwise
        """
        # Check cache first
        cache_key = f"{name}:{version_constraint or ''}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Find tool in PATH
        tool_path = shutil.which(name)
        if tool_path is None:
            info = SystemToolInfo(
                name=name, path=None, version=None, status=ToolDetectionStatus.NOT_FOUND
            )
            self._cache[cache_key] = info
            return info

        # Detect version
        version = self._detect_version(name, Path(tool_path))
        if version is None:
            info = SystemToolInfo(
                name=name,
                path=Path(tool_path),
                version=None,
                status=ToolDetectionStatus.ERROR,
                error_message="Could not detect version",
            )
            self._cache[cache_key] = info
            return info

        # Validate version constraint
        if version_constraint:
            try:
                spec_set = SpecifierSet(version_constraint)
                version_obj = Version(version)
                meets_constraint = spec_set.contains(version_obj)

                status = (
                    ToolDetectionStatus.FOUND_VALID
                    if meets_constraint
                    else ToolDetectionStatus.FOUND_INVALID
                )
            except (InvalidVersion, ValueError) as e:
                self.logger.warning(
                    f"Invalid version '{version}' or constraint '{version_constraint}': {e}"
                )
                status = ToolDetectionStatus.ERROR
        else:
            status = ToolDetectionStatus.FOUND_VALID

        info = SystemToolInfo(name=name, path=Path(tool_path), version=version, status=status)
        self._cache[cache_key] = info
        return info

    def _detect_version(self, name: str, path: Path) -> str | None:
        """Detect tool version by running it with version flag.

        Args:
            name: Tool name for pattern lookup
            path: Path to tool executable

        Returns:
            Version string if detected, None otherwise
        """
        pattern_info = self.VERSION_PATTERNS.get(name)
        if pattern_info is None:
            self.logger.debug(f"No version pattern configured for '{name}'")
            return None

        version_flag, version_regex = pattern_info

        try:
            result = subprocess.run(
                [str(path), version_flag],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,  # Don't raise on non-zero exit
            )

            # Try stdout first, then stderr
            output = result.stdout if result.stdout else result.stderr

            match = re.search(version_regex, output, re.IGNORECASE)
            if match:
                version = match.group(1)
                self.logger.debug(f"Detected {name} version: {version}")
                return version

            self.logger.debug(f"Version regex did not match for {name}. Output: {output[:200]}")
            return None

        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout detecting version for {name}")
            return None
        except Exception as e:
            self.logger.warning(f"Error detecting version for {name}: {e}")
            return None

    def clear_cache(self) -> None:
        """Clear the tool detection cache."""
        self._cache.clear()

    def get_cache_stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        status_counts = {"found_valid": 0, "found_invalid": 0, "not_found": 0, "error": 0}

        for info in self._cache.values():
            status_counts[info.status] += 1

        return {"total_cached": len(self._cache), **status_counts}
