"""
Scheduled Synchronization Manager.

Provides automated scheduled syncs between Master and Backup drives using APScheduler.
Supports interval-based and cron-based triggers with notification callbacks.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
import platform as _platform  # noqa: F401  # Prevent shadowing (Python 3.12)
from typing import TYPE_CHECKING

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from app.core.services.storage_group_service import StorageGroupService

logger = logging.getLogger(__name__)


@dataclass
class SyncSchedule:
    """Represents a sync schedule configuration."""

    schedule_id: str
    group_id: str
    project_path: Path
    schedule_type: str  # "interval" or "cron"
    interval_minutes: int | None = None  # For interval type
    cron_expression: str | None = None  # For cron type
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None


class ScheduledSyncManager:
    """Manages scheduled synchronization operations."""

    def __init__(
        self,
        storage_group_service: StorageGroupService,
        notification_callback: Callable[[str, str, str], None] | None = None,
    ) -> None:
        """
        Initialize scheduled sync manager.

        Args:
            storage_group_service: StorageGroupService for sync operations
            notification_callback: Optional callback(group_id, status, message) for notifications
        """
        self.storage_group_service = storage_group_service
        self.notification_callback = notification_callback
        self.scheduler = BackgroundScheduler()
        self.schedules: dict[str, SyncSchedule] = {}

        logger.info("ScheduledSyncManager initialized")

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown the scheduler.

        Args:
            wait: Wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler stopped")

    def add_interval_schedule(
        self,
        schedule_id: str,
        group_id: str,
        project_path: Path,
        interval_minutes: int,
    ) -> SyncSchedule:
        """
        Add an interval-based sync schedule.

        Args:
            schedule_id: Unique identifier for this schedule
            group_id: Storage group ID
            project_path: Project path to sync
            interval_minutes: Sync interval in minutes

        Returns:
            SyncSchedule object

        Raises:
            ValueError: If schedule_id already exists
        """
        if schedule_id in self.schedules:
            raise ValueError(f"Schedule with ID '{schedule_id}' already exists")

        schedule = SyncSchedule(
            schedule_id=schedule_id,
            group_id=group_id,
            project_path=project_path,
            schedule_type="interval",
            interval_minutes=interval_minutes,
        )

        # Add job to scheduler
        trigger = IntervalTrigger(minutes=interval_minutes)
        self.scheduler.add_job(
            func=self._execute_sync,
            trigger=trigger,
            id=schedule_id,
            args=(schedule_id,),
            name=f"Sync {group_id} every {interval_minutes}m",
        )

        self.schedules[schedule_id] = schedule

        # Update next_run
        job = self.scheduler.get_job(schedule_id)
        if job:
            schedule.next_run = job.next_run_time

        logger.info(f"Added interval schedule: {schedule_id} ({interval_minutes} minutes)")

        return schedule

    def add_cron_schedule(
        self,
        schedule_id: str,
        group_id: str,
        project_path: Path,
        cron_expression: str,
    ) -> SyncSchedule:
        """
        Add a cron-based sync schedule.

        Args:
            schedule_id: Unique identifier for this schedule
            group_id: Storage group ID
            project_path: Project path to sync
            cron_expression: Cron expression (e.g., ``"0 2 * * *"`` for 2 AM daily)

        Returns:
            SyncSchedule object

        Raises:
            ValueError: If schedule_id already exists or invalid cron expression
        """
        if schedule_id in self.schedules:
            raise ValueError(f"Schedule with ID '{schedule_id}' already exists")

        schedule = SyncSchedule(
            schedule_id=schedule_id,
            group_id=group_id,
            project_path=project_path,
            schedule_type="cron",
            cron_expression=cron_expression,
        )

        # Parse cron expression
        try:
            # Cron format: minute hour day month day_of_week
            parts = cron_expression.split()
            if len(parts) != 5:
                raise ValueError(
                    "Cron expression must have 5 parts: minute hour day month day_of_week"
                )

            trigger = CronTrigger(
                minute=parts[0],
                hour=parts[1],
                day=parts[2],
                month=parts[3],
                day_of_week=parts[4],
            )
        except Exception as e:
            raise ValueError(f"Invalid cron expression: {e}") from e

        # Add job to scheduler
        self.scheduler.add_job(
            func=self._execute_sync,
            trigger=trigger,
            id=schedule_id,
            args=(schedule_id,),
            name=f"Sync {group_id} (cron: {cron_expression})",
        )

        self.schedules[schedule_id] = schedule

        # Update next_run
        job = self.scheduler.get_job(schedule_id)
        if job:
            schedule.next_run = job.next_run_time

        logger.info(f"Added cron schedule: {schedule_id} ({cron_expression})")

        return schedule

    def remove_schedule(self, schedule_id: str) -> None:
        """
        Remove a sync schedule.

        Args:
            schedule_id: Schedule identifier

        Raises:
            KeyError: If schedule not found
        """
        if schedule_id not in self.schedules:
            raise KeyError(f"Schedule '{schedule_id}' not found")

        # Remove job from scheduler
        self.scheduler.remove_job(schedule_id)

        # Remove from schedules dict
        del self.schedules[schedule_id]

        logger.info(f"Removed schedule: {schedule_id}")

    def pause_schedule(self, schedule_id: str) -> None:
        """
        Pause a sync schedule.

        Args:
            schedule_id: Schedule identifier

        Raises:
            KeyError: If schedule not found
        """
        if schedule_id not in self.schedules:
            raise KeyError(f"Schedule '{schedule_id}' not found")

        self.scheduler.pause_job(schedule_id)
        self.schedules[schedule_id].enabled = False

        logger.info(f"Paused schedule: {schedule_id}")

    def resume_schedule(self, schedule_id: str) -> None:
        """
        Resume a paused schedule.

        Args:
            schedule_id: Schedule identifier

        Raises:
            KeyError: If schedule not found
        """
        if schedule_id not in self.schedules:
            raise KeyError(f"Schedule '{schedule_id}' not found")

        self.scheduler.resume_job(schedule_id)
        self.schedules[schedule_id].enabled = True

        logger.info(f"Resumed schedule: {schedule_id}")

    def get_schedule(self, schedule_id: str) -> SyncSchedule | None:
        """
        Get schedule details.

        Args:
            schedule_id: Schedule identifier

        Returns:
            SyncSchedule or None if not found
        """
        schedule = self.schedules.get(schedule_id)

        # Update next_run from scheduler
        if schedule:
            job = self.scheduler.get_job(schedule_id)
            if job:
                schedule.next_run = job.next_run_time

        return schedule

    def list_schedules(self) -> list[SyncSchedule]:
        """
        List all sync schedules.

        Returns:
            List of SyncSchedule objects
        """
        # Update next_run times from scheduler
        for schedule_id, schedule in self.schedules.items():
            job = self.scheduler.get_job(schedule_id)
            if job:
                schedule.next_run = job.next_run_time

        return list(self.schedules.values())

    def _execute_sync(self, schedule_id: str) -> None:
        """
        Execute a scheduled sync operation.

        Args:
            schedule_id: Schedule identifier
        """
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            logger.error(f"Schedule {schedule_id} not found during execution")
            return

        logger.info(f"Executing scheduled sync: {schedule_id} (group: {schedule.group_id})")

        try:
            # Update last_run
            schedule.last_run = datetime.now(UTC)

            # Execute sync
            stats = self.storage_group_service.sync_to_backup(
                schedule.group_id,
                schedule.project_path,
                progress_callback=None,  # Background sync - no UI updates
                cancel_event=None,
            )

            # Success notification
            duration_str = "unknown"
            if stats.end_time is not None:
                duration_str = f"{(stats.end_time - stats.start_time).total_seconds():.1f}s"

            message = (
                f"Scheduled sync completed successfully.\n"
                f"Files copied: {stats.files_copied}\n"
                f"Bytes transferred: {stats.bytes_copied / (1024**2):.2f} MB\n"
                f"Duration: {duration_str}"
            )

            logger.info(f"Scheduled sync {schedule_id} completed: {stats.files_copied} files")

            if self.notification_callback:
                self.notification_callback(schedule.group_id, "success", message)

        except Exception as e:
            error_message = f"Scheduled sync failed: {e}"
            logger.exception(f"Scheduled sync {schedule_id} failed")

            if self.notification_callback:
                self.notification_callback(schedule.group_id, "error", error_message)

        # Update next_run
        job = self.scheduler.get_job(schedule_id)
        if job:
            schedule.next_run = job.next_run_time


def parse_friendly_schedule(friendly: str) -> tuple[str, int | None, str | None]:  # noqa: PLR0911 (many returns for different schedule types)
    """
    Parse friendly schedule string into type and parameters.

    Args:
        friendly: Friendly string like "Hourly", "Daily at 2 AM", "Every 30 minutes"

    Returns:
        Tuple of (schedule_type, interval_minutes or None, cron_expression or None)

    Examples:
        "Hourly" -> ("interval", 60, None)
        "Every 30 minutes" -> ("interval", 30, None)
        "Daily at 2 AM" -> ("cron", None, "0 2 * * *")
        "Weekly on Monday at 3 PM" -> ("cron", None, "0 15 * * 1")
    """
    friendly = friendly.lower().strip()

    # Interval patterns
    if friendly == "hourly":
        return ("interval", 60, None)
    if friendly == "every 30 minutes":
        return ("interval", 30, None)
    if friendly == "every 15 minutes":
        return ("interval", 15, None)

    # Cron patterns
    if friendly == "daily at 2 am":
        return ("cron", None, "0 2 * * *")
    if friendly == "daily at midnight":
        return ("cron", None, "0 0 * * *")
    if friendly == "weekly on monday at 3 pm":
        return ("cron", None, "0 15 * * 1")
    if friendly == "weekly on sunday at midnight":
        return ("cron", None, "0 0 * * 0")

    raise ValueError(f"Unsupported schedule format: {friendly}")
