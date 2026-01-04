"""
Project data model.

This module defines the Project dataclass for storing project metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


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
        git_enabled: Whether Git integration is enabled
        settings: Project-specific settings dictionary
    """

    name: str
    path: Path
    created: datetime = field(default_factory=datetime.now)
    modified: datetime = field(default_factory=datetime.now)
    description: str | None = None
    git_enabled: bool = True
    settings: dict = field(default_factory=dict)

    def __post_init__(self):
        """Validate and normalize project data."""
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
    def is_git_repo(self) -> bool:
        """Check if the project is a Git repository."""
        return (self.path / ".git").exists()

    def to_dict(self) -> dict:
        """Convert project to dictionary for serialization."""
        return {
            "name": self.name,
            "path": str(self.path),
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "description": self.description,
            "git_enabled": self.git_enabled,
            "settings": self.settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        """Create project from dictionary."""
        return cls(
            name=data["name"],
            path=Path(data["path"]),
            created=datetime.fromisoformat(data["created"]),
            modified=datetime.fromisoformat(data["modified"]),
            description=data.get("description"),
            git_enabled=data.get("git_enabled", True),
            settings=data.get("settings", {}),
        )
