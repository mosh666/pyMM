"""Mock platform-specific data for consistent cross-platform testing.

This module provides realistic sample data for Windows WMI, macOS diskutil,
and Linux udev responses to ensure tests behave consistently across all
developer machines and CI environments.
"""

from __future__ import annotations

from typing import Any

# ============================================================================
# Windows WMI Mock Data
# ============================================================================

MOCK_WMI_USB_DISK = {
    "DeviceID": r"\\.\PHYSICALDRIVE1",
    "Model": "SanDisk Cruzer USB Device",
    "InterfaceType": "USB",
    "PNPDeviceID": r"USBSTOR\DISK&VEN_SANDISK&PROD_CRUZER&REV_1.00\12345678&0",
    "MediaType": "Removable Media",
    "Size": "32017047552",  # 32GB
    "SerialNumber": "12345678",
}

MOCK_WMI_INTERNAL_DISK = {
    "DeviceID": r"\\.\PHYSICALDRIVE0",
    "Model": "Samsung SSD 970 EVO Plus 1TB",
    "InterfaceType": "NVMe",
    "PNPDeviceID": r"SCSI\DISK&VEN_NVME&PROD_SAMSUNG_SSD_970\4&215468A5&0&000000",
    "MediaType": "Fixed hard disk media",
    "Size": "1000204886016",  # 1TB
    "SerialNumber": "S4EWNX0M123456A",
}

MOCK_WMI_EXTERNAL_HDD = {
    "DeviceID": r"\\.\PHYSICALDRIVE2",
    "Model": "WD My Passport 25E2",
    "InterfaceType": "USB",
    "PNPDeviceID": r"USBSTOR\DISK&VEN_WD&PROD_MY_PASSPORT_25E2&REV_4004\574341314430313030343439&0",
    "MediaType": "External hard disk media",
    "Size": "2000398934016",  # 2TB
    "SerialNumber": "WX71A123456",
}

MOCK_WMI_PARTITION_USB = {
    "DeviceID": "Disk #1, Partition #0",
    "DiskIndex": 1,
    "Index": 0,
    "Size": "32013852672",
}

MOCK_WMI_LOGICAL_DISK_USB = {
    "DeviceID": "E:",
    "VolumeName": "USB_DRIVE",
    "FileSystem": "exFAT",
    "Size": "32013852672",
    "FreeSpace": "28000000000",
    "VolumeSerialNumber": "A1B2C3D4",
}

MOCK_WMI_LOGICAL_DISK_INTERNAL = {
    "DeviceID": "C:",
    "VolumeName": "Windows",
    "FileSystem": "NTFS",
    "Size": "1000169533440",
    "FreeSpace": "450000000000",
    "VolumeSerialNumber": "1A2B3C4D",
}

MOCK_WMI_LOGICAL_DISK_EXTERNAL = {
    "DeviceID": "F:",
    "VolumeName": "MyPassport",
    "FileSystem": "NTFS",
    "Size": "2000365158400",
    "FreeSpace": "1500000000000",
    "VolumeSerialNumber": "5E6F7A8B",
}


class MockWMIDiskDrive:
    """Mock WMI Win32_DiskDrive object."""

    def __init__(self, data: dict[str, Any]):
        """Initialize mock disk drive with data."""
        self.DeviceID = data.get("DeviceID")
        self.Model = data.get("Model")
        self.InterfaceType = data.get("InterfaceType")
        self.PNPDeviceID = data.get("PNPDeviceID")
        self.MediaType = data.get("MediaType")
        self.Size = data.get("Size")
        self.SerialNumber = data.get("SerialNumber")

    def associators(self, wmi_class: str) -> list:
        """Mock WMI associators method."""
        if wmi_class == "Win32_DiskDriveToDiskPartition":
            # Return partition based on disk type
            if "USB" in str(self.InterfaceType):
                return [MockWMIPartition(MOCK_WMI_PARTITION_USB)]
            return []
        return []


