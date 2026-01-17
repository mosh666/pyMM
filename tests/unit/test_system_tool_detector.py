"""Tests for SystemToolDetector.

Tests tool detection logic with mocking to run consistently across all platforms.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from app.plugins.system_tool_detector import (
    SystemToolDetector,
    SystemToolInfo,
    ToolDetectionStatus,
)
from app.plugins.system_tool_detector import (
    SystemToolInfo as ToolInfo,
)


class TestToolDetectionStatus:
    """Test suite for ToolDetectionStatus enum."""

    def test_status_values(self):
        """Test that all expected status values exist."""
        assert ToolDetectionStatus.FOUND_VALID == ToolDetectionStatus.FOUND_VALID
        assert ToolDetectionStatus.FOUND_INVALID == ToolDetectionStatus.FOUND_INVALID
        assert ToolDetectionStatus.NOT_FOUND == ToolDetectionStatus.NOT_FOUND
        assert ToolDetectionStatus.ERROR == ToolDetectionStatus.ERROR


class TestSystemToolInfo:
    """Test suite for SystemToolInfo dataclass."""

    def test_create_tool_info(self):
        """Test creating SystemToolInfo instance."""
        info = SystemToolInfo(
            name="git",
            path=Path("/usr/bin/git"),
            version="2.43.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        assert info.name == "git"
        assert info.path == Path("/usr/bin/git")
        assert info.version == "2.43.0"
        assert info.status == ToolDetectionStatus.FOUND_VALID
        assert info.error_message is None

    def test_tool_info_with_error(self):
        """Test SystemToolInfo with error message."""
        info = SystemToolInfo(
            name="missing",
            path=None,
            version=None,
            status=ToolDetectionStatus.NOT_FOUND,
            error_message="Tool not found in PATH",
        )

        assert info.error_message == "Tool not found in PATH"

    def test_meets_constraint_no_constraint(self):
        """Test meets_constraint with None constraint."""
        info = SystemToolInfo(
            name="git",
            path=Path("/usr/bin/git"),
            version="2.43.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        assert info.meets_constraint(None) is True

    def test_meets_constraint_no_version(self):
        """Test meets_constraint when version is None."""
        info = SystemToolInfo(
            name="git",
            path=None,
            version=None,
            status=ToolDetectionStatus.NOT_FOUND,
        )

        assert info.meets_constraint(">=2.0") is False

    def test_meets_constraint_valid(self):
        """Test meets_constraint with valid version."""
        info = SystemToolInfo(
            name="git",
            path=Path("/usr/bin/git"),
            version="2.43.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        assert info.meets_constraint(">=2.0") is True
        assert info.meets_constraint(">=2.43") is True
        assert info.meets_constraint("<3.0") is True
        assert info.meets_constraint(">=2.40,<3.0") is True

    def test_meets_constraint_invalid(self):
        """Test meets_constraint with invalid version."""
        info = SystemToolInfo(
            name="git",
            path=Path("/usr/bin/git"),
            version="2.43.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        assert info.meets_constraint(">=3.0") is False
        assert info.meets_constraint("<2.0") is False
        assert info.meets_constraint("==2.40.0") is False

    def test_meets_constraint_invalid_format(self):
        """Test meets_constraint with malformed constraint or version."""
        info = SystemToolInfo(
            name="tool",
            path=Path("/usr/bin/tool"),
            version="invalid.version",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        # Should return False for invalid version format
        assert info.meets_constraint(">=2.0") is False


class TestSystemToolDetector:
    """Test suite for SystemToolDetector."""

    @pytest.fixture
    def detector(self):
        """Create SystemToolDetector instance."""
        return SystemToolDetector()

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert hasattr(detector, "logger")
        assert hasattr(detector, "_cache")
        assert isinstance(detector._cache, dict)
        assert len(detector._cache) == 0

    def test_version_patterns_exist(self, detector):
        """Test that VERSION_PATTERNS is defined with common tools."""
        assert "git" in SystemToolDetector.VERSION_PATTERNS
        assert "ffmpeg" in SystemToolDetector.VERSION_PATTERNS
        assert "exiftool" in SystemToolDetector.VERSION_PATTERNS
        assert "magick" in SystemToolDetector.VERSION_PATTERNS
        assert "mysql" in SystemToolDetector.VERSION_PATTERNS

    def test_find_tool_not_in_path(self, detector):
        """Test finding tool that doesn't exist in PATH."""
        # Mock shutil.which to return None
        with patch("shutil.which", return_value=None):
            info = detector.find_system_tool("nonexistent")

            assert info is not None
            assert info.name == "nonexistent"
            assert info.path is None
            assert info.version is None
            assert info.status == ToolDetectionStatus.NOT_FOUND

    def test_find_git_success(self, detector, mock_subprocess_run, mock_shutil_which):
        """Test successfully finding git with version."""
        mock_shutil_which.return_value = "/usr/bin/git"

        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            info = detector.find_system_tool("git")

            assert info is not None
            assert info.name == "git"
            assert info.path == Path("/usr/bin/git")
            assert info.version == "2.43.0"
            assert info.status == ToolDetectionStatus.FOUND_VALID

    def test_find_ffmpeg_success(self, detector, mock_subprocess_run, mock_shutil_which):
        """Test successfully finding ffmpeg with version."""
        mock_shutil_which.return_value = "/usr/bin/ffmpeg"

        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            info = detector.find_system_tool("ffmpeg")

            assert info is not None
            assert info.name == "ffmpeg"
            assert info.path == Path("/usr/bin/ffmpeg")
            assert info.version == "6.0"
            assert info.status == ToolDetectionStatus.FOUND_VALID

    def test_find_tool_with_constraint_valid(
        self, detector, mock_subprocess_run, mock_shutil_which
    ):
        """Test finding tool with version constraint that is satisfied."""
        mock_shutil_which.return_value = "/usr/bin/git"

        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            info = detector.find_system_tool("git", ">=2.0")

            assert info is not None
            assert info.status == ToolDetectionStatus.FOUND_VALID
            assert info.version == "2.43.0"
            assert info.meets_constraint(">=2.0") is True

    def test_find_tool_with_constraint_invalid(
        self, detector, mock_subprocess_run, mock_shutil_which
    ):
        """Test finding tool with version constraint that is not satisfied."""
        mock_shutil_which.return_value = "/usr/bin/git"

        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            info = detector.find_system_tool("git", ">=3.0")

            assert info is not None
            assert info.status == ToolDetectionStatus.FOUND_INVALID
            assert info.version == "2.43.0"
            assert info.meets_constraint(">=3.0") is False

    def test_find_tool_version_command_fails(self, detector, mock_subprocess_run_failure):
        """Test handling of version command failure."""
        # Mock both which and subprocess
        with (
            patch("shutil.which", return_value="/usr/bin/broken"),
            patch("subprocess.run", side_effect=mock_subprocess_run_failure),
        ):
            info = detector.find_system_tool("broken")

            # Tool was found but version detection failed
            assert info is not None
            assert info.path == Path("/usr/bin/broken")
            assert info.status == ToolDetectionStatus.ERROR

    def test_find_tool_caching(self, detector, mock_subprocess_run, mock_shutil_which):
        """Test that results are cached."""
        mock_shutil_which.return_value = "/usr/bin/git"

        with (
            patch("shutil.which", mock_shutil_which) as which_mock,
            patch("subprocess.run", side_effect=mock_subprocess_run) as run_mock,
        ):
            # First call
            info1 = detector.find_system_tool("git", ">=2.0")
            assert info1 is not None

            # Second call with same parameters
            info2 = detector.find_system_tool("git", ">=2.0")
            assert info2 is not None

            # Should be the same cached object
            assert info1 is info2

            # shutil.which and subprocess should only be called once
            assert which_mock.call_count == 1
            assert run_mock.call_count == 1

    def test_find_tool_cache_different_constraints(
        self, detector, mock_subprocess_run, mock_shutil_which
    ):
        """Test that different constraints create separate cache entries."""
        mock_shutil_which.return_value = "/usr/bin/git"

        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            # Call with different constraints
            info1 = detector.find_system_tool("git", ">=2.0")
            info2 = detector.find_system_tool("git", ">=3.0")
            info3 = detector.find_system_tool("git", None)

            # Should have different cache entries with different statuses
            assert info1.status == ToolDetectionStatus.FOUND_VALID
            assert info2.status == ToolDetectionStatus.FOUND_INVALID
            assert info3.status == ToolDetectionStatus.FOUND_VALID

            # But all should have the same version
            assert info1.version == info2.version == info3.version == "2.43.0"

    def test_find_tool_without_version_pattern(self, detector):
        """Test finding tool without known version pattern."""
        with patch("shutil.which", return_value="/usr/bin/unknown"):
            info = detector.find_system_tool("unknown")

            assert info is not None
            assert info.name == "unknown"
            assert info.path == Path("/usr/bin/unknown")
            # Version will be None since we don't have a pattern
            assert info.version is None
            # Status should be ERROR when version detection fails (no pattern)
            assert info.status == ToolDetectionStatus.ERROR
            assert "Could not detect version" in info.error_message

    def test_find_tool_subprocess_exception(self, detector):
        """Test handling of subprocess exceptions."""
        with (
            patch("shutil.which", return_value="/usr/bin/git"),
            patch("subprocess.run", side_effect=Exception("Test error")),
        ):
            info = detector.find_system_tool("git")

            assert info is not None
            assert info.status == ToolDetectionStatus.ERROR
            assert info.error_message is not None

    def test_version_extraction_git(self, detector):
        """Test version extraction from git output."""
        from tests.fixtures.platform_data import MOCK_GIT_VERSION_OUTPUT

        output = MOCK_GIT_VERSION_OUTPUT
        pattern = SystemToolDetector.VERSION_PATTERNS["git"][1]

        import re

        match = re.search(pattern, output)
        assert match is not None
        assert match.group(1) == "2.43.0"

    def test_version_extraction_ffmpeg(self, detector):
        """Test version extraction from ffmpeg output."""
        from tests.fixtures.platform_data import MOCK_FFMPEG_VERSION_OUTPUT

        output = MOCK_FFMPEG_VERSION_OUTPUT
        pattern = SystemToolDetector.VERSION_PATTERNS["ffmpeg"][1]

        import re

        match = re.search(pattern, output)
        assert match is not None
        assert match.group(1) == "6.0"

    def test_version_extraction_exiftool(self, detector):
        """Test version extraction from exiftool output."""
        from tests.fixtures.platform_data import MOCK_EXIFTOOL_VERSION_OUTPUT

        output = MOCK_EXIFTOOL_VERSION_OUTPUT
        pattern = SystemToolDetector.VERSION_PATTERNS["exiftool"][1]

        import re

        match = re.search(pattern, output)
        assert match is not None
        assert match.group(1) == "12.76"

    def test_all_tools_have_valid_patterns(self, detector):
        """Test that all VERSION_PATTERNS are valid regex."""
        import re

        for _flag, pattern in SystemToolDetector.VERSION_PATTERNS.values():
            # Should compile without error
            compiled = re.compile(pattern)
            assert compiled is not None
            # Should have at least one capturing group
            assert compiled.groups >= 1

    def test_find_multiple_tools(self, detector, mock_subprocess_run, mock_shutil_which):
        """Test finding multiple different tools."""
        with (
            patch("shutil.which", mock_shutil_which),
            patch("subprocess.run", side_effect=mock_subprocess_run),
        ):
            tools = ["git", "ffmpeg", "exiftool"]
            results = {}

            for tool in tools:
                info = detector.find_system_tool(tool)
                results[tool] = info

            # All should be found
            assert all(info.status == ToolDetectionStatus.FOUND_VALID for info in results.values())
            assert all(info.version is not None for info in results.values())

            # Check specific versions
            assert results["git"].version == "2.43.0"
            assert results["ffmpeg"].version == "6.0"
            assert results["exiftool"].version == "12.76"

    def test_detect_version_subprocess_timeout(self, detector):
        """Test version detection when subprocess times out."""
        import subprocess

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("test", 5)):
            result = detector._detect_version("git", Path("/usr/bin/git"))

        assert result is None

    def test_detect_version_generic_exception(self, detector):
        """Test version detection with unexpected exception."""
        with patch("subprocess.run", side_effect=Exception("Unexpected error")):
            result = detector._detect_version("git", Path("/usr/bin/git"))

        assert result is None

    def test_get_cache_stats_with_mixed_statuses(self, detector):
        """Test cache statistics with various detection statuses."""
        # Manually populate cache with different statuses
        detector._cache["tool1"] = ToolInfo(
            name="tool1",
            path=Path("/usr/bin/tool1"),
            version="1.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )
        detector._cache["tool2"] = ToolInfo(
            name="tool2",
            path=Path("/usr/bin/tool2"),
            version="0.5",
            status=ToolDetectionStatus.FOUND_INVALID,
        )
        detector._cache["tool3"] = ToolInfo(
            name="tool3", path=None, version=None, status=ToolDetectionStatus.NOT_FOUND
        )
        detector._cache["tool4"] = ToolInfo(
            name="tool4", path=None, version=None, status=ToolDetectionStatus.ERROR
        )

        stats = detector.get_cache_stats()

        assert stats["total_cached"] == 4
        assert stats["found_valid"] == 1
        assert stats["found_invalid"] == 1
        assert stats["not_found"] == 1
        assert stats["error"] == 1

    def test_clear_cache(self, detector):
        """Test clearing the detection cache."""
        # Add some items to cache
        detector._cache["tool1"] = ToolInfo(
            name="tool1",
            path=Path("/usr/bin/tool1"),
            version="1.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )
        detector._cache["tool2"] = ToolInfo(
            name="tool2",
            path=Path("/usr/bin/tool2"),
            version="2.0",
            status=ToolDetectionStatus.FOUND_VALID,
        )

        assert len(detector._cache) == 2

        detector.clear_cache()

        assert len(detector._cache) == 0
