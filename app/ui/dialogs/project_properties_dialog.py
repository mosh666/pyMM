"""
Project Properties Dialog.

Provides UI for viewing and editing project settings including:
- General information (name, description, path)
- Storage Group assignment for redundancy
- Project statistics and metadata
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.core.services.storage_group_service import StorageGroupService
    from app.core.services.storage_service import StorageService
    from app.models.project import Project
    from app.services.project_service import ProjectService

logger = logging.getLogger(__name__)


class ProjectPropertiesDialog(QDialog):
    """Dialog for viewing and editing project properties."""

    def __init__(
        self,
        project: Project,
        project_service: ProjectService,
        storage_service: StorageService | None = None,
        storage_group_service: StorageGroupService | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize project properties dialog.

        Args:
            project: Project to display/edit
            project_service: ProjectService for saving changes
            storage_service: Optional StorageService for drive detection
            storage_group_service: Optional StorageGroupService for group assignment
            parent: Parent widget
        """
        super().__init__(parent)
        self.project = project
        self.project_service = project_service
        self.storage_service = storage_service
        self.storage_group_service = storage_group_service

        self.setWindowTitle(f"Project Properties - {project.name}")
        self.setMinimumSize(600, 500)
        self._init_ui()
        self._load_data()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tabs = QTabWidget()

        # General tab
        self.general_tab = self._create_general_tab()
        self.tabs.addTab(self.general_tab, "General")

        # Storage tab (only if storage_group_service available)
        if self.storage_group_service:
            self.storage_tab = self._create_storage_tab()
            self.tabs.addTab(self.storage_tab, "Storage")

        # Metadata tab
        self.metadata_tab = self._create_metadata_tab()
        self.tabs.addTab(self.metadata_tab, "Metadata")

        layout.addWidget(self.tabs)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_button)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._ok_clicked)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _create_general_tab(self) -> QWidget:
        """Create the General tab with basic project information."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Basic Information
        info_group = QGroupBox("Basic Information")
        info_layout = QFormLayout(info_group)

        self.name_edit = QLineEdit()
        self.name_edit.setText(self.project.name)
        info_layout.addRow("Name:", self.name_edit)

        path_label = QLabel(str(self.project.path))
        path_label.setWordWrap(True)
        path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        info_layout.addRow("Location:", path_label)

        exists_label = QLabel("✓ Exists" if self.project.exists else "✗ Not Found")
        exists_label.setStyleSheet("color: #2E7D32;" if self.project.exists else "color: #D32F2F;")
        info_layout.addRow("Status:", exists_label)

        self.description_edit = QTextEdit()
        self.description_edit.setPlainText(self.project.description or "")
        self.description_edit.setMaximumHeight(100)
        info_layout.addRow("Description:", self.description_edit)

        layout.addWidget(info_group)

        # Template Information
        template_group = QGroupBox("Template Information")
        template_layout = QFormLayout(template_group)

        template_name = self.project.template_name or "None"
        template_label = QLabel(template_name)
        template_layout.addRow("Template:", template_label)

        template_version = self.project.template_version or "N/A"
        version_label = QLabel(template_version)
        template_layout.addRow("Version:", version_label)

        layout.addWidget(template_group)

        layout.addStretch()
        return widget

    def _create_storage_tab(self) -> QWidget:
        """Create the Storage tab for Storage Group assignment."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(
            "Storage Groups provide Master/Backup drive redundancy for this project.\n"
            "Assign a group to enable automatic failover when drives are unavailable."
        )
        header.setWordWrap(True)
        header.setStyleSheet("padding: 10px; background-color: #E3F2FD;")
        layout.addWidget(header)

        # Current Assignment
        assignment_group = QGroupBox("Storage Group Assignment")
        assignment_layout = QFormLayout(assignment_group)

        # Group selection dropdown
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self._on_group_selection_changed)
        assignment_layout.addRow("Assigned Group:", self.group_combo)

        # Current status display
        self.group_status_label = QLabel()
        self.group_status_label.setWordWrap(True)
        assignment_layout.addRow("Status:", self.group_status_label)

        # Drive information
        self.master_drive_label = QLabel()
        self.master_drive_label.setWordWrap(True)
        assignment_layout.addRow("Master Drive:", self.master_drive_label)

        self.backup_drive_label = QLabel()
        self.backup_drive_label.setWordWrap(True)
        assignment_layout.addRow("Backup Drive:", self.backup_drive_label)

        layout.addWidget(assignment_group)

        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Create Group from Project button
        self.create_group_button = QPushButton("Create Storage Group from Current Drive")
        self.create_group_button.clicked.connect(self._create_group_from_project)
        self.create_group_button.setToolTip(
            "Automatically create a new Storage Group using the drive this project is on"
        )
        actions_layout.addWidget(self.create_group_button)

        # Sync to Backup button
        self.sync_button = QPushButton("Sync Project to Backup Drive")
        self.sync_button.clicked.connect(self._sync_to_backup)
        self.sync_button.setEnabled(False)
        self.sync_button.setToolTip("Manually sync this project's files to the Backup drive")
        actions_layout.addWidget(self.sync_button)

        # Check Conflicts button
        self.check_conflicts_button = QPushButton("Check & Resolve Conflicts")
        self.check_conflicts_button.clicked.connect(self._check_conflicts)
        self.check_conflicts_button.setEnabled(False)
        self.check_conflicts_button.setToolTip(
            "Detect and resolve sync conflicts between Master and Backup"
        )
        actions_layout.addWidget(self.check_conflicts_button)

        # Configure Schedule button
        self.schedule_button = QPushButton("Configure Scheduled Sync...")
        self.schedule_button.clicked.connect(self._configure_schedule)
        self.schedule_button.setEnabled(False)
        self.schedule_button.setToolTip("Set up automatic scheduled syncs")
        actions_layout.addWidget(self.schedule_button)

        # Schedule status label
        self.schedule_status_label = QLabel()
        self.schedule_status_label.setWordWrap(True)
        actions_layout.addWidget(self.schedule_status_label)

        # Real-time sync toggle
        self.realtime_sync_checkbox = QCheckBox("Enable Real-Time Sync")
        self.realtime_sync_checkbox.setEnabled(False)
        self.realtime_sync_checkbox.setToolTip(
            "Automatically sync file changes to Backup drive in real-time (500ms debounce)"
        )
        self.realtime_sync_checkbox.toggled.connect(self._on_realtime_sync_toggled)
        actions_layout.addWidget(self.realtime_sync_checkbox)

        # Real-time sync status
        self.realtime_status_label = QLabel()
        self.realtime_status_label.setWordWrap(True)
        actions_layout.addWidget(self.realtime_status_label)

        # View Sync History button
        self.history_button = QPushButton("View Sync History...")
        self.history_button.clicked.connect(self._view_sync_history)
        self.history_button.setEnabled(False)
        self.history_button.setToolTip("View sync operation history and logs")
        actions_layout.addWidget(self.history_button)

        # Advanced Options button
        self.advanced_options_button = QPushButton("Advanced Sync Options...")
        self.advanced_options_button.clicked.connect(self._configure_advanced_options)
        self.advanced_options_button.setEnabled(False)
        self.advanced_options_button.setToolTip(
            "Configure bandwidth throttling, encryption, compression, and parallel copying"
        )
        actions_layout.addWidget(self.advanced_options_button)

        # Manage Groups button
        manage_button = QPushButton("Manage Storage Groups...")
        manage_button.clicked.connect(self._manage_storage_groups)
        actions_layout.addWidget(manage_button)

        layout.addWidget(actions_group)

        layout.addStretch()
        return widget

    def _create_metadata_tab(self) -> QWidget:
        """Create the Metadata tab with timestamps and history."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Timestamps
        timestamps_group = QGroupBox("Timestamps")
        timestamps_layout = QFormLayout(timestamps_group)

        created_label = QLabel(self.project.created.strftime("%Y-%m-%d %H:%M:%S"))
        timestamps_layout.addRow("Created:", created_label)

        modified_label = QLabel(self.project.modified.strftime("%Y-%m-%d %H:%M:%S"))
        timestamps_layout.addRow("Modified:", modified_label)

        layout.addWidget(timestamps_group)

        # Migration History
        if self.project.migration_history:
            history_group = QGroupBox("Migration History")
            history_layout = QVBoxLayout(history_group)

            history_text = QTextEdit()
            history_text.setReadOnly(True)
            history_text.setMaximumHeight(150)

            history_content = []
            for entry in self.project.migration_history:
                timestamp = entry.get("timestamp", "Unknown")
                from_version = entry.get("from_version", "?")
                to_version = entry.get("to_version", "?")
                history_content.append(f"{timestamp}: {from_version} → {to_version}")

            history_text.setPlainText("\n".join(history_content))
            history_layout.addWidget(history_text)

            layout.addWidget(history_group)

        # Pending Migration
        if self.project.pending_migration:
            pending_group = QGroupBox("Pending Migration")
            pending_layout = QFormLayout(pending_group)

            target = self.project.pending_migration.get("target_version", "Unknown")
            pending_layout.addRow("Target Version:", QLabel(target))

            reason = self.project.pending_migration.get("reason", "Not specified")
            reason_label = QLabel(reason)
            reason_label.setWordWrap(True)
            pending_layout.addRow("Reason:", reason_label)

            layout.addWidget(pending_group)

        layout.addStretch()
        return widget

    def _load_data(self) -> None:
        """Load data into the UI fields."""
        if not self.storage_group_service:
            return

        # Populate group combo box
        self.group_combo.clear()
        self.group_combo.addItem("(None)", None)

        groups = self.storage_group_service.list_groups()
        for group in groups:
            self.group_combo.addItem(group.name, group.id)

        # Select current group if assigned
        if self.project.storage_group_id:
            for i in range(self.group_combo.count()):
                if self.group_combo.itemData(i) == self.project.storage_group_id:
                    self.group_combo.setCurrentIndex(i)
                    break

        self._update_group_status()

    def _on_group_selection_changed(self, _index: int) -> None:
        """Handle storage group selection change."""
        self._update_group_status()

    def _update_group_status(self) -> None:
        """Update the storage group status display."""
        if not self.storage_group_service:
            return

        group_id = self.group_combo.currentData()

        if not group_id:
            # No group assigned
            self.group_status_label.setText("Not assigned to any Storage Group")
            self.group_status_label.setStyleSheet("color: gray;")
            self.master_drive_label.setText("—")
            self.backup_drive_label.setText("—")
            self.sync_button.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.schedule_status_label.setText("")
            self.realtime_sync_checkbox.setEnabled(False)
            self.realtime_sync_checkbox.setChecked(False)
            self.realtime_status_label.setText("")
            return

        # Get group details
        group = self.storage_group_service.get_group(group_id)
        if not group:
            self.group_status_label.setText("⚠ Group not found")
            self.group_status_label.setStyleSheet("color: #D32F2F;")
            self.master_drive_label.setText("—")
            self.backup_drive_label.setText("—")
            self.sync_button.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.schedule_status_label.setText("")
            self.realtime_sync_checkbox.setEnabled(False)
            self.realtime_sync_checkbox.setChecked(False)
            self.realtime_status_label.setText("")
            self.history_button.setEnabled(False)
            self.advanced_options_button.setEnabled(False)
            return

        # Check drive connectivity
        master_info = self.storage_group_service.find_drive_info(group.master_drive)
        backup_info = self.storage_group_service.find_drive_info(group.backup_drive)

        # Update status
        if master_info and backup_info:
            self.group_status_label.setText("✓ Both drives connected")
            self.group_status_label.setStyleSheet("color: #2E7D32;")
            self.sync_button.setEnabled(True)
            self.check_conflicts_button.setEnabled(True)
            self.schedule_button.setEnabled(True)
            self.realtime_sync_checkbox.setEnabled(True)
            self.history_button.setEnabled(True)
            self.advanced_options_button.setEnabled(True)
        elif master_info:
            self.group_status_label.setText("⚠ Only Master drive connected")
            self.group_status_label.setStyleSheet("color: #F57C00;")
            self.sync_button.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.realtime_sync_checkbox.setEnabled(False)
            self.history_button.setEnabled(True)  # Can still view history
            self.advanced_options_button.setEnabled(True)  # Can still configure options
        elif backup_info:
            self.group_status_label.setText("⚠ Only Backup drive connected")
            self.group_status_label.setStyleSheet("color: #F57C00;")
            self.sync_button.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.realtime_sync_checkbox.setEnabled(False)
            self.history_button.setEnabled(True)  # Can still view history
            self.advanced_options_button.setEnabled(True)  # Can still configure options
        else:
            self.group_status_label.setText("✗ No drives connected")
            self.group_status_label.setStyleSheet("color: #D32F2F;")
            self.sync_button.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.realtime_sync_checkbox.setEnabled(False)
            self.check_conflicts_button.setEnabled(False)
            self.schedule_button.setEnabled(False)
            self.history_button.setEnabled(True)  # Can still view history
            self.advanced_options_button.setEnabled(True)  # Can still configure options

        # Update drive labels
        if master_info:
            self.master_drive_label.setText(f"✓ {master_info.label} ({master_info.drive_letter})")
            self.master_drive_label.setStyleSheet("color: #2E7D32;")
        else:
            self.master_drive_label.setText(f"✗ {group.master_drive.label} (Not Connected)")
            self.master_drive_label.setStyleSheet("color: #D32F2F;")

        # Update schedule status
        self._update_schedule_status()

        # Update real-time sync status
        self._update_realtime_sync_status()

        if backup_info:
            self.backup_drive_label.setText(f"✓ {backup_info.label} ({backup_info.drive_letter})")
            self.backup_drive_label.setStyleSheet("color: #2E7D32;")
        else:
            self.backup_drive_label.setText(f"✗ {group.backup_drive.label} (Not Connected)")
            self.backup_drive_label.setStyleSheet("color: #D32F2F;")

    def _create_group_from_project(self) -> None:
        """Create a new Storage Group using the project's current drive as Master."""
        if not self.storage_service or not self.storage_group_service:
            QMessageBox.warning(self, "Service Unavailable", "Storage services are not available.")
            return

        # Get the drive containing this project
        drive_info = self.storage_service.get_drive_info(self.project.path)

        if not drive_info:
            QMessageBox.warning(
                self, "Drive Not Found", "Could not detect the drive for this project."
            )
            return

        if not drive_info.is_removable:
            QMessageBox.warning(
                self,
                "Not Removable",
                "Storage Groups require removable drives.\n\n"
                f"The project is on a fixed drive: {drive_info.label} ({drive_info.drive_letter})",
            )
            return

        # Launch storage group dialog with pre-filled Master drive
        from app.ui.dialogs.storage_group_dialog import StorageGroupEditorDialog

        dialog = StorageGroupEditorDialog(
            self.storage_service, self.storage_group_service, parent=self
        )

        # Pre-fill the master drive
        dialog.master_drive = drive_info
        dialog._update_drive_labels()  # noqa: SLF001 (internal dialog method)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            name, master, backup, description = dialog.get_group_data()

            try:
                group = self.storage_group_service.create_group(name, master, backup, description)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Storage group '{name}' created successfully.\n\n"
                    "The new group has been automatically assigned to this project.",
                )

                # Reload groups and select the new one
                self._load_data()

                # Auto-assign the new group
                for i in range(self.group_combo.count()):
                    if self.group_combo.itemData(i) == group.id:
                        self.group_combo.setCurrentIndex(i)
                        break

            except Exception as e:
                logger.exception("Failed to create storage group")
                QMessageBox.critical(self, "Error", f"Failed to create storage group:\n\n{e!s}")

    def _sync_to_backup(self) -> None:
        """Manually sync the project to the Backup drive."""
        group_id = self.group_combo.currentData()
        if not group_id:
            QMessageBox.warning(self, "No Group", "Please assign a Storage Group first.")
            return

        # Import here to avoid circular dependency
        from app.ui.dialogs.sync_progress_dialog import SyncProgressDialog

        assert self.storage_group_service is not None
        dialog = SyncProgressDialog(
            self.storage_group_service,
            group_id,
            self.project.path,
            parent=self,
        )
        dialog.exec()

        # Refresh status after sync
        self._update_group_status()

    def _check_conflicts(self) -> None:
        """Check for conflicts and launch resolution dialog."""
        group_id = self.group_combo.currentData()
        if not group_id:
            QMessageBox.warning(self, "No Group", "Please assign a Storage Group first.")
            return

        try:
            # Detect conflicts
            assert self.storage_group_service is not None
            conflicts = self.storage_group_service.detect_conflicts(group_id, self.project.path)

            if not conflicts:
                QMessageBox.information(
                    self,
                    "No Conflicts",
                    "No sync conflicts detected.\n\nMaster and Backup drives are in sync.",
                )
                return

            # Get drive roots for conflict resolution
            group = self.storage_group_service.get_group(group_id)
            if group is None:
                QMessageBox.critical(self, "Error", "Storage group not found.")
                return
            master_info = self.storage_group_service.find_drive_info(group.master_drive)
            backup_info = self.storage_group_service.find_drive_info(group.backup_drive)

            if not master_info or not backup_info:
                QMessageBox.critical(
                    self,
                    "Drive Error",
                    "Both Master and Backup drives must be connected to resolve conflicts.",
                )
                return

            # Launch conflict resolution dialog
            from app.ui.dialogs.conflict_resolution_dialog import ConflictResolutionDialog

            conflict_dialog = ConflictResolutionDialog(
                conflicts,
                Path(master_info.drive_letter),
                Path(backup_info.drive_letter),
                parent=self,
            )

            if conflict_dialog.exec() == QDialog.DialogCode.Accepted:
                # Apply resolutions
                resolutions = conflict_dialog.get_resolutions()

                assert self.storage_group_service is not None
                result = self.storage_group_service.resolve_conflicts(group_id, resolutions)

                # Show summary
                message = (
                    f"Conflict Resolution Summary:\n\n"
                    f"✓ Resolved: {result['resolved']}\n"
                    f"⊘ Skipped: {result['skipped']}\n"
                    f"✗ Failed: {result['failed']}"
                )

                if result["errors"]:
                    message += "\n\nErrors:\n" + "\n".join(result["errors"][:5])
                    if len(result["errors"]) > 5:
                        message += f"\n...and {len(result['errors']) - 5} more"

                QMessageBox.information(self, "Resolution Complete", message)

                # Refresh status
                self._update_group_status()

        except Exception as e:
            logger.exception("Failed to check conflicts")
            QMessageBox.critical(self, "Error", f"Failed to check conflicts:\n\n{e!s}")

    def _configure_schedule(self) -> None:
        """Configure scheduled sync for this project."""
        group_id = self.group_combo.currentData()
        if not group_id:
            QMessageBox.warning(self, "No Group", "Please assign a Storage Group first.")
            return

        from app.ui.dialogs.sync_schedule_dialog import SyncScheduleDialog

        dialog = SyncScheduleDialog(
            current_schedule=self.project.sync_schedule,
            parent=self,
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Get new schedule configuration
            schedule_config = dialog.get_schedule_config()
            self.project.sync_schedule = schedule_config

            # Update status display
            self._update_schedule_status()

            QMessageBox.information(
                self,
                "Schedule Updated",
                "Sync schedule has been updated.\n\n"
                "Changes will take effect when you save the project.",
            )

    def _update_schedule_status(self) -> None:
        """Update the schedule status label."""
        if not self.project.sync_schedule or not self.project.sync_schedule.get("enabled"):
            self.schedule_status_label.setText("📅 Scheduled Sync: Disabled")
            self.schedule_status_label.setStyleSheet("color: gray;")
            return

        schedule_type = self.project.sync_schedule.get("type")

        if schedule_type == "interval":
            interval = self.project.sync_schedule.get("interval_minutes", 60)
            status_text = f"📅 Scheduled Sync: Every {interval} minutes"
        elif schedule_type == "cron":
            cron_expr = self.project.sync_schedule.get("cron_expression", "")
            status_text = f"📅 Scheduled Sync: {cron_expr}"
        else:
            status_text = "📅 Scheduled Sync: Enabled"

        self.schedule_status_label.setText(status_text)
        self.schedule_status_label.setStyleSheet("color: #1976D2; font-weight: bold;")

    def _update_realtime_sync_status(self) -> None:
        """Update the real-time sync status."""
        # Update checkbox state
        self.realtime_sync_checkbox.blockSignals(True)
        self.realtime_sync_checkbox.setChecked(self.project.realtime_sync_enabled)
        self.realtime_sync_checkbox.blockSignals(False)

        # Update status label
        if self.project.realtime_sync_enabled and self.project.realtime_sync_watch_id:
            self.realtime_status_label.setText("⚡ Real-Time Sync: Active")
            self.realtime_status_label.setStyleSheet("color: #388E3C; font-weight: bold;")
        else:
            self.realtime_status_label.setText("⚡ Real-Time Sync: Disabled")
            self.realtime_status_label.setStyleSheet("color: gray;")

    def _on_realtime_sync_toggled(self, checked: bool) -> None:
        """Handle real-time sync checkbox toggle."""
        group_id = self.group_combo.currentData()
        if not group_id:
            self.realtime_sync_checkbox.setChecked(False)
            return

        try:
            assert self.storage_group_service is not None
            if checked:
                # Enable real-time sync
                watch_id = self.storage_group_service.enable_realtime_sync(
                    group_id=group_id,
                    watch_path=self.project.path,
                    debounce_seconds=0.5,
                )

                self.project.realtime_sync_enabled = True
                self.project.realtime_sync_watch_id = watch_id

                logger.info(f"Enabled real-time sync for project: {watch_id}")

            else:
                # Disable real-time sync
                if self.project.realtime_sync_watch_id:
                    self.storage_group_service.disable_realtime_sync(
                        self.project.realtime_sync_watch_id
                    )

                self.project.realtime_sync_enabled = False
                self.project.realtime_sync_watch_id = None

                logger.info("Disabled real-time sync for project")

            # Update status
            self._update_realtime_sync_status()

            QMessageBox.information(
                self,
                "Real-Time Sync",
                f"Real-time sync has been {'enabled' if checked else 'disabled'}.\n\n"
                "Changes will take effect when you save the project.",
            )

        except Exception as e:
            logger.exception("Failed to toggle real-time sync")
            QMessageBox.critical(self, "Error", f"Failed to toggle real-time sync:\n\n{e!s}")
            # Revert checkbox
            self.realtime_sync_checkbox.blockSignals(True)
            self.realtime_sync_checkbox.setChecked(not checked)
            self.realtime_sync_checkbox.blockSignals(False)

    def _view_sync_history(self) -> None:
        """Open the Sync History dialog."""
        group_id = self.group_combo.currentData()
        if not group_id:
            return

        from app.ui.dialogs.sync_history_dialog import SyncHistoryDialog

        assert self.storage_group_service is not None
        dialog = SyncHistoryDialog(
            self.storage_group_service,
            group_id,
            parent=self,
        )
        dialog.exec()

    def _configure_advanced_options(self) -> None:
        """Open the Advanced Sync Options dialog."""
        from app.core.sync.advanced_sync_options import AdvancedSyncOptions
        from app.ui.dialogs.advanced_sync_options_dialog import AdvancedSyncOptionsDialog

        # Load existing options or create new
        if self.project.advanced_sync_options:
            options = AdvancedSyncOptions.from_dict(self.project.advanced_sync_options)
        else:
            options = AdvancedSyncOptions()

        dialog = AdvancedSyncOptionsDialog(options, parent=self)
        if dialog.exec():
            # Save options to project
            self.project.advanced_sync_options = dialog.get_options().to_dict()
            logger.info("Updated advanced sync options for project")

    def _manage_storage_groups(self) -> None:
        """Open the Storage Groups management dialog."""
        from app.ui.dialogs.storage_group_dialog import StorageGroupDialog

        assert self.storage_service is not None
        assert self.storage_group_service is not None
        dialog = StorageGroupDialog(self.storage_service, self.storage_group_service, parent=self)
        dialog.exec()

        # Reload groups after management
        self._load_data()

    def _apply_changes(self) -> None:
        """Apply changes to the project."""
        # Update project fields
        new_name = self.name_edit.text().strip()
        if new_name and new_name != self.project.name:
            self.project.name = new_name

        new_description = self.description_edit.toPlainText().strip()
        self.project.description = new_description if new_description else None

        # Update storage group assignment
        if self.storage_group_service:
            new_group_id = self.group_combo.currentData()
            if new_group_id != self.project.storage_group_id:
                self.project.storage_group_id = new_group_id
                logger.info(
                    f"Project '{self.project.name}' storage group changed to: {new_group_id or 'None'}"
                )

        # Save project
        try:
            self.project_service.save_project(self.project)
            QMessageBox.information(self, "Success", "Project properties saved successfully.")
        except Exception as e:
            logger.exception("Failed to save project")
            QMessageBox.critical(self, "Error", f"Failed to save project properties:\n\n{e!s}")

    def _ok_clicked(self) -> None:
        """Handle OK button click."""
        self._apply_changes()
        self.accept()
