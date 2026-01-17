"""
Storage Group Service.

This module provides business logic for managing Master/Backup drive relationships.
Handles CRUD operations, drive matching, persistence, and drive resolution with
user prompts for failover scenarios.

Phase 1 Features:
- Relationship tracking between Master and Backup drives
- Multi-strategy drive matching (serial number, label+size)
- YAML persistence with in-memory caching
- Drive resolution with user prompts when Master unavailable
- Validation (no duplicate assignments, removable drives only)

Phase 2 Features:
- Manual sync with progress tracking
- Conflict detection and resolution
- Incremental backup support
- Scheduled and real-time sync
"""

from __future__ import annotations

from datetime import UTC, datetime
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import ValidationError
import yaml

from app.core.services.storage_service import DriveInfo, StorageService
from app.core.sync.file_synchronizer import FileConflict, FileSynchronizer, SyncStatistics
from app.models.storage_group import (
    DriveGroup,
    DriveIdentity,
    DriveRole,
    StorageGroupConfig,
)

if TYPE_CHECKING:
    from collections.abc import Callable
    from threading import Event

    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class StorageGroupError(Exception):
    """Base exception for storage group operations."""


class DriveNotFoundError(StorageGroupError):
    """Raised when a required drive is not found."""


class DuplicateAssignmentError(StorageGroupError):
    """Raised when attempting to assign a drive already in use."""


