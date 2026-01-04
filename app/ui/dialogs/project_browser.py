"""
Project browser dialog for viewing and managing projects.
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QLabel,
    QMessageBox,
    QWidget,
)
from PySide6.QtCore import Qt, Signal

from app.models.project import Project
from app.services.project_service import ProjectService


class ProjectBrowserDialog(QDialog):
    """
    Dialog for browsing and managing projects.
    
    Allows users to:
    - View list of existing projects
    - Create new projects
    - Open selected project
    - Delete projects
    """
    
    project_selected = Signal(Project)  # Emitted when user selects to open a project
    
    def __init__(self, project_service: ProjectService, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.project_service = project_service
        self.selected_project: Optional[Project] = None
        
        self._init_ui()
        self._load_projects()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Project Browser")
        self.setMinimumSize(700, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Select or create a project")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.setAlternatingRowColors(True)
        self.project_list.itemDoubleClicked.connect(self._on_project_double_clicked)
        self.project_list.currentItemChanged.connect(self._on_selection_changed)
        layout.addWidget(self.project_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("New Project")
        self.new_button.clicked.connect(self._on_new_project)
        button_layout.addWidget(self.new_button)
        
        self.open_button = QPushButton("Open")
        self.open_button.clicked.connect(self._on_open_project)
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._on_delete_project)
        self.delete_button.setEnabled(False)
        self.delete_button.setStyleSheet("QPushButton { color: #d32f2f; }")
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _load_projects(self):
        """Load and display all projects."""
        self.project_list.clear()
        
        projects = self.project_service.list_projects()
        
        if not projects:
            item = QListWidgetItem("No projects found. Click 'New Project' to create one.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setData(Qt.ItemDataRole.UserRole, None)
            self.project_list.addItem(item)
            return
        
        for project in projects:
            item = QListWidgetItem()
            
            # Format display text
            status = "✓" if project.exists else "✗"
            git_icon = "📁" if project.is_git_repo else "📂"
            
            name = f"{git_icon} {project.name}"
            path_str = str(project.path)
            modified_str = project.modified.strftime("%Y-%m-%d %H:%M")
            
            item.setText(f"{status} {name}\n    {path_str}\n    Modified: {modified_str}")
            item.setData(Qt.ItemDataRole.UserRole, project)
            
            # Style missing projects differently
            if not project.exists:
                item.setForeground(Qt.GlobalColor.gray)
            
            self.project_list.addItem(item)
    
    def _on_selection_changed(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle project selection change."""
        if current is None:
            self.open_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.selected_project = None
            return
        
        project = current.data(Qt.ItemDataRole.UserRole)
        
        if project is None:
            self.open_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.selected_project = None
        else:
            self.open_button.setEnabled(project.exists)
            self.delete_button.setEnabled(True)
            self.selected_project = project
    
    def _on_project_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on a project."""
        project = item.data(Qt.ItemDataRole.UserRole)
        if project and project.exists:
            self._open_project(project)
    
    def _on_new_project(self):
        """Handle new project button."""
        from app.ui.dialogs.project_wizard import ProjectWizard
        
        wizard = ProjectWizard(self.project_service, self)
        if wizard.exec():
            # Reload project list
            self._load_projects()
    
    def _on_open_project(self):
        """Handle open project button."""
        if self.selected_project:
            self._open_project(self.selected_project)
    
    def _open_project(self, project: Project):
        """Open the selected project."""
        if not project.exists:
            QMessageBox.warning(
                self,
                "Project Not Found",
                f"The project directory does not exist:\n{project.path}",
            )
            return
        
        self.project_selected.emit(project)
        self.accept()
    
    def _on_delete_project(self):
        """Handle delete project button."""
        if not self.selected_project:
            return
        
        project = self.selected_project
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete Project",
            f"Are you sure you want to delete '{project.name}'?\n\n"
            f"This will only remove the project from the list.\n"
            f"Project files will NOT be deleted.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.project_service.delete_project(project, delete_files=False)
                self._load_projects()
                QMessageBox.information(
                    self,
                    "Project Deleted",
                    f"Project '{project.name}' has been removed from the list.",
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete project:\n{str(e)}",
                )
