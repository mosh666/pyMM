"""Detect connected drives using platform-specific APIs.

This example demonstrates cross-platform drive detection:
- Windows: WMI (Win32_DiskDrive)
- Linux: udev (udisks2/sysfs)
- macOS: DiskArbitration/IOKit
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_service import StorageService


def main() -> None:
    """Detect and display all connected drives."""
    service = StorageService()
    drives = service.get_available_drives()

    if not drives:
        print("No drives detected.")
        return

    print(f"Detected {len(drives)} drive(s):\n")

    for drive in drives:
        print(f"Device: {drive.device_path}")
        print(f"  Label: {drive.label or '(No label)'}")
        print(f"  Serial: {drive.serial_number}")
        print(f"  Size: {drive.total_size / (1024**3):.2f} GB")
        print(f"  Type: {drive.drive_type}")
        print(f"  Removable: {drive.is_removable}")
        print()


if __name__ == "__main__":
    main()
