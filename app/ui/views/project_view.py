"""
Project view for managing media projects.
"""
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal

from app.models.project import Project
from app.services.project_service import ProjectService


class ProjectView(QWidget):
    """View for managing media projects."""
    
    project_opened = Signal(Project)  # Emitted when a project is opened

    def __init__(self, project_service: ProjectService, parent=None) -> None:
        super().__init__(parent)
        
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
            "folder on your portable drive with version control support."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.setMinimumHeight(300)
        self.projects_list.itemDoubleClicked.connect(self._on_item_double_clicked)
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
            placeholder = QListWidgetItem("No projects found. Create your first project to get started!")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.projects_list.addItem(placeholder)
            return
        
        for project in projects:
            item = QListWidgetItem()
            
            # Format display
            git_icon = "📁" if project.is_git_repo else "📂"
            status = "✓" if project.exists else "✗"
            
            item.setText(f"{status} {git_icon} {project.name}\n    {project.path}")
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
