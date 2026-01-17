"""
File Synchronization Module.

Handles file synchronization operations between Master and Backup drives
including conflict detection, progress tracking, incremental backup support,
and error handling.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
import hashlib
import logging
from pathlib import Path
import shutil
from threading import Event

from app.core.sync.backup_tracking import BackupTrackingDatabase

logger = logging.getLogger(__name__)


@dataclass
class FileConflict:
    """Represents a file synchronization conflict."""

    relative_path: str
    master_mtime: datetime | None
    backup_mtime: datetime | None
    master_size: int | None
    backup_size: int | None
    conflict_type: str  # "modified_both", "deleted_master", "deleted_backup", "size_mismatch"
    master_checksum: str | None = None
    backup_checksum: str | None = None


@dataclass
class SyncStatistics:
    """Statistics for a sync operation."""

    files_copied: int = 0
    files_skipped: int = 0
    files_failed: int = 0
    bytes_copied: int = 0
    conflicts_detected: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None


class FileSynchronizer:
    """Handles file synchronization operations."""

    def __init__(
        self,
        chunk_size: int = 8192,
        tracking_db: BackupTrackingDatabase | None = None,
    ):
        """
        Initialize file synchronizer.

        Args:
            chunk_size: Size of chunks for file copying (default 8KB)
            tracking_db: Optional backup tracking database for incremental syncs
        """
        self.chunk_size = chunk_size
        self.tracking_db = tracking_db
        self.logger = logging.getLogger(__name__)

    def sync_directory(
        self,
        source: Path,
        destination: Path,
        progress_callback: Callable[[int, int], None] | None = None,
        cancel_event: Event | None = None,
        skip_existing: bool = False,
        verify_checksums: bool = False,
        group_id: str | None = None,
        incremental: bool = True,
    ) -> SyncStatistics:
        """
        Synchronize a directory from source to destination.

        Args:
            source: Source directory path
            destination: Destination directory path
            progress_callback: Optional callback(current_file, progress_info)
            cancel_event: Optional threading.Event to signal cancellation
            skip_existing: Skip files that already exist at destination
            verify_checksums: Verify file integrity with SHA-256 checksums
            group_id: Optional storage group ID for tracking
            incremental: Use tracking database to skip unchanged files (default True)

        Returns:
            SyncStatistics with operation results

        Raises:
            FileNotFoundError: If source does not exist
            PermissionError: If insufficient permissions
        """
        if not source.exists():
            raise FileNotFoundError(f"Source path does not exist: {source}")

        if not source.is_dir():
            raise ValueError(f"Source must be a directory: {source}")

        stats = SyncStatistics()
        operation_id = None

        # Start tracking if database available
        if self.tracking_db and group_id:
            operation_id = self.tracking_db.start_sync_operation(
                group_id, "sync", source, destination
            )

        try:
            # Create destination if it doesn't exist
            destination.mkdir(parents=True, exist_ok=True)

            # Collect all files to sync
            files_to_sync = list(self._collect_files(source))
            total_files = len(files_to_sync)
            total_bytes = sum(f.stat().st_size for f in files_to_sync)

            self.logger.info(
                f"Starting sync: {total_files} files ({total_bytes / (1024**2):.2f} MB)"
            )

            bytes_processed = 0

            for file_path in files_to_sync:
                # Check for cancellation
                if cancel_event and cancel_event.is_set():
                    self.logger.info("Sync cancelled by user")
                    break

                try:
                    relative_path = file_path.relative_to(source)
                    dest_file = destination / relative_path
                    file_size = file_path.stat().st_size
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=UTC)

                    # Check if file needs sync (incremental backup)
                    if (
                        incremental
                        and self.tracking_db
                        and group_id
                        and not self.tracking_db.needs_sync(
                            group_id, str(relative_path), file_size, file_mtime
                        )
                    ):
                        # File unchanged - skip
                        stats.files_skipped += 1
                        bytes_processed += file_size

                        if progress_callback:
                            progress_callback(
                                stats.files_copied + stats.files_skipped,
                                total_files,
                            )
                        continue

                    # Check if should skip existing
                    if skip_existing and dest_file.exists():
                        stats.files_skipped += 1
                        bytes_processed += file_size

                        if progress_callback:
                            progress_callback(
                                stats.files_copied + stats.files_skipped,
                                total_files,
                            )
                        continue

                    # Create parent directory
                    dest_file.parent.mkdir(parents=True, exist_ok=True)

                    # Copy file and get checksum
                    checksum = self._copy_file(
                        file_path,
                        dest_file,
                        verify_checksum=verify_checksums,
                    )

                    stats.files_copied += 1
                    stats.bytes_copied += file_size
                    bytes_processed += file_size

                    # Track file sync in database
                    if self.tracking_db and group_id and operation_id:
                        self.tracking_db.track_file_sync(
                            group_id,
                            str(relative_path),
                            file_size,
                            checksum,
                            file_mtime,
                            operation_id,
                        )

                    # Update progress
                    if progress_callback:
                        progress_callback(
                            stats.files_copied + stats.files_skipped,
                            total_files,
                        )

                except Exception:
                    self.logger.exception(f"Failed to sync file {file_path}")
                    stats.files_failed += 1

            stats.end_time = datetime.now(UTC)
            duration = (stats.end_time - stats.start_time).total_seconds()

            self.logger.info(
                f"Sync completed: {stats.files_copied} files copied, "
                f"{stats.files_skipped} skipped, {stats.files_failed} failed "
                f"in {duration:.1f}s"
            )

            # Complete tracking
            if self.tracking_db and operation_id:
                self.tracking_db.complete_sync_operation(
                    operation_id,
                    "completed" if stats.files_failed == 0 else "completed_with_errors",
                    stats.files_copied,
                    stats.bytes_copied,
                    duration,
                    f"{stats.files_failed} files failed" if stats.files_failed > 0 else None,
                )

            return stats

        except Exception as e:
            # Mark operation as failed
            if self.tracking_db and operation_id:
                self.tracking_db.complete_sync_operation(
                    operation_id,
                    "failed",
                    stats.files_copied,
                    stats.bytes_copied,
                    0.0,
                    str(e),
                )
            raise

        self.logger.info(
            f"Sync completed: {stats.files_copied} copied, "
            f"{stats.files_skipped} skipped, {stats.files_failed} failed "
            f"in {duration:.1f}s"
        )

        return stats

    def _collect_files(self, directory: Path) -> list[Path]:
        """
        Recursively collect all files in a directory.

        Args:
            directory: Directory to scan

        Returns:
            List of file paths
        """
        files: list[Path] = []
        try:
            files.extend(item for item in directory.rglob("*") if item.is_file())
        except PermissionError as e:
            self.logger.warning(f"Permission denied accessing {directory}: {e}")

        return files

    def _copy_file(self, source: Path, destination: Path, verify_checksum: bool = False) -> str:
        """
        Copy a single file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path
            verify_checksum: Verify integrity with SHA-256

        Returns:
            SHA-256 checksum of the copied file

        Raises:
            IOError: If copy operation fails
            ValueError: If checksum verification fails
        """
        # Copy file
        shutil.copy2(source, destination)  # Preserves metadata

        # Calculate checksum
        checksum = self._calculate_checksum(destination)

        # Verify checksum if requested
        if verify_checksum:
            source_hash = self._calculate_checksum(source)

            if source_hash != checksum:
                self.logger.error(f"Checksum mismatch: {source} -> {destination}")
                raise ValueError("File copy verification failed - checksum mismatch")

        return checksum

    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of SHA-256 hash
        """
        sha256 = hashlib.sha256()

        with file_path.open("rb") as f:
            while chunk := f.read(self.chunk_size):
                sha256.update(chunk)

        return sha256.hexdigest()

    def detect_conflicts(self, master_path: Path, backup_path: Path) -> list[FileConflict]:
        """
        Detect synchronization conflicts between Master and Backup.

        Args:
            master_path: Path to Master directory
            backup_path: Path to Backup directory

        Returns:
            List of detected conflicts
        """
        conflicts: list[FileConflict] = []

        if not master_path.exists():
            self.logger.warning(f"Master path does not exist: {master_path}")
            return conflicts

        if not backup_path.exists():
            self.logger.info(f"Backup path does not exist (initial sync): {backup_path}")
            return conflicts

        # Collect files from both sides
        master_files = {f.relative_to(master_path): f for f in self._collect_files(master_path)}
        backup_files = {f.relative_to(backup_path): f for f in self._collect_files(backup_path)}

        # Check all files
        all_relative_paths = set(master_files.keys()) | set(backup_files.keys())

        for relative_path in all_relative_paths:
            master_file = master_files.get(relative_path)
            backup_file = backup_files.get(relative_path)

            # File only in master (new file, no conflict)
            if master_file and not backup_file:
                continue

            # File only in backup (deleted from master or manual backup edit)
            if backup_file and not master_file:
                backup_stat = backup_file.stat()
                conflicts.append(
                    FileConflict(
                        relative_path=str(relative_path),
                        master_mtime=None,
                        backup_mtime=datetime.fromtimestamp(backup_stat.st_mtime, tz=UTC),
                        master_size=None,
                        backup_size=backup_stat.st_size,
                        conflict_type="deleted_master",
                    )
                )
                continue

            # File exists in both - check for modifications
            if master_file and backup_file:
                master_stat = master_file.stat()
                backup_stat = backup_file.stat()

                master_mtime = datetime.fromtimestamp(master_stat.st_mtime, tz=UTC)
                backup_mtime = datetime.fromtimestamp(backup_stat.st_mtime, tz=UTC)

                # Size mismatch
                if master_stat.st_size != backup_stat.st_size:
                    conflicts.append(
                        FileConflict(
                            relative_path=str(relative_path),
                            master_mtime=master_mtime,
                            backup_mtime=backup_mtime,
                            master_size=master_stat.st_size,
                            backup_size=backup_stat.st_size,
                            conflict_type="size_mismatch",
                        )
                    )
                # Both modified after last sync (assuming backup should be older)
                elif backup_mtime > master_mtime:
                    # Backup is newer - possible manual edit
                    conflicts.append(
                        FileConflict(
                            relative_path=str(relative_path),
                            master_mtime=master_mtime,
                            backup_mtime=backup_mtime,
                            master_size=master_stat.st_size,
                            backup_size=backup_stat.st_size,
                            conflict_type="modified_both",
                        )
                    )

        return conflicts

    def verify_file_integrity(self, file1: Path, file2: Path) -> bool:
        """
        Verify two files are identical using checksums.

        Args:
            file1: First file path
            file2: Second file path

        Returns:
            True if files are identical, False otherwise
        """
        if not file1.exists() or not file2.exists():
            return False

        # Quick check: size
        if file1.stat().st_size != file2.stat().st_size:
            return False

        # Thorough check: checksum
        hash1 = self._calculate_checksum(file1)
        hash2 = self._calculate_checksum(file2)

        return hash1 == hash2
