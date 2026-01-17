"""
Conflict Resolution Dialog.

Provides UI for resolving file synchronization conflicts between
Master and Backup drives with visual diff viewer and resolution options.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from pathlib import Path

    from app.core.sync.file_synchronizer import FileConflict

logger = logging.getLogger(__name__)


class ConflictResolutionDialog(QDialog):
    """Dialog for resolving synchronization conflicts."""

    def __init__(
        self,
        conflicts: list[FileConflict],
        master_root: Path,
        backup_root: Path,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize conflict resolution dialog.

        Args:
            conflicts: List of detected conflicts
            master_root: Root path of Master drive
            backup_root: Root path of Backup drive
            parent: Parent widget
        """
        super().__init__(parent)
        self.conflicts = conflicts
        self.master_root = master_root
        self.backup_root = backup_root
        self.resolutions: dict[
            str, str
        ] = {}  # relative_path -> resolution ("master"/"backup"/"skip"/"both")

        self.setWindowTitle(f"Resolve Conflicts - {len(conflicts)} file(s)")
        self.setMinimumSize(900, 600)
        self._init_ui()

        if conflicts:
            self.conflict_list.setCurrentRow(0)

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QHBoxLayout(self)

        # Left panel: Conflict list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        list_header = QLabel(f"Conflicts ({len(self.conflicts)})")
        list_header.setStyleSheet("font-weight: bold; font-size: 13px;")
        left_layout.addWidget(list_header)

        self.conflict_list = QListWidget()
        self.conflict_list.currentRowChanged.connect(self._on_conflict_selected)

        for conflict in self.conflicts:
            item = QListWidgetItem(conflict.relative_path)
            item.setData(Qt.ItemDataRole.UserRole, conflict)

            # Set icon based on conflict type
            if conflict.conflict_type == "modified_both":
                item.setIcon(
                    self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxWarning)
                )
            elif conflict.conflict_type == "deleted_master":
                item.setIcon(
                    self.style().standardIcon(self.style().StandardPixmap.SP_DialogNoButton)
                )
            elif conflict.conflict_type == "size_mismatch":
                item.setIcon(
                    self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxCritical)
                )

            self.conflict_list.addItem(item)

        left_layout.addWidget(self.conflict_list)

        # Batch resolution buttons
        batch_group = QGroupBox("Batch Actions")
        batch_layout = QVBoxLayout(batch_group)

        use_master_all_btn = QPushButton("Use Master for All")
        use_master_all_btn.clicked.connect(lambda: self._batch_resolve("master"))
        batch_layout.addWidget(use_master_all_btn)

        use_backup_all_btn = QPushButton("Use Backup for All")
        use_backup_all_btn.clicked.connect(lambda: self._batch_resolve("backup"))
        batch_layout.addWidget(use_backup_all_btn)

        skip_all_btn = QPushButton("Skip All")
        skip_all_btn.clicked.connect(lambda: self._batch_resolve("skip"))
        batch_layout.addWidget(skip_all_btn)

        left_layout.addWidget(batch_group)

        left_panel.setMaximumWidth(300)
        layout.addWidget(left_panel)

        # Right panel: Conflict details and resolution
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # File information
        self.info_group = QGroupBox("Conflict Information")
        info_layout = QFormLayout(self.info_group)

        self.file_name_label = QLabel()
        self.file_name_label.setWordWrap(True)
        info_layout.addRow("File:", self.file_name_label)

        self.conflict_type_label = QLabel()
        info_layout.addRow("Conflict Type:", self.conflict_type_label)

        self.master_info_label = QLabel()
        info_layout.addRow("Master:", self.master_info_label)

        self.backup_info_label = QLabel()
        info_layout.addRow("Backup:", self.backup_info_label)

        right_layout.addWidget(self.info_group)

        # File content preview (for text files)
        preview_group = QGroupBox("Content Preview")
        preview_layout = QVBoxLayout(preview_group)

        preview_label = QLabel("Select a file to preview content (text files only)")
        preview_label.setStyleSheet("font-style: italic; color: gray;")
        preview_layout.addWidget(preview_label)

        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        self.content_preview.setMaximumHeight(200)
        preview_layout.addWidget(self.content_preview)

        right_layout.addWidget(preview_group)

        # Resolution options
        resolution_group = QGroupBox("Resolution")
        resolution_layout = QVBoxLayout(resolution_group)

        self.resolution_buttons = QButtonGroup()

        self.use_master_radio = QRadioButton("Use Master version (overwrite Backup)")
        self.resolution_buttons.addButton(self.use_master_radio, 0)
        resolution_layout.addWidget(self.use_master_radio)

        self.use_backup_radio = QRadioButton("Use Backup version (overwrite Master)")
        self.resolution_buttons.addButton(self.use_backup_radio, 1)
        resolution_layout.addWidget(self.use_backup_radio)

        self.keep_both_radio = QRadioButton("Keep both (rename Backup with .backup suffix)")
        self.resolution_buttons.addButton(self.keep_both_radio, 2)
        resolution_layout.addWidget(self.keep_both_radio)

        self.skip_radio = QRadioButton("Skip this file (leave unchanged)")
        self.resolution_buttons.addButton(self.skip_radio, 3)
        self.skip_radio.setChecked(True)
        resolution_layout.addWidget(self.skip_radio)

        self.resolution_buttons.buttonClicked.connect(self._on_resolution_changed)

        right_layout.addWidget(resolution_group)

        right_layout.addStretch()

        layout.addWidget(right_panel)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_button = QPushButton("Apply Resolutions")
        self.apply_button.clicked.connect(self._apply_resolutions)
        self.apply_button.setStyleSheet("font-weight: bold; min-width: 150px;")
        button_layout.addWidget(self.apply_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        right_layout.addLayout(button_layout)

    def _on_conflict_selected(self, row: int) -> None:
        """Handle conflict selection change."""
        if row < 0 or row >= len(self.conflicts):
            return

        conflict = self.conflicts[row]

        # Update file info
        self.file_name_label.setText(conflict.relative_path)

        # Conflict type
        type_text = {
            "modified_both": "Both Master and Backup modified",
            "deleted_master": "Deleted from Master, exists on Backup",
            "size_mismatch": "File sizes don't match",
        }.get(conflict.conflict_type, conflict.conflict_type)

        self.conflict_type_label.setText(type_text)
        self.conflict_type_label.setStyleSheet("color: #D32F2F; font-weight: bold;")

        # Master info
        if conflict.master_mtime and conflict.master_size is not None:
            master_text = (
                f"{conflict.master_mtime.strftime('%Y-%m-%d %H:%M:%S')} "
                f"({conflict.master_size / 1024:.1f} KB)"
            )
            self.master_info_label.setText(master_text)
        else:
            self.master_info_label.setText("(File not found)")
            self.master_info_label.setStyleSheet("color: #D32F2F;")

        # Backup info
        if conflict.backup_mtime and conflict.backup_size is not None:
            backup_text = (
                f"{conflict.backup_mtime.strftime('%Y-%m-%d %H:%M:%S')} "
                f"{conflict.backup_size / 1024:.1f} KB)"
            )
            self.backup_info_label.setText(backup_text)
        else:
            self.backup_info_label.setText("(File not found)")
            self.backup_info_label.setStyleSheet("color: #D32F2F;")

        # Try to preview content
        self._preview_content(conflict)

        # Load saved resolution if exists
        saved_resolution = self.resolutions.get(conflict.relative_path, "skip")
        resolution_map = {
            "master": self.use_master_radio,
            "backup": self.use_backup_radio,
            "both": self.keep_both_radio,
            "skip": self.skip_radio,
        }
        resolution_map.get(saved_resolution, self.skip_radio).setChecked(True)

    def _preview_content(self, conflict: FileConflict) -> None:
        """Preview file content (text files only)."""
        master_path = self.master_root / conflict.relative_path
        backup_path = self.backup_root / conflict.relative_path

        try:
            # Try to read as text
            preview_text = ""

            if master_path.exists():
                with master_path.open(encoding="utf-8", errors="ignore") as f:
                    master_content = f.read(1000)  # Read first 1000 chars
                    preview_text += "=== MASTER ===\n" + master_content + "\n\n"

            if backup_path.exists():
                with backup_path.open(encoding="utf-8", errors="ignore") as f:
                    backup_content = f.read(1000)
                    preview_text += "=== BACKUP ===\n" + backup_content

            self.content_preview.setPlainText(preview_text if preview_text else "(Binary file)")

        except Exception as e:
            self.content_preview.setPlainText(f"(Cannot preview: {e})")

    def _on_resolution_changed(self) -> None:
        """Handle resolution radio button change."""
        current_row = self.conflict_list.currentRow()
        if current_row < 0:
            return

        conflict = self.conflicts[current_row]

        # Map button to resolution
        button_to_resolution = {
            0: "master",
            1: "backup",
            2: "both",
            3: "skip",
        }

        button_id = self.resolution_buttons.id(self.resolution_buttons.checkedButton())
        resolution = button_to_resolution.get(button_id, "skip")

        self.resolutions[conflict.relative_path] = resolution

        # Update list item color
        item = self.conflict_list.item(current_row)
        if resolution == "skip":
            item.setBackground(Qt.GlobalColor.transparent)
        elif resolution == "master":
            item.setBackground(Qt.GlobalColor.lightGreen)
        elif resolution == "backup":
            item.setBackground(Qt.GlobalColor.lightBlue)
        elif resolution == "both":
            item.setBackground(Qt.GlobalColor.yellow)

    def _batch_resolve(self, resolution: str) -> None:
        """Apply resolution to all conflicts."""
        reply = QMessageBox.question(
            self,
            "Batch Resolution",
            f"Apply '{resolution}' resolution to all {len(self.conflicts)} conflicts?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for conflict in self.conflicts:
                self.resolutions[conflict.relative_path] = resolution

            # Update list item colors
            for i in range(self.conflict_list.count()):
                item = self.conflict_list.item(i)
                if resolution == "skip":
                    item.setBackground(Qt.GlobalColor.transparent)
                elif resolution == "master":
                    item.setBackground(Qt.GlobalColor.lightGreen)
                elif resolution == "backup":
                    item.setBackground(Qt.GlobalColor.lightBlue)
                elif resolution == "both":
                    item.setBackground(Qt.GlobalColor.yellow)

            QMessageBox.information(self, "Success", f"Applied '{resolution}' to all conflicts.")

    def _apply_resolutions(self) -> None:
        """Apply all selected resolutions and close dialog."""
        # Check if all conflicts have resolutions
        unresolved = [
            c.relative_path for c in self.conflicts if c.relative_path not in self.resolutions
        ]

        if unresolved:
            reply = QMessageBox.question(
                self,
                "Unresolved Conflicts",
                f"{len(unresolved)} conflicts have no resolution selected.\n\n"
                "They will be skipped. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply != QMessageBox.StandardButton.Yes:
                return

            # Set unresolved to skip
            for relative_path in unresolved:
                self.resolutions[relative_path] = "skip"

        self.accept()

    def get_resolutions(self) -> dict[str, str]:
        """
        Get resolution decisions for all conflicts.

        Returns:
            Dictionary mapping relative_path to resolution
            ("master"/"backup"/"skip"/"both")
        """
        return self.resolutions