class MockWMIPartition:
    """Mock WMI Win32_DiskPartition object."""

    def __init__(self, data: dict[str, Any]):
        """Initialize mock partition with data."""
        self.DeviceID = data.get("DeviceID")
        self.DiskIndex = data.get("DiskIndex")
        self.Index = data.get("Index")
        self.Size = data.get("Size")

    def associators(self, wmi_class: str) -> list:
        """Mock WMI associators method."""
        if wmi_class == "Win32_LogicalDiskToPartition":
            return [MockWMILogicalDisk(MOCK_WMI_LOGICAL_DISK_USB)]
        return []


class MockWMILogicalDisk:
    """Mock WMI Win32_LogicalDisk object."""

    def __init__(self, data: dict[str, Any]):
        """Initialize mock logical disk with data."""
        self.DeviceID = data.get("DeviceID")
        self.VolumeName = data.get("VolumeName")
        self.FileSystem = data.get("FileSystem")
        self.Size = data.get("Size")
        self.FreeSpace = data.get("FreeSpace")
        self.VolumeSerialNumber = data.get("VolumeSerialNumber")


class MockWMI:
    """Mock WMI connection object."""

    def __init__(self, drives: list[dict[str, Any]] | None = None):
        """Initialize mock WMI with optional drive data."""
        self.drives = drives or [
            MOCK_WMI_INTERNAL_DISK,
            MOCK_WMI_USB_DISK,
            MOCK_WMI_EXTERNAL_HDD,
        ]

    def Win32_DiskDrive(self) -> list[MockWMIDiskDrive]:  # noqa: N802
        """Return mock disk drives."""
        return [MockWMIDiskDrive(drive) for drive in self.drives]


# ============================================================================
# macOS diskutil Mock Data
# ============================================================================

MOCK_DISKUTIL_INTERNAL = {
    "DeviceIdentifier": "disk0",
    "MediaName": "AppleAPFSMedia",
    "VolumeName": "Macintosh HD",
    "MountPoint": "/",
    "FilesystemType": "apfs",
    "Size": 1000204886016,
    "FreeSpace": 450000000000,
    "Removable": False,
    "Ejectable": False,
    "Internal": True,
    "DeviceNode": "/dev/disk0",
    "VolumeUUID": "12345678-1234-5678-1234-567812345678",
}

MOCK_DISKUTIL_USB = {
    "DeviceIdentifier": "disk2",
    "MediaName": "Generic Flash Disk Media",
    "VolumeName": "USB_DRIVE",
    "MountPoint": "/Volumes/USB_DRIVE",
    "FilesystemType": "exfat",
    "Size": 32017047552,
    "FreeSpace": 28000000000,
    "Removable": True,
    "Ejectable": True,
    "Internal": False,
    "DeviceNode": "/dev/disk2",
    "VolumeUUID": "ABCDEFGH-1234-5678-ABCD-1234567890AB",
}

MOCK_DISKUTIL_EXTERNAL = {
    "DeviceIdentifier": "disk3",
    "MediaName": "WD My Passport Media",
    "VolumeName": "MyPassport",
    "MountPoint": "/Volumes/MyPassport",
    "FilesystemType": "hfs+",
    "Size": 2000398934016,
    "FreeSpace": 1500000000000,
    "Removable": True,
    "Ejectable": True,
    "Internal": False,
    "DeviceNode": "/dev/disk3",
    "VolumeUUID": "98765432-4321-8765-4321-876543218765",
}

MOCK_DISKUTIL_LIST_OUTPUT = """
/dev/disk0 (internal):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      GUID_partition_scheme                         1.0 TB     disk0
   1:             Apple_APFS_ISC                         524.3 MB   disk0s1
   2:                 Apple_APFS Container disk3         994.7 GB   disk0s2

/dev/disk2 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:     FDisk_partition_scheme                        *32.0 GB    disk2
   1:               Windows_NTFS USB_DRIVE               32.0 GB    disk2s1

/dev/disk3 (external, physical):
   #:                       TYPE NAME                    SIZE       IDENTIFIER
   0:      GUID_partition_scheme                        *2.0 TB     disk3
   1:                        EFI EFI                     209.7 MB   disk3s1
   2:                  Apple_HFS MyPassport              2.0 TB     disk3s2
"""

