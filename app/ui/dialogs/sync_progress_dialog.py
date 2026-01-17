"""
Sync Progress Dialog.

Displays real-time progress for file synchronization operations between
Master and Backup drives with cancellation support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
import logging
from pathlib import Path
from threading import Event, Thread
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.core.services.storage_group_service import StorageGroupService

logger = logging.getLogger(__name__)


@dataclass
class SyncProgress:
    """Progress information for sync operations."""

    current_file: str = ""
    files_completed: int = 0
    files_total: int = 0
    bytes_completed: int = 0
    bytes_total: int = 0
    current_speed: float = 0.0  # bytes per second
    errors: list[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    is_cancelled: bool = False
    is_complete: bool = False


class SyncProgressDialog(QDialog):
    """Dialog displaying file synchronization progress."""

    # Signal emitted when sync completes
    sync_completed = Signal(bool, str)  # (success, message)

    def __init__(
        self,
        storage_group_service: StorageGroupService,
        group_id: str,
        source_path: Path,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize sync progress dialog.

        Args:
            storage_group_service: StorageGroupService for sync operations
            group_id: Storage group identifier
            source_path: Path to sync from Master
            parent: Parent widget
        """
        super().__init__(parent)
        self.storage_group_service = storage_group_service
        self.group_id = group_id
        self.source_path = source_path

        self.progress = SyncProgress()
        self.cancel_event = Event()
        self.sync_thread: Thread | None = None

        self.setWindowTitle("Syncing to Backup Drive")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self._init_ui()

        # Start sync operation
        self._start_sync()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Synchronizing project files to Backup drive...")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Current file
        self.current_file_label = QLabel("Preparing...")
        self.current_file_label.setWordWrap(True)
        self.current_file_label.setStyleSheet("padding: 5px;")
        layout.addWidget(self.current_file_label)

        # File progress bar
        self.file_progress = QProgressBar()
        self.file_progress.setFormat("File: %p%")
        layout.addWidget(self.file_progress)

        # Overall progress bar
        self.overall_progress = QProgressBar()
        self.overall_progress.setFormat("Overall: %p%")
        layout.addWidget(self.overall_progress)

        # Statistics
        stats_layout = QHBoxLayout()

        self.files_label = QLabel("Files: 0 / 0")
        stats_layout.addWidget(self.files_label)

        self.speed_label = QLabel("Speed: 0 MB/s")
        stats_layout.addWidget(self.speed_label)

        self.eta_label = QLabel("ETA: Calculating...")
        stats_layout.addWidget(self.eta_label)

        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Log output
        log_label = QLabel("Operation Log:")
        layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_button)

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setEnabled(False)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_ui)
        self.update_timer.start(100)  # Update every 100ms

    def _start_sync(self) -> None:
        """Start the sync operation in a background thread."""
        self.sync_thread = Thread(target=self._run_sync, daemon=True)
        self.sync_thread.start()

    def _run_sync(self) -> None:
        """Execute the sync operation (runs in background thread)."""
        try:
            self._log("Starting synchronization...")
            self._log(f"Source: {self.source_path}")

            # Progress callback
            def progress_callback(progress: SyncProgress) -> None:
                """Update UI with sync progress.

                Args:
                    progress: Current sync progress information.
                """
                self.progress = progress

            # Execute sync
            self.storage_group_service.sync_to_backup(
                self.group_id,
                self.source_path,
                progress_callback=progress_callback,
                cancel_event=self.cancel_event,
            )

            if self.progress.is_cancelled:
                self._log("\n⚠ Sync cancelled by user")
                self.sync_completed.emit(False, "Sync cancelled by user")
            else:
                self.progress.is_complete = True
                duration = (datetime.now(UTC) - self.progress.start_time).total_seconds()
                self._log(f"\n✓ Sync completed successfully in {duration:.1f} seconds")
                self._log(f"Files synced: {self.progress.files_completed}")
                self._log(f"Data transferred: {self.progress.bytes_completed / (1024**2):.2f} MB")

                if self.progress.errors:
                    self._log(f"\n⚠ Errors encountered: {len(self.progress.errors)}")
                    for error in self.progress.errors[:10]:  # Show first 10 errors
                        self._log(f"  • {error}")

                self.sync_completed.emit(True, "Sync completed successfully")

        except Exception as e:
            logger.exception("Sync operation failed")
            self.progress.is_complete = True
            self.progress.errors.append(str(e))
            self._log(f"\n✗ Sync failed: {e}")
            self.sync_completed.emit(False, f"Sync failed: {e}")

    def _update_ui(self) -> None:  # noqa: C901 (UI update logic)
        """Update UI with current progress (called from timer)."""
        # Current file
        if self.progress.current_file:
            display_name = Path(self.progress.current_file).name
            self.current_file_label.setText(f"Current: {display_name}")

        # Files progress
        if self.progress.files_total > 0:
            files_percent = int((self.progress.files_completed / self.progress.files_total) * 100)
            self.file_progress.setValue(files_percent)
            self.files_label.setText(
                f"Files: {self.progress.files_completed} / {self.progress.files_total}"
            )

        # Overall progress (bytes)
        if self.progress.bytes_total > 0:
            bytes_percent = int((self.progress.bytes_completed / self.progress.bytes_total) * 100)
            self.overall_progress.setValue(bytes_percent)

        # Speed
        if self.progress.current_speed > 0:
            speed_mb = self.progress.current_speed / (1024**2)
            self.speed_label.setText(f"Speed: {speed_mb:.2f} MB/s")

        # ETA
        if (
            self.progress.current_speed > 0
            and self.progress.bytes_total > self.progress.bytes_completed
        ):
            remaining_bytes = self.progress.bytes_total - self.progress.bytes_completed
            eta_seconds = remaining_bytes / self.progress.current_speed
            if eta_seconds < 60:
                self.eta_label.setText(f"ETA: {eta_seconds:.0f} seconds")
            elif eta_seconds < 3600:
                self.eta_label.setText(f"ETA: {eta_seconds / 60:.1f} minutes")
            else:
                self.eta_label.setText(f"ETA: {eta_seconds / 3600:.1f} hours")

        # Completion state
        if self.progress.is_complete:
            self.update_timer.stop()
            self.cancel_button.setEnabled(False)
            self.close_button.setEnabled(True)
            self.close_button.setDefault(True)

            if self.progress.errors:
                self.current_file_label.setText("⚠ Completed with errors")
                self.current_file_label.setStyleSheet("color: #F57C00; padding: 5px;")
            elif self.progress.is_cancelled:
                self.current_file_label.setText("⚠ Cancelled")
                self.current_file_label.setStyleSheet("color: #F57C00; padding: 5px;")
            else:
                self.current_file_label.setText("✓ Completed successfully")
                self.current_file_label.setStyleSheet("color: #2E7D32; padding: 5px;")

    def _log(self, message: str) -> None:
        """Add a message to the log output."""
        timestamp = datetime.now(UTC).strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        reply = QPushButton().question(
            self,
            "Cancel Sync",
            "Are you sure you want to cancel the sync operation?\n\n"
            "Partially synced files will be kept.",
        )

        if reply == QPushButton.StandardButton.Yes:
            self._log("Cancelling sync operation...")
            self.cancel_event.set()
            self.progress.is_cancelled = True
            self.cancel_button.setEnabled(False)

    def closeEvent(self, event: object) -> None:  # noqa: N802 (Qt override)
        """Handle dialog close event."""
        if not self.progress.is_complete:
            event.ignore()
            self._on_cancel()
        else:
            self.update_timer.stop()
            event.accept()
