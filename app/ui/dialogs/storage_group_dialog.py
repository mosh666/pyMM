"""
Storage Group Dialog.

Provides UI for managing Master/Backup drive relationships.
Users can create, edit, and delete storage groups with two-step drive selection.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.services.storage_group_service import (
    DuplicateAssignmentError,
    StorageGroupService,
)
from app.models.storage_group import DriveGroup, DriveIdentity

if TYPE_CHECKING:
    from app.core.services.storage_service import DriveInfo, StorageService

logger = logging.getLogger(__name__)


class DriveSelectionDialog(QDialog):
    """Dialog for selecting a drive from available removable drives."""

    def __init__(
        self,
        storage_service: StorageService,
        title: str,
        message: str,
        exclude_drives: list[DriveInfo] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize drive selection dialog.

        Args:
            storage_service: StorageService for drive detection
            title: Dialog window title
            message: Instructional message to display
            exclude_drives: List of drives to exclude from selection
            parent: Parent widget
        """
        super().__init__(parent)
        self.storage_service = storage_service
        self.exclude_drives = exclude_drives or []
        self.selected_drive: DriveInfo | None = None

        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        self._init_ui(message)
        self._load_drives()

    def _init_ui(self, message: str) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header message
        header = QLabel(message)
        header.setWordWrap(True)
        header.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(header)

        # Drive table
        self.drive_table = QTableWidget()
        self.drive_table.setColumnCount(5)
        self.drive_table.setHorizontalHeaderLabels(
            ["Drive", "Label", "Serial", "Total Size", "Free Space"]
        )
        self.drive_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.drive_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.drive_table.horizontalHeader().setStretchLastSection(True)
        self.drive_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.drive_table.itemDoubleClicked.connect(self._on_drive_double_clicked)
        layout.addWidget(self.drive_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_drives)
        button_layout.addWidget(self.refresh_button)

        self.select_button = QPushButton("Select")
        self.select_button.clicked.connect(self._on_select_clicked)
        self.select_button.setDefault(True)
        button_layout.addWidget(self.select_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_drives(self) -> None:
        """Load and display available removable drives."""
        self.drive_table.setRowCount(0)

        removable_drives = self.storage_service.get_removable_drives()

        # Filter out excluded drives
        exclude_ids = {(d.serial_number, d.label, d.total_size) for d in self.exclude_drives}

        available_drives = [
            d
            for d in removable_drives
            if (d.serial_number, d.label, d.total_size) not in exclude_ids
        ]

        if not available_drives:
            QMessageBox.warning(
                self,
                "No Drives Available",
                "No removable drives are currently available for selection.\n\n"
                "Please connect a removable drive and try again.",
            )
            return

        for drive in available_drives:
            row = self.drive_table.rowCount()
            self.drive_table.insertRow(row)

            # Store drive info in first column item
            drive_item = QTableWidgetItem(drive.drive_letter)
            drive_item.setData(Qt.ItemDataRole.UserRole, drive)
            self.drive_table.setItem(row, 0, drive_item)

            self.drive_table.setItem(row, 1, QTableWidgetItem(drive.label))
            self.drive_table.setItem(row, 2, QTableWidgetItem(drive.serial_number or "N/A"))

            # Format sizes
            total_gb = drive.total_size / (1024**3)
            free_gb = drive.free_space / (1024**3)
            self.drive_table.setItem(row, 3, QTableWidgetItem(f"{total_gb:.1f} GB"))
            self.drive_table.setItem(row, 4, QTableWidgetItem(f"{free_gb:.1f} GB"))

        # Auto-resize columns
        self.drive_table.resizeColumnsToContents()

        logger.info(f"Loaded {len(available_drives)} removable drives for selection")

    def _on_drive_double_clicked(self, _item: QTableWidgetItem) -> None:
        """Handle double-click on drive row."""
        self._on_select_clicked()

    def _on_select_clicked(self) -> None:
        """Handle select button click."""
        selected_rows = self.drive_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a drive first.")
            return

        # Get drive from first column of selected row
        row = self.drive_table.currentRow()
        drive_item = self.drive_table.item(row, 0)
        if drive_item is None:
            return
        self.selected_drive = drive_item.data(Qt.ItemDataRole.UserRole)

        self.accept()

    def get_selected_drive(self) -> DriveInfo | None:
        """Get the selected drive."""
        return self.selected_drive


class StorageGroupEditorDialog(QDialog):
    """Dialog for creating or editing a storage group."""

    def __init__(
        self,
        storage_service: StorageService,
        storage_group_service: StorageGroupService,
        existing_group: DriveGroup | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize storage group editor dialog.

        Args:
            storage_service: StorageService for drive detection
            storage_group_service: StorageGroupService for validation
            existing_group: Existing group to edit (None for new group)
            parent: Parent widget
        """
        super().__init__(parent)
        self.storage_service = storage_service
        self.storage_group_service = storage_group_service
        self.existing_group = existing_group

        self.master_drive: DriveInfo | None = None
        self.backup_drive: DriveInfo | None = None

        # Pre-populate if editing
        if existing_group:
            self.master_drive = storage_group_service.find_drive_info(existing_group.master_drive)
            self.backup_drive = storage_group_service.find_drive_info(existing_group.backup_drive)

        title = "Edit Storage Group" if existing_group else "Create Storage Group"
        self.setWindowTitle(title)
        self.setMinimumSize(500, 400)
        self._init_ui()

        # Load existing values
        if existing_group:
            self.name_edit.setText(existing_group.name)
            if existing_group.description:
                self.description_edit.setPlainText(existing_group.description)
            self._update_drive_labels()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header_text = (
            "Edit the storage group configuration."
            if self.existing_group
            else "Create a new storage group by pairing Master and Backup drives."
        )
        header = QLabel(header_text)
        header.setWordWrap(True)
        header.setStyleSheet("font-size: 12px; padding: 10px;")
        layout.addWidget(header)

        # Form section
        form_group = QGroupBox("Group Details")
        form_layout = QFormLayout(form_group)

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Project Archive 2026")
        form_layout.addRow("Name:", self.name_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Optional description of this storage group...")
        self.description_edit.setMaximumHeight(60)
        form_layout.addRow("Description:", self.description_edit)

        layout.addWidget(form_group)

        # Drive selection section
        drives_group = QGroupBox("Drive Selection")
        drives_layout = QVBoxLayout(drives_group)

        # Master drive
        master_layout = QHBoxLayout()
        master_layout.addWidget(QLabel("Master Drive:"))
        self.master_label = QLabel("Not selected")
        self.master_label.setStyleSheet("color: gray; font-style: italic;")
        master_layout.addWidget(self.master_label)
        master_layout.addStretch()
        self.select_master_button = QPushButton("Select Master...")
        self.select_master_button.clicked.connect(self._select_master_drive)
        master_layout.addWidget(self.select_master_button)
        drives_layout.addLayout(master_layout)

        # Backup drive
        backup_layout = QHBoxLayout()
        backup_layout.addWidget(QLabel("Backup Drive:"))
        self.backup_label = QLabel("Not selected")
        self.backup_label.setStyleSheet("color: gray; font-style: italic;")
        backup_layout.addWidget(self.backup_label)
        backup_layout.addStretch()
        self.select_backup_button = QPushButton("Select Backup...")
        self.select_backup_button.clicked.connect(self._select_backup_drive)
        backup_layout.addWidget(self.select_backup_button)
        drives_layout.addLayout(backup_layout)

        layout.addWidget(drives_group)

        # Warning label
        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #D32F2F; padding: 5px;")
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        layout.addWidget(self.warning_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._on_save_clicked)
        self.save_button.setDefault(True)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _select_master_drive(self) -> None:
        """Open dialog to select Master drive."""
        exclude = [self.backup_drive] if self.backup_drive else []

        dialog = DriveSelectionDialog(
            self.storage_service,
            "Select Master Drive",
            "Select the removable drive to use as the Master (primary) drive for this group.",
            exclude_drives=exclude,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.master_drive = dialog.get_selected_drive()
            self._update_drive_labels()
            self._validate_selection()

    def _select_backup_drive(self) -> None:
        """Open dialog to select Backup drive."""
        exclude = [self.master_drive] if self.master_drive else []

        dialog = DriveSelectionDialog(
            self.storage_service,
            "Select Backup Drive",
            "Select the removable drive to use as the Backup (secondary) drive for this group.",
            exclude_drives=exclude,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.backup_drive = dialog.get_selected_drive()
            self._update_drive_labels()
            self._validate_selection()

    def _update_drive_labels(self) -> None:
        """Update drive selection labels."""
        if self.master_drive:
            text = f"{self.master_drive.label} ({self.master_drive.drive_letter})"
            self.master_label.setText(text)
            self.master_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        else:
            self.master_label.setText("Not selected")
            self.master_label.setStyleSheet("color: gray; font-style: italic;")

        if self.backup_drive:
            text = f"{self.backup_drive.label} ({self.backup_drive.drive_letter})"
            self.backup_label.setText(text)
            self.backup_label.setStyleSheet("color: #1976D2; font-weight: bold;")
        else:
            self.backup_label.setText("Not selected")
            self.backup_label.setStyleSheet("color: gray; font-style: italic;")

    def _validate_selection(self) -> bool:
        """Validate drive selection and show warnings."""
        self.warning_label.hide()

        if not self.master_drive or not self.backup_drive:
            return True  # Not yet complete, but no error

        # Check if same drive
        if self.master_drive.drive_letter == self.backup_drive.drive_letter or (
            self.master_drive.serial_number
            and self.backup_drive.serial_number
            and self.master_drive.serial_number == self.backup_drive.serial_number
        ):
            self.warning_label.setText("⚠️ Master and Backup cannot be the same drive!")
            self.warning_label.show()
            return False

        # Check for duplicate assignments (excluding current group if editing)
        exclude_id = self.existing_group.id if self.existing_group else None

        try:
            # Validate master
            master_identity = DriveIdentity(
                serial_number=self.master_drive.serial_number,
                label=self.master_drive.label,
                total_size=self.master_drive.total_size,
            )
            self.storage_group_service._validate_drive_not_assigned(master_identity, exclude_id)

            # Validate backup
            backup_identity = DriveIdentity(
                serial_number=self.backup_drive.serial_number,
                label=self.backup_drive.label,
                total_size=self.backup_drive.total_size,
            )
            self.storage_group_service._validate_drive_not_assigned(backup_identity, exclude_id)

        except DuplicateAssignmentError as e:
            self.warning_label.setText(f"⚠️ {e!s}")
            self.warning_label.show()
            return False

        return True

    def _on_save_clicked(self) -> None:
        """Handle save button click."""
        # Validate name
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a group name.")
            self.name_edit.setFocus()
            return

        # Validate drives
        if not self.master_drive:
            QMessageBox.warning(self, "Validation Error", "Please select a Master drive.")
            return

        if not self.backup_drive:
            QMessageBox.warning(self, "Validation Error", "Please select a Backup drive.")
            return

        # Final validation
        if not self._validate_selection():
            return

        self.accept()

    def get_group_data(self) -> tuple[str, DriveIdentity, DriveIdentity, str | None]:
        """
        Get the configured group data.

        Returns:
            Tuple of (name, master_identity, backup_identity, description)
        """
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip() or None

        assert self.master_drive is not None
        assert self.backup_drive is not None
        master_identity = DriveIdentity(
            serial_number=self.master_drive.serial_number,
            label=self.master_drive.label,
            total_size=self.master_drive.total_size,
        )

        backup_identity = DriveIdentity(
            serial_number=self.backup_drive.serial_number,
            label=self.backup_drive.label,
            total_size=self.backup_drive.total_size,
        )

        return name, master_identity, backup_identity, description


class StorageGroupDialog(QDialog):
    """Main dialog for managing storage groups."""

    def __init__(
        self,
        storage_service: StorageService,
        storage_group_service: StorageGroupService,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize storage group management dialog.

        Args:
            storage_service: StorageService for drive detection
            storage_group_service: StorageGroupService for group management
            parent: Parent widget
        """
        super().__init__(parent)
        self.storage_service = storage_service
        self.storage_group_service = storage_group_service

        self.setWindowTitle("Manage Storage Groups")
        self.setMinimumSize(800, 500)
        self._init_ui()
        self._load_groups()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel(
            "Storage Groups define Master/Backup drive relationships for data redundancy.\n"
            "Projects can be assigned to groups for automatic failover support."
        )
        header.setWordWrap(True)
        header.setStyleSheet("font-size: 12px; padding: 10px; background-color: #E3F2FD;")
        layout.addWidget(header)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Group")
        self.add_button.clicked.connect(self._add_group)
        toolbar_layout.addWidget(self.add_button)

        self.edit_button = QPushButton("Edit Group")
        self.edit_button.clicked.connect(self._edit_group)
        self.edit_button.setEnabled(False)
        toolbar_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete Group")
        self.delete_button.clicked.connect(self._delete_group)
        self.delete_button.setEnabled(False)
        toolbar_layout.addWidget(self.delete_button)

        toolbar_layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_groups)
        toolbar_layout.addWidget(self.refresh_button)

        layout.addLayout(toolbar_layout)

        # Group table
        self.group_table = QTableWidget()
        self.group_table.setColumnCount(4)
        self.group_table.setHorizontalHeaderLabels(
            ["Name", "Master Drive", "Backup Drive", "Status"]
        )
        self.group_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.group_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.group_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.group_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.group_table.itemDoubleClicked.connect(self._edit_group)

        # Set column widths
        header_view = self.group_table.horizontalHeader()
        assert header_view is not None
        header_view.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header_view.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        layout.addWidget(self.group_table)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _load_groups(self) -> None:
        """Load and display all storage groups."""
        self.group_table.setRowCount(0)

        groups = self.storage_group_service.list_groups()

        for group in groups:
            row = self.group_table.rowCount()
            self.group_table.insertRow(row)

            # Name (store group ID in UserRole)
            name_item = QTableWidgetItem(group.name)
            name_item.setData(Qt.ItemDataRole.UserRole, group.id)
            self.group_table.setItem(row, 0, name_item)

            # Master drive
            master_info = self.storage_group_service.find_drive_info(group.master_drive)
            master_text = f"{group.master_drive.label}"
            if master_info:
                master_text += f" ({master_info.drive_letter}) ✓"
            else:
                master_text += " (Not Connected)"
            self.group_table.setItem(row, 1, QTableWidgetItem(master_text))

            # Backup drive
            backup_info = self.storage_group_service.find_drive_info(group.backup_drive)
            backup_text = f"{group.backup_drive.label}"
            if backup_info:
                backup_text += f" ({backup_info.drive_letter}) ✓"
            else:
                backup_text += " (Not Connected)"
            self.group_table.setItem(row, 2, QTableWidgetItem(backup_text))

            # Status
            if master_info and backup_info:
                status = "✓ Both Connected"
                color = "#2E7D32"  # Green
            elif master_info or backup_info:
                status = "⚠ Partial"
                color = "#F57C00"  # Orange
            else:
                status = "✗ Disconnected"
                color = "#D32F2F"  # Red

            status_item = QTableWidgetItem(status)
            status_item.setForeground(Qt.GlobalColor.black)
            status_item.setData(Qt.ItemDataRole.BackgroundRole, color)
            self.group_table.setItem(row, 3, status_item)

        logger.info(f"Loaded {len(groups)} storage groups")

    def _on_selection_changed(self) -> None:
        """Handle table selection changes."""
        has_selection = bool(self.group_table.selectedItems())
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _add_group(self) -> None:
        """Open dialog to add a new group."""
        dialog = StorageGroupEditorDialog(
            self.storage_service, self.storage_group_service, parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, master, backup, description = dialog.get_group_data()

            try:
                self.storage_group_service.create_group(name, master, backup, description)
                QMessageBox.information(
                    self, "Success", f"Storage group '{name}' created successfully."
                )
                self._load_groups()
            except Exception as e:
                logger.exception("Failed to create storage group")
                QMessageBox.critical(self, "Error", f"Failed to create storage group:\n\n{e!s}")

    def _edit_group(self) -> None:
        """Open dialog to edit selected group."""
        selected_rows = self.group_table.selectedItems()
        if not selected_rows:
            return

        row = self.group_table.currentRow()
        name_item = self.group_table.item(row, 0)
        if name_item is None:
            return
        group_id = name_item.data(Qt.ItemDataRole.UserRole)

        group = self.storage_group_service.get_group(group_id)
        if not group:
            QMessageBox.warning(self, "Error", "Selected group not found.")
            return

        dialog = StorageGroupEditorDialog(
            self.storage_service, self.storage_group_service, existing_group=group, parent=self
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, master, backup, description = dialog.get_group_data()

            try:
                self.storage_group_service.update_group(
                    group_id,
                    name=name,
                    master_drive=master,
                    backup_drive=backup,
                    description=description,
                )
                QMessageBox.information(
                    self, "Success", f"Storage group '{name}' updated successfully."
                )
                self._load_groups()
            except Exception as e:
                logger.exception("Failed to update storage group")
                QMessageBox.critical(self, "Error", f"Failed to update storage group:\n\n{e!s}")

    def _delete_group(self) -> None:
        """Delete selected group."""
        selected_rows = self.group_table.selectedItems()
        if not selected_rows:
            return

        row = self.group_table.currentRow()
        name_item = self.group_table.item(row, 0)
        if name_item is None:
            return
        group_id = name_item.data(Qt.ItemDataRole.UserRole)

        group = self.storage_group_service.get_group(group_id)
        if not group:
            QMessageBox.warning(self, "Error", "Selected group not found.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete storage group '{group.name}'?\n\n"
            "This will NOT delete any files, only the group relationship.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.storage_group_service.delete_group(group_id)
                QMessageBox.information(
                    self, "Success", f"Storage group '{group.name}' deleted successfully."
                )
                self._load_groups()
            except Exception as e:
                logger.exception("Failed to delete storage group")
                QMessageBox.critical(self, "Error", f"Failed to delete storage group:\n\n{e!s}")
