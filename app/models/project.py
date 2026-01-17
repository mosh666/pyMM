"""
Project data model.

This module defines the Project dataclass for storing project metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class Project:
    """
    Represents a media management project.

    Attributes:
        name: Display name of the project
        path: Absolute path to the project directory
        created: Creation timestamp
        modified: Last modification timestamp
        description: Optional project description
        settings: Project-specific settings dictionary
        template_name: Name of template used to create project
        template_version: Version of template when project was created
        pending_migration: Deferred migration information (target_version, scheduled_at, reason)
        migration_history: Audit trail of template migrations applied to this project
        storage_group_id: Optional ID of assigned storage group for redundancy
    """

    name: str
    path: Path
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    description: str | None = None
    settings: dict[str, Any] = field(default_factory=dict)
    template_name: str | None = None
    template_version: str | None = None
    pending_migration: dict[str, Any] | None = None
    migration_history: list[dict[str, Any]] = field(default_factory=list)
    storage_group_id: str | None = None
    sync_schedule: dict[str, Any] | None = None  # Scheduled sync configuration
    realtime_sync_enabled: bool = False  # Real-time sync toggle
    realtime_sync_watch_id: str | None = None  # Active watcher ID
    advanced_sync_options: dict[str, Any] | None = None  # Advanced sync configuration

    def __post_init__(self) -> None:
        """Validate and normalize project data."""
        # Validate name is not empty
        if not self.name or not self.name.strip():
            raise ValueError("Project name cannot be empty")

        # Convert path to Path object if it's a string
        if isinstance(self.path, str):
            self.path = Path(self.path)

        # Ensure path is absolute
        if not self.path.is_absolute():
            raise ValueError(f"Project path must be absolute: {self.path}")

    @property
    def exists(self) -> bool:
        """Check if the project directory exists."""
        return self.path.exists()

    @property
    def backup_path(self) -> Path | None:
        """
        Get the backup drive path for this project if assigned to a storage group.

        Returns:
            Path to backup drive root if group assigned and backup connected, None otherwise.

        Note:
            This property requires StorageGroupService to be initialized.
            Returns None if no storage group assigned or backup drive not connected.
        """
        if not self.storage_group_id:
            return None

        # Note: This is a simplified property - actual usage should inject service
        # For real usage, call storage_group_service.get_backup_path(group_id) from service layer
        return None  # Placeholder - service layer should handle this

    def to_dict(self) -> dict[str, Any]:
        """Convert project to dictionary for serialization."""
        return {
            "name": self.name,
            "path": str(self.path),
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "description": self.description,
            "settings": self.settings,
            "template_name": self.template_name,
            "template_version": self.template_version,
            "pending_migration": self.pending_migration,
            "migration_history": self.migration_history,
            "storage_group_id": self.storage_group_id,
            "sync_schedule": self.sync_schedule,
            "realtime_sync_enabled": self.realtime_sync_enabled,
            "realtime_sync_watch_id": self.realtime_sync_watch_id,
            "advanced_sync_options": self.advanced_sync_options,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        """Create project from dictionary."""
        return cls(
            name=data["name"],
            path=Path(data["path"]),
            created=datetime.fromisoformat(data["created"]),
            modified=datetime.fromisoformat(data["modified"]),
            description=data.get("description"),
            settings=data.get("settings", {}),
            template_name=data.get("template_name"),
            template_version=data.get("template_version"),
            pending_migration=data.get("pending_migration"),
            migration_history=data.get("migration_history", []),
            storage_group_id=data.get("storage_group_id"),
            sync_schedule=data.get("sync_schedule"),
            realtime_sync_enabled=data.get("realtime_sync_enabled", False),
            realtime_sync_watch_id=data.get("realtime_sync_watch_id"),
            advanced_sync_options=data.get("advanced_sync_options"),
        )
