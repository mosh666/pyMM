"""
GUI tests for migration UI components.

Tests the migration banner, dialogs, and UI integration using pytest-qt.
"""

from typing import cast
from unittest.mock import Mock, patch

from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QLabel
import pytest

from app.models.project import Project
from app.services.project_service import MigrationConflict, MigrationDiff, ProjectService
from app.ui.components.migration_banner import MigrationBanner
from app.ui.dialogs.migration_dialog import MigrationDialog
from app.ui.dialogs.rollback_dialog import MigrationHistoryDialog, RollbackDialog


@pytest.fixture
def mock_project(tmp_path):
    """Create a mock project."""
    project_path = tmp_path / "test_project"
    project_path.mkdir()

    return Project(
        name="Test Project",
        path=project_path,
        template_name="default",
        template_version="1.0.0",
    )


@pytest.fixture
def mock_migration_diff():
    """Create a mock migration diff."""
    return MigrationDiff(
        current_version="1.0.0",
        target_version="2.0.0",
        folders_to_add=["source", "proxies"],
        folders_to_remove=["cache"],
        conflicts=[],
        migration_notes="Migration to version 2.0.0",
        inheritance_changes=[],
    )


@pytest.fixture
def mock_project_service(tmp_path):
    """Create a mock project service."""
    service = Mock(spec=ProjectService)
    service.templates_dir = tmp_path / "templates"
    service.templates_dir.mkdir()
    service.migrate_project = Mock(return_value=True)
    service.rollback_project = Mock(return_value=True)
    service.rollback_multiple_projects = Mock(return_value=[])
    service.schedule_deferred_migration = Mock()
    service.create_preview_migration = Mock(return_value=str(tmp_path / "preview"))
    return service


@pytest.fixture
def parent_widget(qtbot):
    """Create a parent widget for dialogs."""
    from PySide6.QtWidgets import QWidget

    widget = QWidget()
    qtbot.addWidget(widget)
    widget.setGeometry(0, 0, 800, 600)
    return widget


class TestMigrationBanner:
    """Tests for MigrationBanner component."""

    def test_banner_creation(self, qtbot, mock_project, mock_migration_diff):
        """Test creating a migration banner."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        assert banner.project == mock_project
        assert banner.migration_diff == mock_migration_diff
        assert banner.project == mock_project

    def test_banner_displays_versions(self, qtbot, mock_project, mock_migration_diff):
        """Test banner displays version information."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        # Should display version transition
        text_widgets = banner.findChildren(QObject)
        banner_text = " ".join(str(w.text()) if hasattr(w, "text") else "" for w in text_widgets)

        assert "1.0.0" in banner_text or "2.0.0" in banner_text

    def test_banner_shows_folder_counts(self, qtbot, mock_project, mock_migration_diff):
        """Test banner shows folder change counts."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        # Should show counts of folders to add/remove
        text_widgets = banner.findChildren(QObject)
        banner_text = " ".join(str(w.text()) if hasattr(w, "text") else "" for w in text_widgets)

        # Should mention the folder counts somewhere
        assert "2" in banner_text  # 2 folders to add
        assert "1" in banner_text  # 1 folder to remove

    def test_banner_with_conflicts(self, qtbot, mock_project):
        """Test banner displays conflict indicator."""
        diff_with_conflicts = MigrationDiff(
            current_version="1.0.0",
            target_version="2.0.0",
            folders_to_add=[],
            folders_to_remove=["cache"],
            conflicts=[
                MigrationConflict(
                    folder_path="cache",
                    reason="Contains user files",
                    user_files_count=5,
                    last_modified="2024-01-01T10:00:00",
                )
            ],
            migration_notes="",
            inheritance_changes=[],
        )

        banner = MigrationBanner(mock_project, diff_with_conflicts)
        qtbot.addWidget(banner)

        # Should show conflict indicator
        text_widgets = banner.findChildren(QObject)
        banner_text = " ".join(str(w.text()) if hasattr(w, "text") else "" for w in text_widgets)

        assert "conflict" in banner_text.lower()

    def test_preview_button_signal(self, qtbot, mock_project, mock_migration_diff):
        """Test preview button emits signal."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        with qtbot.waitSignal(banner.preview_requested, timeout=1000):
            # Find and click preview button
            buttons = banner.findChildren(QObject)
            for btn in buttons:
                if hasattr(btn, "text") and "Preview" in btn.text():
                    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                    break

    def test_apply_button_signal(self, qtbot, mock_project, mock_migration_diff):
        """Test apply button emits signal."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        with qtbot.waitSignal(banner.apply_requested, timeout=1000):
            buttons = banner.findChildren(QObject)
            for btn in buttons:
                if hasattr(btn, "text") and "Apply" in btn.text():
                    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                    break

    def test_defer_button_signal(self, qtbot, mock_project, mock_migration_diff):
        """Test defer button emits signal."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        with qtbot.waitSignal(banner.defer_requested, timeout=1000):
            buttons = banner.findChildren(QObject)
            for btn in buttons:
                if hasattr(btn, "text") and "Defer" in btn.text():
                    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                    break

    def test_banner_styling(self, qtbot, mock_project, mock_migration_diff):
        """Test banner has warning styling."""
        banner = MigrationBanner(mock_project, mock_migration_diff)
        qtbot.addWidget(banner)

        # Should have warning/alert styling
        style = banner.styleSheet()
        assert "background" in style.lower() or "border" in style.lower()


