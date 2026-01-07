"""Migration warning banner component for displaying project template update notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget
from qfluentwidgets import InfoBar, InfoBarPosition, InfoLevel, PushButton

if TYPE_CHECKING:
    from app.models.project import Project
    from app.services.project_service import MigrationDiff


class MigrationBanner(QWidget):
    """
    Warning banner that appears when a project has template updates available.

    Displays migration information and provides quick actions for preview/apply/defer.
    """

    # Signals
    preview_requested = Signal()  # User wants to preview migration
    apply_requested = Signal()  # User wants to apply migration immediately
    defer_requested = Signal()  # User wants to schedule for later

    def __init__(
        self, project: Project, migration_diff: MigrationDiff, parent: QWidget | None = None
    ) -> None:
        """
        Initialize migration banner.

        Args:
            project: Project that needs migration
            migration_diff: Details about template changes
            parent: Parent widget
        """
        super().__init__(parent)
        self.project = project
        self.migration_diff = migration_diff

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # Warning icon and message
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)

        # Migration message
        current_ver = self.project.template_version or "unknown"
        target_ver = self.migration_diff.target_version

        message = QLabel(
            f"Template update available: {current_ver} → {target_ver}  |  "
            f"{len(self.migration_diff.folders_to_add)} folders to add, "
            f"{len(self.migration_diff.folders_to_remove)} to remove"
        )
        message.setWordWrap(True)
        layout.addWidget(message, 1)

        # Conflict indicator
        if self.migration_diff.conflicts:
            conflict_label = QLabel(f"🚨 {len(self.migration_diff.conflicts)} conflict(s) detected")
            conflict_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            conflict_label.setToolTip("Some folders contain user files that would be removed")
            layout.addWidget(conflict_label)

        # Action buttons
        preview_btn = PushButton("Preview Changes")
        preview_btn.clicked.connect(self.preview_requested.emit)
        layout.addWidget(preview_btn)

        apply_btn = PushButton("Apply Now")
        apply_btn.clicked.connect(self.apply_requested.emit)
        apply_btn.setToolTip("Apply migration with automatic backup")
        if self.migration_diff.conflicts:
            apply_btn.setToolTip("Conflicting folders will be skipped unless manually resolved")
        layout.addWidget(apply_btn)

        defer_btn = PushButton("Defer")
        defer_btn.clicked.connect(self.defer_requested.emit)
        defer_btn.setToolTip("Schedule migration for later")
        layout.addWidget(defer_btn)

        # Styling
        self.setStyleSheet(
            """
            MigrationBanner {
                background-color: #fff8e1;
                border: 1px solid #ffa726;
                border-radius: 4px;
            }
            """
        )

    @staticmethod
    def show_info_bar(
        message: str,
        level: InfoLevel = InfoLevel.INFOAMTION,
        duration: int = 3000,
        parent: QWidget | None = None,
    ) -> None:
        """
        Show a temporary info bar notification.

        Args:
            message: Message to display
            level: Notification level (INFO, SUCCESS, WARNING, ERROR)
            duration: Display duration in milliseconds
            parent: Parent widget for positioning
        """
        InfoBar.new(
            icon=level,
            title="",
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=parent or QWidget(),
        )

    @staticmethod
    def show_migration_success(
        project_name: str, old_version: str, new_version: str, parent: QWidget | None = None
    ) -> None:
        """Show success notification after migration."""
        MigrationBanner.show_info_bar(
            f"✅ {project_name} migrated: {old_version} → {new_version}",
            InfoLevel.SUCCESS,
            parent=parent,
        )

    @staticmethod
    def show_migration_error(project_name: str, error: str, parent: QWidget | None = None) -> None:
        """Show error notification after failed migration."""
        MigrationBanner.show_info_bar(
            f"❌ Migration failed for {project_name}: {error}",
            InfoLevel.ERROR,
            duration=5000,
            parent=parent,
        )

    @staticmethod
    def show_rollback_success(project_name: str, parent: QWidget | None = None) -> None:
        """Show success notification after rollback."""
        MigrationBanner.show_info_bar(
            f"↩️  {project_name} rolled back successfully",
            InfoLevel.SUCCESS,
            parent=parent,
        )
