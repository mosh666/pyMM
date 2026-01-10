"""
Project view for managing media projects.
"""

import logging

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.models.project import Project
from app.services.project_service import MigrationDiff, ProjectService
from app.ui.components.migration_banner import MigrationBanner
from app.ui.dialogs.migration_dialog import MigrationDialog


class ProjectView(QWidget):
    """View for managing media projects."""

    project_opened = Signal(Project)  # Emitted when a project is opened

    def __init__(self, project_service: ProjectService, parent: QWidget | None = None) -> None:
        """Initialize project management view.

        Args:
            project_service: Project service instance.
            parent: Parent widget (optional).

        Examples:
            >>> view = ProjectView(project_service)
        """
        super().__init__(parent)
        self.setObjectName("projectView")

        self.logger = logging.getLogger(__name__)
        self.project_service = project_service
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Project Management")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Create and manage media projects. Each project is stored in the 'pyMM.Projects' "
            "folder on your portable drive."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Migration banner placeholder (hidden by default)
        self.migration_banner_container = QWidget()
        self.migration_banner_container.setVisible(False)
        self.migration_banner_layout = QVBoxLayout(self.migration_banner_container)
        self.migration_banner_layout.setContentsMargins(0, 0, 0, 12)
        self.migration_banner_layout.setSpacing(8)
        layout.addWidget(self.migration_banner_container)

        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.setMinimumHeight(300)
        self.projects_list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.projects_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.projects_list)

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = QPushButton("➕ Create Project")
        create_btn.clicked.connect(self._create_project)
        button_layout.addWidget(create_btn)

        open_btn = QPushButton("📂 Open Project")
        open_btn.clicked.connect(self._open_project)
        button_layout.addWidget(open_btn)

        button_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self._refresh_projects)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Initial refresh
        self._refresh_projects()

    def _refresh_projects(self) -> None:
        """Refresh the projects list."""
        self.projects_list.clear()

        projects = self.project_service.list_projects()

        if not projects:
            placeholder = QListWidgetItem(
                "No projects found. Create your first project to get started!"
            )
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.projects_list.addItem(placeholder)
            return

        for project in projects:
            item = QListWidgetItem()

            # Format display with migration indicator
            status = "✓" if project.exists else "✗"
            migration_indicator = ""

            # Check if project has migration available
            try:
                migration_diff = self.project_service.check_project_migration(project)
                if migration_diff:
                    migration_indicator = " 🔄"
            except Exception as e:
                self.logger.debug(f"Failed to check migration for {project.name}: {e}")

            # Check if pending migration scheduled
            pending_indicator = " ⏰" if project.pending_migration else ""

            item.setText(
                f"{status} 📁 {project.name}{migration_indicator}{pending_indicator}\n"
                f"    {project.path}"
            )
            item.setData(Qt.ItemDataRole.UserRole, project)

            if not project.exists:
                item.setForeground(Qt.GlobalColor.gray)

            self.projects_list.addItem(item)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handle double-click on project item."""
        project = item.data(Qt.ItemDataRole.UserRole)
        if project and project.exists:
            self.project_opened.emit(project)

    def _create_project(self) -> None:
        """Create a new project."""
        from app.ui.dialogs.project_wizard import ProjectWizard

        wizard = ProjectWizard(self.project_service, self)
        if wizard.exec():
            self._refresh_projects()

            # Optionally open the newly created project
            if wizard.created_project:
                self.project_opened.emit(wizard.created_project)

    def _open_project(self) -> None:
        """Open selected project."""
        from app.ui.dialogs.project_browser import ProjectBrowserDialog

        browser = ProjectBrowserDialog(self.project_service, self)
        browser.project_selected.connect(self.project_opened.emit)
        browser.exec()

        # Refresh in case projects were deleted
        self._refresh_projects()

    def _on_selection_changed(self) -> None:
        """Handle project selection change and check for migrations.

        Updates UI and checks if selected project has pending migrations,
        offering to apply them if available.

        Examples:
            >>> project_view._on_selection_changed()
            # Checks selected project for migration availability
        """
        # Clear existing banner
        while self.migration_banner_layout.count():
            child = self.migration_banner_layout.takeAt(0)
            if widget := child.widget():
                widget.deleteLater()

        # Get selected project
        selected_items = self.projects_list.selectedItems()
        if not selected_items:
            self.migration_banner_container.setVisible(False)
            return

        project = selected_items[0].data(Qt.ItemDataRole.UserRole)
        if not project or not project.exists:
            self.migration_banner_container.setVisible(False)
            return

        # Check for migration
        try:
            needs_migration, migration_diff = self.project_service.check_project_migration(project)
            if needs_migration and migration_diff:
                # Show migration banner
                banner = MigrationBanner(project, migration_diff, self)
                banner.preview_requested.connect(
                    lambda: self._preview_migration(project, migration_diff)
                )
                banner.apply_requested.connect(
                    lambda: self._apply_migration(project, migration_diff)
                )
                banner.defer_requested.connect(
                    lambda: self._defer_migration(project, migration_diff)
                )

                self.migration_banner_layout.addWidget(banner)
                self.migration_banner_container.setVisible(True)
            else:
                self.migration_banner_container.setVisible(False)
        except Exception:
            self.logger.exception("Failed to check migration for %s", project.name)
            self.migration_banner_container.setVisible(False)

    def _preview_migration(self, project: Project, migration_diff: MigrationDiff) -> None:
        """Preview migration changes."""
        dialog = MigrationDialog(project, migration_diff, self.project_service, self)
        if dialog.exec():
            self._refresh_projects()

    def _apply_migration(self, project: Project, migration_diff: MigrationDiff) -> None:
        """Apply migration directly."""
        try:
            success, _ = self.project_service.migrate_project(
                project,
                backup=True,
                skip_conflicts=True,
                preview_mode=False,
            )

            if success:
                MigrationBanner.show_migration_success(
                    project.name,
                    project.template_version or "unknown",
                    migration_diff.target_version,
                    self,
                )
                self._refresh_projects()
            else:
                MigrationBanner.show_migration_error(
                    project.name,
                    "Migration failed. Check logs for details.",
                    self,
                )
        except Exception as e:
            self.logger.exception("Failed to apply migration")
            MigrationBanner.show_migration_error(project.name, str(e), self)

    def _defer_migration(self, project: Project, migration_diff: MigrationDiff) -> None:
        """Defer migration for later."""
        try:
            self.project_service.schedule_deferred_migration(
                project,
                migration_diff.target_version,
                reason="Deferred by user from project view",
            )
            MigrationBanner.show_info_bar(
                f"📅 Migration deferred for {project.name}",
                parent=self,
            )
            self._refresh_projects()
            self._on_selection_changed()  # Refresh banner
        except Exception as e:
            self.logger.exception("Failed to defer migration")
            MigrationBanner.show_migration_error(project.name, str(e), self)

    def refresh_projects(self) -> None:
        """Public method to refresh projects list (called from MainWindow)."""
        self._refresh_projects()
