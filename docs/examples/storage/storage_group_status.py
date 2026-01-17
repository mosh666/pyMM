"""Check storage group sync status.

This example demonstrates querying storage group status and sync information.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService


def main() -> None:
    """Display detailed status for a storage group."""
    if len(sys.argv) < 2:
        print("Usage: python storage_group_status.py <group_id>")
        print("\nAvailable groups:")
        service = StorageGroupService()
        for group in service.get_all_groups():
            print(f"  {group.id} - {group.name}")
        sys.exit(1)

    group_id = sys.argv[1]
    service = StorageGroupService()
    group = service.get_group(group_id)

    if not group:
        print(f"Storage group not found: {group_id}")
        sys.exit(1)

    print(f"Storage Group: {group.name}")
    print(f"ID: {group.id}")
    print(f"Description: {group.description or 'N/A'}")
    print("\nMaster Drive:")
    print(f"  Label: {group.master_drive.label}")
    print(f"  Serial: {group.master_drive.serial_number}")
    print(f"  Size: {group.master_drive.total_size / (1024**3):.2f} GB")
    print("\nBackup Drive:")
    print(f"  Label: {group.backup_drive.label}")
    print(f"  Serial: {group.backup_drive.serial_number}")
    print(f"  Size: {group.backup_drive.total_size / (1024**3):.2f} GB")
    print(f"\nLast Modified: {group.modified}")


if __name__ == "__main__":
    main()
