"""List all configured storage groups.

This minimal example demonstrates how to load and display storage groups.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService


def main() -> None:
    """List all storage groups and their properties."""
    service = StorageGroupService()
    groups = service.get_all_groups()

    if not groups:
        print("No storage groups configured.")
        print("Create one in config/storage_groups.yaml")
        return

    print(f"Found {len(groups)} storage group(s):\n")

    for group in groups:
        print(f"[{group.id}] {group.name}")
        print(f"  Description: {group.description or 'N/A'}")
        print(f"  Created: {group.created}")
        print(
            f"  Master Drive: {group.master_drive.label} (Serial: {group.master_drive.serial_number})"
        )
        print(
            f"  Backup Drive: {group.backup_drive.label} (Serial: {group.backup_drive.serial_number})"
        )
        print()


if __name__ == "__main__":
    main()
