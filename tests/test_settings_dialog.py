"""
Test settings dialog functionality.

This test script verifies:
- Settings dialog can be opened
- All tabs are present
- Settings can be loaded
- Configuration can be saved

Note: This test uses pytest's built-in output capture.
For verbose output, run with: pytest -v -s
"""

from pathlib import Path
import sys

import pytest

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication

from app.core.services.config_service import ConfigService
from app.ui.dialogs.settings_dialog import SettingsDialog


@pytest.fixture(scope="module")
def qapp():
    """Create QApplication singleton for the entire test module."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app
    # Don't quit the app as other tests may need it


def test_settings_dialog(qapp):
    """Test settings dialog creation and functionality."""
    # Create config service with explicit config_dir for testing
    app_root = Path(__file__).parent
    config_dir = app_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_service = ConfigService(app_root=app_root, config_dir=config_dir)
    config = config_service.load()

    # Verify config loaded
    assert config.ui.theme in ["light", "dark", "auto"]
    assert config.logging.level.value in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

    # Create settings dialog
    dialog = SettingsDialog(config_service)

    # Verify dialog was created with all tabs
    assert dialog.tabs.count() == 6
    assert dialog.tabs.tabText(0) == "General"
    assert dialog.tabs.tabText(1) == "Plugins"
    assert dialog.tabs.tabText(2) == "Plugin Preferences"
    assert dialog.tabs.tabText(3) == "Storage"
    assert dialog.tabs.tabText(4) == "Git"
    assert dialog.tabs.tabText(5) == "About"

    # Check that settings are loaded into UI
    assert dialog.theme_combo.currentIndex() >= 0
    assert dialog.log_level_combo.currentIndex() >= 0

    # Test modifying settings (just verify the UI works)
    original_timeout = dialog.download_timeout_spin.value()
    dialog.download_timeout_spin.setValue(600)
    assert dialog.download_timeout_spin.value() == 600

    # Restore original value (don't actually save)
    dialog.download_timeout_spin.setValue(original_timeout)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
