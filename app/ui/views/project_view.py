"""
Project view for managing media projects.
"""
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt


class ProjectView(QWidget):
    """View for managing media projects."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
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

    def _refresh_projects(self):
        """Refresh the projects list."""
        self.projects_list.clear()

        # TODO: Implement project discovery
        placeholder = QListWidgetItem("No projects found. Create your first project to get started!")
        placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
        self.projects_list.addItem(placeholder)

    def _create_project(self):
        """Create a new project."""
        # TODO: Implement project creation dialog
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self, "Coming Soon", "Project creation functionality coming soon!")

    def _open_project(self):
        """Open selected project."""
        # TODO: Implement project opening
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(self, "Coming Soon", "Project opening functionality coming soon!")
