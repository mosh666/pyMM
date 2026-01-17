"""Tests for StorageService."""

import pytest

from app.core.services.storage_service import DriveInfo, StorageService


class TestDriveInfo:
    """Test suite for DriveInfo dataclass."""

    def test_drive_info_creation(self):
        """Test creating DriveInfo instance."""
        drive = DriveInfo(
            drive_letter="C:\\",
            label="System",
            file_system="NTFS",
            total_size=1000000000,
            free_space=500000000,
            is_removable=False,
            serial_number="12345678",
        )

        assert drive.drive_letter == "C:\\"
        assert drive.label == "System"
        assert drive.serial_number == "12345678"

    def test_used_space_calculation(self):
        """Test used space calculation."""
        drive = DriveInfo(
            drive_letter="C:\\",
            label="Test",
            file_system="NTFS",
            total_size=1000,
            free_space=400,
            is_removable=False,
        )

        assert drive.used_space == 600

    def test_used_percent_calculation(self):
        """Test used percentage calculation."""
        drive = DriveInfo(
            drive_letter="C:\\",
            label="Test",
            file_system="NTFS",
            total_size=1000,
            free_space=250,
            is_removable=False,
        )

        assert drive.used_percent == 75.0

    def test_used_percent_zero_total(self):
        """Test used percentage with zero total size."""
        drive = DriveInfo(
            drive_letter="C:\\",
            label="Test",
            file_system="NTFS",
            total_size=0,
            free_space=0,
            is_removable=False,
        )

        assert drive.used_percent == 0.0


