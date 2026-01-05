"""Pytest configuration and shared fixtures."""

import shutil
import tempfile
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def app_root(temp_dir):
    """Create a mock application root directory structure."""
    root = temp_dir / "pyMM"
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
    
    # Store original method
    original_get_drive_root = FileSystemService.get_drive_root
    
    def mock_get_drive_root_method(self):
        """Mock implementation that returns temp directory instead of system drive."""
        # If _drive_root was explicitly set (not None), use it
        # Otherwise return the mock drive
        if hasattr(self, '_drive_root') and self._drive_root is not None:
            # Check if it's already pointing to a temp location
            if str(mock_drive) in str(self._drive_root):
                return self._drive_root
        
        # Set and return mock drive root
        self._drive_root = mock_drive
        return mock_drive
    
    # Monkey patch the method
    monkeypatch.setattr(FileSystemService, "get_drive_root", mock_get_drive_root_method)
    
    yield mock_drive
