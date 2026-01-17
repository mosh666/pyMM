"""
Real-Time File Synchronization.

Provides file system watching for automatic synchronization between Master and Backup drives
using watchdog library. Includes debouncing to batch rapid changes and prevent sync loops.
"""

from __future__ import annotations

import logging
from pathlib import Path
import threading
import time
from typing import TYPE_CHECKING, Any

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

if TYPE_CHECKING:
    from collections.abc import Callable

    from app.core.services.storage_group_service import StorageGroupService

logger = logging.getLogger(__name__)


class RealtimeSyncHandler(FileSystemEventHandler):
    """Handles file system events for real-time sync."""

    def __init__(
        self,
        group_id: str,
        source_root: Path,
        destination_root: Path,
        storage_group_service: StorageGroupService,
        debounce_seconds: float = 0.5,
        sync_callback: Callable[[str, list[Path]], None] | None = None,
    ) -> None:
        """
        Initialize real-time sync handler.

        Args:
            group_id: Storage group identifier
            source_root: Root path being watched (Master drive)
            destination_root: Destination path (Backup drive)
            storage_group_service: Service for executing syncs
            debounce_seconds: Delay before processing events (default 0.5s)
            sync_callback: Optional callback(event_type, paths) for notifications
        """
        super().__init__()
        self.group_id = group_id
        self.source_root = source_root
        self.destination_root = destination_root
        self.storage_group_service = storage_group_service
        self.debounce_seconds = debounce_seconds
        self.sync_callback = sync_callback

        # Event batching
        self.pending_events: dict[str, float] = {}  # path -> timestamp
        self.event_types: dict[str, str] = {}  # path -> event_type
        self.lock = threading.Lock()
        self.processing = False

        # Sync direction tracking to prevent loops
        self._sync_in_progress = False

        # Start debounce processor
        self.processor_thread = threading.Thread(target=self._process_events, daemon=True)
        self.processor_thread.start()

        logger.info(
            f"RealtimeSyncHandler initialized for group {group_id}: "
            f"{source_root} -> {destination_root}"
        )

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation event."""
        if event.is_directory:
            return  # Ignore directory creation - will sync files inside

        self._queue_event(str(event.src_path), "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification event."""
        if event.is_directory:
            return

        self._queue_event(str(event.src_path), "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion event."""
        if event.is_directory:
            return

        self._queue_event(str(event.src_path), "deleted")

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move/rename event."""
        if event.is_directory:
            return

        # Treat as delete + create
        self._queue_event(str(event.src_path), "deleted")
        self._queue_event(str(event.dest_path), "created")

    def _queue_event(self, path: str, event_type: str) -> None:
        """
        Queue an event for debounced processing.

        Args:
            path: File path that changed
            event_type: Type of event ("created", "modified", "deleted")
        """
        # Skip if sync is in progress (prevent loops)
        if self._sync_in_progress:
            logger.debug(f"Skipping event during sync: {path}")
            return

        with self.lock:
            current_time = time.time()
            self.pending_events[path] = current_time
            self.event_types[path] = event_type

            logger.debug(f"Queued {event_type} event: {path}")

    def _process_events(self) -> None:
        """Background thread to process debounced events."""
        while True:
            time.sleep(0.1)  # Check every 100ms

            with self.lock:
                if not self.pending_events or self.processing:
                    continue

                current_time = time.time()
                ready_paths = []

                # Find events that have been stable for debounce_seconds
                for path, timestamp in list(self.pending_events.items()):
                    if current_time - timestamp >= self.debounce_seconds:
                        ready_paths.append(path)

                if not ready_paths:
                    continue

                # Extract ready events
                events_to_process = {path: self.event_types[path] for path in ready_paths}

                # Remove from pending
                for path in ready_paths:
                    del self.pending_events[path]
                    del self.event_types[path]

                self.processing = True

            # Process events outside lock
            try:
                self._sync_files(events_to_process)
            except Exception:
                logger.exception("Error processing events")
            finally:
                with self.lock:
                    self.processing = False

    def _sync_files(self, events: dict[str, str]) -> None:
        """
        Synchronize changed files to backup.

        Args:
            events: Dictionary of path -> event_type
        """
        if not events:
            return

        logger.info(f"Processing {len(events)} file events")

        # Group by event type
        created_modified = []
        deleted = []

        for path_str, event_type in events.items():
            path = Path(path_str)

            if event_type == "deleted":
                deleted.append(path)
            elif path.exists():  # Verify file still exists
                created_modified.append(path)

        # Sync created/modified files
        if created_modified:
            try:
                self._sync_in_progress = True

                # Use FileSynchronizer for individual files
                for file_path in created_modified:
                    try:
                        relative_path = file_path.relative_to(self.source_root)
                        dest_file = self.destination_root / relative_path

                        # Ensure destination directory exists
                        dest_file.parent.mkdir(parents=True, exist_ok=True)

                        # Copy file
                        import shutil

                        shutil.copy2(file_path, dest_file)

                        logger.info(f"Synced: {relative_path}")

                    except Exception:
                        logger.exception(f"Failed to sync {file_path}")

                if self.sync_callback:
                    self.sync_callback("synced", created_modified)

            finally:
                self._sync_in_progress = False

        # Handle deletions
        if deleted:
            try:
                for file_path in deleted:
                    try:
                        relative_path = file_path.relative_to(self.source_root)
                        dest_file = self.destination_root / relative_path

                        if dest_file.exists():
                            dest_file.unlink()
                            logger.info(f"Deleted from backup: {relative_path}")

                    except Exception:
                        logger.exception(f"Failed to delete {file_path}")

                if self.sync_callback:
                    self.sync_callback("deleted", deleted)

            except Exception:
                logger.exception("Error processing deletions")


class RealtimeSyncManager:
    """Manages real-time file synchronization watchers."""

    def __init__(self, storage_group_service: StorageGroupService) -> None:
        """
        Initialize real-time sync manager.

        Args:
            storage_group_service: StorageGroupService for sync operations
        """
        self.storage_group_service = storage_group_service
        self.watchers: dict[str, tuple[Any, RealtimeSyncHandler]] = {}
        self.lock = threading.Lock()

        logger.info("RealtimeSyncManager initialized")

    def start_watching(
        self,
        watch_id: str,
        group_id: str,
        watch_path: Path,
        debounce_seconds: float = 0.5,
        sync_callback: Callable[[str, list[Path]], None] | None = None,
    ) -> None:
        """
        Start watching a directory for changes.

        Args:
            watch_id: Unique identifier for this watcher
            group_id: Storage group ID
            watch_path: Path to watch (on Master drive)
            debounce_seconds: Delay before processing events (default 0.5s)
            sync_callback: Optional callback(event_type, paths) for notifications

        Raises:
            ValueError: If watch_id already exists or group not found
        """
        with self.lock:
            if watch_id in self.watchers:
                raise ValueError(f"Watcher with ID '{watch_id}' already exists")

        # Get group details
        group = self.storage_group_service.get_group(group_id)
        if not group:
            raise ValueError(f"Storage group '{group_id}' not found")

        # Verify drives connected
        master_info = self.storage_group_service.find_drive_info(group.master_drive)
        backup_info = self.storage_group_service.find_drive_info(group.backup_drive)

        if not master_info:
            raise ValueError("Master drive not connected")

        if not backup_info:
            raise ValueError("Backup drive not connected")

        # Calculate destination path
        master_root = Path(master_info.drive_letter)
        backup_root = Path(backup_info.drive_letter)

        try:
            relative_path = watch_path.relative_to(master_root)
            destination_path = backup_root / relative_path
        except ValueError:
            raise ValueError(
                f"Watch path {watch_path} is not on Master drive {master_root}"
            ) from None

        # Create handler and observer
        handler = RealtimeSyncHandler(
            group_id=group_id,
            source_root=watch_path,
            destination_root=destination_path,
            storage_group_service=self.storage_group_service,
            debounce_seconds=debounce_seconds,
            sync_callback=sync_callback,
        )

        observer = Observer()
        observer.schedule(handler, str(watch_path), recursive=True)
        observer.start()

        with self.lock:
            self.watchers[watch_id] = (observer, handler)

        logger.info(
            f"Started real-time sync watcher: {watch_id} ({watch_path} -> {destination_path})"
        )

    def stop_watching(self, watch_id: str) -> None:
        """
        Stop watching a directory.

        Args:
            watch_id: Watcher identifier

        Raises:
            KeyError: If watcher not found
        """
        with self.lock:
            if watch_id not in self.watchers:
                raise KeyError(f"Watcher '{watch_id}' not found")

            observer, _handler = self.watchers[watch_id]

            # Stop observer
            observer.stop()
            observer.join(timeout=5.0)

            # Remove from watchers
            del self.watchers[watch_id]

        logger.info(f"Stopped real-time sync watcher: {watch_id}")

    def is_watching(self, watch_id: str) -> bool:
        """
        Check if a watcher is active.

        Args:
            watch_id: Watcher identifier

        Returns:
            True if watcher exists and is running
        """
        with self.lock:
            if watch_id not in self.watchers:
                return False

            observer, _ = self.watchers[watch_id]
            return bool(observer.is_alive())

    def list_watchers(self) -> list[str]:
        """
        List all active watchers.

        Returns:
            List of watcher IDs
        """
        with self.lock:
            return list(self.watchers.keys())

    def stop_all(self) -> None:
        """Stop all watchers."""
        with self.lock:
            watch_ids = list(self.watchers.keys())

        for watch_id in watch_ids:
            try:
                self.stop_watching(watch_id)
            except Exception:
                logger.exception(f"Error stopping watcher {watch_id}")

        logger.info("All real-time sync watchers stopped")