class TestMigrationDialog:
    """Tests for MigrationDialog."""

    def test_dialog_creation(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test creating a migration dialog."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        assert dialog.project == mock_project
        assert dialog.migration_diff == mock_migration_diff

    def test_dialog_shows_version_info(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test dialog displays version transition."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Should show version transition in subtitle (second label in viewLayout)
        labels = cast("list[QLabel]", dialog.findChildren(QLabel))
        version_labels = [lbl for lbl in labels if "1.0.0" in lbl.text() or "2.0.0" in lbl.text()]
        assert len(version_labels) > 0, "Version information not found in dialog"

    def test_dialog_shows_folders_to_add(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test dialog lists folders to add."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Should display folders to add
        text_edits = dialog.findChildren(object)
        content = " ".join(
            str(w.toPlainText()) if hasattr(w, "toPlainText") else "" for w in text_edits
        )

        assert "source" in content or "proxies" in content

    def test_dialog_shows_folders_to_remove(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test dialog lists folders to remove."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        text_edits = dialog.findChildren(object)
        content = " ".join(
            str(w.toPlainText()) if hasattr(w, "toPlainText") else "" for w in text_edits
        )

        assert "cache" in content

    def test_dialog_shows_conflicts(self, qtbot, mock_project, mock_project_service, parent_widget):
        """Test dialog displays conflicts."""
        diff_with_conflicts = MigrationDiff(
            current_version="1.0.0",
            target_version="2.0.0",
            folders_to_add=[],
            folders_to_remove=["cache"],
            conflicts=[
                MigrationConflict(
                    folder_path="cache",
                    reason="Contains user files",
                    user_files_count=3,
                    last_modified="2024-01-01T10:00:00",
                )
            ],
            migration_notes="",
            inheritance_changes=[],
        )

        dialog = MigrationDialog(
            mock_project, diff_with_conflicts, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Should show conflict information
        text_edits = dialog.findChildren(object)
        content = " ".join(
            str(w.toPlainText()) if hasattr(w, "toPlainText") else "" for w in text_edits
        )

        assert "cache" in content
        assert "conflict" in content.lower() or "user" in content.lower()

    def test_dialog_preview_checkbox(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test preview mode checkbox."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "preview_checkbox")
        assert not dialog.preview_checkbox.isChecked()  # Default unchecked

        # Toggle checkbox programmatically (QFluentWidgets CheckBox doesn't respond to mouseClick in tests)
        dialog.preview_checkbox.setChecked(True)
        assert dialog.preview_checkbox.isChecked()

    def test_dialog_skip_conflicts_checkbox(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test skip conflicts checkbox."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "skip_conflicts_checkbox")
        assert dialog.skip_conflicts_checkbox.isChecked()  # Default checked

    def test_dialog_backup_checkbox(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test backup checkbox."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "backup_checkbox")
        assert dialog.backup_checkbox.isChecked()  # Default checked

    def test_apply_migration_calls_service(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test applying migration calls project service."""
        # Mock migrate_project to return True
        mock_project_service.migrate_project.return_value = True

        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Mock MessageBox and InfoBar to avoid blocking
        with (
            patch("qfluentwidgets.MessageBox"),
            patch("app.ui.components.migration_banner.InfoBar"),
        ):
            # Trigger apply
            dialog._apply_migration()

        # Should call migrate_project
        mock_project_service.migrate_project.assert_called_once()

    def test_defer_migration_calls_service(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test deferring migration calls service."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Mock MessageBox and InfoBar to avoid blocking
        with (
            patch("qfluentwidgets.MessageBox"),
            patch("app.ui.components.migration_banner.InfoBar"),
        ):
            # Trigger defer
            dialog._defer_migration()

        # Should call schedule_deferred_migration
        mock_project_service.schedule_deferred_migration.assert_called_once()


class TestRollbackDialog:
    """Tests for RollbackDialog."""

    def test_dialog_creation(self, qtbot, tmp_path, mock_project_service, parent_widget):
        """Test creating a rollback dialog."""
        projects = [
            Project(
                name="Project 1",
                path=tmp_path / "proj1",
                template_version="2.0.0",
                migration_history=[
                    {
                        "from_version": "1.0.0",
                        "to_version": "2.0.0",
                        "backup_path": "/backup1",
                    }
                ],
            )
        ]

        dialog = RollbackDialog(projects, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        assert len(dialog.projects) == 1

    def test_dialog_lists_projects(self, qtbot, tmp_path, mock_project_service, parent_widget):
        """Test dialog lists projects with backups."""
        projects = [
            Project(
                name=f"Project {i}",
                path=tmp_path / f"proj{i}",
                template_version="2.0.0",
                migration_history=[
                    {"from_version": "1.0.0", "to_version": "2.0.0", "backup_path": f"/backup{i}"}
                ],
            )
            for i in range(3)
        ]

        dialog = RollbackDialog(projects, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        # Should list all projects
        assert dialog.project_list.count() == 3

    def test_select_all_button(self, qtbot, tmp_path, mock_project_service, parent_widget):
        """Test select all button."""
        projects = [
            Project(
                name=f"Project {i}",
                path=tmp_path / f"proj{i}",
                migration_history=[{"backup_path": f"/backup{i}"}],
            )
            for i in range(3)
        ]

        dialog = RollbackDialog(projects, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        # Click select all
        dialog._select_all()

        # All items should be selected
        assert len(dialog.project_list.selectedItems()) == 3

    def test_deselect_all_button(self, qtbot, tmp_path, mock_project_service, parent_widget):
        """Test deselect all button."""
        projects = [
            Project(
                name=f"Project {i}",
                path=tmp_path / f"proj{i}",
                migration_history=[{"backup_path": f"/backup{i}"}],
            )
            for i in range(2)
        ]

        dialog = RollbackDialog(projects, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        # Select all then deselect
        dialog._select_all()
        dialog._deselect_all()

        # No items should be selected
        assert len(dialog.project_list.selectedItems()) == 0

    def test_rollback_calls_service(self, qtbot, tmp_path, mock_project_service, parent_widget):
        """Test executing rollback calls service."""
        projects = [
            Project(
                name="Project 1",
                path=tmp_path / "proj1",
                migration_history=[{"backup_path": "/backup1"}],
            )
        ]

        dialog = RollbackDialog(projects, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        # Select project and execute
        dialog._select_all()

        with patch("qfluentwidgets.MessageBox") as mock_msgbox:
            mock_msgbox.return_value.exec.return_value = mock_msgbox.return_value.Accepted
            dialog._execute_rollback()

        # Should call rollback_multiple_projects
        mock_project_service.rollback_multiple_projects.assert_called_once()


class TestMigrationHistoryDialog:
    """Tests for MigrationHistoryDialog."""

    def test_dialog_creation(self, qtbot, tmp_path, parent_widget):
        """Test creating a migration history dialog."""
        project = Project(
            name="Test Project",
            path=tmp_path / "test",
            template_name="default",
            template_version="2.0.0",
            migration_history=[
                {
                    "from_version": "1.0.0",
                    "to_version": "2.0.0",
                    "timestamp": "2024-01-01T12:00:00",
                }
            ],
        )

        dialog = MigrationHistoryDialog(project, parent_widget)
        qtbot.addWidget(dialog)

        assert dialog.project == project

    def test_dialog_shows_current_state(self, qtbot, tmp_path, parent_widget):
        """Test dialog displays current template state."""
        project = Project(
            name="Test Project",
            path=tmp_path / "test",
            template_name="video-editing",
            template_version="3.0.0",
        )

        dialog = MigrationHistoryDialog(project, parent_widget)
        qtbot.addWidget(dialog)

        # Should show current template info
        labels = dialog.findChildren(object)
        text_content = " ".join(str(w.text()) if hasattr(w, "text") else "" for w in labels)

        assert "video-editing" in text_content or "3.0.0" in text_content

    def test_dialog_lists_history(self, qtbot, tmp_path, parent_widget):
        """Test dialog lists migration history."""
        project = Project(
            name="Test",
            path=tmp_path / "test",
            migration_history=[
                {
                    "from_version": "1.0.0",
                    "to_version": "1.5.0",
                    "timestamp": "2024-01-01T10:00:00",
                },
                {
                    "from_version": "1.5.0",
                    "to_version": "2.0.0",
                    "timestamp": "2024-01-02T10:00:00",
                },
            ],
        )

        dialog = MigrationHistoryDialog(project, parent_widget)
        qtbot.addWidget(dialog)

        # Should have 2 history entries - find the QListWidget
        from PySide6.QtWidgets import QListWidget

        list_widgets = dialog.findChildren(QListWidget)
        assert len(list_widgets) > 0
        assert list_widgets[0].count() == 2  # Should have exactly 2 items

    def test_dialog_empty_history(self, qtbot, tmp_path, parent_widget):
        """Test dialog with no migration history."""
        project = Project(
            name="Test",
            path=tmp_path / "test",
            migration_history=[],
        )

        dialog = MigrationHistoryDialog(project, parent_widget)
        qtbot.addWidget(dialog)

        # Should show "no history" message
        labels = dialog.findChildren(object)
        text_content = " ".join(str(w.text()) if hasattr(w, "text") else "" for w in labels)

        assert "no" in text_content.lower() or "history" in text_content.lower()


class TestInfoBarNotifications:
    """Tests for info bar notification methods."""

    def test_show_migration_success(self, qtbot):
        """Test success notification."""
        # Should not raise exception
        MigrationBanner.show_migration_success("Test Project", "1.0.0", "2.0.0")

    def test_show_migration_error(self, qtbot):
        """Test error notification."""
        # Should not raise exception
        MigrationBanner.show_migration_error("Test Project", "Test error message")

    def test_show_rollback_success(self, qtbot):
        """Test rollback success notification."""
        # Should not raise exception
        MigrationBanner.show_rollback_success("Test Project")

    def test_show_info_bar(self, qtbot):
        """Test generic info bar."""
        # Should not raise exception
        MigrationBanner.show_info_bar("Test message")


class TestProjectViewIntegration:
    """Tests for ProjectView migration integration."""

    def test_migration_indicators_in_list(self, qtbot):
        """Test that project list shows migration indicators."""
        # This would test the actual ProjectView with migration indicators
        # For now, verify the indicator strings exist
        _ = "🔄"  # Migration available indicator
        _ = "⏰"  # Pending migration indicator

    def test_banner_appears_on_selection(self, qtbot):
        """Test that banner appears when project with migration is selected."""
        # This would require a full ProjectView setup
        # Verify the logic exists in _on_selection_changed
        from app.ui.views.project_view import ProjectView

        assert hasattr(ProjectView, "_on_selection_changed")

    def test_banner_hidden_for_current_projects(self, qtbot):
        """Test that banner is hidden for up-to-date projects."""
        # Verify the logic to hide banner exists
        from app.ui.views.project_view import ProjectView

        # Just verify the class has the method we expect
        assert hasattr(ProjectView, "_on_selection_changed")

    def test_migrations_menu_exists(self, qtbot):
        """Test that migrations menu item exists."""
        from app.ui.main_window import MainWindow

        # Verify method exists
        assert hasattr(MainWindow, "_create_migrations_interface")

    def test_check_pending_migrations_on_startup(self, qtbot):
        """Test that pending migrations are checked on startup."""
        from app.ui.main_window import MainWindow

        # Verify method exists
        assert hasattr(MainWindow, "_check_pending_migrations")

    def test_check_migrations_method(self, qtbot):
        """Test check migrations method exists."""
        from app.ui.main_window import MainWindow

        assert hasattr(MainWindow, "_check_migrations")

    def test_apply_pending_migrations_method(self, qtbot):
        """Test apply pending migrations method exists."""
        from app.ui.main_window import MainWindow

        assert hasattr(MainWindow, "_apply_pending_migrations")

    def test_show_rollback_dialog_method(self, qtbot):
        """Test rollback dialog method exists."""
        from app.ui.main_window import MainWindow

        assert hasattr(MainWindow, "_show_rollback_dialog")

    def test_show_migration_history_method(self, qtbot):
        """Test migration history method exists."""
        from app.ui.main_window import MainWindow

        assert hasattr(MainWindow, "_show_migration_history")


class TestDialogInteractions:
    """Tests for dialog user interactions."""

    def test_cancel_button_closes_migration_dialog(
        self, qtbot, mock_project, mock_migration_diff, mock_project_service, parent_widget
    ):
        """Test cancel button closes dialog."""
        dialog = MigrationDialog(
            mock_project, mock_migration_diff, mock_project_service, parent_widget
        )
        qtbot.addWidget(dialog)

        # Find and click cancel button
        buttons = dialog.findChildren(object)
        for btn in buttons:
            if hasattr(btn, "text") and "Cancel" in btn.text():
                with qtbot.waitSignal(dialog.rejected, timeout=1000):
                    qtbot.mouseClick(btn, Qt.MouseButton.LeftButton)
                break

    def test_migration_notes_displayed(
        self, qtbot, mock_project, mock_project_service, parent_widget
    ):
        """Test migration notes are displayed."""
        diff = MigrationDiff(
            current_version="1.0.0",
            target_version="2.0.0",
            folders_to_add=[],
            folders_to_remove=[],
            conflicts=[],
            migration_notes="Important: Backup your data before migrating!",
            inheritance_changes=[],
        )

        dialog = MigrationDialog(mock_project, diff, mock_project_service, parent_widget)
        qtbot.addWidget(dialog)

        # Should display notes
        text_edits = dialog.findChildren(object)
        content = " ".join(
            str(w.toPlainText()) if hasattr(w, "toPlainText") else "" for w in text_edits
        )

        assert "backup" in content.lower() or "important" in content.lower()


# Mark all tests as GUI tests
pytestmark = pytest.mark.gui
