"""Set up scheduled sync with cron-like expressions.

This example demonstrates configuring scheduled sync using APScheduler.
"""

from pathlib import Path
import sys
import time

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService
from app.core.sync.scheduled_sync import ScheduledSyncManager


def main() -> None:
    """Set up scheduled sync for all storage groups."""
    service = StorageGroupService()
    groups = service.get_all_groups()

    if not groups:
        print("No storage groups configured.")
        sys.exit(1)

    print("Setting up scheduled sync...")
    manager = ScheduledSyncManager()

    # Schedule daily sync at 2 AM for each group
    for group in groups:
        manager.add_schedule(
            group_id=group.id,
            cron_expression="0 2 * * *",  # Daily at 2 AM
            description=f"Daily sync for {group.name}",
        )
        print(f"Scheduled: {group.name} - Daily at 2:00 AM")

    print("\nScheduled sync is running. Press Ctrl+C to stop.")
    print("Next sync times:")
    for group in groups:
        next_run = manager.get_next_run_time(group.id)
        print(f"  {group.name}: {next_run}")

    try:
        while True:
            time.sleep(60)  # Keep alive
    except KeyboardInterrupt:
        print("\nStopping scheduled sync...")
        manager.shutdown()


if __name__ == "__main__":
    main()
