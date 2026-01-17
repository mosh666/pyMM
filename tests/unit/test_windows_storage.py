"""Tests for Windows storage detection.

Uses mocking to test Windows-specific code on all platforms.
Only true integration tests that cannot be effectively mocked use @pytest.mark.windows.
"""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest


class TestWindowsStorage:
    """Test suite for WindowsStorage (mocked to run on all platforms)."""

    @pytest.fixture
    def windows_storage(self):
        """Create WindowsStorage instance with mocked WMI."""
        # Import only when needed
        from app.core.services.storage_service import WindowsStorage

        # Mock WMI to avoid requiring Windows
        with patch("app.core.services.storage_service.WMI_AVAILABLE", True):
            return WindowsStorage()

    def test_initialization(self, mock_wmi):
        """Test WindowsStorage initialization with mocked WMI."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            assert storage is not None
            assert hasattr(storage, "_external_drive_cache")
            assert isinstance(storage._external_drive_cache, dict)

    def test_detect_external_drives_via_wmi(self, mock_wmi):
        """Test USB drive detection through WMI."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            # USB drive should be detected
            assert "E:" in storage._external_drive_cache
            assert storage._external_drive_cache["E:"] is True

    def test_detect_no_external_drives(self, mock_wmi_no_usb):
        """Test WMI detection when no USB drives present."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi_no_usb)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            # No USB drives should be in cache
            assert len(storage._external_drive_cache) == 0

    def test_is_external_drive(self, mock_wmi):
        """Test checking if drive is external."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            # E: is USB drive
            assert storage._is_external_drive("E:") is True
            assert storage._is_external_drive("E:\\") is True

            # C: is not external
            assert storage._is_external_drive("C:") is False

    def test_is_removable_with_windows_api(self, mock_wmi, mock_ctypes_windll):
        """Test is_removable using mocked Windows API."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock partition
        mock_partition = Mock()
        mock_partition.mountpoint = "E:\\"
        mock_partition.opts = ""
        mock_partition.fstype = "exFAT"

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("ctypes.windll", mock_ctypes_windll, create=True),
        ):
            storage = WindowsStorage()

            # Mock GetDriveTypeW to return DRIVE_REMOVABLE
            mock_ctypes_windll.kernel32.GetDriveTypeW.return_value = 2  # DRIVE_REMOVABLE

            result = storage.is_removable(mock_partition)
            assert result is True

    def test_is_removable_fixed_drive(self, mock_wmi, mock_ctypes_windll):
        """Test is_removable for fixed drive."""
        from app.core.services.storage_service import WindowsStorage

        mock_partition = Mock()
        mock_partition.mountpoint = "C:\\"
        mock_partition.opts = ""
        mock_partition.fstype = "NTFS"

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("ctypes.windll", mock_ctypes_windll, create=True),
        ):
            storage = WindowsStorage()

            # Mock GetDriveTypeW to return DRIVE_FIXED
            mock_ctypes_windll.kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED

            result = storage.is_removable(mock_partition)
            # Should be False (not in USB cache and not removable type)
            assert result is False

    def test_is_removable_by_filesystem(self, mock_wmi, mock_ctypes_windll):
        """Test removable detection by filesystem type."""
        from app.core.services.storage_service import WindowsStorage

        mock_partition = Mock()
        mock_partition.mountpoint = "F:\\"
        mock_partition.opts = ""
        mock_partition.fstype = "vfat"

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("ctypes.windll", mock_ctypes_windll, create=True),
        ):
            storage = WindowsStorage()

            # Mock GetDriveTypeW to return unknown type
            mock_ctypes_windll.kernel32.GetDriveTypeW.return_value = 0

            result = storage.is_removable(mock_partition)
            # vfat filesystem suggests removable
            assert result is True

    def test_get_drive_label(self, mock_wmi, mock_ctypes_windll):
        """Test getting drive label via Windows API."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("ctypes.windll", mock_ctypes_windll, create=True),
        ):
            storage = WindowsStorage()
            label = storage.get_drive_label("C:\\")

            # Should get label from mock (set in conftest.py)
            assert label == "TestDrive"

    def test_get_drive_label_error_handling(self, mock_wmi):
        """Test drive label retrieval with error."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            # Mock ctypes to raise exception
            with patch("ctypes.windll", side_effect=Exception("Test error"), create=True):
                label = storage.get_drive_label("X:\\")

                # Should return empty string on error
                assert label == ""

    def test_get_drive_serial(self, mock_wmi, mock_ctypes_windll):
        """Test getting drive serial number."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("ctypes.windll", mock_ctypes_windll, create=True),
        ):
            storage = WindowsStorage()

            # Mock expects format like "C:"
            serial = storage.get_drive_serial("C:")

            # Serial should be returned (mocked in fixture)
            assert serial is not None

    def test_get_all_drives_mocked(self, mock_wmi):
        """Test get_all_drives with fully mocked environment."""
        from app.core.services.storage_service import DriveInfo, WindowsStorage

        # Mock psutil disk_partitions
        mock_partition = Mock()
        mock_partition.device = "C:"
        mock_partition.mountpoint = "C:\\"
        mock_partition.fstype = "NTFS"
        mock_partition.opts = ""

        # Mock psutil disk_usage
        mock_usage = Mock()
        mock_usage.total = 1000000000000  # 1TB
        mock_usage.free = 500000000000  # 500GB

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(return_value=mock_wmi)

        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
            patch("psutil.disk_partitions", return_value=[mock_partition]),
            patch("psutil.disk_usage", return_value=mock_usage),
            patch("ctypes.windll", create=True) as mock_windll,
        ):
            # Setup Windows API mocks
            mock_windll.kernel32.GetDriveTypeW.return_value = 3  # DRIVE_FIXED
            mock_windll.kernel32.GetVolumeInformationW.return_value = True

            storage = WindowsStorage()
            drives = storage.get_all_drives()

            assert len(drives) > 0
            assert isinstance(drives[0], DriveInfo)
            assert drives[0].drive_letter == "C:"

    def test_wmi_unavailable_fallback(self):
        """Test that WindowsStorage works when WMI is unavailable."""
        from app.core.services.storage_service import WindowsStorage

        with patch("app.core.services.storage_service.WMI_AVAILABLE", False):
            storage = WindowsStorage()

            # Should initialize but with empty cache
            assert storage._external_drive_cache == {}

    def test_wmi_exception_handling(self):
        """Test WMI initialization handles exceptions gracefully."""
        from app.core.services.storage_service import WindowsStorage

        # Create mock wmi module
        mock_wmi_module = Mock()
        mock_wmi_module.WMI = Mock(side_effect=Exception("WMI error"))

        # Mock WMI to raise exception
        with (
            patch("app.core.services.storage_service.WMI_AVAILABLE", True),
            patch.dict("sys.modules", {"wmi": mock_wmi_module}),
            patch("app.core.services.storage_service.wmi", mock_wmi_module, create=True),
        ):
            storage = WindowsStorage()

            # Should initialize with empty cache
            assert storage._external_drive_cache == {}


class TestWindowsStorageIntegration:
    """Integration tests requiring actual Windows OS.

    These tests are marked with @pytest.mark.windows and will only run
    on Windows systems. Use these sparingly - prefer mocked tests above.
    """

    @pytest.mark.windows
    def test_real_wmi_connection(self):
        """Test actual WMI connection on Windows (integration test)."""
        from app.core.services.storage_service import WMI_AVAILABLE, WindowsStorage

        if not WMI_AVAILABLE:
            pytest.skip("WMI not available")

        storage = WindowsStorage()
        assert storage is not None

    @pytest.mark.windows
    def test_real_drive_detection(self):
        """Test real drive detection on Windows (integration test)."""
        from app.core.services.storage_service import WMI_AVAILABLE, WindowsStorage

        if not WMI_AVAILABLE:
            pytest.skip("WMI not available")

        storage = WindowsStorage()
        drives = storage.get_all_drives()

        # Should detect at least C: drive on Windows
        assert len(drives) > 0
        drive_letters = [d.drive_letter for d in drives]
        assert any("C:" in letter for letter in drive_letters)
