"""Query sync history and display backup tracking metadata.

This example demonstrates accessing sync history for a storage group.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService
from app.core.sync.backup_tracking import BackupTracker


def main() -> None:
    """Display sync history for a storage group."""
    if len(sys.argv) < 2:
        print("Usage: python sync_history.py <storage_group_id>")
        sys.exit(1)

    group_id = sys.argv[1]
    service = StorageGroupService()
    group = service.get_group(group_id)

    if not group:
        print(f"Storage group not found: {group_id}")
        sys.exit(1)

    tracker = BackupTracker(group)
    history = tracker.get_history(limit=10)

    if not history:
        print(f"No sync history for: {group.name}")
        return

    print(f"Sync history for: {group.name}")
    print(f"Showing last {len(history)} sync operations:\n")

    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry.timestamp}")
        print(f"   Status: {entry.status}")
        print(f"   Files: {entry.files_synced}")
        print(f"   Size: {entry.bytes_transferred / (1024**2):.2f} MB")
        if entry.errors:
            print(f"   Errors: {len(entry.errors)}")
        print()


if __name__ == "__main__":
    main()
