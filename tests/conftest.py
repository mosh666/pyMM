"""Pytest configuration and shared fixtures."""

from pathlib import Path
import shutil
from unittest.mock import patch

from PySide6.QtWidgets import QApplication
import pytest


@pytest.fixture(autouse=True)
def mock_app_version():
    """Ensure app version satisfies template requirements during tests."""
    with (
        patch("app.__version__", "1.0.0"),
        patch("app.services.project_service.__version__", "1.0.0"),
    ):
        yield


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