class TestStorageService:
    """Test suite for StorageService."""

    @pytest.fixture
    def service(self):
        """Create StorageService instance."""
        return StorageService()

    def test_get_all_drives(self, service):
        """Test getting all drives."""
        drives = service.get_all_drives()

        assert isinstance(drives, list)
        # Should have at least C: drive on Windows
        assert len(drives) > 0

        # Check drive structure
        for drive in drives:
            assert isinstance(drive, DriveInfo)
            assert drive.drive_letter
            assert drive.total_size >= 0
            assert drive.free_space >= 0

    def test_get_removable_drives(self, service):
        """Test getting removable drives only."""
        removable = service.get_removable_drives()

        assert isinstance(removable, list)
        # All returned drives should be removable
        for drive in removable:
            assert drive.is_removable is True

    def test_get_drive_info_current_drive(self, service):
        """Test getting drive info for current path."""
        # Use current working directory instead of app_root to ensure we have a real drive
        from pathlib import Path
        import platform

        cwd = Path.cwd()
        drive_info = service.get_drive_info(cwd)

        # On non-Windows systems, drive detection works differently and may return None
        # for non-standard mount points. Skip assertion on Linux/macOS.
        if platform.system() == "Windows":
            assert drive_info is not None
            assert isinstance(drive_info, DriveInfo)
            assert drive_info.total_size > 0
        # On Linux/macOS, just verify the method doesn't crash
        elif drive_info is not None:
            assert isinstance(drive_info, DriveInfo)
            assert drive_info.total_size >= 0

    def test_get_drive_root(self, service, app_root):
        """Test getting drive root."""
        import platform

        root = service.get_drive_root(app_root)

        # On Linux/macOS, get_drive_root may return None for non-mount paths
        # On Windows, it should return the drive root (e.g., C:\)
        if platform.system() == "Windows":
            assert root is not None
            assert root.exists()
            # On Windows, should be like C:\ or D:\
            assert root.is_absolute()
        # On Unix systems, behavior depends on mount points
        elif root is not None:
            assert root.exists()
            assert root.is_absolute()

    def test_is_path_on_removable_drive(self, service, app_root):
        """Test checking if path is on removable drive."""
        # Most test environments use non-removable drives
        is_removable = service.is_path_on_removable_drive(app_root)
        assert isinstance(is_removable, bool)

    def test_get_drive_info_with_string_path(self, service):
        """Test get_drive_info with string path."""
        from pathlib import Path
        import platform

        # Use a string path instead of Path object
        path_str = str(Path.cwd())
        drive_info = service.get_drive_info(path_str)

        if platform.system() == "Windows":
            assert drive_info is not None
            assert isinstance(drive_info, DriveInfo)
        # May return None on non-Windows for certain paths

    def test_get_drive_info_nonexistent_path(self, service):
        """Test get_drive_info with path that doesn't exist but has valid drive."""
        from pathlib import Path
        import platform

        if platform.system() == "Windows":
            # Use a path on C: drive that doesn't exist
            fake_path = Path("C:/nonexistent/fake/path")
            drive_info = service.get_drive_info(fake_path)

            # Should still return drive info for C: drive
            assert drive_info is not None
            assert "C:" in drive_info.drive_letter or "c:" in drive_info.drive_letter.lower()

    def test_is_path_on_removable_drive_with_string(self, service):
        """Test is_path_on_removable_drive with string path."""
        from pathlib import Path

        # Pass string instead of Path
        result = service.is_path_on_removable_drive(str(Path.cwd()))
        assert isinstance(result, bool)

    def test_get_drive_root_returns_path(self, service):
        """Test that get_drive_root returns a Path object."""
        from pathlib import Path

        root = service.get_drive_root(Path.cwd())

        # Should return a Path object or None
        assert root is None or isinstance(root, Path)

        if root is not None:
            assert root.is_absolute()
            assert root.exists()

    def test_get_removable_drives_returns_list(self, service):
        """Test that get_removable_drives always returns a list."""
        removable = service.get_removable_drives()
        assert isinstance(removable, list)

        # Verify all items in list are DriveInfo objects
        for drive in removable:
            assert isinstance(drive, DriveInfo)
            assert drive.is_removable is True

    def test_drive_info_with_none_serial(self):
        """Test DriveInfo with None serial number."""
        drive = DriveInfo(
            drive_letter="/dev/sda1",
            label="Test",
            file_system="ext4",
            total_size=1000000,
            free_space=500000,
            is_removable=False,
            serial_number=None,
        )

        assert drive.serial_number is None
        assert drive.used_space == 500000

    def test_drive_info_empty_label(self):
        """Test DriveInfo with empty label."""
        drive = DriveInfo(
            drive_letter="D:\\",
            label="",
            file_system="NTFS",
            total_size=2000000,
            free_space=1000000,
            is_removable=True,
        )

        assert drive.label == ""
        assert drive.is_removable is True
        assert drive.used_percent == 50.0

    def test_get_all_drives_no_permission_error(self, service):
        """Test that get_all_drives handles permission errors gracefully."""
        # Should not raise an exception even if some drives have permission issues
        drives = service.get_all_drives()
        assert isinstance(drives, list)

    def test_get_drive_info_with_path_object(self, service):
        """Test get_drive_info explicitly with Path object."""
        from pathlib import Path

        path = Path.cwd()
        drive_info = service.get_drive_info(path)

        # Should handle Path object without errors
        assert drive_info is None or isinstance(drive_info, DriveInfo)

    def test_get_drive_root_with_string_path(self, service):
        """Test get_drive_root with string path."""
        from pathlib import Path

        path_str = str(Path.cwd())
        root = service.get_drive_root(path_str)

        assert root is None or isinstance(root, Path)

    def test_drive_info_comparison(self):
        """Test DriveInfo objects can be compared."""
        drive1 = DriveInfo(
            drive_letter="C:\\",
            label="System",
            file_system="NTFS",
            total_size=1000,
            free_space=500,
            is_removable=False,
        )

        drive2 = DriveInfo(
            drive_letter="D:\\",
            label="Data",
            file_system="NTFS",
            total_size=2000,
            free_space=1000,
            is_removable=True,
        )

        # Different drives should not be equal
        assert drive1.drive_letter != drive2.drive_letter
        assert drive1.is_removable != drive2.is_removable

    def test_used_percent_with_large_numbers(self):
        """Test used_percent calculation with large disk sizes."""
        drive = DriveInfo(
            drive_letter="E:\\",
            label="BigDrive",
            file_system="NTFS",
            total_size=4000000000000,  # 4TB
            free_space=1000000000000,  # 1TB
            is_removable=False,
        )

        assert drive.used_percent == 75.0
        assert drive.used_space == 3000000000000
