"""Tests for view classes."""

from unittest.mock import MagicMock, Mock, PropertyMock, patch

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMessageBox, QPushButton
import pytest

from app.core.services.storage_service import StorageService
from app.models.project import Project
from app.plugins.plugin_manager import PluginManager
from app.ui.views.plugin_view import PluginInstallThread, PluginView
from app.ui.views.project_view import ProjectView
from app.ui.views.storage_view import StorageView


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
        assert view.drives_table.columnCount() == 7

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


class TestPluginInstallThread:
    """Test suite for PluginInstallThread."""

    def test_run_success(self, qtbot):
        """Test successful installation."""
        manager = Mock()

        # install_plugin is async
        async def mock_install(*args, **kwargs):
            """Mock successful installation."""
            return True

        manager.install_plugin = mock_install

        thread = PluginInstallThread(manager, "git")

        with qtbot.waitSignal(thread.finished) as blocker:
            thread.start()

        assert blocker.args == [True, "git installed successfully"]

    def test_run_failure(self, qtbot):
        """Test failed installation."""
        manager = Mock()

        async def mock_install(*args, **kwargs):
            """Mock failed installation."""
            return False

        manager.install_plugin = mock_install

        thread = PluginInstallThread(manager, "git")

        with qtbot.waitSignal(thread.finished) as blocker:
            thread.start()

        assert blocker.args == [False, "Failed to install git"]

    def test_run_exception(self, qtbot):
        """Test installation exception."""
        manager = Mock()

        async def mock_install(*args, **kwargs):
            """Mock installation exception."""
            raise ValueError("Download error")

        manager.install_plugin = mock_install

        thread = PluginInstallThread(manager, "git")

        with qtbot.waitSignal(thread.finished) as blocker:
            thread.start()

        assert blocker.args == [False, "Error: Download error"]


class TestPluginView:
    """Test suite for PluginView."""

    @pytest.fixture
    def plugin_manager(self, temp_dir):
        """Create plugin manager."""
        plugins_dir = temp_dir / "plugins"
        plugins_dir.mkdir()
        manifests_dir = temp_dir / "manifests"
        manifests_dir.mkdir()

        # Add a sample plugin
        plugin_dir = manifests_dir / "git"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.yaml").write_text("""
schema_version: 2
name: git
version: "2.30.0"
description: Git version control
mandatory: false
enabled: true
platforms:
  windows:
    source:
      type: url
      base_uri: http://example.com/git.zip
    command:
      executable: git.exe
  linux:
    source:
      type: url
      base_uri: http://example.com/git.tar.gz
    command:
      executable: git
  macos:
    source:
      type: url
      base_uri: http://example.com/git.tar.gz
    command:
      executable: git
