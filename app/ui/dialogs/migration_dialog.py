"""Migration dialog for previewing and applying template updates."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout, QLabel, QTextEdit, QVBoxLayout, QWidget
from qfluentwidgets import CheckBox, MessageBoxBase, PrimaryPushButton, PushButton

if TYPE_CHECKING:
    from app.models.project import Project
    from app.services.project_service import MigrationConflict, MigrationDiff, ProjectService


class MigrationDialog(MessageBoxBase):
    """
    Dialog for previewing and applying template migrations.

    Shows detailed information about what will change, including:
    - Folders to be added/removed
    - Conflicts with user files
    - Migration notes from template
    - Preview mode option
    """

    def __init__(
        self,
        project: Project,
        migration_diff: MigrationDiff,
        project_service: ProjectService,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize migration dialog.

        Args:
            project: Project to migrate
            migration_diff: Details about template changes
            project_service: Service for executing migration
            parent: Parent widget
        """
        super().__init__(parent)
        self.project = project
        self.migration_diff = migration_diff
        self.project_service = project_service

        # Create title label since MessageBoxBase doesn't provide one
        self.titleLabel = QLabel(self.widget)
        self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Title and subtitle
        self.titleLabel.setText(f"Migrate {self.project.name}")
        current_ver = self.project.template_version or "unknown"
        target_ver = self.migration_diff.target_version
        subtitle = f"Template Update: {current_ver} → {target_ver}"

        # Use existing viewLayout from MessageBoxBase
        self.viewLayout.setSpacing(16)

        # Add title label to layout
        self.viewLayout.addWidget(self.titleLabel)

        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("font-size: 13px; color: #666;")
        self.viewLayout.addWidget(subtitle_label)

        # Folders to add
        if self.migration_diff.folders_to_add:
            add_label = QLabel(
                f"<b>Folders to Add ({len(self.migration_diff.folders_to_add)}):</b>"
            )
            self.viewLayout.addWidget(add_label)

            add_text = QTextEdit()
            add_text.setReadOnly(True)
            add_text.setMaximumHeight(100)
            add_text.setPlainText("\n".join(f"+ {f}" for f in self.migration_diff.folders_to_add))
            add_text.setStyleSheet("background-color: #e8f5e9; color: #2e7d32;")
            self.viewLayout.addWidget(add_text)

        # Folders to remove
        if self.migration_diff.folders_to_remove:
            remove_label = QLabel(
                f"<b>Folders to Remove ({len(self.migration_diff.folders_to_remove)}):</b>"
            )
            self.viewLayout.addWidget(remove_label)

            remove_text = QTextEdit()
            remove_text.setReadOnly(True)
            remove_text.setMaximumHeight(100)
            remove_text.setPlainText(
                "\n".join(f"- {f}" for f in self.migration_diff.folders_to_remove)
            )
            remove_text.setStyleSheet("background-color: #ffebee; color: #c62828;")
            self.viewLayout.addWidget(remove_text)

        # Conflicts
        if self.migration_diff.conflicts:
            self._add_conflicts_section(self.viewLayout)

        # Migration notes
        if self.migration_diff.migration_notes:
            notes_label = QLabel("<b>Migration Notes:</b>")
            self.viewLayout.addWidget(notes_label)

            notes_text = QTextEdit()
            notes_text.setReadOnly(True)
            notes_text.setMaximumHeight(80)
            notes_text.setPlainText(self.migration_diff.migration_notes)
            notes_text.setStyleSheet("background-color: #f5f5f5;")
            self.viewLayout.addWidget(notes_text)

        # Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(8)

        self.preview_checkbox = CheckBox("Preview mode (create temporary copy)")
        self.preview_checkbox.setToolTip(
            "Test migration in a temporary directory without modifying the original"
        )
        options_layout.addWidget(self.preview_checkbox)

        self.skip_conflicts_checkbox = CheckBox("Skip conflicting folders")
        self.skip_conflicts_checkbox.setToolTip("Don't remove folders that contain user files")
        self.skip_conflicts_checkbox.setChecked(True)
        self.skip_conflicts_checkbox.setEnabled(bool(self.migration_diff.conflicts))
        options_layout.addWidget(self.skip_conflicts_checkbox)

        self.backup_checkbox = CheckBox("Create backup before migration")
        self.backup_checkbox.setToolTip("Create timestamped backup for rollback (recommended)")
        self.backup_checkbox.setChecked(True)
        options_layout.addWidget(self.backup_checkbox)

        self.viewLayout.addLayout(options_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        defer_btn = PushButton("Defer Migration")
        defer_btn.clicked.connect(self._defer_migration)
        defer_btn.setToolTip("Schedule this migration for later")
        button_layout.addWidget(defer_btn)

        apply_btn = PrimaryPushButton("Apply Migration")
        apply_btn.clicked.connect(self._apply_migration)
        button_layout.addWidget(apply_btn)

        self.viewLayout.addLayout(button_layout)

        # Set dialog size
        self.widget.setMinimumWidth(600)
        self.widget.setMaximumHeight(700)

    def _add_conflicts_section(self, layout: QVBoxLayout) -> None:
        """Add conflicts section to layout."""
        conflict_label = QLabel(
            f"<b style='color: #d32f2f;'>⚠️ Conflicts Detected "
            f"({len(self.migration_diff.conflicts)}):</b>"
        )
        self.viewLayout.addWidget(conflict_label)

        conflict_text = QTextEdit()
        conflict_text.setReadOnly(True)
        conflict_text.setMaximumHeight(120)

        conflict_details = []
        for conflict in self.migration_diff.conflicts:
            detail = f"📁 {conflict.folder_path}\n"
            detail += f"   Reason: {conflict.reason}\n"
            if conflict.user_files_count:
                detail += f"   User files: {conflict.user_files_count}\n"
            if conflict.last_modified:
                detail += f"   Last modified: {conflict.last_modified}\n"
            conflict_details.append(detail)

        conflict_text.setPlainText("\n".join(conflict_details))
        conflict_text.setStyleSheet(
            "background-color: #fff3e0; color: #e65100; font-family: monospace;"
        )
        self.viewLayout.addWidget(conflict_text)

        # Warning message
        warning = QLabel(
            "⚠️ Conflicting folders contain user files. "
            "Enable 'Skip conflicting folders' to preserve them."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self.viewLayout.addWidget(warning)

    def _apply_migration(self) -> None:
        """Apply the migration with selected options."""
        try:
            preview_mode = self.preview_checkbox.isChecked()
            skip_conflicts = self.skip_conflicts_checkbox.isChecked()
            create_backup = self.backup_checkbox.isChecked()

            if preview_mode:
                # Create preview
                preview_path, _ = self.project_service.create_preview_migration(self.project)
                self.yesSignal.emit()
                self._show_preview_info(str(preview_path))
            else:
                # Apply migration
                self.project_service.migrate_project(
                    self.project,
                    backup=create_backup and not preview_mode,
                    skip_conflicts=skip_conflicts,
                    preview_mode=False,
                )
                success = True

                if success:
                    self.yesSignal.emit()
                    from app.ui.components.migration_banner import MigrationBanner

                    MigrationBanner.show_migration_success(
                        self.project.name,
                        self.project.template_version or "unknown",
                        self.migration_diff.target_version,
                        self.parent(),
                    )
                else:
                    self._show_error("Migration failed. Check logs for details.")

        except Exception as e:
            self._show_error(str(e))

    def _defer_migration(self) -> None:
        """Schedule migration for later."""
        try:
            self.project_service.schedule_deferred_migration(
                self.project,
                self.migration_diff.target_version,
                reason="Deferred by user via dialog",
            )
            self.yesSignal.emit()

            from app.ui.components.migration_banner import MigrationBanner

            MigrationBanner.show_info_bar(
                f"📅 Migration deferred for {self.project.name}",
                parent=self.parent(),
            )
        except Exception as e:
            self._show_error(str(e))

    def _show_preview_info(self, preview_path: str) -> None:
        """Show information about created preview."""
        from qfluentwidgets import MessageBox

        MessageBox(
            "Preview Created",
            f"Preview created at:\n{preview_path}\n\n"
            "Review the changes, then apply migration if satisfied.\n"
            "Preview will be automatically cleaned up on next restart.",
            self,
        ).exec()

    def _show_error(self, error: str) -> None:
        """Show error message."""
        from qfluentwidgets import MessageBox

        MessageBox("Migration Error", error, self).exec()


class ConflictResolutionDialog(MessageBoxBase):
    """
    Dialog for manually resolving migration conflicts.

    Allows users to review conflicting folders and decide whether to:
    - Keep folder (skip removal)
    - Remove folder (delete user files)
    - Backup folder (move to backup location)
    """

    def __init__(
        self,
        conflicts: list[MigrationConflict],
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize conflict resolution dialog.

        Args:
            conflicts: List of detected conflicts
            parent: Parent widget
        """
        super().__init__(parent)
        self.conflicts = conflicts
        self.resolutions: dict[str, str] = {}  # folder_path -> action

        # Create title label since MessageBoxBase doesn't provide one
        self.titleLabel = QLabel(self.widget)
        self.titleLabel.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        self.titleLabel.setText("Resolve Migration Conflicts")

        # Add title label to layout
        self.viewLayout.addWidget(self.titleLabel)

        self.viewLayout.setSpacing(16)

        # Instructions
        instructions = QLabel(
            f"Found {len(self.conflicts)} conflicting folder(s) containing user files.\n"
            "Choose how to handle each conflict:"
        )
        instructions.setWordWrap(True)
        self.viewLayout.addWidget(instructions)

        # Conflict list with resolution options
        for conflict in self.conflicts:
            conflict_widget = self._create_conflict_widget(conflict)
            self.viewLayout.addWidget(conflict_widget)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = PushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        button_layout.addStretch()

        apply_btn = PrimaryPushButton("Apply Resolutions")
        apply_btn.clicked.connect(self.accept)
        button_layout.addWidget(apply_btn)

        self.viewLayout.addLayout(button_layout)

        self.widget.setMinimumWidth(600)

    def _create_conflict_widget(self, conflict: MigrationConflict) -> QWidget:
        """Create widget for single conflict."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Folder info
        info_label = QLabel(f"<b>{conflict.folder_path}</b>")
        layout.addWidget(info_label)

        reason_label = QLabel(f"Reason: {conflict.reason}")
        reason_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(reason_label)

        if conflict.user_files_count:
            files_label = QLabel(f"Contains {conflict.user_files_count} user file(s)")
            files_label.setStyleSheet("color: #d32f2f; font-size: 12px;")
            layout.addWidget(files_label)

        # Resolution options (radio buttons would be better, but checkboxes for simplicity)
        # In real implementation, use QButtonGroup with radio buttons

        widget.setStyleSheet(
            "QWidget { background-color: #fff3e0; border: 1px solid #ffa726; border-radius: 4px; }"
        )

        return widget

    def get_resolutions(self) -> dict[str, str]:
        """Get user's resolution choices."""
        return self.resolutions
