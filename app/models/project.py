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
        )
