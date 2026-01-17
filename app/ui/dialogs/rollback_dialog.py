"""Rollback dialog for reverting template migrations."""

from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QWidget,
)
from qfluentwidgets import CheckBox, MessageBoxBase, PrimaryPushButton, PushButton

if TYPE_CHECKING:
    from app.models.project import Project
    from app.services.project_service import ProjectService


class RollbackDialog(MessageBoxBase):
    """
    Dialog for rolling back template migrations.

    Allows users to:
    - View migration history
    - Select projects to rollback
    - Preview rollback effects
    - Execute batch rollback
    """

    def __init__(
        self,
        projects: list[Project],
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize rollback dialog.

        Args:
            projects: Projects eligible for rollback (have migration backups)
            project_service: Service for executing rollback
            parent: Parent widget
        """
        super().__init__(parent)
        self.projects = projects
        self.project_service = project_service
        self.selected_projects: list[Project] = []

        # Create title label since MessageBoxBase doesn't provide one
        self.titleLabel = QLabel(self.widget)
        self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.titleLabel.setText("Rollback Template Migrations")

        # Add title label to layout
        self.viewLayout.addWidget(self.titleLabel)

        self.viewLayout.setSpacing(16)

        # Instructions
        instructions = QLabel(
            f"Found {len(self.projects)} project(s) with migration backups.\n"
            "Select projects to rollback to their previous template version."
        )
        instructions.setWordWrap(True)
        self.viewLayout.addWidget(instructions)

        # Warning
        warning = QLabel(
            "⚠️ Rollback will restore the project to its pre-migration state. "
            "Any changes made after migration will be lost."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(
            "background-color: #fff3e0; color: #e65100; padding: 8px; border-radius: 4px;"
        )
        self.viewLayout.addWidget(warning)

        # Project list
        list_label = QLabel("<b>Projects:</b>")
        self.viewLayout.addWidget(list_label)

        self.project_list = QListWidget()
        self.project_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.project_list.setMinimumHeight(200)

        for project in self.projects:
            item = self._create_project_item(project)
            self.project_list.addItem(item)

        self.viewLayout.addWidget(self.project_list)

        # Selection controls
        select_layout = QHBoxLayout()
        select_all_btn = PushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        select_layout.addWidget(select_all_btn)

        deselect_all_btn = PushButton("Deselect All")
        deselect_all_btn.clicked.connect(self._deselect_all)
        select_layout.addWidget(deselect_all_btn)

        select_layout.addStretch()
        self.viewLayout.addLayout(select_layout)

        # Options
        self.delete_backup_checkbox = CheckBox("Delete backups after rollback")
        self.delete_backup_checkbox.setToolTip("Remove backup folders after successful rollback")
        self.delete_backup_checkbox.setChecked(False)
        self.viewLayout.addWidget(self.delete_backup_checkbox)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        preview_btn = PushButton("Preview Rollback")
        preview_btn.clicked.connect(self._preview_rollback)
        preview_btn.setToolTip("Show what will be restored")
        button_layout.addWidget(preview_btn)

        rollback_btn = PrimaryPushButton("Rollback Selected")
        rollback_btn.clicked.connect(self._execute_rollback)
        button_layout.addWidget(rollback_btn)

        self.viewLayout.addLayout(button_layout)

        self.widget.setMinimumWidth(600)
        self.widget.setMaximumHeight(600)

    def _create_project_item(self, project: Project) -> QListWidgetItem:
        """Create list item for project."""
        # Get latest migration from history
        latest_migration = None
        if project.migration_history:
            latest_migration = project.migration_history[-1]

        current_ver = project.template_version or "unknown"
        previous_ver = "unknown"
        migration_date = "unknown"

        if latest_migration:
            previous_ver = latest_migration.get("from_version", "unknown")
            timestamp = latest_migration.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    migration_date = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    pass

        text = (
            f"{project.name}  |  "
            f"Current: v{current_ver}  →  Will restore: v{previous_ver}  |  "
            f"Migrated: {migration_date}"
        )

        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, project)

        return item

    def _select_all(self) -> None:
        """Select all projects."""
        for i in range(self.project_list.count()):
            self.project_list.item(i).setSelected(True)

    def _deselect_all(self) -> None:
        """Deselect all projects."""
        self.project_list.clearSelection()

    def _get_selected_projects(self) -> list[Project]:
        """Get currently selected projects."""
        selected = []
        for item in self.project_list.selectedItems():
            project = item.data(Qt.ItemDataRole.UserRole)
            if project:
                selected.append(project)
        return selected

    def _preview_rollback(self) -> None:
        """Show preview of what will be rolled back."""
        selected = self._get_selected_projects()

        if not selected:
            from qfluentwidgets import MessageBox

            MessageBox(
                "No Selection", "Please select at least one project to preview.", self
            ).exec()
            return

        # Build preview message
        preview_lines = []
        for project in selected:
            if project.migration_history:
                latest = project.migration_history[-1]
                from_ver = latest.get("from_version", "unknown")
                to_ver = latest.get("to_version", "unknown")
                preview_lines.append(f"• {project.name}: v{to_ver} → v{from_ver}")

        preview_text = f"Will rollback {len(selected)} project(s):\n\n" + "\n".join(preview_lines)

        from qfluentwidgets import MessageBox

        MessageBox("Rollback Preview", preview_text, self).exec()

    def _execute_rollback(self) -> None:  # noqa: C901
        """Execute rollback for selected projects."""
        selected = self._get_selected_projects()

        if not selected:
            from qfluentwidgets import MessageBox

            MessageBox(
                "No Selection", "Please select at least one project to rollback.", self
            ).exec()
            return

        # Confirm action
        from qfluentwidgets import MessageBox

        confirm = MessageBox(
            "Confirm Rollback",
            f"Are you sure you want to rollback {len(selected)} project(s)?\n\n"
            "This will restore projects to their pre-migration state. "
            "Any changes made after migration will be lost.",
            self,
        )
        if confirm.exec() != confirm.Accepted:
            return

        # Execute rollback
        try:
            rollback_targets = []
            for project in selected:
                if project.migration_history:
                    # Get latest backup path
                    # We need to find the backup path corresponding to the latest migration
                    # Assuming last entry in history is what we're rolling back from
                    latest = project.migration_history[-1]
                    backup_path_str = latest.get("backup_path")
                    if backup_path_str:
                        from pathlib import Path

                        rollback_targets.append((project, Path(backup_path_str)))

            if not rollback_targets:
                from qfluentwidgets import MessageBox

                MessageBox("Error", "No backup paths found for selected projects.", self).exec()
                return

            results = self.project_service.rollback_multiple_projects(rollback_targets)

            # Count successes and failures
            successes = sum(1 for success in results.values() if success)
            failures = len(results) - successes

            # Show results
            if failures == 0:
                result_msg = f"✅ Successfully rolled back {successes} project(s)."
            else:
                result_msg = (
                    f"⚠️ Rollback completed with issues:\n"
                    f"  • Successful: {successes}\n"
                    f"  • Failed: {failures}\n\n"
                    f"Check logs for details on failed rollbacks."
                )

            MessageBox("Rollback Complete", result_msg, self).exec()

            # Delete backups if requested
            if self.delete_backup_checkbox.isChecked():
                self._delete_backups(selected)

            # Close dialog on success
            if failures == 0:
                self.accept()

        except Exception as e:
            from qfluentwidgets import MessageBox

            MessageBox("Rollback Error", f"Failed to rollback projects:\n{e!s}", self).exec()

    def _delete_backups(self, projects: list[Project]) -> None:
        """Delete backup folders for projects."""
        from pathlib import Path
        import shutil

        for project in projects:
            backup_pattern = f"{project.name}_backup_*"
            project_parent = Path(project.path).parent

            # Find and delete matching backups
            for backup_dir in project_parent.glob(backup_pattern):
                if backup_dir.is_dir():
                    try:
                        shutil.rmtree(backup_dir)
                    except Exception as e:
                        # Log but don't fail
                        logging.warning(f"Failed to delete backup {backup_dir}: {e}")


class MigrationHistoryDialog(MessageBoxBase):
    """
    Dialog for viewing detailed migration history of a project.

    Shows chronological list of all migrations with:
    - Version transitions
    - Timestamps
    - Folders added/removed
    - Backup availability
    """

    def __init__(
        self,
        project: Project,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize migration history dialog.

        Args:
            project: Project to show history for
            parent: Parent widget
        """
        super().__init__(parent)
        self.project = project

        # Create title label since MessageBoxBase doesn't provide one
        self.titleLabel = QLabel(self.widget)
        self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.titleLabel.setText(f"Migration History: {self.project.name}")

        # Add title label to layout
        self.viewLayout.addWidget(self.titleLabel)

        self.viewLayout.setSpacing(16)

        # Current state
        current_label = QLabel(
            f"<b>Current Template:</b> {self.project.template_name or 'None'} "
            f"v{self.project.template_version or 'N/A'}"
        )
        self.viewLayout.addWidget(current_label)

        # History list
        if not self.project.migration_history:
            no_history = QLabel("No migration history available.")
            no_history.setStyleSheet("color: #999; font-style: italic;")
            self.viewLayout.addWidget(no_history)
        else:
            history_label = QLabel(
                f"<b>Migration History ({len(self.project.migration_history)}):</b>"
            )
            self.viewLayout.addWidget(history_label)

            history_list = QListWidget()
            history_list.setMinimumHeight(300)

            for i, migration in enumerate(reversed(self.project.migration_history)):
                item_text = self._format_migration_entry(migration, i)
                item = QListWidgetItem(item_text)
                history_list.addItem(item)

            self.viewLayout.addWidget(history_list)

        # Close button
        close_btn = PrimaryPushButton("Close")
        close_btn.clicked.connect(self.accept)
        self.viewLayout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self.widget.setMinimumWidth(600)

    def _format_migration_entry(self, migration: dict[str, Any], index: int) -> str:
        """Format migration entry for display."""
        from_ver = migration.get("from_version", "unknown")
        to_ver = migration.get("to_version", "unknown")
        timestamp = migration.get("timestamp", "unknown")
        backup_path = migration.get("backup_path", "")

        # Format timestamp
        if timestamp != "unknown":
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass

        backup_status = "✓ Backup available" if backup_path else "✗ No backup"

        return (
            f"#{len(self.project.migration_history) - index}  |  "
            f"{timestamp}  |  "
            f"v{from_ver} → v{to_ver}  |  "
            f"{backup_status}"
        )
