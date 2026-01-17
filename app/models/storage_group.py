"""
Storage Group data models.

This module defines Pydantic models for managing Master/Backup drive relationships.
Storage Groups enable redundant storage configurations where projects can be stored
on paired drives for data protection and failover support.

Phase 1: Relationship tracking only (no automatic sync)
Phase 2: Sync functionality, conflict resolution, incremental backups
"""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class DriveRole(str, Enum):
    """Role designation for drives within a storage group."""

    MASTER = "master"
    BACKUP = "backup"


class DriveIdentity(BaseModel):
    """
    Unique identification characteristics for a storage drive.

    Uses multi-strategy matching:
    1. Serial number (exact match) - Windows/some Linux via WMI/udev
    2. Label + Size (±5% tolerance) - cross-platform fallback

    Attributes:
        serial_number: Hardware serial number (may be None on some platforms)
        label: Drive volume label
        total_size: Total drive capacity in bytes
    """

    serial_number: str | None = Field(
        None, description="Hardware serial number for exact drive identification"
    )
    label: str = Field(..., description="Volume label of the drive")
    total_size: int = Field(..., gt=0, description="Total drive capacity in bytes")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str) -> str:
        """Validate label is not empty."""
        if not v or not v.strip():
            raise ValueError("Drive label cannot be empty")
        return v.strip()

    def matches(self, other: "DriveIdentity") -> bool:
        """
        Check if this DriveIdentity matches another using multi-strategy logic.

        Strategy 1 (Preferred): Serial number exact match
        Strategy 2 (Fallback): Label exact match + Size within ±5% tolerance

        Args:
            other: DriveIdentity to compare against

        Returns:
            True if drives match, False otherwise

        Examples:
            >>> master = DriveIdentity(serial_number="ABC123", label="Master", total_size=1000000000000)
            >>> backup = DriveIdentity(serial_number="ABC123", label="Backup", total_size=900000000000)
            >>> master.matches(backup)  # Matches by serial
            True

            >>> master = DriveIdentity(serial_number=None, label="MediaDrive", total_size=1000000000000)
            >>> backup = DriveIdentity(serial_number=None, label="MediaDrive", total_size=1020000000000)
            >>> master.matches(backup)  # Matches by label+size (2% difference)
            True
        """
        # Strategy 1: Serial number exact match (most reliable)
        if self.serial_number and other.serial_number:
            return self.serial_number == other.serial_number

        # Strategy 2: Label + Size with tolerance (cross-platform fallback)
        label_match = self.label.lower() == other.label.lower()
        size_tolerance = other.total_size * 0.05  # 5% tolerance
        size_match = abs(self.total_size - other.total_size) <= size_tolerance

        return label_match and size_match

    def to_display_string(self) -> str:
        """
        Format drive identity for UI display.

        Returns:
            Human-readable string like "Master (SN: ABC123, 1.0 TB)"
        """
        size_gb = self.total_size / (1024**3)
        serial_info = f"SN: {self.serial_number}" if self.serial_number else "No Serial"
        return f"{self.label} ({serial_info}, {size_gb:.1f} GB)"


class DriveGroup(BaseModel):
    """
    Storage Group representing Master/Backup drive pairing.

    Attributes:
        id: Unique identifier for the group
        name: User-friendly group name
        created: Creation timestamp
        modified: Last modification timestamp
        master_drive: Identity information for the Master drive
        backup_drive: Identity information for the Backup drive
        description: Optional description of the group's purpose
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique group identifier")
    name: str = Field(..., min_length=1, max_length=100, description="User-friendly group name")
    created: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    modified: datetime = Field(
        default_factory=datetime.now, description="Last modification timestamp"
    )
    master_drive: DriveIdentity = Field(..., description="Master drive identification")
    backup_drive: DriveIdentity = Field(..., description="Backup drive identification")
    description: str | None = Field(None, description="Optional group description")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate group name is not empty and trim whitespace."""
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        return v.strip()

    def model_post_init(self, __context: Any) -> None:
        """Validate that Master and Backup drives are different."""
        if self.master_drive.matches(self.backup_drive):
            raise ValueError("Master and Backup drives cannot be the same drive")

    def get_drive_by_role(self, role: DriveRole) -> DriveIdentity:
        """
        Get drive identity by role.

        Args:
            role: MASTER or BACKUP

        Returns:
            DriveIdentity for the specified role
        """
        return self.master_drive if role == DriveRole.MASTER else self.backup_drive

    def touch_modified(self) -> None:
        """Update the modified timestamp to current time."""
        self.modified = datetime.now(UTC)


class StorageGroupConfig(BaseModel):
    """
    Root configuration model for storage groups YAML file.

    This wraps the list of groups and provides schema version tracking
    for future migrations.

    Attributes:
        version: Schema version for migration support
        groups: List of configured drive groups
    """

    version: int = Field(default=1, description="Configuration schema version")
    groups: list[DriveGroup] = Field(default_factory=list, description="Configured storage groups")

    def get_group_by_id(self, group_id: str) -> DriveGroup | None:
        """
        Find a group by its ID.

        Args:
            group_id: Group identifier to search for

        Returns:
            DriveGroup if found, None otherwise
        """
        return next((g for g in self.groups if g.id == group_id), None)

    def get_group_by_name(self, name: str) -> DriveGroup | None:
        """
        Find a group by its name (case-insensitive).

        Args:
            name: Group name to search for

        Returns:
            DriveGroup if found, None otherwise
        """
        name_lower = name.lower()
        return next((g for g in self.groups if g.name.lower() == name_lower), None)

    def add_group(self, group: DriveGroup) -> None:
        """
        Add a new group to the configuration.

        Args:
            group: DriveGroup to add

        Raises:
            ValueError: If group name or ID already exists
        """
        if self.get_group_by_id(group.id):
            raise ValueError(f"Group with ID '{group.id}' already exists")
        if self.get_group_by_name(group.name):
            raise ValueError(f"Group with name '{group.name}' already exists")
        self.groups.append(group)

    def remove_group(self, group_id: str) -> bool:
        """
        Remove a group by ID.

        Args:
            group_id: Group identifier to remove

        Returns:
            True if group was removed, False if not found
        """
        initial_count = len(self.groups)
        self.groups = [g for g in self.groups if g.id != group_id]
        return len(self.groups) < initial_count

    def update_group(self, group: DriveGroup) -> bool:
        """
        Update an existing group.

        Args:
            group: DriveGroup with updated values (must have existing ID)

        Returns:
            True if group was updated, False if not found
        """
        for i, existing in enumerate(self.groups):
            if existing.id == group.id:
                group.touch_modified()
                self.groups[i] = group
                return True
        return False
