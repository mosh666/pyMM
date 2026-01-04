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
