"""
Storage view for managing portable drives.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.services.storage_group_service import StorageGroupService
from app.core.services.storage_service import StorageService
from app.models.storage_group import DriveRole


class StorageView(QWidget):
    """View for displaying and managing storage drives."""

    def __init__(
        self,
        storage_service: StorageService,
        storage_group_service: StorageGroupService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize storage management view.

        Args:
            storage_service: Storage service for drive operations.
            storage_group_service: Optional storage group service for group management.
            parent: Parent widget (optional).

        Examples:
            >>> view = StorageView(storage_service)
        """
        super().__init__(parent)
        self.setObjectName("storageView")

        self.logger = logging.getLogger(__name__)
        self.storage_service = storage_service
        self.storage_group_service = storage_group_service
        self._init_ui()
        self.refresh_drives()

    def _init_ui(self) -> None:
        """Initialize UI components for storage view.

        Creates table for drive information including drive letter,
        label, type, sizes, group role, and status.

        Examples:
            >>> storage_view._init_ui()
            # Creates storage management UI with drives table
        """
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
        self.drives_table.setColumnCount(7)
        self.drives_table.setHorizontalHeaderLabels(
            ["Drive", "Label", "Type", "Total Size", "Free Space", "Group Role", "Status"]
        )
        self.drives_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.drives_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.drives_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.drives_table)

        # Buttons
        button_layout = QHBoxLayout()

        # Manage Storage Groups button (only if service available)
        if self.storage_group_service:
            manage_groups_btn = QPushButton("📁 Manage Storage Groups")
            manage_groups_btn.clicked.connect(self._manage_storage_groups)
            button_layout.addWidget(manage_groups_btn)

        button_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_drives)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

    def refresh_drives(self) -> None:
        """Refresh the drives table with group role information."""
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

            # Group Role
            group_role_text = "—"
            tooltip = None

            if self.storage_group_service:
                role_info = self.storage_group_service.get_drive_role(drive)
                if role_info:
                    group, role = role_info
                    if role == DriveRole.MASTER:
                        group_role_text = "🔵 Master"
                        # Find paired backup
                        backup_info = self.storage_group_service.find_drive_info(group.backup_drive)
                        if backup_info:
                            tooltip = f"Master for: {group.name}\nPaired with: {backup_info.label} ({backup_info.drive_letter})"
                        else:
                            tooltip = f"Master for: {group.name}\nPaired with: {group.backup_drive.label} (Not Connected)"
                    else:  # BACKUP
                        group_role_text = "🟢 Backup"
                        # Find paired master
                        master_info = self.storage_group_service.find_drive_info(group.master_drive)
                        if master_info:
                            tooltip = f"Backup for: {group.name}\nPaired with: {master_info.label} ({master_info.drive_letter})"
                        else:
                            tooltip = f"Backup for: {group.name}\nPaired with: {group.master_drive.label} (Not Connected)"

            group_role_item = QTableWidgetItem(group_role_text)
            if tooltip:
                group_role_item.setToolTip(tooltip)
            self.drives_table.setItem(row, 5, group_role_item)

            # Status
            used_pct = drive.used_percent
            status = f"{used_pct:.1f}% used"
            self.drives_table.setItem(row, 6, QTableWidgetItem(status))

    def _manage_storage_groups(self) -> None:
        """Open the storage groups management dialog."""
        from app.ui.dialogs.storage_group_dialog import StorageGroupDialog

        assert self.storage_service is not None
        assert self.storage_group_service is not None
        dialog = StorageGroupDialog(self.storage_service, self.storage_group_service, parent=self)
        dialog.exec()

        # Refresh drives after dialog closes
        self.refresh_drives()

    def get_selected_drive(self) -> Path | None:
        """
        Get the currently selected drive.

        Returns:
            Path to selected drive or None
        """
        selected_rows = self.drives_table.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.drives_table.item(row, 0)
            if item is not None:
                drive_letter = item.text()
                return Path(drive_letter)
        return None