MOCK_DISKUTIL_INFO_USB = """
   Device Identifier:        disk2s1
   Device Node:              /dev/disk2s1
   Whole:                    No
   Part of Whole:            disk2
   Device / Media Name:      Generic Flash Disk Media

   Volume Name:              USB_DRIVE
   Mounted:                  Yes
   Mount Point:              /Volumes/USB_DRIVE

   File System Personality:  ExFAT
   Type (Bundle):            exfat
   Name (User Visible):      ExFAT

   Partition Type:           Windows_NTFS
   OS Can Be Installed:      No
   Media Type:               Generic
   Protocol:                 USB
   SMART Status:             Not Supported

   Disk Size:                32.0 GB (32017047552 Bytes)
   Device Block Size:        512 Bytes

   Volume Total Space:       32.0 GB (32013852672 Bytes)
   Volume Free Space:        28.0 GB (28000000000 Bytes)

   Read-Only Media:          No
   Read-Only Volume:         No

   Device Location:          External
   Removable Media:          Removable
   Media Removal:            Software-Activated

   Virtual:                  No
"""


# ============================================================================
# Linux udev Mock Data
# ============================================================================

MOCK_UDEV_USB_DEVICE_PROPERTIES = {
    "DEVNAME": "/dev/sdb",
    "DEVTYPE": "disk",
    "ID_BUS": "usb",
    "ID_MODEL": "Cruzer",
    "ID_VENDOR": "SanDisk",
    "ID_SERIAL": "SanDisk_Cruzer_12345678",
    "ID_SERIAL_SHORT": "12345678",
    "ID_USB_DRIVER": "usb-storage",
    "ID_TYPE": "disk",
    "SUBSYSTEM": "block",
}

MOCK_UDEV_USB_PARTITION_PROPERTIES = {
    "DEVNAME": "/dev/sdb1",
    "DEVTYPE": "partition",
    "ID_BUS": "usb",
    "ID_FS_TYPE": "exfat",
    "ID_FS_UUID": "A1B2-C3D4",
    "ID_FS_LABEL": "USB_DRIVE",
    "ID_PART_ENTRY_NUMBER": "1",
    "ID_PART_ENTRY_SIZE": "62527488",
    "SUBSYSTEM": "block",
}

MOCK_UDEV_INTERNAL_DEVICE_PROPERTIES = {
    "DEVNAME": "/dev/nvme0n1",
    "DEVTYPE": "disk",
    "ID_MODEL": "Samsung_SSD_970_EVO_Plus_1TB",
    "ID_SERIAL": "Samsung_SSD_970_EVO_Plus_1TB_S4EWNX0M123456A",
    "ID_SERIAL_SHORT": "S4EWNX0M123456A",
    "SUBSYSTEM": "block",
}

MOCK_UDEV_EXTERNAL_HDD_PROPERTIES = {
    "DEVNAME": "/dev/sdc",
    "DEVTYPE": "disk",
    "ID_BUS": "usb",
    "ID_MODEL": "My_Passport_25E2",
    "ID_VENDOR": "WD",
    "ID_SERIAL": "WD_My_Passport_25E2_WX71A123456",
    "ID_SERIAL_SHORT": "WX71A123456",
    "ID_USB_DRIVER": "usb-storage",
    "ID_TYPE": "disk",
    "SUBSYSTEM": "block",
}