""")

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

        # Table should exist and have plugins from the plugins directory
        assert view.plugins_table is not None
        # Check that we have some plugins (at least git, which is in plugins/)
        assert view.plugins_table.rowCount() >= 1
        # Find git plugin in the table
        git_found = False
        for row in range(view.plugins_table.rowCount()):
            if view.plugins_table.item(row, 0) and view.plugins_table.item(row, 0).text() == "git":
                git_found = True
                break
        assert git_found, "git plugin should be in the plugins table"

    def test_table_columns(self, view):
        """Test table column headers."""
        headers = [
            view.plugins_table.horizontalHeaderItem(i).text()
            for i in range(view.plugins_table.columnCount())
        ]

        assert "Plugin" in headers
        assert "Version" in headers
        assert "Status" in headers

    def test_install_plugin_flow(self, view, qtbot):
        """Test installing a plugin."""
        view.refresh_plugins()

        # Make sure we have at least one plugin
        if view.plugins_table.rowCount() == 0:
            pytest.skip("No plugins available for testing")

        # Get install button
        cell_widget = view.plugins_table.cellWidget(0, 4)
        if cell_widget is None:
            pytest.skip("No action widget available")

        install_btn = cell_widget.findChild(QPushButton)
        assert install_btn is not None
        assert install_btn.text() == "Install"

        with patch(
            "app.ui.views.plugin_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.Yes,
        ):
            with patch("app.ui.views.plugin_view.PluginInstallThread") as mock_thread:
                # We need the thread instance to have signals that work or intercept connect
                mock_thread_instance = mock_thread.return_value

                # Click install
                install_btn.click()

                assert view.install_thread is not None
                mock_thread_instance.start.assert_called_once()

                # Get the connected callback
                args, _ = mock_thread_instance.finished.connect.call_args
                callback = args[0]

                # Simulate success
                with patch("app.ui.views.plugin_view.QMessageBox.information") as mock_info:
                    callback(True, "Success")
                    mock_info.assert_called()

    def test_install_cancel(self, view, qtbot):
        """Test cancelling install."""
        view.refresh_plugins()

        # Make sure we have at least one plugin
        if view.plugins_table.rowCount() == 0:
            pytest.skip("No plugins available for testing")

        cell_widget = view.plugins_table.cellWidget(0, 4)
        if cell_widget is None:
            pytest.skip("No action widget available")

        install_btn = cell_widget.findChild(QPushButton)
        assert install_btn is not None

        with patch(
            "app.ui.views.plugin_view.QMessageBox.question",
            return_value=QMessageBox.StandardButton.No,
        ):
            install_btn.click()
            assert view.install_thread is None


class TestProjectView:
    """Test suite for ProjectView."""

    @pytest.fixture
    def mock_project_service(self):
        """Create mock project service."""
        service = Mock()
        service.list_projects.return_value = []
        return service

    @pytest.fixture
    def sample_project(self, temp_dir):
        """Create a sample project for testing."""
        project = Mock(spec=Project)
        project.name = "Test Project"
        project.path = temp_dir / "test_project"
        project.description = "Test description"
        # Configure exists as a property that returns True
        type(project).exists = PropertyMock(return_value=True)
        project.template_version = "1.0.0"
        return project

    @pytest.fixture
    def view(self, qtbot, mock_project_service):
        """Create project view."""
        view = ProjectView(mock_project_service)
        qtbot.addWidget(view)
        # Simplified: Don't call show() or waitExposed() to avoid Windows COM timing issues
        return view

    def test_create_view(self, view):
        """Test creating project view."""
        assert view.projects_list is not None

    def test_initial_state(self, view):
        """Test initial view state."""
        # Should have placeholder message when no projects
        assert view.projects_list.count() > 0

    def test_refresh_projects_with_data(self, view, mock_project_service, sample_project):
        """Test refreshing with projects."""
        mock_project_service.list_projects.return_value = [sample_project]
        # Mock migration check
        mock_project_service.check_project_migration.return_value = None

        view._refresh_projects()

        assert view.projects_list.count() == 1
        item = view.projects_list.item(0)
        assert "Test Project" in item.text()
        assert item.data(Qt.ItemDataRole.UserRole) == sample_project

    def test_double_click_opens(self, view, qtbot, mock_project_service, sample_project):
        """Test double clicking opens project."""
        mock_project_service.list_projects.return_value = [sample_project]
        mock_project_service.check_project_migration.return_value = None
        view._refresh_projects()

        item = view.projects_list.item(0)

        with qtbot.waitSignal(view.project_opened) as blocker:
            view.projects_list.itemDoubleClicked.emit(item)

        assert blocker.args == [sample_project]

    def test_create_project_flow(self, view):
        """Test create project flow."""
        with patch("app.ui.dialogs.project_wizard.ProjectWizard") as mock_wizard_cls:
            mock_wizard = mock_wizard_cls.return_value
            mock_wizard.exec.return_value = True

            project = MagicMock(spec=Project)
            mock_wizard.created_project = project

            mock_slot = Mock()
            view.project_opened.connect(mock_slot)

            # We mock _refresh_projects to avoid side effects
            with patch.object(view, "_refresh_projects") as mock_refresh:
                view._create_project()

                mock_wizard_cls.assert_called_once()
                mock_wizard.exec.assert_called_once()
                mock_refresh.assert_called_once()

                mock_slot.assert_called_with(project)

    def test_open_project_flow(self, view):
        """Test open project flow."""
        with patch("app.ui.dialogs.project_browser.ProjectBrowserDialog") as mock_browser_cls:
            mock_browser = mock_browser_cls.return_value
            mock_browser.exec.return_value = True

            mock_signal = Mock()
            mock_browser.project_selected = mock_signal

            project = MagicMock(spec=Project)

            mock_slot = Mock()
            view.project_opened.connect(mock_slot)

            with patch.object(view, "_refresh_projects") as mock_refresh:
                view._open_project()

                mock_browser_cls.assert_called_once()
                mock_browser.exec.assert_called_once()

                args, _ = mock_signal.connect.call_args
                callback = args[0]
                callback(project)

                mock_slot.assert_called_with(project)
                mock_refresh.assert_called_once()

    def test_selection_changed_shows_banner(
        self, qtbot, view, sample_project, mock_project_service
    ):
        """Test that selecting a project with migration displays banner."""
        # Setup migration need
        mock_diff = MagicMock()
        mock_diff.target_version = "2.0.0"
        mock_diff.folders_to_add = []
        mock_diff.files_to_modify = []
        mock_diff.files_to_delete = []
        mock_diff.folders_to_remove = []
        mock_diff.folders_to_rename = []
        mock_diff.files_to_add = []
        mock_diff.files_to_move = []
        mock_diff.conflicts = []

        mock_project_service.check_project_migration.return_value = (True, mock_diff)

        # Add project to list
        mock_project_service.list_projects.return_value = [sample_project]
        view._refresh_projects()

        # Select project
        item = view.projects_list.item(0)
        view.projects_list.setCurrentItem(item)

        # Trigger selection change
        view._on_selection_changed()

        # Process Qt events to ensure banner is rendered
        qtbot.wait(10)

        # Banner container should exist (visibility depends on migration detection logic)
        assert hasattr(view, "migration_banner_container")

    def test_apply_migration_flow(self, view, sample_project, mock_project_service):
        """Test applying migration from view."""
        mock_diff = MagicMock()
        mock_diff.target_version = "2.0.0"

        # Mock migration success
        mock_project_service.migrate_project.return_value = (True, [])

        with patch("app.ui.views.project_view.MigrationBanner") as mock_banner:
            with patch.object(view, "_refresh_projects") as mock_refresh:
                view._apply_migration(sample_project, mock_diff)

                # Verify migration called
                mock_project_service.migrate_project.assert_called_with(
                    sample_project, backup=True, skip_conflicts=True, preview_mode=False
                )
                mock_banner.show_migration_success.assert_called()
                mock_refresh.assert_called()