class StorageGroupService:
    """
    Service for managing storage groups (Master/Backup drive relationships).

    This service provides:
    - CRUD operations for drive groups
    - YAML persistence with caching for performance
    - Drive matching using multi-strategy identification
    - Drive resolution with user prompts for failover
    - Validation to prevent configuration conflicts

    Attributes:
        _storage_service: StorageService for drive detection
        _config_path: Path to storage_groups.yaml file
        _config: In-memory cached configuration
    """

    def __init__(
        self,
        config_path: Path,
        storage_service: StorageService | None = None,
        tracking_db_path: Path | None = None,
    ) -> None:
        """
        Initialize StorageGroupService.

        Args:
            config_path: Path to storage_groups.yaml configuration file
            storage_service: Optional StorageService instance (creates new if None)
            tracking_db_path: Optional path to SQLite tracking database for incremental backups
        """
        self._config_path = config_path
        self._storage_service = storage_service or StorageService()
        self._config = self._load_config()

        # Initialize backup tracking database
        from app.core.sync.backup_tracking import (
            BackupTrackingDatabase,
        )

        if tracking_db_path:
            self._tracking_db = BackupTrackingDatabase(tracking_db_path)
        else:
            # Default to config directory
            default_db_path = config_path.parent / "backup_tracking.db"
            self._tracking_db = BackupTrackingDatabase(default_db_path)

        self._synchronizer = FileSynchronizer(tracking_db=self._tracking_db)

        # Initialize real-time sync manager
        from app.core.sync.realtime_sync import RealtimeSyncManager

        self._realtime_manager = RealtimeSyncManager(self)

        logger.info(
            f"StorageGroupService initialized with {len(self._config.groups)} groups, "
            f"tracking DB: {self._tracking_db.db_path}"
        )

    def _load_config(self) -> StorageGroupConfig:
        """
        Load storage group configuration from YAML file.

        Returns:
            StorageGroupConfig with loaded groups

        Raises:
            StorageGroupError: If YAML is invalid
        """
        if not self._config_path.exists():
            logger.info(f"Config file not found at {self._config_path}, creating empty config")
            return StorageGroupConfig()

        try:
            with self._config_path.open(encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            config = StorageGroupConfig(**data)
            logger.info(f"Loaded {len(config.groups)} storage groups from {self._config_path}")
            return config

        except (yaml.YAMLError, ValidationError) as e:
            logger.exception("Failed to load storage groups config")
            raise StorageGroupError(f"Invalid storage groups configuration: {e}") from e

    def _save_config(self) -> None:
        """
        Save current configuration to YAML file.

        Raises:
            StorageGroupError: If save operation fails
        """
        try:
            # Ensure parent directory exists
            self._config_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert to dict for YAML serialization
            data = self._config.model_dump(mode="json")

            with self._config_path.open("w", encoding="utf-8") as f:
                yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

            logger.info(f"Saved {len(self._config.groups)} storage groups to {self._config_path}")

        except (OSError, yaml.YAMLError) as e:
            logger.exception("Failed to save storage groups config")
            raise StorageGroupError(f"Failed to save configuration: {e}") from e

    def refresh(self) -> None:
        """
        Manually refresh the cached configuration from disk.

        Use this after external modifications to the YAML file.
        """
        logger.info("Refreshing storage groups from disk")
        self._config = self._load_config()

    def list_groups(self) -> list[DriveGroup]:
        """
        Get all configured storage groups.

        Returns:
            List of DriveGroup objects (from cache)
        """
        return self._config.groups.copy()

    def get_group(self, group_id: str) -> DriveGroup | None:
        """
        Get a storage group by ID.

        Args:
            group_id: Unique group identifier

        Returns:
            DriveGroup if found, None otherwise
        """
        return self._config.get_group_by_id(group_id)

    def get_group_by_name(self, name: str) -> DriveGroup | None:
        """
        Get a storage group by name (case-insensitive).

        Args:
            name: Group name to search for

        Returns:
            DriveGroup if found, None otherwise
        """
        return self._config.get_group_by_name(name)

    def create_group(
        self,
        name: str,
        master_drive: DriveIdentity,
        backup_drive: DriveIdentity,
        description: str | None = None,
    ) -> DriveGroup:
        """
        Create a new storage group.

        Args:
            name: User-friendly group name
            master_drive: Master drive identification
            backup_drive: Backup drive identification
            description: Optional group description

        Returns:
            Created DriveGroup

        Raises:
            ValueError: If validation fails (duplicate name, same drives, etc.)
            DuplicateAssignmentError: If drives already assigned to another group
        """
        # Validate drives are not already assigned
        self._validate_drive_not_assigned(master_drive, exclude_group_id=None)
        self._validate_drive_not_assigned(backup_drive, exclude_group_id=None)

        # Create new group (validation happens in model)
        group = DriveGroup(
            name=name, master_drive=master_drive, backup_drive=backup_drive, description=description
        )

        # Add to config (checks for duplicate name/ID)
        self._config.add_group(group)

        # Persist to disk
        self._save_config()

        logger.info(f"Created storage group '{name}' (ID: {group.id})")
        return group

    def update_group(
        self,
        group_id: str,
        name: str | None = None,
        master_drive: DriveIdentity | None = None,
        backup_drive: DriveIdentity | None = None,
        description: str | None = None,
    ) -> DriveGroup:
        """
        Update an existing storage group.

        Args:
            group_id: ID of group to update
            name: New name (None to keep current)
            master_drive: New master drive (None to keep current)
            backup_drive: New backup drive (None to keep current)
            description: New description (None to keep current)

        Returns:
            Updated DriveGroup

        Raises:
            ValueError: If group not found or validation fails
            DuplicateAssignmentError: If drives already assigned to another group
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        # Update fields
        if name is not None:
            group.name = name
        if master_drive is not None:
            self._validate_drive_not_assigned(master_drive, exclude_group_id=group_id)
            group.master_drive = master_drive
        if backup_drive is not None:
            self._validate_drive_not_assigned(backup_drive, exclude_group_id=group_id)
            group.backup_drive = backup_drive
        if description is not None:
            group.description = description

        # Validate master != backup
        if group.master_drive.matches(group.backup_drive):
            raise ValueError("Master and Backup drives cannot be the same")

        # Update in config
        if not self._config.update_group(group):
            raise ValueError(f"Failed to update group '{group_id}'")

        # Persist to disk
        self._save_config()

        logger.info(f"Updated storage group '{group.name}' (ID: {group_id})")
        return group

    def delete_group(self, group_id: str) -> bool:
        """
        Delete a storage group.

        Args:
            group_id: ID of group to delete

        Returns:
            True if group was deleted, False if not found
        """
        removed = self._config.remove_group(group_id)

        if removed:
            self._save_config()
            logger.info(f"Deleted storage group (ID: {group_id})")
        else:
            logger.warning(f"Attempted to delete non-existent group (ID: {group_id})")

        return removed

    def _validate_drive_not_assigned(
        self, drive_identity: DriveIdentity, exclude_group_id: str | None
    ) -> None:
        """
        Validate that a drive is not already assigned to another group.

        Args:
            drive_identity: Drive to check
            exclude_group_id: Group ID to exclude from check (for updates)

        Raises:
            DuplicateAssignmentError: If drive already assigned
        """
        for group in self._config.groups:
            if exclude_group_id and group.id == exclude_group_id:
                continue

            if group.master_drive.matches(drive_identity):
                raise DuplicateAssignmentError(
                    f"Drive already assigned as Master in group '{group.name}'"
                )

            if group.backup_drive.matches(drive_identity):
                raise DuplicateAssignmentError(
                    f"Drive already assigned as Backup in group '{group.name}'"
                )

    def find_drive_info(self, drive_identity: DriveIdentity) -> DriveInfo | None:
        """
        Find currently connected drive matching the given identity.

        Args:
            drive_identity: Drive identification to match

        Returns:
            DriveInfo if matching drive is connected, None otherwise
        """
        all_drives = self._storage_service.get_all_drives()

        for drive_info in all_drives:
            # Create DriveIdentity from current drive
            current_identity = DriveIdentity(
                serial_number=drive_info.serial_number,
                label=drive_info.label,
                total_size=drive_info.total_size,
            )

            if drive_identity.matches(current_identity):
                return drive_info

        return None

    def get_drive_role(self, drive_info: DriveInfo) -> tuple[DriveGroup, DriveRole] | None:
        """
        Determine if a drive is part of any group and its role.

        Args:
            drive_info: Drive to check

        Returns:
            Tuple of (DriveGroup, DriveRole) if drive is in a group, None otherwise
        """
        drive_identity = DriveIdentity(
            serial_number=drive_info.serial_number,
            label=drive_info.label,
            total_size=drive_info.total_size,
        )

        for group in self._config.groups:
            if group.master_drive.matches(drive_identity):
                return (group, DriveRole.MASTER)
            if group.backup_drive.matches(drive_identity):
                return (group, DriveRole.BACKUP)

        return None

    def resolve_drive(
        self, group_id: str, project_name: str, parent: QWidget | None = None
    ) -> Path | None:
        """
        Resolve which drive to use for a project (Master or Backup).

        Logic:
        1. If Master drive connected: return Master path
        2. If only Backup connected: prompt user "Use Backup?" → return Backup or None
        3. If neither connected: show error → return None

        Args:
            group_id: Storage group identifier
            project_name: Project name for error messages
            parent: Parent widget for dialogs

        Returns:
            Path to use (Master or Backup drive root), or None if unavailable/cancelled

        Raises:
            ValueError: If group not found
        """
        from PySide6.QtWidgets import QMessageBox

        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        # Check Master drive
        master_info = self.find_drive_info(group.master_drive)
        if master_info:
            logger.info(f"Master drive '{master_info.label}' available for group '{group.name}'")
            return Path(master_info.drive_letter)

        # Master not available, check Backup
        backup_info = self.find_drive_info(group.backup_drive)

        if backup_info:
            # Backup available - prompt user
            logger.warning(
                f"Master drive unavailable for group '{group.name}', Backup drive '{backup_info.label}' available"
            )

            reply = QMessageBox.question(
                parent,
                "Master Drive Unavailable",
                f"The Master drive for project '{project_name}' is not connected.\n\n"
                f"Storage Group: {group.name}\n"
                f"Master: {group.master_drive.label} (not found)\n"
                f"Backup: {backup_info.label} ({backup_info.drive_letter})\n\n"
                f"Would you like to use the Backup drive instead?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                logger.info(f"User chose to use Backup drive for project '{project_name}'")
                return Path(backup_info.drive_letter)
            logger.info(f"User declined to use Backup drive for project '{project_name}'")
            return None

        # Neither drive available - error
        logger.error(f"No drives available for group '{group.name}'")

        QMessageBox.critical(
            parent,
            "No Drives Available",
            f"Cannot open project '{project_name}'.\n\n"
            f"No drives from storage group '{group.name}' are connected.\n\n"
            f"Please connect either:\n"
            f"  • Master: {group.master_drive.label}\n"
            f"  • Backup: {group.backup_drive.label}",
        )

        return None

    def get_backup_path(self, group_id: str) -> Path | None:
        """
        Get the path to the Backup drive if connected.

        Args:
            group_id: Storage group identifier

        Returns:
            Path to Backup drive root if connected, None otherwise

        Raises:
            ValueError: If group not found
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        backup_info = self.find_drive_info(group.backup_drive)
        return Path(backup_info.drive_letter) if backup_info else None

    # ========================================================================
    # Phase 2: Sync Functionality
    # ========================================================================

    def sync_to_backup(
        self,
        group_id: str,
        source_path: Path,
        progress_callback: object | None = None,
        cancel_event: Event | None = None,
        skip_existing: bool = False,
        verify_checksums: bool = False,
    ) -> SyncStatistics:
        """
        Sync data from Master to Backup drive.

        Args:
            group_id: Storage group identifier
            source_path: Path on Master drive to sync
            progress_callback: Optional callback for progress updates
            cancel_event: Optional threading.Event to signal cancellation
            skip_existing: Skip files that already exist at destination
            verify_checksums: Verify file integrity with SHA-256 checksums

        Returns:
            SyncStatistics with operation results

        Raises:
            ValueError: If group not found or drives unavailable
            FileNotFoundError: If source path doesn't exist
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        # Verify Master drive
        master_info = self.find_drive_info(group.master_drive)
        if not master_info:
            raise ValueError(f"Master drive '{group.master_drive.label}' not connected")

        # Verify Backup drive
        backup_info = self.find_drive_info(group.backup_drive)
        if not backup_info:
            raise ValueError(f"Backup drive '{group.backup_drive.label}' not connected")

        # Calculate destination path (mirror structure on backup)
        master_root = Path(master_info.drive_letter)
        backup_root = Path(backup_info.drive_letter)

        # Get relative path from master root
        try:
            relative_path = source_path.relative_to(master_root)
            destination_path = backup_root / relative_path
        except ValueError:
            raise ValueError(
                f"Source path {source_path} is not on Master drive {master_root}"
            ) from None

        logger.info(
            f"Starting sync: {source_path} -> {destination_path} "
            f"(skip_existing={skip_existing}, verify={verify_checksums})"
        )

        # Wrap progress callback to match FileSynchronizer signature
        def wrapped_callback(files_done: int, files_total: int) -> None:
            """Convert FileSynchronizer progress to SyncProgress format.

            Args:
                files_done: Number of files completed.
                files_total: Total number of files to sync.
            """
            if progress_callback and callable(progress_callback):
                # Import here to avoid circular dependency
                from app.ui.dialogs.sync_progress_dialog import SyncProgress

                # Calculate speed (simple moving average)
                elapsed = (datetime.now(UTC) - stats.start_time).total_seconds()
                speed = stats.bytes_copied / elapsed if elapsed > 0 else 0

                progress = SyncProgress(
                    current_file="",
                    files_completed=files_done,
                    files_total=files_total,
                    bytes_completed=stats.bytes_copied,
                    bytes_total=0,  # Unknown at this point
                    current_speed=speed,
                    start_time=stats.start_time,
                )
                progress_callback(progress)

        # Execute sync with incremental backup support
        stats = self._synchronizer.sync_directory(
            source_path,
            destination_path,
            progress_callback=wrapped_callback if progress_callback else None,
            cancel_event=cancel_event,
            skip_existing=skip_existing,
            verify_checksums=verify_checksums,
            group_id=group_id,  # Enable incremental tracking
            incremental=True,  # Use tracking database
        )

        logger.info(
            f"Sync completed: {stats.files_copied} files copied, "
            f"{stats.bytes_copied / (1024**2):.2f} MB transferred"
        )

        return stats

    def restore_from_backup(
        self,
        group_id: str,
        target_path: Path,
        progress_callback: object | None = None,  # noqa: ARG002
        cancel_event: Event | None = None,
    ) -> SyncStatistics:
        """
        Restore data from Backup to Master drive.

        Args:
            group_id: Storage group identifier
            target_path: Path on Master drive to restore to
            progress_callback: Optional callback for progress updates
            cancel_event: Optional threading.Event to signal cancellation

        Returns:
            SyncStatistics with operation results

        Raises:
            ValueError: If group not found or drives unavailable
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        # Verify drives
        master_info = self.find_drive_info(group.master_drive)
        backup_info = self.find_drive_info(group.backup_drive)

        if not backup_info:
            raise ValueError(f"Backup drive '{group.backup_drive.label}' not connected")

        if not master_info:
            raise ValueError(f"Master drive '{group.master_drive.label}' not connected")

        # Calculate source path on backup
        master_root = Path(master_info.drive_letter)
        backup_root = Path(backup_info.drive_letter)

        try:
            relative_path = target_path.relative_to(master_root)
            source_path = backup_root / relative_path
        except ValueError:
            raise ValueError(
                f"Target path {target_path} is not on Master drive {master_root}"
            ) from None

        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist on Backup drive: {source_path}")

        logger.info(f"Starting restore: {source_path} -> {target_path}")

        # Execute sync (from backup to master)
        stats = self._synchronizer.sync_directory(
            source_path,
            target_path,
            progress_callback=None,  # Restore doesn't report progress callbacks
            cancel_event=cancel_event,
            skip_existing=False,  # Overwrite for restore
            verify_checksums=True,  # Always verify for restore
        )

        logger.info(f"Restore completed: {stats.files_copied} files restored")

        return stats

    def detect_conflicts(self, group_id: str, path: Path) -> list[FileConflict]:
        """
        Detect synchronization conflicts between Master and Backup drives.

        Args:
            group_id: Storage group identifier
            path: Path to check for conflicts

        Returns:
            List of detected conflicts

        Raises:
            ValueError: If group not found or drives unavailable
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        master_info = self.find_drive_info(group.master_drive)
        backup_info = self.find_drive_info(group.backup_drive)

        if not master_info:
            raise ValueError(f"Master drive '{group.master_drive.label}' not connected")

        if not backup_info:
            raise ValueError(f"Backup drive '{group.backup_drive.label}' not connected")

        # Calculate paths
        master_root = Path(master_info.drive_letter)
        backup_root = Path(backup_info.drive_letter)

        try:
            relative_path = path.relative_to(master_root)
            backup_path = backup_root / relative_path
        except ValueError:
            raise ValueError(f"Path {path} is not on Master drive {master_root}") from None

        logger.info(f"Detecting conflicts: {path} <-> {backup_path}")

        conflicts = self._synchronizer.detect_conflicts(path, backup_path)

        logger.info(f"Found {len(conflicts)} conflicts")

        return conflicts

    def verify_sync_status(self, group_id: str, path: Path) -> dict[str, Any]:
        """
        Verify sync status between Master and Backup drives.

        Args:
            group_id: Storage group identifier
            path: Path to verify

        Returns:
            Dictionary with sync status information:
            - in_sync: bool
            - conflicts: list of conflicts
            - files_out_of_sync: int
            - last_checked: datetime

        Raises:
            ValueError: If group not found or drives unavailable
        """
        conflicts = self.detect_conflicts(group_id, path)

        return {
            "in_sync": len(conflicts) == 0,
            "conflicts": conflicts,
            "files_out_of_sync": len(conflicts),
            "last_checked": datetime.now(UTC),
        }

    def resolve_conflicts(
        self,
        group_id: str,
        resolutions: dict[str, str],
    ) -> dict[str, Any]:
        """
        Apply user-selected conflict resolutions.

        Args:
            group_id: Storage group identifier
            resolutions: Dict mapping relative_path to resolution action
                        ("master"/"backup"/"skip"/"both")

        Returns:
            Dictionary with resolution results:
            - resolved: int (number of successfully resolved conflicts)
            - failed: int (number of failed resolutions)
            - skipped: int (number of skipped conflicts)
            - errors: list of error messages

        Raises:
            ValueError: If group not found or drives unavailable
        """
        group = self.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group with ID '{group_id}' not found")

        master_info = self.find_drive_info(group.master_drive)
        backup_info = self.find_drive_info(group.backup_drive)

        if not master_info or not backup_info:
            raise ValueError("Both Master and Backup drives must be connected")

        master_root = Path(master_info.drive_letter)
        backup_root = Path(backup_info.drive_letter)

        resolved_count = 0
        failed_count = 0
        skipped_count = 0
        errors = []

        logger.info(f"Resolving {len(resolutions)} conflicts for group {group_id}")

        for relative_path, action in resolutions.items():
            master_path = master_root / relative_path
            backup_path = backup_root / relative_path

            try:
                if action == "skip":
                    skipped_count += 1
                    logger.debug(f"Skipped: {relative_path}")

                elif action == "master":
                    # Copy Master -> Backup (overwrite)
                    if master_path.exists():
                        backup_path.parent.mkdir(parents=True, exist_ok=True)
                        import shutil

                        shutil.copy2(master_path, backup_path)
                        resolved_count += 1
                        logger.debug(f"Resolved (Master): {relative_path}")
                    else:
                        errors.append(f"{relative_path}: Master file not found")
                        failed_count += 1

                elif action == "backup":
                    # Copy Backup -> Master (overwrite)
                    if backup_path.exists():
                        master_path.parent.mkdir(parents=True, exist_ok=True)
                        import shutil

                        shutil.copy2(backup_path, master_path)
                        resolved_count += 1
                        logger.debug(f"Resolved (Backup): {relative_path}")
                    else:
                        errors.append(f"{relative_path}: Backup file not found")
                        failed_count += 1

                elif action == "both":
                    # Keep both: rename Backup with .backup suffix
                    if backup_path.exists():
                        renamed_backup = backup_path.with_suffix(backup_path.suffix + ".backup")
                        backup_path.rename(renamed_backup)
                        logger.debug(f"Resolved (Both): {relative_path} -> {renamed_backup.name}")

                        # Then copy Master to original backup location
                        if master_path.exists():
                            import shutil

                            shutil.copy2(master_path, backup_path)
                            resolved_count += 1
                        else:
                            errors.append(f"{relative_path}: Master file not found after rename")
                            failed_count += 1
                    else:
                        errors.append(f"{relative_path}: Backup file not found")
                        failed_count += 1

                else:
                    errors.append(f"{relative_path}: Unknown action '{action}'")
                    failed_count += 1

            except Exception as e:
                errors.append(f"{relative_path}: {e}")
                failed_count += 1
                logger.exception(f"Failed to resolve {relative_path}")

        result = {
            "resolved": resolved_count,
            "failed": failed_count,
            "skipped": skipped_count,
            "errors": errors,
        }

        logger.info(
            f"Resolution complete: {resolved_count} resolved, "
            f"{failed_count} failed, {skipped_count} skipped"
        )

        return result

    def enable_realtime_sync(
        self,
        group_id: str,
        watch_path: Path,
        debounce_seconds: float = 0.5,
        notification_callback: Callable[[str, list[Path]], None] | None = None,
    ) -> str:
        """
        Enable real-time file watching and sync.

        Monitors the watch_path for file changes and automatically syncs to Backup drive.
        Uses debouncing to batch rapid changes.

        Args:
            group_id: Storage group identifier
            watch_path: Path to watch for changes (on Master drive)
            debounce_seconds: Delay before processing events (default 0.5s)
            notification_callback: Optional callback(event_type, paths) for notifications

        Returns:
            Watch ID for this watcher

        Raises:
            ValueError: If group not found or drives unavailable
        """
        # Generate unique watch ID
        watch_id = f"{group_id}_{watch_path.name}"

        logger.info(f"Enabling real-time sync for {group_id}: {watch_path}")

        self._realtime_manager.start_watching(
            watch_id=watch_id,
            group_id=group_id,
            watch_path=watch_path,
            debounce_seconds=debounce_seconds,
            sync_callback=notification_callback,
        )

        return watch_id

    def disable_realtime_sync(self, watch_id: str) -> None:
        """
        Disable real-time sync for a watcher.

        Args:
            watch_id: Watcher identifier (returned from enable_realtime_sync)

        Raises:
            KeyError: If watcher not found
        """
        logger.info(f"Disabling real-time sync: {watch_id}")
        self._realtime_manager.stop_watching(watch_id)

    def is_realtime_sync_enabled(self, watch_id: str) -> bool:
        """
        Check if real-time sync is enabled for a watcher.

        Args:
            watch_id: Watcher identifier

        Returns:
            True if watcher is active
        """
        return self._realtime_manager.is_watching(watch_id)

    def list_realtime_watchers(self) -> list[str]:
        """
        List all active real-time sync watchers.

        Returns:
            List of watcher IDs
        """
        return self._realtime_manager.list_watchers()

    def get_sync_history(self, group_id: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        Get sync operation history for a storage group.

        Args:
            group_id: Storage group identifier
            limit: Maximum number of records to return (default 50)

        Returns:
            List of sync operations with details (newest first)
        """
        return self._tracking_db.get_sync_history(group_id, limit)

    def get_operation_files(self, operation_id: int) -> list[dict[str, Any]]:
        """
        Get list of files synced in a specific operation.

        Args:
            operation_id: Sync operation ID

        Returns:
            List of file details for the operation
        """
        return self._tracking_db.get_operation_files(operation_id)

    def close(self) -> None:
        """
        Close all resources and database connections.

        This method should be called when the service is no longer needed
        to ensure proper cleanup of database connections and real-time watchers.
        """
        logger.debug("Closing StorageGroupService resources")

        # Stop real-time sync watchers
        try:
            if hasattr(self, "_realtime_manager"):
                self._realtime_manager.stop_all()
        except Exception:
            logger.exception("Error stopping real-time manager")

        # Close database connection
        try:
            if hasattr(self, "_tracking_db"):
                self._tracking_db.close()
        except Exception:
            logger.exception("Error closing tracking database")

        logger.debug("StorageGroupService resources closed")

    def __del__(self) -> None:
        """Destructor to ensure cleanup on garbage collection."""
        self.close()
