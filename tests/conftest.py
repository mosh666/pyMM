"""Pytest configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any
from unittest.mock import MagicMock, Mock, patch

from PySide6.QtWidgets import QApplication
import pytest

from app.core.platform import Platform, current_platform
from tests.fixtures.platform_data import (
    MockPyudevContext,
    MockWMI,
    get_mock_tool_version_output,
)

# Platform marker names for auto-skip logic
PLATFORM_MARKERS = {"windows", "linux", "macos", "unix"}


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with platform markers."""
    # Register markers (also defined in pyproject.toml, but this ensures they're available)
    config.addinivalue_line(
        "markers",
        "windows: Tests that only run on Windows (composable with other platform markers)",
    )
    config.addinivalue_line(
        "markers",
        "linux: Tests that only run on Linux (composable with other platform markers)",
    )
    config.addinivalue_line(
        "markers",
        "macos: Tests that only run on macOS (composable with other platform markers)",
    )
    config.addinivalue_line(
        "markers",
        "unix: Tests that run on Unix-like systems (Linux and macOS)",
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """
    Modify test collection to skip tests based on platform markers.

    Platform markers are composable with OR logic:
    - @pytest.mark.linux @pytest.mark.macos -> runs on Linux OR macOS
    - @pytest.mark.windows -> runs only on Windows
    - @pytest.mark.unix -> runs on Linux OR macOS (shorthand)
    - No platform markers -> runs on all platforms
    """
    platform = current_platform()

    for item in items:
        # Get all platform markers on this test
        test_platforms: set[str] = set()
        for marker_name in PLATFORM_MARKERS:
            if item.get_closest_marker(marker_name):
                test_platforms.add(marker_name)

        # If no platform markers, test runs everywhere
        if not test_platforms:
            continue

        # Check if current platform matches any marker (OR logic)
        should_run = False

        if "windows" in test_platforms and platform == Platform.WINDOWS:
            should_run = True
        if "linux" in test_platforms and platform == Platform.LINUX:
            should_run = True
        if "macos" in test_platforms and platform == Platform.MACOS:
            should_run = True
        if "unix" in test_platforms and platform in (Platform.LINUX, Platform.MACOS):
            should_run = True

        if not should_run:
            skip_marker = pytest.mark.skip(
                reason=f"Test requires platform(s): {', '.join(sorted(test_platforms))}; "
                f"current platform: {platform.value}"
            )
            item.add_marker(skip_marker)


@pytest.fixture(autouse=True)
def mock_app_version():
    """Ensure app version satisfies template requirements during tests."""
    with (
        patch("app.__version__", "1.0.0"),
        patch("app.services.project_service.__version__", "1.0.0"),
    ):
        yield


@pytest.fixture(autouse=True)
def cleanup_watchdog_observers():
    """
    Automatically cleanup watchdog observers after each test.

    This fixture prevents accumulation of file system watchers that
    can cause Windows COM errors (0x8001010d) during test runs.
    """
    # Track all ProjectService instances created during the test
    project_services = []

    # Store original __init__ to wrap it
    from app.services.project_service import ProjectService

    original_init = ProjectService.__init__

    def wrapped_init(self, *args, **kwargs):
        """Wrapped init that tracks instances."""
        # Disable watching by default in tests unless explicitly enabled
        if "disable_watch" not in kwargs:
            kwargs["disable_watch"] = True
        original_init(self, *args, **kwargs)
        project_services.append(self)

    # Patch the __init__ method
    with patch.object(ProjectService, "__init__", wrapped_init):
        yield

    # Cleanup: stop all observers that were created
    for service in project_services:
        observer = getattr(service, "_observer", None)
        if observer is not None:
            try:
                observer.stop()
                observer.join(timeout=1.0)
            except Exception:
                pass  # Ignore cleanup errors


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def temp_dir(tmp_path):
    """
    Fixture for backward compatibility.
    Returns the standard tmp_path fixture.
    """
    return tmp_path


@pytest.fixture
def app_root(tmp_path):
    """Create a mock application root directory structure."""
    root = tmp_path / "pyMM"
    root.mkdir()

    # Create basic structure
    (root / "app").mkdir()
    (root / "config").mkdir()
    (root / "plugins").mkdir()

    return root


@pytest.fixture(autouse=True)
def mock_drive_root(monkeypatch, tmp_path):
    """
    Automatically mock FileSystemService.get_drive_root() to prevent
    tests from creating folders on the system drive.

    This fixture is autouse=True, so it applies to all tests automatically.
    """
    from app.core.services.file_system_service import FileSystemService

    # Create a mock drive root in the temp directory
    mock_drive = tmp_path / "mock_drive_root"
    mock_drive.mkdir(exist_ok=True)

    # Capture original method for bypass
    original_get_drive_root = FileSystemService.get_drive_root

    def mock_get_drive_root_method(self):
        """Mock implementation that returns temp directory instead of system drive."""
        # Allow bypassing the mock for unit tests of the service itself
        if getattr(self, "_bypass_drive_mock", False):
            return original_get_drive_root(self)

        # If _drive_root was explicitly set (not None), use it
        # Otherwise return the mock drive
        if hasattr(self, "_drive_root") and self._drive_root is not None:
            # Check if it's already pointing to a temp location
            if str(mock_drive) in str(self._drive_root):
                return self._drive_root

        # Set and return mock drive root
        self._drive_root = mock_drive
        return mock_drive

    # Monkey patch the method
    monkeypatch.setattr(FileSystemService, "get_drive_root", mock_get_drive_root_method)

    return mock_drive


# ============================================================================
# Shared Mock Fixtures for Common Patterns
# ============================================================================


@pytest.fixture
def mock_wmi():
    """Mock WMI module and connection for Windows storage testing.

    Returns a mock WMI connection with realistic USB, internal, and external
    drive data.  Use this fixture to test Windows storage detection without
    requiring Windows or actual WMI.

    Example:
        def test_windows_storage(mock_wmi):
            with patch('wmi.WMI', return_value=mock_wmi):
                storage = WindowsStorage()
    """
    return MockWMI()


@pytest.fixture
def mock_wmi_no_usb():
    """Mock WMI with only internal drives (no USB/removable)."""
    from tests.fixtures.platform_data import MOCK_WMI_INTERNAL_DISK

    return MockWMI(drives=[MOCK_WMI_INTERNAL_DISK])


@pytest.fixture
def mock_pyudev_context():
    """Mock pyudev Context for Linux udev testing.

    Returns a mock pyudev Context with realistic USB, internal, and external
    device data. Use this fixture to test Linux storage detection without
    requiring Linux or actual udev.

    Example:
        def test_linux_storage(mock_pyudev_context):
            with patch('pyudev.Context', return_value=mock_pyudev_context):
                storage = LinuxStorage()
    """
    return MockPyudevContext()


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for tool detection testing.

    Returns a mock that simulates version command outputs for various tools
    (git, ffmpeg, exiftool, etc.). Automatically handles common version flags
    and returns realistic output.

    Example:
        def test_tool_detection(mock_subprocess_run):
            with patch('subprocess.run', side_effect=mock_subprocess_run):
                detector.find_system_tool('git')
    """

    def _mock_run(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        """Mock subprocess.run with realistic tool outputs."""
        if not cmd:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr="No command provided",
            )

        # Get tool name - strip path if present
        tool_path = cmd[0]
        tool_name = Path(tool_path).name if "/" in tool_path or "\\" in tool_path else tool_path

        # Remove .exe extension on Windows
        if tool_name.endswith(".exe"):
            tool_name = tool_name[:-4]

        # Get mock output for this tool
        output = get_mock_tool_version_output(tool_name)

        if not output:
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=1,
                stdout="",
                stderr=f"{tool_name}: command not found",
            )

        # Return completed process with text output
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=output,
            stderr="",
        )

    return _mock_run


@pytest.fixture
def mock_subprocess_run_failure():
    """Mock subprocess.run that simulates command failures.

    Useful for testing error handling when tools are not found or fail.

    Example:
        def test_missing_tool(mock_subprocess_run_failure):
            with patch('subprocess.run', side_effect=mock_subprocess_run_failure):
                info = detector.find_system_tool('nonexistent')
    """

    def _mock_run_failure(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        """Mock subprocess.run that fails."""
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=1,
            stdout="",
            stderr="Command not found",
        )

    return _mock_run_failure


@pytest.fixture
def mock_qt_widgets(qapp):
    """Mock Qt widgets and common GUI components for testing.

    Provides mocks for common Qt operations that do not need full widget
    lifecycle testing. Useful for testing UI logic without rendering.

    Args:
        qapp: Qt application fixture (dependency)

    Returns:
        Dictionary of mock Qt objects and helpers

    Example:
        def test_dialog(mock_qt_widgets):
            dialog = MyDialog()
            dialog.accept = mock_qt_widgets['accept']
            dialog.accept()
    """
    return {
        "accept": Mock(),
        "reject": Mock(),
        "close": Mock(),
        "show": Mock(),
        "hide": Mock(),
        "exec": Mock(return_value=1),  # QDialog.Accepted
        "addWidget": Mock(),
        "addLayout": Mock(),
        "setLayout": Mock(),
    }


@pytest.fixture
def mock_qmessagebox():
    """Mock QMessageBox for testing dialogs without user interaction.

    Returns a mock that automatically returns 'Yes' for questions.
    Useful for testing confirmation dialogs in unit tests.

    Example:
        def test_confirmation(mock_qmessagebox):
            with patch('PySide6.QtWidgets.QMessageBox', mock_qmessagebox):
                result = show_delete_confirmation()
    """
    mock_box = MagicMock()
    mock_box.question.return_value = mock_box.Yes
    mock_box.information.return_value = mock_box.Ok
    mock_box.warning.return_value = mock_box.Ok
    mock_box.critical.return_value = mock_box.Ok
    return mock_box


@pytest.fixture
def mock_diskutil():
    """Mock macOS diskutil command for storage testing.

    Returns a function that mocks subprocess.run calls to diskutil,
    returning realistic JSON and text output.

    Example:
        def test_macos_storage(mock_diskutil):
            with patch('subprocess.run', side_effect=mock_diskutil):
                storage = MacOSStorage()
    """
    from tests.fixtures.platform_data import (
        MOCK_DISKUTIL_INFO_USB,
        MOCK_DISKUTIL_LIST_OUTPUT,
    )

    def _mock_diskutil(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess:
        """Mock diskutil command execution."""
        if "list" in cmd:
            output = MOCK_DISKUTIL_LIST_OUTPUT
        elif "info" in cmd:
            output = MOCK_DISKUTIL_INFO_USB
        else:
            output = ""

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=0,
            stdout=output,
            stderr="",
        )

    return _mock_diskutil


@pytest.fixture
def mock_shutil_which():
    """Mock shutil.which to simulate tool availability.

    Returns a mock that reports common tools as found in PATH.
    Customize the return value for specific tests.

    Example:
        def test_git_found(mock_shutil_which):
            mock_shutil_which.return_value = '/usr/bin/git'
            with patch('shutil.which', mock_shutil_which):
                path = shutil.which('git')
    """
    mock = Mock()

    def side_effect(tool_name: str) -> str | None:
        """Return path for common tools."""
        common_tools = {"git", "ffmpeg", "exiftool", "magick", "mysql", "mkvmerge"}
        if tool_name in common_tools:
            return f"/usr/bin/{tool_name}"
        return None

    mock.side_effect = side_effect
    return mock


@pytest.fixture
def mock_ctypes_windll():
    """Mock ctypes.windll for Windows API testing.

    Provides mocks for common Windows kernel32 functions used in
    storage detection (GetDriveTypeW, GetVolumeInformationW).

    Example:
        def test_windows_api(mock_ctypes_windll):
            with patch('ctypes.windll', mock_ctypes_windll):
                drive_type = windll.kernel32.GetDriveTypeW('C:')
    """
    mock_kernel32 = MagicMock()

    # GetDriveTypeW constants
    drive_fixed = 3

    # Default to fixed drive
    mock_kernel32.GetDriveTypeW.return_value = drive_fixed

    # GetVolumeInformationW - modifies buffer in place
    def mock_get_volume_info(path, name_buf, name_size, serial, max_len, flags, fs_buf, fs_size):
        """Simulate writing drive info to buffers."""
        name_buf.value = "TestDrive"
        fs_buf.value = "NTFS"
        return True

    mock_kernel32.GetVolumeInformationW.side_effect = mock_get_volume_info

    mock_windll = MagicMock()
    mock_windll.kernel32 = mock_kernel32

    return mock_windll
