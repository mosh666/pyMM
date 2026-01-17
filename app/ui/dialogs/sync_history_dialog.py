"""
Sync History Dialog.

Displays synchronization operation history with detailed file lists
and export capabilities for audit trails.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
import json
import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.core.services.storage_group_service import StorageGroupService

logger = logging.getLogger(__name__)


class SyncHistoryDialog(QDialog):
    """Dialog for viewing sync operation history."""

    def __init__(
        self,
        storage_group_service: StorageGroupService,
        group_id: str,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize sync history dialog.

        Args:
            storage_group_service: Storage group service instance
            group_id: Storage group to show history for
            parent: Parent widget
        """
        super().__init__(parent)
        self.storage_group_service = storage_group_service
        self.group_id = group_id
        self.history_data: list[dict[str, object | None]] = []

        self.setWindowTitle("Sync History")
        self.resize(900, 600)

        self._create_ui()
        self._load_history()

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        layout = QVBoxLayout(self)

        # Top controls
        top_layout = QHBoxLayout()

        # Limit selector
        limit_label = QLabel("Show last:")
        top_layout.addWidget(limit_label)

        self.limit_combo = QComboBox()
        self.limit_combo.addItems(["50", "100", "200", "500", "All"])
        self.limit_combo.setCurrentIndex(0)
        self.limit_combo.currentIndexChanged.connect(self._load_history)
        top_layout.addWidget(self.limit_combo)

        top_layout.addStretch()

        # Export buttons
        self.export_csv_button = QPushButton("Export CSV")
        self.export_csv_button.clicked.connect(self._export_csv)
        top_layout.addWidget(self.export_csv_button)

        self.export_json_button = QPushButton("Export JSON")
        self.export_json_button.clicked.connect(self._export_json)
        top_layout.addWidget(self.export_json_button)

        layout.addLayout(top_layout)

        # Main splitter (operations table + details)
        splitter = QSplitter(Qt.Vertical)

        # Operations table
        operations_group = QGroupBox("Sync Operations")
        operations_layout = QVBoxLayout(operations_group)

        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(7)
        self.operations_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Operation",
                "Status",
                "Files",
                "Size",
                "Duration",
                "Started",
            ]
        )

        # Configure table
        header = self.operations_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.Stretch)

        self.operations_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.operations_table.setSelectionMode(QTableWidget.SingleSelection)
        self.operations_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.operations_table.itemSelectionChanged.connect(self._on_operation_selected)

        operations_layout.addWidget(self.operations_table)
        splitter.addWidget(operations_group)

        # Details panel
        details_group = QGroupBox("Operation Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("Select an operation to view details...")
        details_layout.addWidget(self.details_text)

        splitter.addWidget(details_group)

        # Set splitter sizes
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self._load_history)
        button_layout.addWidget(self.refresh_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setDefault(True)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def _load_history(self) -> None:
        """Load sync history from database."""
        try:
            # Get limit
            limit_text = self.limit_combo.currentText()
            limit = 999999 if limit_text == "All" else int(limit_text)

            # Load history
            self.history_data = self.storage_group_service.get_sync_history(
                self.group_id, limit=limit
            )

            # Populate table
            self.operations_table.setRowCount(len(self.history_data))

            for row_idx, operation in enumerate(self.history_data):
                # ID
                id_item = QTableWidgetItem(str(operation["id"]))
                self.operations_table.setItem(row_idx, 0, id_item)

                # Operation type
                op_type = operation["operation_type"]
                op_item = QTableWidgetItem(op_type.replace("_", " ").title())
                self.operations_table.setItem(row_idx, 1, op_item)

                # Status
                status = operation["status"]
                status_item = QTableWidgetItem(status.title())

                # Color code status
                if status == "completed":
                    status_item.setForeground(Qt.darkGreen)
                elif status == "failed":
                    status_item.setForeground(Qt.red)
                elif status == "cancelled":
                    status_item.setForeground(Qt.darkYellow)
                elif status == "in_progress":
                    status_item.setForeground(Qt.blue)

                self.operations_table.setItem(row_idx, 2, status_item)

                # Files copied
                files_item = QTableWidgetItem(str(operation["files_copied"]))
                files_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.operations_table.setItem(row_idx, 3, files_item)

                # Bytes copied
                bytes_copied_val = operation["bytes_copied"]
                bytes_copied: int = int(str(bytes_copied_val)) if bytes_copied_val else 0
                size_str = self._format_bytes(bytes_copied)
                size_item = QTableWidgetItem(size_str)
                size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.operations_table.setItem(row_idx, 4, size_item)

                # Duration
                duration_val = operation["duration_seconds"]
                duration: float | None = (
                    float(str(duration_val)) if duration_val is not None else None
                )
                duration_str = self._format_duration(duration) if duration is not None else "N/A"
                duration_item = QTableWidgetItem(duration_str)
                duration_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.operations_table.setItem(row_idx, 5, duration_item)

                # Started timestamp
                started_at = operation["started_at"]
                if started_at:
                    timestamp_str = started_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    timestamp_str = "Unknown"
                timestamp_item = QTableWidgetItem(timestamp_str)
                self.operations_table.setItem(row_idx, 6, timestamp_item)

            logger.info(f"Loaded {len(self.history_data)} sync operations")

        except Exception as e:
            logger.exception("Failed to load sync history")
            QMessageBox.critical(self, "Error", f"Failed to load sync history:\n\n{e!s}")

    def _on_operation_selected(self) -> None:  # noqa: C901 (detailed display logic)
        """Handle operation selection change."""
        selected_rows = self.operations_table.selectedItems()
        if not selected_rows:
            self.details_text.clear()
            return

        # Get selected row
        row_idx = self.operations_table.currentRow()
        if row_idx < 0 or row_idx >= len(self.history_data):
            return

        operation = self.history_data[row_idx]

        # Build details text
        details = []
        details.append("=" * 60)
        details.append(f"OPERATION #{operation['id']}")
        details.append("=" * 60)
        details.append("")

        # Basic info
        op_type_val = operation["operation_type"]
        op_type: str = str(op_type_val).replace("_", " ").title() if op_type_val else "Unknown"
        status_val = operation["status"]
        status: str = str(status_val).title() if status_val else "Unknown"
        details.append(f"Type:         {op_type}")
        details.append(f"Status:       {status}")
        details.append("")

        # Timestamps
        if operation["started_at"]:
            details.append(f"Started:      {operation['started_at'].strftime('%Y-%m-%d %H:%M:%S')}")
        if operation["completed_at"]:
            details.append(
                f"Completed:    {operation['completed_at'].strftime('%Y-%m-%d %H:%M:%S')}"
            )
        details.append("")

        # Paths
        details.append(f"Source:       {operation['source_path']}")
        details.append(f"Destination:  {operation['destination_path']}")
        details.append("")

        # Statistics
        details.append(f"Files Copied: {operation['files_copied']}")
        bytes_copied_val2 = operation["bytes_copied"]
        bytes_copied_int2: int = int(str(bytes_copied_val2)) if bytes_copied_val2 else 0
        details.append(f"Bytes Copied: {self._format_bytes(bytes_copied_int2)}")

        duration_val2 = operation["duration_seconds"]
        duration_float2: float | None = (
            float(str(duration_val2)) if duration_val2 is not None else None
        )
        if duration_float2 is not None:
            duration_str2 = self._format_duration(duration_float2)
            details.append(f"Duration:     {duration_str2}")

            # Calculate speed
            if duration_float2 > 0 and bytes_copied_int2 > 0:
                speed = bytes_copied_int2 / duration_float2
                details.append(f"Speed:        {self._format_bytes(int(speed))}/s")

        # Error message
        error_msg = operation["error_message"]
        if error_msg:
            details.append("")
            details.append("ERROR MESSAGE:")
            details.append(str(error_msg))

        # File list
        try:
            operation_id_val = operation["id"]
            operation_id_int2: int = int(str(operation_id_val)) if operation_id_val else 0
            files = self.storage_group_service.get_operation_files(operation_id_int2)
            if files:
                details.append("")
                details.append(f"FILES ({len(files)}):")
                details.append("-" * 60)
                for file_info in files:
                    size_str = self._format_bytes(file_info["file_size"])
                    details.append(f"  {file_info['relative_path']} ({size_str})")
        except Exception as e:
            logger.warning(f"Failed to load file list: {e}")

        self.details_text.setPlainText("\n".join(details))

    def _export_csv(self) -> None:
        """Export sync history to CSV file."""
        if not self.history_data:
            QMessageBox.information(self, "Export", "No data to export.")
            return

        # Ask for file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Sync History",
            f"sync_history_{self.group_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV Files (*.csv)",
        )

        if not file_path:
            return

        try:
            with file_path.open("w", newline="", encoding="utf-8") as csvfile:
                fieldnames = [
                    "ID",
                    "Operation Type",
                    "Status",
                    "Source Path",
                    "Destination Path",
                    "Files Copied",
                    "Bytes Copied",
                    "Duration (seconds)",
                    "Started At",
                    "Completed At",
                    "Error Message",
                ]

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for operation in self.history_data:
                    writer.writerow(
                        {
                            "ID": operation["id"],
                            "Operation Type": operation["operation_type"],
                            "Status": operation["status"],
                            "Source Path": operation["source_path"],
                            "Destination Path": operation["destination_path"],
                            "Files Copied": operation["files_copied"],
                            "Bytes Copied": operation["bytes_copied"],
                            "Duration (seconds)": operation["duration_seconds"] or "",
                            "Started At": operation["started_at"].isoformat()
                            if operation["started_at"]
                            else "",
                            "Completed At": operation["completed_at"].isoformat()
                            if operation["completed_at"]
                            else "",
                            "Error Message": operation["error_message"] or "",
                        }
                    )

            QMessageBox.information(
                self, "Success", f"Exported {len(self.history_data)} records to:\n{file_path}"
            )
            logger.info(f"Exported sync history to CSV: {file_path}")

        except Exception as e:
            logger.exception("Failed to export CSV")
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\n\n{e!s}")

    def _export_json(self) -> None:
        """Export sync history to JSON file."""
        if not self.history_data:
            QMessageBox.information(self, "Export", "No data to export.")
            return

        # Ask for file path
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Sync History",
            f"sync_history_{self.group_id}_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        try:
            # Convert datetime objects to ISO strings
            export_data = []
            for operation in self.history_data:
                op_dict = operation.copy()
                if op_dict["started_at"]:
                    op_dict["started_at"] = op_dict["started_at"].isoformat()
                if op_dict["completed_at"]:
                    op_dict["completed_at"] = op_dict["completed_at"].isoformat()
                export_data.append(op_dict)

            with file_path.open("w", encoding="utf-8") as jsonfile:
                json.dump(export_data, jsonfile, indent=2)

            QMessageBox.information(
                self, "Success", f"Exported {len(self.history_data)} records to:\n{file_path}"
            )
            logger.info(f"Exported sync history to JSON: {file_path}")

        except Exception as e:
            logger.exception("Failed to export JSON")
            QMessageBox.critical(self, "Error", f"Failed to export JSON:\n\n{e!s}")

    def _format_bytes(self, bytes_count: int) -> str:
        """Format bytes as human-readable string."""
        if bytes_count == 0:
            return "0 B"

        units = ["B", "KB", "MB", "GB", "TB"]
        unit_idx = 0
        size = float(bytes_count)

        while size >= 1024 and unit_idx < len(units) - 1:
            size /= 1024
            unit_idx += 1

        return f"{size:.2f} {units[unit_idx]}"

    def _format_duration(self, seconds: float) -> str:
        """Format duration as human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        if seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        hours = seconds / 3600
        return f"{hours:.2f}h"