class MockPyudevDevice:
    """Mock pyudev Device object."""

    def __init__(self, properties: dict[str, str], parent_device=None):
        """Initialize mock udev device with properties."""
        self._properties_dict = properties
        self.device_node = properties.get("DEVNAME")
        self.device_type = properties.get("DEVTYPE")
        self._parent_device = parent_device
        # Create properties namespace object
        self.properties = MockDeviceProperties(properties, parent_device)
        # Also expose attributes for legacy access
        self.attributes = MockDeviceAttributes(properties)

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get property value."""
        return self._properties_dict.get(key, default)

    def __getitem__(self, key: str) -> str:
        """Get property value (dict-style access)."""
        return self._properties_dict[key]


class MockDeviceProperties:
    """Mock for pyudev Device.properties namespace."""

    def __init__(self, properties: dict[str, str], parent_device=None):
        """Initialize properties namespace."""
        self._properties = properties
        self.parent = parent_device
        self.subsystem = properties.get("SUBSYSTEM")

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get property value."""
        return self._properties.get(key, default)

    def __getitem__(self, key: str) -> str:
        """Get property value (dict-style access)."""
        return self._properties[key]


class MockDeviceAttributes:
    """Mock for pyudev Device.attributes."""

    def __init__(self, properties: dict[str, str]):
        """Initialize attributes namespace."""
        self._properties = properties

    def get(self, key: str, default=None):
        """Get attribute value."""
        # Map common attribute keys
        if key == "removable":
            return self._properties.get("ID_USB_DRIVER", b"0")
        return default


class MockPyudevContext:
    """Mock pyudev Context object."""

    def __init__(self, devices: list[dict[str, str]] | None = None):
        """Initialize mock context with devices."""
        self.devices = devices or [
            MOCK_UDEV_INTERNAL_DEVICE_PROPERTIES,
            MOCK_UDEV_USB_DEVICE_PROPERTIES,
            MOCK_UDEV_EXTERNAL_HDD_PROPERTIES,
        ]

    def list_devices(self, subsystem: str | None = None) -> list[MockPyudevDevice]:
        """List mock devices, optionally filtered by subsystem."""
        devices = [MockPyudevDevice(props) for props in self.devices]
        if subsystem:
            devices = [d for d in devices if d.subsystem == subsystem]
        return devices


# ============================================================================
# subprocess Mock Data for Tool Detection
# ============================================================================

MOCK_GIT_VERSION_OUTPUT = "git version 2.43.0\n"
MOCK_FFMPEG_VERSION_OUTPUT = """ffmpeg version 6.0 Copyright (c) 2000-2023 the FFmpeg developers
built with gcc 11.2.0 (Ubuntu 11.2.0-19ubuntu1)
configuration: --prefix=/usr
"""
MOCK_EXIFTOOL_VERSION_OUTPUT = "12.76\n"
MOCK_IMAGEMAGICK_VERSION_OUTPUT = """Version: ImageMagick 7.1.1-21 Q16-HDRI x86_64 21933
Copyright: (C) 1999 ImageMagick Studio LLC
"""
MOCK_MYSQL_VERSION_OUTPUT = "mysql  Ver 8.0.35 for Linux on x86_64 (MySQL Community Server - GPL)\n"
MOCK_MKVMERGE_VERSION_OUTPUT = "mkvmerge v79.0 ('Mimi') 64-bit\n"
MOCK_GIT_LFS_VERSION_OUTPUT = "git-lfs/3.4.0 (GitHub; linux amd64; go 1.21.0)\n"

# Map of tool names to their version output
MOCK_TOOL_VERSION_OUTPUTS = {
    "git": MOCK_GIT_VERSION_OUTPUT,
    "ffmpeg": MOCK_FFMPEG_VERSION_OUTPUT,
    "exiftool": MOCK_EXIFTOOL_VERSION_OUTPUT,
    "magick": MOCK_IMAGEMAGICK_VERSION_OUTPUT,
    "convert": MOCK_IMAGEMAGICK_VERSION_OUTPUT,
    "mysql": MOCK_MYSQL_VERSION_OUTPUT,
    "mkvmerge": MOCK_MKVMERGE_VERSION_OUTPUT,
    "git-lfs": MOCK_GIT_LFS_VERSION_OUTPUT,
}


def get_mock_tool_version_output(tool_name: str) -> str:
    """Get mock version output for a tool.

    Args:
        tool_name: Name of the tool (e.g., 'git', 'ffmpeg')

    Returns:
        Mock version command output string
    """
    return MOCK_TOOL_VERSION_OUTPUTS.get(tool_name, "")
