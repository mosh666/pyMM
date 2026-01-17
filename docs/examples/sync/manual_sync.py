"""Perform manual sync between master and backup drives.

This example demonstrates a one-time sync operation for a storage group.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService
from app.core.sync.file_synchronizer import FileSynchronizer


def main() -> None:
    """Perform manual sync for a storage group."""
    if len(sys.argv) < 2:
        print("Usage: python manual_sync.py <storage_group_id>")
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

    print(f"Starting sync for: {group.name}")
    print(f"Master: {group.master_drive.label}")
    print(f"Backup: {group.backup_drive.label}\n")

    # Initialize synchronizer
    synchronizer = FileSynchronizer(group)

    # Perform sync
    result = synchronizer.sync()

    print("\nSync completed:")
    print(f"  Files copied: {result.get('files_copied', 0)}")
    print(f"  Files updated: {result.get('files_updated', 0)}")
    print(f"  Conflicts: {result.get('conflicts', 0)}")
    print(f"  Errors: {result.get('errors', 0)}")


if __name__ == "__main__":
    main()
