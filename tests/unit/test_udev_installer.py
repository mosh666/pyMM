"""Tests for Linux udev rules installer."""

from pathlib import Path
import sys
from unittest.mock import MagicMock, patch

import pytest

from app.platform.linux.udev_installer import (
    LinuxUdevInstaller,
    UdevInstallStatus,
)


class TestLinuxUdevInstaller:
    """Test suite for LinuxUdevInstaller."""

    def test_init(self):
        """Test installer initialization."""
        installer = LinuxUdevInstaller()
        assert installer.RULES_FILENAME == "99-pymm-usb.rules"
        assert Path("/etc/udev/rules.d") == installer.RULES_DIR
        assert installer.rules_path == Path("/etc/udev/rules.d/99-pymm-usb.rules")

    @pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test")
    def test_is_linux_on_linux(self):
        """Test is_linux on Linux systems."""
        installer = LinuxUdevInstaller()
        assert installer.is_linux() is True

    @patch("sys.platform", "win32")
    def test_is_linux_on_non_linux(self):
        """Test is_linux on non-Linux systems."""
        installer = LinuxUdevInstaller()
        assert installer.is_linux() is False

    def test_get_rules_content(self):
        """Test getting rules content."""
        installer = LinuxUdevInstaller()
        content = installer.get_rules_content()
        assert "pyMediaManager" in content
        assert "SUBSYSTEM==" in content
        assert "ID_BUS" in content
        assert "usb" in content

    @patch("sys.platform", "linux")
    def test_is_installed_true(self):
        """Test is_installed when rules are installed."""
        installer = LinuxUdevInstaller()
        with patch.object(Path, "exists", return_value=True):
            assert installer.is_installed() is True

    @patch("sys.platform", "linux")
    def test_is_installed_false(self):
        """Test is_installed when rules are not installed."""
        installer = LinuxUdevInstaller()
        with patch.object(Path, "exists", return_value=False):
            assert installer.is_installed() is False

    @patch("sys.platform", "win32")
    def test_is_installed_on_non_linux(self):
        """Test is_installed on non-Linux systems."""
        installer = LinuxUdevInstaller()
        assert installer.is_installed() is False

    @patch("sys.platform", "win32")
    def test_install_on_non_linux(self):
        """Test install returns NOT_LINUX on non-Linux systems."""
        installer = LinuxUdevInstaller()
        result = installer.install()
        assert result.status == UdevInstallStatus.NOT_LINUX

    @patch("sys.platform", "linux")
    def test_install_already_installed(self):
        """Test install returns ALREADY_INSTALLED when rules exist."""
        installer = LinuxUdevInstaller()
        with patch.object(Path, "exists", return_value=True):
            result = installer.install()
            assert result.status == UdevInstallStatus.ALREADY_INSTALLED

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    @patch("subprocess.run")
    def test_install_with_privilege_dialog_success(self, mock_subprocess, mock_dialog):
        """Test successful installation with privilege dialog."""
        # Mock privilege dialog returning success
        mock_dialog.run_with_privileges.return_value = (0, "", "")

        # Mock subprocess for udevadm
        mock_subprocess.return_value = MagicMock(returncode=0)

        installer = LinuxUdevInstaller()

        # Mock Path.exists for initial check (False) and post-install check (True)
        with patch.object(Path, "exists", side_effect=[False, True]):
            result = installer.install(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.SUCCESS
        assert mock_dialog.run_with_privileges.called

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    def test_install_with_privilege_dialog_denied(self, mock_dialog):
        """Test installation when user denies privileges."""
        # Mock privilege dialog returning denial (pkexec returns 126 on cancel)
        mock_dialog.run_with_privileges.return_value = (126, "", "User cancelled")

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=False):
            result = installer.install(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.PERMISSION_DENIED

    @pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test (requires os.geteuid)")
    @patch("sys.platform", "linux")
    @patch("os.geteuid", return_value=1000)
    def test_install_direct_without_root(self, _mock_geteuid):
        """Test direct installation without root privileges."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=False):
            result = installer.install(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.PERMISSION_DENIED

    @patch("subprocess.run")
    def test_reload_udev_rules_success(self, mock_subprocess):
        """Test successful udev rules reload."""
        mock_subprocess.return_value = MagicMock(returncode=0)

        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is True
        # Should call udevadm twice (reload and trigger)
        assert mock_subprocess.call_count == 2

    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_reload_udev_rules_udevadm_not_found(self, _mock_subprocess):
        """Test reload when udevadm is not found."""
        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is False

    @patch("subprocess.run", side_effect=Exception("Test error"))
    def test_reload_udev_rules_failure(self, _mock_subprocess):
        """Test reload failure."""
        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is False

    @patch("sys.platform", "win32")
    def test_uninstall_on_non_linux(self):
        """Test uninstall returns NOT_LINUX on non-Linux systems."""
        installer = LinuxUdevInstaller()
        result = installer.uninstall()

        assert result.status == UdevInstallStatus.NOT_LINUX

    @patch("sys.platform", "linux")
    def test_uninstall_not_installed(self):
        """Test uninstall when rules are not installed."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=False):
            result = installer.uninstall()

        assert result.status == UdevInstallStatus.SUCCESS

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    @patch("subprocess.run")
    def test_uninstall_with_privilege_dialog_success(self, mock_subprocess, mock_dialog):
        """Test successful uninstall with privilege dialog."""
        # Mock privilege dialog returning success
        mock_dialog.run_with_privileges.return_value = (0, "", "")

        # Mock subprocess for udevadm
        mock_subprocess.return_value = MagicMock(returncode=0)

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            result = installer.uninstall(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.SUCCESS

    @patch("sys.platform", "win32")
    def test_verify_installation_not_linux(self):
        """Test verify_installation on non-Linux systems."""
        installer = LinuxUdevInstaller()
        results = installer.verify_installation()

        assert results["rules_installed"] is False
        assert results["rules_readable"] is False
        assert results["udevadm_available"] is False
        assert results["correct_permissions"] is False

    @patch("sys.platform", "linux")
    @patch("pathlib.Path.stat")
    @patch("subprocess.run")
    def test_verify_installation_complete(self, mock_subprocess, mock_stat):
        """Test verify_installation with everything working."""
        # Mock file permissions (stat result with S_IROTH set)
        mock_stat_result = MagicMock()
        mock_stat_result.st_mode = 0o644
        mock_stat.return_value = mock_stat_result

        # Mock subprocess for udevadm
        mock_subprocess.return_value = MagicMock(returncode=0)

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", return_value="test content"):
                results = installer.verify_installation()

        assert results["rules_installed"] is True
        assert results["rules_readable"] is True
        assert results["udevadm_available"] is True
        assert results["correct_permissions"] is True

    @patch("sys.platform", "linux")
    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_verify_installation_partial(self, _mock_subprocess):
        """Test verify_installation with partial functionality."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", side_effect=Exception("Read error")):
                results = installer.verify_installation()

        assert results["rules_installed"] is True
        assert results["rules_readable"] is False
        assert results["udevadm_available"] is False
