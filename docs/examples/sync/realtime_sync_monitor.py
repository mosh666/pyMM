"""Monitor directory for changes and trigger real-time sync.

This example demonstrates real-time file watching with watchdog.
"""

from pathlib import Path
import sys
import time

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.sync.realtime_sync import RealtimeSyncMonitor


def main() -> None:
    """Start real-time sync monitoring for a directory."""
    if len(sys.argv) < 2:
        print("Usage: python realtime_sync_monitor.py <watch_directory>")
        sys.exit(1)

    watch_dir = Path(sys.argv[1])
    if not watch_dir.exists():
        print(f"Directory not found: {watch_dir}")
        sys.exit(1)

    print(f"Starting real-time sync monitor for: {watch_dir}")
    print("Watching for file changes... Press Ctrl+C to stop.\n")

    monitor = RealtimeSyncMonitor(watch_path=watch_dir)
    monitor.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        monitor.stop()
        print("Monitor stopped.")


if __name__ == "__main__":
    main()
