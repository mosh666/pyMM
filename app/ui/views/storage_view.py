"""
Storage view for managing portable drives.
"""
import logging
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt

from app.core.services.storage_service import StorageService, DriveInfo


class StorageView(QWidget):
    """View for displaying and managing storage drives."""

    def __init__(self, storage_service: StorageService, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.storage_service = storage_service
        self._init_ui()
        self.refresh_drives()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Storage Management")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Manage removable drives for portable projects and logs. "
            "Projects will be stored in 'pyMM.Projects' and logs in 'pyMM.Logs' at the drive root."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Drives table
        self.drives_table = QTableWidget()
        self.drives_table.setColumnCount(6)
        self.drives_table.setHorizontalHeaderLabels(
            ["Drive", "Label", "Type", "Total Size", "Free Space", "Status"]
        )
        self.drives_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.drives_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.drives_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.drives_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_drives)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

    def refresh_drives(self):
        """Refresh the drives table."""
        drives = self.storage_service.get_all_drives()

        self.drives_table.setRowCount(len(drives))

        for row, drive in enumerate(drives):
            # Drive letter
            self.drives_table.setItem(row, 0, QTableWidgetItem(drive.drive_letter))

            # Label
            self.drives_table.setItem(row, 1, QTableWidgetItem(drive.label or "-"))

            # Type
            drive_type = "Removable" if drive.is_removable else "Fixed"
            self.drives_table.setItem(row, 2, QTableWidgetItem(drive_type))

            # Total size
            total_gb = drive.total_size / (1024**3)
            self.drives_table.setItem(row, 3, QTableWidgetItem(f"{total_gb:.2f} GB"))

            # Free space
            free_gb = drive.free_space / (1024**3)
            self.drives_table.setItem(row, 4, QTableWidgetItem(f"{free_gb:.2f} GB"))

            # Status
            used_pct = drive.used_percent
            status = f"{used_pct:.1f}% used"
            self.drives_table.setItem(row, 5, QTableWidgetItem(status))

    def get_selected_drive(self) -> Path:
        """
        Get the currently selected drive.

        Returns:
            Path to selected drive or None
        """
        selected_rows = self.drives_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            drive_letter = self.drives_table.item(row, 0).text()
            return Path(drive_letter)
        return None
