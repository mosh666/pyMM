"""
Notification System for Storage Group Operations.

Provides toast-style notifications for scheduled sync completions/failures.
"""

from __future__ import annotations

import logging

from PySide6.QtWidgets import QMessageBox, QWidget

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages notifications for storage group operations."""

    def __init__(self, parent_widget: QWidget | None = None) -> None:
        """
        Initialize notification manager.

        Args:
            parent_widget: Parent widget for message boxes
        """
        self.parent_widget = parent_widget

    def notify_sync_complete(
        self,
        group_id: str,
        status: str,
        message: str,
        show_dialog: bool = False,
    ) -> None:
        """
        Notify user of sync completion.

        Args:
            group_id: Storage group ID
            status: Status ("success", "error", "warning")
            message: Detailed message
            show_dialog: Show modal dialog instead of toast (for errors)
        """
        logger.info(f"Sync notification for {group_id}: {status} - {message}")

        if show_dialog or status == "error":
            # Show modal dialog for errors
            if status == "success":
                QMessageBox.information(
                    self.parent_widget,
                    "Sync Complete",
                    message,
                )
            elif status == "error":
                QMessageBox.critical(
                    self.parent_widget,
                    "Sync Failed",
                    message,
                )
            elif status == "warning":
                QMessageBox.warning(
                    self.parent_widget,
                    "Sync Warning",
                    message,
                )
        else:
            # Log success notification (toast would require additional UI framework)
            logger.info(f"Scheduled sync completed for group {group_id}")

    def notify_schedule_active(self, project_name: str, schedule_info: str) -> None:
        """
        Notify that a schedule is now active.

        Args:
            project_name: Name of project
            schedule_info: Schedule description
        """
        logger.info(f"Schedule activated for {project_name}: {schedule_info}")


# Singleton instance
_notification_manager: NotificationManager | None = None


def get_notification_manager(parent_widget: QWidget | None = None) -> NotificationManager:
    """
    Get or create notification manager singleton.

    Args:
        parent_widget: Parent widget for first initialization

    Returns:
        NotificationManager instance
    """
    global _notification_manager  # noqa: PLW0603 (singleton pattern)

    if _notification_manager is None:
        _notification_manager = NotificationManager(parent_widget)

    return _notification_manager
