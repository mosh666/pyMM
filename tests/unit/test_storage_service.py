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

    def test_get_drive_info_current_drive(self, service, app_root):
        """Test getting drive info for current path."""
        drive_info = service.get_drive_info(app_root)

        assert drive_info is not None
        assert isinstance(drive_info, DriveInfo)
        assert drive_info.total_size > 0

    def test_get_drive_root(self, service, app_root):
        """Test getting drive root."""
        root = service.get_drive_root(app_root)

        assert root is not None
        assert root.exists()
        # On Windows, should be like C:\ or D:\
        assert root.is_absolute()

    def test_is_path_on_removable_drive(self, service, app_root):
        """Test checking if path is on removable drive."""
        # Most test environments use non-removable drives
        is_removable = service.is_path_on_removable_drive(app_root)
        assert isinstance(is_removable, bool)
