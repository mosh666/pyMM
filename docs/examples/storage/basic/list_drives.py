#!/usr/bin/env python3
"""List all available storage drives.

This example demonstrates:
- Using StorageService for drive detection
- Getting drive information
- Cross-platform storage handling
"""

import logging

from app.services.storage_service import StorageService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def format_size(bytes_size: int) -> str:
    """Format size in human-readable format.

    Args:
        bytes_size: Size in bytes.

    Returns:
        Formatted size string (e.g., "1.5 GB").
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def main() -> None:
    """List all available drives with details."""
    # Initialize storage service
    storage_service = StorageService()

    try:
        # Discover all drives
        drives = storage_service.get_drives()

        if not drives:
            return

        for drive in drives:
            if drive.total_space:
                format_size(drive.total_space)
                format_size(drive.free_space)
                ((drive.total_space - drive.free_space) / drive.total_space) * 100

            if drive.is_portable:
                pass

            if drive.is_ready:
                pass
            else:
                pass

        # Count by type
        sum(1 for d in drives if d.drive_type == "fixed")
        sum(1 for d in drives if d.drive_type == "removable")
        sum(1 for d in drives if d.drive_type == "network")

    except Exception as e:
        logging.exception(f"Error listing drives: {e}")


if __name__ == "__main__":
    main()
