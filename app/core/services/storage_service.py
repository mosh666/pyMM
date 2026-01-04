"""
Storage service for detecting and managing portable drives.
"""
from dataclasses import dataclass
from pathlib import Path

import psutil


@dataclass
class DriveInfo:
    """Information about a storage drive."""

    drive_letter: str
    label: str
    file_system: str
    total_size: int  # bytes
    free_space: int  # bytes
    is_removable: bool
    serial_number: str | None = None

    @property
    def used_space(self) -> int:
        """Calculate used space in bytes."""
        return self.total_size - self.free_space

    @property
    def used_percent(self) -> float:
        """Calculate used space as percentage."""
        if self.total_size == 0:
            return 0.0
        return (self.used_space / self.total_size) * 100


class StorageService:
    """Service for detecting and managing portable storage drives."""

    def __init__(self):
        """Initialize storage service."""
        pass

    def get_all_drives(self) -> list[DriveInfo]:
        """
        Get information about all mounted drives.

        Returns:
            List of DriveInfo objects for all drives
        """
        drives = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                drive_info = DriveInfo(
                    drive_letter=partition.device,
                    label=self._get_drive_label(partition.mountpoint),
                    file_system=partition.fstype,
                    total_size=usage.total,
                    free_space=usage.free,
                    is_removable=self._is_removable_drive(partition),
                    serial_number=self._get_drive_serial(partition.device),
                )
                drives.append(drive_info)
            except (PermissionError, OSError):
                # Skip drives we can't access
                continue

        return drives

    def get_removable_drives(self) -> list[DriveInfo]:
        """
        Get information about removable drives only.

        Returns:
            List of DriveInfo objects for removable drives
        """
        return [drive for drive in self.get_all_drives() if drive.is_removable]

    def get_drive_info(self, path: Path | str) -> DriveInfo | None:
        """
        Get drive information for the drive containing the given path.

        Args:
            path: Any path on the drive

        Returns:
            DriveInfo object or None if drive not found
        """
        path = Path(path).resolve()

        # Get all drives and find the one matching this path
        for drive in self.get_all_drives():
            drive_path = Path(drive.drive_letter)
            try:
                # Check if path is on this drive
                path.relative_to(drive_path)
                return drive
            except ValueError:
                continue

        return None

    def is_path_on_removable_drive(self, path: Path | str) -> bool:
        """
        Check if a path is on a removable drive.

        Args:
            path: Path to check

        Returns:
            True if path is on a removable drive
        """
        drive_info = self.get_drive_info(path)
        return drive_info.is_removable if drive_info else False

    def get_drive_root(self, path: Path | str) -> Path | None:
        """
        Get the root path of the drive containing the given path.

        Args:
            path: Any path on the drive

        Returns:
            Path object pointing to drive root, or None if not found
        """
        path = Path(path).resolve()

        for partition in psutil.disk_partitions(all=False):
            try:
                mount_point = Path(partition.mountpoint)
                # Check if path is under this mount point
                path.relative_to(mount_point)
                return mount_point
            except ValueError:
                continue

        return None

    def _is_removable_drive(self, partition) -> bool:
        """
        Determine if a partition is on a removable drive.

        Args:
            partition: psutil partition object

        Returns:
            True if drive is removable
        """
        # On Windows, check for removable option
        opts = partition.opts.lower()
        return "removable" in opts or partition.fstype in ["vfat", "exfat"]

    def _get_drive_label(self, mountpoint: str) -> str:
        """
        Get the volume label for a drive.

        Args:
            mountpoint: Drive mount point

        Returns:
            Volume label or empty string
        """
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
            serial_number = None
            max_component_length = None
            file_system_flags = None

            kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(mountpoint),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                serial_number,
                max_component_length,
                file_system_flags,
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer),
            )

            return volumeNameBuffer.value
        except Exception:
            return ""

    def _get_drive_serial(self, device: str) -> str | None:
        """
        Get the serial number for a drive.

        Args:
            device: Drive device path

        Returns:
            Serial number as hex string or None
        """
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)
            serial_number = ctypes.c_ulong()

            kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(device),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                ctypes.byref(serial_number),
                None,
                None,
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer),
            )

            return f"{serial_number.value:08X}"
        except Exception:
            return None
