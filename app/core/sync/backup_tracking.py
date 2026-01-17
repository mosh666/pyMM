"""
Backup Tracking Database.

Provides SQLite-based tracking of file synchronization history, checksums,
and change detection for incremental backups. Enables efficient skip_unchanged
logic by recording last sync times and file states.
"""

from __future__ import annotations

from datetime import UTC, datetime
import logging
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class BackupTrackingDatabase:
    """Manages backup tracking database for incremental syncs."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path) -> None:
        """
        Initialize backup tracking database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection | None = None
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database schema if not exists."""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Create schema version table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
        """)

        # Check current version
        cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
        row = cursor.fetchone()
        current_version = row[0] if row else 0

        if current_version < self.SCHEMA_VERSION:
            self._apply_migrations(current_version)

        self.conn.commit()

    def _apply_migrations(self, from_version: int) -> None:
        """Apply database migrations."""
        assert self.conn is not None
        cursor = self.conn.cursor()

        if from_version < 1:
            logger.info("Applying migration: Initial schema (v1)")

            # Sync operations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    source_path TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    status TEXT NOT NULL,
                    files_copied INTEGER DEFAULT 0,
                    bytes_copied INTEGER DEFAULT 0,
                    duration_seconds REAL,
                    error_message TEXT
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sync_ops_group
                ON sync_operations(group_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sync_ops_timestamp
                ON sync_operations(started_at DESC)
            """)

            # File tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_tracking (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    checksum TEXT NOT NULL,
                    last_synced TEXT NOT NULL,
                    last_modified TEXT NOT NULL,
                    sync_operation_id INTEGER,
                    FOREIGN KEY (sync_operation_id) REFERENCES sync_operations(id),
                    UNIQUE(group_id, relative_path)
                )
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_tracking_group
                ON file_tracking(group_id, relative_path)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_file_tracking_checksum
                ON file_tracking(checksum)
            """)

            # Record schema version
            cursor.execute(
                """
                INSERT INTO schema_version (version, applied_at)
                VALUES (?, ?)
            """,
                (1, datetime.now(UTC).isoformat()),
            )

            logger.info("Migration v1 applied successfully")

        self.conn.commit()

    def start_sync_operation(
        self,
        group_id: str,
        operation_type: str,
        source_path: Path,
        destination_path: Path,
    ) -> int:
        """
        Record the start of a sync operation.

        Args:
            group_id: Storage group identifier
            operation_type: Type of operation ("sync" or "restore")
            source_path: Source directory
            destination_path: Destination directory

        Returns:
            Operation ID for tracking
        """
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO sync_operations (
                group_id, operation_type, source_path, destination_path,
                started_at, status
            ) VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                group_id,
                operation_type,
                str(source_path),
                str(destination_path),
                datetime.now(UTC).isoformat(),
                "in_progress",
            ),
        )

        self.conn.commit()
        operation_id: int = cursor.lastrowid or 0
        logger.info(f"Started sync operation {operation_id}: {group_id} {operation_type}")

        return operation_id

    def complete_sync_operation(
        self,
        operation_id: int,
        status: str,
        files_copied: int = 0,
        bytes_copied: int = 0,
        duration_seconds: float = 0.0,
        error_message: str | None = None,
    ) -> None:
        """
        Mark a sync operation as complete.

        Args:
            operation_id: Operation ID from start_sync_operation()
            status: Final status ("completed", "failed", "cancelled")
            files_copied: Number of files copied
            bytes_copied: Total bytes transferred
            duration_seconds: Operation duration in seconds
            error_message: Optional error message if failed
        """
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE sync_operations
            SET completed_at = ?,
                status = ?,
                files_copied = ?,
                bytes_copied = ?,
                duration_seconds = ?,
                error_message = ?
            WHERE id = ?
        """,
            (
                datetime.now(UTC).isoformat(),
                status,
                files_copied,
                bytes_copied,
                duration_seconds,
                error_message,
                operation_id,
            ),
        )

        self.conn.commit()
        logger.info(f"Completed sync operation {operation_id}: {status}")

    def track_file_sync(
        self,
        group_id: str,
        relative_path: str,
        file_size: int,
        checksum: str,
        last_modified: datetime,
        operation_id: int,
    ) -> None:
        """
        Track a synced file's state.

        Args:
            group_id: Storage group identifier
            relative_path: Relative path from source root
            file_size: File size in bytes
            checksum: SHA-256 checksum
            last_modified: File modification timestamp
            operation_id: Associated sync operation ID
        """
        assert self.conn is not None
        cursor = self.conn.cursor()

        # Upsert file tracking record
        cursor.execute(
            """
            INSERT INTO file_tracking (
                group_id, relative_path, file_size, checksum,
                last_synced, last_modified, sync_operation_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(group_id, relative_path) DO UPDATE SET
                file_size = excluded.file_size,
                checksum = excluded.checksum,
                last_synced = excluded.last_synced,
                last_modified = excluded.last_modified,
                sync_operation_id = excluded.sync_operation_id
        """,
            (
                group_id,
                relative_path,
                file_size,
                checksum,
                datetime.now(UTC).isoformat(),
                last_modified.isoformat(),
                operation_id,
            ),
        )

        assert self.conn is not None
        self.conn.commit()

    def get_file_state(self, group_id: str, relative_path: str) -> dict[str, object] | None:
        """
        Get tracked state for a file.

        Args:
            group_id: Storage group identifier
            relative_path: Relative path from source root

        Returns:
            Dictionary with file state or None if not tracked:
            - file_size: int
            - checksum: str
            - last_synced: datetime
            - last_modified: datetime
        """
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT file_size, checksum, last_synced, last_modified
            FROM file_tracking
            WHERE group_id = ? AND relative_path = ?
        """,
            (group_id, relative_path),
        )

        row = cursor.fetchone()
        if not row:
            return None

        return {
            "file_size": row["file_size"],
            "checksum": row["checksum"],
            "last_synced": datetime.fromisoformat(row["last_synced"]),
            "last_modified": datetime.fromisoformat(row["last_modified"]),
        }

    def needs_sync(
        self,
        group_id: str,
        relative_path: str,
        current_size: int,
        current_mtime: datetime,
        current_checksum: str | None = None,
    ) -> bool:
        """
        Check if file needs synchronization based on tracked state.

        Args:
            group_id: Storage group identifier
            relative_path: Relative path from source root
            current_size: Current file size
            current_mtime: Current modification time
            current_checksum: Optional pre-calculated checksum for verification

        Returns:
            True if file needs sync, False if unchanged
        """
        state = self.get_file_state(group_id, relative_path)

        if not state:
            # File not tracked - needs sync
            return True

        # Quick check: size mismatch
        if state["file_size"] != current_size:
            return True

        # Check modification time
        if state["last_modified"] != current_mtime:
            # Modification time changed - verify with checksum if provided
            # Same content despite mtime change (e.g., touch command) returns False
            return not (current_checksum and state["checksum"] == current_checksum)

        # File appears unchanged
        return False

    def get_sync_history(self, group_id: str, limit: int = 50) -> list[dict[str, object]]:
        """
        Get sync operation history for a group.

        Args:
            group_id: Storage group identifier
            limit: Maximum number of records to return

        Returns:
            List of sync operations (newest first)
        """
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT
                id, operation_type, source_path, destination_path,
                started_at, completed_at, status, files_copied,
                bytes_copied, duration_seconds, error_message
            FROM sync_operations
            WHERE group_id = ?
            ORDER BY started_at DESC
            LIMIT ?
        """,
            (group_id, limit),
        )

        return [
            {
                "id": row["id"],
                "operation_type": row["operation_type"],
                "source_path": row["source_path"],
                "destination_path": row["destination_path"],
                "started_at": datetime.fromisoformat(row["started_at"])
                if row["started_at"]
                else None,
                "completed_at": datetime.fromisoformat(row["completed_at"])
                if row["completed_at"]
                else None,
                "status": row["status"],
                "files_copied": row["files_copied"],
                "bytes_copied": row["bytes_copied"],
                "duration_seconds": row["duration_seconds"],
                "error_message": row["error_message"],
            }
            for row in cursor.fetchall()
        ]

    def get_operation_files(self, operation_id: int) -> list[dict[str, object]]:
        """
        Get list of files synced in an operation.

        Args:
            operation_id: Sync operation ID

        Returns:
            List of file tracking records for this operation
        """
        assert self.conn is not None
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT relative_path, file_size, checksum, last_modified
            FROM file_tracking
            WHERE sync_operation_id = ?
            ORDER BY relative_path
        """,
            (operation_id,),
        )

        return [
            {
                "relative_path": row["relative_path"],
                "file_size": row["file_size"],
                "checksum": row["checksum"],
                "last_modified": datetime.fromisoformat(row["last_modified"]),
            }
            for row in cursor.fetchall()
        ]

    def clear_group_tracking(self, group_id: str) -> None:
        """
        Clear all tracking data for a group.

        Args:
            group_id: Storage group identifier
        """
        assert self.conn is not None
        cursor = self.conn.cursor()

        # Delete file tracking
        cursor.execute("DELETE FROM file_tracking WHERE group_id = ?", (group_id,))

        # Delete sync operations
        cursor.execute("DELETE FROM sync_operations WHERE group_id = ?", (group_id,))

        assert self.conn is not None
        self.conn.commit()
        logger.info(f"Cleared all tracking data for group: {group_id}")

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self) -> BackupTrackingDatabase:
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Context manager exit."""
        self.close()
