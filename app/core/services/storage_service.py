"""
Storage service for detecting and managing portable drives.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import contextlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psutil

from app.core.platform import Platform, current_platform

try:
    import wmi

    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False


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


class StoragePlatform(ABC):
    """Abstract base class for platform-specific storage detection."""

    @abstractmethod
    def get_all_drives(self) -> list[DriveInfo]:
        """Get information about all mounted drives."""
        ...

    @abstractmethod
    def is_removable(self, partition: Any) -> bool:
        """Check if a partition is on a removable drive."""
        ...

    @abstractmethod
    def get_drive_serial(self, device: str) -> str | None:
        """Get serial number for a drive."""
        ...

    @abstractmethod
    def get_drive_label(self, mountpoint: str) -> str:
        """Get volume label for a drive."""
        ...


class WindowsStorage(StoragePlatform):
    """Windows-specific storage detection using WMI and ctypes."""

    def __init__(self) -> None:
        """Initialize Windows storage detection."""
        self._external_drive_cache: dict[str, bool] = {}
        self._initialize_external_drive_detection()

    def _initialize_external_drive_detection(self) -> None:
        """Initialize external drive detection using WMI."""
        if not WMI_AVAILABLE:
            return

        with contextlib.suppress(Exception):
            self._external_drive_cache = self._detect_external_drives_via_wmi()

    def _detect_external_drives_via_wmi(self) -> dict[str, bool]:
        """Detect USB and external drives using WMI."""
        usb_drives = {}

        try:
            c = wmi.WMI()

            for disk in c.Win32_DiskDrive():
                is_external = False

                if disk.InterfaceType and "USB" in disk.InterfaceType.upper():
                    is_external = True

                if disk.PNPDeviceID and "USB" in disk.PNPDeviceID.upper():
                    is_external = True

                if disk.MediaType:
                    media_type = disk.MediaType.lower()
                    if any(keyword in media_type for keyword in ["removable", "external"]):
                        is_external = True

                if is_external:
                    for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                        for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                            if logical_disk.DeviceID:
                                usb_drives[logical_disk.DeviceID] = True

        except Exception:
            pass

        return usb_drives

    def _is_external_drive(self, drive_letter: str) -> bool:
        """Check if drive is external (USB, external HDD/SSD)."""
        normalized = drive_letter.rstrip("\\").upper()
        if not normalized.endswith(":"):
            normalized += ":"
        return self._external_drive_cache.get(normalized, False)

    def get_all_drives(self) -> list[DriveInfo]:
        """Get all drives on Windows."""
        drives = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                drive_info = DriveInfo(
                    drive_letter=partition.device,
                    label=self.get_drive_label(partition.mountpoint),
                    file_system=partition.fstype,
                    total_size=usage.total,
                    free_space=usage.free,
                    is_removable=self.is_removable(partition),
                    serial_number=self.get_drive_serial(partition.device),
                )
                drives.append(drive_info)
            except (PermissionError, OSError):
                continue

        return drives

    def is_removable(self, partition: Any) -> bool:
        """Determine if partition is on removable drive using Windows API."""
        try:
            import ctypes

            DRIVE_REMOVABLE = 2
            DRIVE_FIXED = 3
            DRIVE_REMOTE = 4
            DRIVE_CDROM = 5
            DRIVE_RAMDISK = 6

            kernel32 = ctypes.windll.kernel32
            drive_type = kernel32.GetDriveTypeW(ctypes.c_wchar_p(partition.mountpoint))

            if drive_type == DRIVE_REMOVABLE:
                return True

            if drive_type in [DRIVE_REMOTE, DRIVE_CDROM, DRIVE_RAMDISK]:
                return False

            if self._is_external_drive(partition.mountpoint):
                return True

            opts = partition.opts.lower()
            if "removable" in opts:
                return True

            if partition.fstype in ["vfat", "exfat", "fat32"]:
                if drive_type not in [DRIVE_FIXED, DRIVE_REMOTE]:
                    return True

            return False
        except Exception:
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["vfat", "exfat"]

    def get_drive_label(self, mountpoint: str) -> str:
        """Get volume label using Windows API."""
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            fileSystemNameBuffer = ctypes.create_unicode_buffer(1024)

            kernel32.GetVolumeInformationW(
                ctypes.c_wchar_p(mountpoint),
                volumeNameBuffer,
                ctypes.sizeof(volumeNameBuffer),
                None,
                None,
                None,
                fileSystemNameBuffer,
                ctypes.sizeof(fileSystemNameBuffer),
            )

            return volumeNameBuffer.value
        except Exception:
            return ""

    def get_drive_serial(self, device: str) -> str | None:
        """Get drive serial number using Windows API."""
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


class LinuxStorage(StoragePlatform):
    """Linux-specific storage detection using pyudev."""

    def __init__(self) -> None:
        """Initialize Linux storage detection."""
        try:
            import pyudev

            self.context = pyudev.Context()
            self._udev_available = True
        except ImportError:
            self.context = None
            self._udev_available = False

    def get_all_drives(self) -> list[DriveInfo]:
        """Get all drives on Linux."""
        drives = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                drive_info = DriveInfo(
                    drive_letter=partition.mountpoint,
                    label=self.get_drive_label(partition.mountpoint),
                    file_system=partition.fstype,
                    total_size=usage.total,
                    free_space=usage.free,
                    is_removable=self.is_removable(partition),
                    serial_number=self.get_drive_serial(partition.device),
                )
                drives.append(drive_info)
            except (PermissionError, OSError):
                continue

        return drives

    def is_removable(self, partition: Any) -> bool:
        """Check if partition is on removable drive using udev."""
        if not self._udev_available or not self.context:
            # Fallback to partition options
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["vfat", "exfat"]

        try:
            import pyudev

            # Get device name from partition device
            device_path = partition.device
            if device_path.startswith("/dev/"):
                device_name = device_path.replace("/dev/", "")

                # Try to find the device in udev
                try:
                    device = pyudev.Devices.from_name(self.context, "block", device_name)

                    # Check if device or its parent is removable
                    if device.properties.get("ID_BUS") in ["usb", "ieee1394"]:
                        return True

                    # Check removable attribute
                    if device.attributes.get("removable") == b"1":
                        return True

                    # Check parent device
                    parent = device.properties.parent
                    while parent:
                        if parent.properties.get("ID_BUS") in ["usb", "ieee1394"]:
                            return True
                        if parent.properties.subsystem == "usb":
                            return True
                        parent = parent.properties.parent

                except Exception:
                    pass

            # Fallback
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["vfat", "exfat"]

        except Exception:
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["vfat", "exfat"]

    def get_drive_label(self, mountpoint: str) -> str:
        """Get volume label on Linux."""
        if not self._udev_available or not self.context:
            return ""

        try:
            import pyudev

            # Try to read label from /proc/mounts or device info
            for partition in psutil.disk_partitions():
                if partition.mountpoint == mountpoint:
                    device_name = partition.device.replace("/dev/", "")
                    try:
                        device = pyudev.Devices.from_name(self.context, "block", device_name)
                        label = device.properties.get("ID_FS_LABEL", "")
                        return label if label else ""
                    except Exception:
                        return ""

            return ""
        except Exception:
            return ""

    def get_drive_serial(self, device: str) -> str | None:
        """Get drive serial number on Linux using udev."""
        if not self._udev_available or not self.context:
            return None

        try:
            import pyudev

            if device.startswith("/dev/"):
                device_name = device.replace("/dev/", "")
                try:
                    udev_device = pyudev.Devices.from_name(self.context, "block", device_name)

                    # Try various serial number attributes
                    serial = (
                        udev_device.properties.get("ID_SERIAL_SHORT")
                        or udev_device.properties.get("ID_SERIAL")
                        or udev_device.properties.get("ID_MODEL")
                    )

                    return serial if serial else None

                except Exception:
                    return None

            return None
        except Exception:
            return None


class MacOSStorage(StoragePlatform):
    """macOS-specific storage detection using DiskArbitration framework."""

    def __init__(self) -> None:
        """Initialize macOS storage detection."""
        try:
            from AppKit import NSWorkspace

            self.workspace = NSWorkspace.sharedWorkspace()
            self._objc_available = True
        except ImportError:
            self.workspace = None
            self._objc_available = False

    def get_all_drives(self) -> list[DriveInfo]:
        """Get all drives on macOS."""
        drives = []

        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)

                drive_info = DriveInfo(
                    drive_letter=partition.mountpoint,
                    label=self.get_drive_label(partition.mountpoint),
                    file_system=partition.fstype,
                    total_size=usage.total,
                    free_space=usage.free,
                    is_removable=self.is_removable(partition),
                    serial_number=self.get_drive_serial(partition.device),
                )
                drives.append(drive_info)
            except (PermissionError, OSError):
                continue

        return drives

    def is_removable(self, partition: Any) -> bool:
        """Check if partition is on removable drive using macOS APIs."""
        if not self._objc_available or not self.workspace:
            # Fallback
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["msdos", "exfat"]

        try:
            # Use NSWorkspace to check if volume is removable
            mountpoint = partition.mountpoint

            # Get mounted volumes
            mounted_volumes = self.workspace.mountedLocalVolumePaths()

            if mountpoint in mounted_volumes:
                # Check device path for common removable indicators
                if "/Volumes/" in mountpoint and mountpoint != "/Volumes/Macintosh HD":
                    return True

            # Fallback to filesystem type
            return partition.fstype in ["msdos", "exfat", "ntfs"]

        except Exception:
            opts = partition.opts.lower()
            return "removable" in opts or partition.fstype in ["msdos", "exfat"]

    def get_drive_label(self, mountpoint: str) -> str:
        """Get volume label on macOS."""
        try:
            # On macOS, the volume label is usually the last component of the mount path
            if mountpoint.startswith("/Volumes/"):
                return Path(mountpoint).name

            return ""
        except Exception:
            return ""

    def get_drive_serial(self, device: str) -> str | None:
        """Get drive serial number on macOS using diskutil."""
        try:
            import subprocess

            # Use diskutil to get disk information
            result = subprocess.run(  # noqa: S603
                ["diskutil", "info", device],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )

            if result.returncode == 0:
                # Parse output for volume UUID or serial
                for line in result.stdout.splitlines():
                    if "Volume UUID:" in line or "Disk / Partition UUID:" in line:
                        parts = line.split(":", 1)
                        if len(parts) == 2:
                            return parts[1].strip()

            return None
        except Exception:
            return None


class StorageService:
    """Service for detecting and managing portable storage drives."""

    def __init__(self) -> None:
        """Initialize storage service with platform-specific implementation."""
        self._platform = self._create_platform_impl()

    @staticmethod
    def _create_platform_impl() -> StoragePlatform:
        """Factory method to create platform-specific storage implementation."""
        match current_platform():
            case Platform.WINDOWS:
                return WindowsStorage()
            case Platform.MACOS:
                return MacOSStorage()
            case Platform.LINUX:
                return LinuxStorage()

    def get_all_drives(self) -> list[DriveInfo]:
        """
        Get information about all mounted drives.

        Returns:
            List of DriveInfo objects for all drives
        """
        return self._platform.get_all_drives()

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
        # Try to find the drive with the longest matching mountpoint
        best_match = None
        best_match_len = 0

        for drive in self.get_all_drives():
            drive_path = Path(drive.drive_letter)
            try:
                # Check if path is on this drive
                path.relative_to(drive_path)
                # Keep track of the longest matching path (most specific mount)
                path_len = len(str(drive_path))
                if path_len > best_match_len:
                    best_match = drive
                    best_match_len = path_len
            except ValueError:
                continue

        return best_match

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
