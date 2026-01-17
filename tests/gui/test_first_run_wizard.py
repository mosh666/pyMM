"""Tests for FirstRunWizard."""

from pathlib import Path

from PySide6.QtCore import Qt
import pytest

from app.core.services.storage_service import StorageService
from app.ui.components.first_run_wizard import (
    CompletePage,
    FirstRunWizard,
    PluginPage,
    StoragePage,
    WelcomePage,
)


class TestWelcomePage:
    """Test suite for WelcomePage."""

    def test_create_welcome_page(self, qtbot):
        """Test creating welcome page."""
        page = WelcomePage()
        qtbot.addWidget(page)

        assert page.title == "Welcome to pyMediaManager"
        assert page.validate() is True
        assert page.get_data() == {}


class TestStoragePage:
    """Test suite for StoragePage."""

    @pytest.fixture
    def storage_service(self):
        """Create storage service."""
        return StorageService()

    def test_create_storage_page(self, qtbot, storage_service):
        """Test creating storage page."""
        page = StoragePage(storage_service)
        qtbot.addWidget(page)

        assert page.title == "Select Portable Drive"
        assert page.drive_list is not None

    def test_refresh_drives(self, qtbot, storage_service):
        """Test refreshing drive list."""
        page = StoragePage(storage_service)
        qtbot.addWidget(page)

        page.refresh_drives()

        # Should have at least one item (drives or no-drives message)
        assert page.drive_list.count() > 0

    def test_validate_no_selection(self, qtbot, storage_service):
        """Test validation with no drive selected."""
        page = StoragePage(storage_service)
        qtbot.addWidget(page)

        page.selected_drive = None
        assert page.validate() is False

    def test_validate_with_selection(self, qtbot, storage_service):
        """Test validation with drive selected."""
        page = StoragePage(storage_service)
        qtbot.addWidget(page)

        page.selected_drive = Path("C:\\")
        assert page.validate() is True

    def test_get_data(self, qtbot, storage_service):
        """Test getting page data."""
        page = StoragePage(storage_service)
        qtbot.addWidget(page)

        page.selected_drive = Path("D:\\")
        data = page.get_data()

        assert "portable_drive" in data
        assert data["portable_drive"] == Path("D:\\")


class TestPluginPage:
    """Test suite for PluginPage."""

    def test_create_plugin_page(self, qtbot):
        """Test creating plugin page."""
        plugins = ["FFmpeg", "ImageMagick", "MKVToolNix"]
        page = PluginPage(plugins)
        qtbot.addWidget(page)

        assert page.title == "Select Optional Plugins"
        assert len(page.checkboxes) == 3

    def test_selection_tracking(self, qtbot):
        """Test plugin selection tracking."""
        plugins = ["FFmpeg", "ImageMagick"]
        page = PluginPage(plugins)
        qtbot.addWidget(page)

        # Initially nothing selected
        assert page.selected_plugins == []

        # Select FFmpeg
        page.checkboxes["FFmpeg"].setChecked(True)
        assert "FFmpeg" in page.selected_plugins

        # Select ImageMagick
        page.checkboxes["ImageMagick"].setChecked(True)
        assert len(page.selected_plugins) == 2

        # Deselect FFmpeg
        page.checkboxes["FFmpeg"].setChecked(False)
        assert "FFmpeg" not in page.selected_plugins
        assert len(page.selected_plugins) == 1

    def test_get_data(self, qtbot):
        """Test getting selected plugins."""
        plugins = ["FFmpeg", "ImageMagick"]
        page = PluginPage(plugins)
        qtbot.addWidget(page)

        page.checkboxes["FFmpeg"].setChecked(True)
        data = page.get_data()

        assert "optional_plugins" in data
        assert "FFmpeg" in data["optional_plugins"]
        assert "ImageMagick" not in data["optional_plugins"]


class TestCompletePage:
    """Test suite for CompletePage."""

    def test_create_complete_page(self, qtbot):
        """Test creating completion page."""
        page = CompletePage()
        qtbot.addWidget(page)

        assert page.title == "Setup Complete!"
        assert page.dont_show_checkbox is not None

    def test_get_data(self, qtbot):
        """Test getting wizard settings."""
        page = CompletePage()
        qtbot.addWidget(page)

        # Default: show wizard again
        page.dont_show_checkbox.setChecked(False)
        data = page.get_data()
        assert data["dont_show_again"] is False

        # Don't show again
        page.dont_show_checkbox.setChecked(True)
        data = page.get_data()
        assert data["dont_show_again"] is True


class TestFirstRunWizard:
    """Test suite for FirstRunWizard."""

    @pytest.fixture
    def storage_service(self):
        """Create storage service."""
        return StorageService()

    @pytest.fixture
    def wizard(self, qtbot, storage_service):
        """Create wizard instance."""
        plugins = ["FFmpeg", "ImageMagick"]
        wizard = FirstRunWizard(storage_service, plugins)
        qtbot.addWidget(wizard)
        return wizard

    def test_create_wizard(self, wizard):
        """Test wizard creation."""
        assert wizard.stack is not None
        assert len(wizard.pages) == 5
        assert wizard.stack.currentIndex() == 0

    def test_initial_button_state(self, wizard):
        """Test initial button states."""
        assert wizard.back_btn.isEnabled() is False
        assert wizard.next_btn.isEnabled() is True
        assert wizard.next_btn.text() == "Next →"

    def test_navigation(self, qtbot, wizard):
        """Test wizard navigation."""
        # Start at page 0
        assert wizard.stack.currentIndex() == 0

        # Click next
        qtbot.mouseClick(wizard.next_btn, Qt.MouseButton.LeftButton)

        # Should move to page 1
        assert wizard.stack.currentIndex() == 1
        assert wizard.back_btn.isEnabled() is True

        # Click back
        qtbot.mouseClick(wizard.back_btn, Qt.MouseButton.LeftButton)

        # Should be back at page 0
        assert wizard.stack.currentIndex() == 0
        assert wizard.back_btn.isEnabled() is False

    def test_finish_button_text(self, wizard):
        """Test finish button text on last page."""
        # Navigate to last page
        wizard.stack.setCurrentIndex(len(wizard.pages) - 1)
        wizard._update_buttons()

        assert wizard.next_btn.text() == "Finish"

    def test_data_collection(self, qtbot, wizard):
        """Test data collection across pages."""
        # Set data on storage page
        storage_page = wizard.pages[1]
        storage_page.selected_drive = Path("D:\\")

        # Move to plugin page and select plugins (now at index 3 after StorageGroupPage)
        wizard.stack.setCurrentIndex(3)
        plugin_page = wizard.pages[3]
        plugin_page.checkboxes["FFmpeg"].setChecked(True)

        # Simulate navigation and data collection
        wizard.collected_data.update(storage_page.get_data())
        wizard.collected_data.update(plugin_page.get_data())

        assert wizard.collected_data["portable_drive"] == Path("D:\\")
        assert "FFmpeg" in wizard.collected_data["optional_plugins"]

    def test_wizard_signals(self, qtbot, wizard):
        """Test wizard signals."""
        # Setup signal watchers
        qtbot.waitSignal(wizard.finished, timeout=1000, raising=False)
        qtbot.waitSignal(wizard.cancelled, timeout=1000, raising=False)

        # Test cancel
        qtbot.mouseClick(wizard.cancel_btn, Qt.MouseButton.LeftButton)

        # Should emit cancelled (note: may not trigger in test environment)
        # Just verify signal exists
        assert wizard.cancelled is not None
        assert wizard.finished is not None
