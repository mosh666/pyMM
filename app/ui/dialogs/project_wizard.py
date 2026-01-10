"""
Project creation wizard.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

from app.models.project import Project
from app.services.project_service import ProjectService


class ProjectWizard(QDialog):
    """
    Wizard for creating new projects.

    Collects project information:
    - Project name
    - Project location
    - Description
    - Project structure options
    """

    def __init__(self, project_service: ProjectService, parent: "QWidget | None" = None) -> None:
        """Initialize project creation wizard.

        Args:
            project_service: Project service for creating projects.
            parent: Parent widget (optional).

        Examples:
            >>> wizard = ProjectWizard(project_service)
        """
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)
        self.project_service = project_service
        self.created_project: Project | None = None

        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        self.setWindowTitle("Create New Project")
        self.setMinimumSize(600, 450)

        # Main layout
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Create a new media management project")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Form section
        form_group = QGroupBox("Project Details")
        form_layout = QFormLayout(form_group)

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("My Media Project")
        self.name_edit.textChanged.connect(self._on_name_changed)
        form_layout.addRow("Project Name:", self.name_edit)

        # Project location
        location_layout = QHBoxLayout()
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("C:/Users/username/Documents/pyMM_projects")
        self.location_edit.textChanged.connect(self._validate_form)
        location_layout.addWidget(self.location_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self._on_browse_location)
        location_layout.addWidget(self.browse_button)

        form_layout.addRow("Location:", location_layout)

        # Full path display
        self.path_label = QLabel()
        self.path_label.setStyleSheet("color: gray; font-style: italic;")
        self.path_label.setWordWrap(True)
        form_layout.addRow("Full Path:", self.path_label)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional project description...")
        self.description_edit.setMaximumHeight(80)
        form_layout.addRow("Description:", self.description_edit)

        layout.addWidget(form_group)

        # Options section
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.template_checkbox = QCheckBox("Use default project structure")
        self.template_checkbox.setChecked(True)
        self.template_checkbox.setToolTip("Create media/, exports/, and cache/ directories")
        options_layout.addWidget(self.template_checkbox)

        layout.addWidget(options_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.create_button = QPushButton("Create Project")
        self.create_button.clicked.connect(self._on_create_project)
        self.create_button.setEnabled(False)
        self.create_button.setStyleSheet("QPushButton { font-weight: bold; min-width: 120px; }")
        button_layout.addWidget(self.create_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Set default location
        default_location = Path.home() / "Documents" / "pyMM_projects"
        self.location_edit.setText(str(default_location))

    def _on_name_changed(self, text: str) -> None:
        """Handle project name change and update path label.

        Args:
            text: New project name text.

        Examples:
            >>> wizard._on_name_changed('My New Project')
            # Updates path label and validates form
        """
        self._update_path_label()
        self._validate_form()

    def _on_browse_location(self) -> None:
        """Handle browse button click."""
        current_path = self.location_edit.text()

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Project Location",
            current_path if current_path else str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )

        if directory:
            self.location_edit.setText(directory)

    def _update_path_label(self) -> None:
        """Update the full path label."""
        name = self.name_edit.text().strip()
        location = self.location_edit.text().strip()

        if name and location:
            # Sanitize project name for directory
            dir_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
            dir_name = dir_name.replace(" ", "_")

            full_path = Path(location) / dir_name
            self.path_label.setText(str(full_path))
        else:
            self.path_label.setText("")

    def _validate_form(self) -> None:
        """Validate form inputs and enable/disable create button."""
        name = self.name_edit.text().strip()
        location = self.location_edit.text().strip()

        # Check if both fields are filled
        if not name or not location:
            self.create_button.setEnabled(False)
            return

        # Check if location exists
        location_path = Path(location)
        if not location_path.exists():
            self.create_button.setEnabled(False)
            self.path_label.setStyleSheet("color: red; font-style: italic;")
            return

        self.create_button.setEnabled(True)
        self.path_label.setStyleSheet("color: green; font-style: italic;")

    def _on_create_project(self) -> None:
        """Handle create project button."""
        name = self.name_edit.text().strip()
        location = self.location_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        use_template = self.template_checkbox.isChecked()

        # Sanitize project name for directory
        dir_name = "".join(c for c in name if c.isalnum() or c in (" ", "-", "_")).strip()
        dir_name = dir_name.replace(" ", "_")

        project_path = Path(location) / dir_name

        # Check if directory already exists
        if project_path.exists():
            reply = QMessageBox.question(
                self,
                "Directory Exists",
                f"The directory already exists:\n{project_path}\n\n"
                f"Do you want to use this directory anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.No:
                return

        try:
            # Create project
            if project_path.exists():
                # Directory exists, just create metadata
                self.created_project = Project(
                    name=name,
                    path=project_path,
                    description=description if description else None,
                )
                self.project_service.save_project(self.created_project)
            else:
                # Create new project
                self.created_project = self.project_service.create_project(
                    name=name,
                    path=project_path,
                    description=description if description else None,
                    use_template="default" if use_template else None,
                )

            QMessageBox.information(
                self,
                "Success",
                f"Project '{name}' created successfully!",
            )

            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to create project:\n{e!s}",
            )
