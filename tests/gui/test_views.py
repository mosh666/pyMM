"""Tests for view classes."""
import pytest
from PySide6.QtCore import Qt
from app.ui.views.storage_view import StorageView
from app.ui.views.plugin_view import PluginView
from app.ui.views.project_view import ProjectView
from app.core.services.storage_service import StorageService
from app.plugins.plugin_manager import PluginManager


class TestStorageView:
    """Test suite for StorageView."""

    @pytest.fixture
    def storage_service(self):
        """Create storage service."""
        return StorageService()

    @pytest.fixture
    def view(self, qtbot, storage_service):
        """Create storage view."""
        view = StorageView(storage_service)
        qtbot.addWidget(view)
        return view

    def test_create_view(self, view):
        """Test creating storage view."""
        assert view.drives_table is not None
        assert view.drives_table.columnCount() == 6

    def test_refresh_drives(self, view):
        """Test refreshing drives table."""
        view.refresh_drives()

        # Should have at least one drive
        assert view.drives_table.rowCount() > 0

    def test_table_columns(self, view):
        """Test table column headers."""
        headers = [
            view.drives_table.horizontalHeaderItem(i).text()
            for i in range(view.drives_table.columnCount())
        ]

        assert "Drive" in headers
        assert "Label" in headers
        assert "Status" in headers


class TestPluginView:
    """Test suite for PluginView."""

    @pytest.fixture
    def plugin_manager(self, temp_dir):
        """Create plugin manager."""
        plugins_dir = temp_dir / "plugins"
        manifests_dir = temp_dir / "manifests"
        manifests_dir.mkdir()

        return PluginManager(plugins_dir, manifests_dir)

    @pytest.fixture
    def view(self, qtbot, plugin_manager):
        """Create plugin view."""
        view = PluginView(plugin_manager)
        qtbot.addWidget(view)
        return view

    def test_create_view(self, view):
        """Test creating plugin view."""
        assert view.plugins_table is not None
        assert view.plugins_table.columnCount() == 5

    def test_refresh_plugins(self, view):
        """Test refreshing plugins table."""
        view.refresh_plugins()

        # Table should exist even with no plugins
        assert view.plugins_table is not None

    def test_table_columns(self, view):
        """Test table column headers."""
        headers = [
            view.plugins_table.horizontalHeaderItem(i).text()
            for i in range(view.plugins_table.columnCount())
        ]

        assert "Plugin" in headers
        assert "Version" in headers
        assert "Status" in headers


class TestProjectView:
    """Test suite for ProjectView."""

    @pytest.fixture
    def view(self, qtbot):
        """Create project view."""
        view = ProjectView()
        qtbot.addWidget(view)
        return view

    def test_create_view(self, view):
        """Test creating project view."""
        assert view.projects_list is not None

    def test_initial_state(self, view):
        """Test initial view state."""
        # Should have placeholder message
        assert view.projects_list.count() > 0
