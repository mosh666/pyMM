"""Create a new storage group.

This example demonstrates creating a storage group programmatically.
"""

from datetime import UTC, datetime
from pathlib import Path
import sys
from uuid import uuid4

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService
from app.models.storage_group import DriveInfo, StorageGroup


def main() -> None:
    """Create a new storage group with example drives."""
    service = StorageGroupService()

    # Create storage group with example drive info
    new_group = StorageGroup(
        id=str(uuid4()),
        name="Example Storage Group",
        description="Created programmatically via API example",
        created=datetime.now(UTC),
        modified=datetime.now(UTC),
        master_drive=DriveInfo(
            serial_number="MASTER_SERIAL_123",
            label="MasterDrive",
            total_size=2000000000000,  # 2TB
        ),
        backup_drive=DriveInfo(
            serial_number="BACKUP_SERIAL_456",
            label="BackupDrive",
            total_size=2000000000000,  # 2TB
        ),
    )

    # Save to configuration
    service.add_group(new_group)
    print(f"Created storage group: {new_group.name}")
    print(f"ID: {new_group.id}")
    print("\nUpdate serial numbers in config/storage_groups.yaml with real values.")


if __name__ == "__main__":
    main()
