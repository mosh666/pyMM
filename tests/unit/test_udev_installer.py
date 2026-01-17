"""Tests for Linux udev rules installer."""

from pathlib import Path
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

    @pytest.mark.linux
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

    @pytest.mark.linux
    @patch("sys.platform", "linux")
    @patch("os.geteuid", return_value=1000)
    def test_install_direct_without_root(self, _mock_geteuid):  # noqa: PT019
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
    def test_reload_udev_rules_udevadm_not_found(self, _mock_subprocess):  # noqa: PT019
        """Test reload when udevadm is not found."""
        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is False

    @patch("subprocess.run", side_effect=Exception("Test error"))
    def test_reload_udev_rules_failure(self, _mock_subprocess):  # noqa: PT019
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
    def test_verify_installation_partial(self, _mock_subprocess):  # noqa: PT019
        """Test verify_installation with partial functionality."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "read_text", side_effect=Exception("Read error")):
                results = installer.verify_installation()

        assert results["rules_installed"] is True
        assert results["rules_readable"] is False
        assert results["udevadm_available"] is False


class TestEdgeCasesAndErrors:
    """Test suite for edge cases and error handling in udev installer."""

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog", None)
    def test_install_privilege_dialog_not_available(self):
        """Test installation when privilege dialog is not available."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=False):
            result = installer.install(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "not available" in result.message.lower()

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    def test_install_privilege_dialog_write_failed(self, mock_dialog):
        """Test installation when write command fails."""
        # Mock privilege dialog returning non-zero, non-126 exit code
        mock_dialog.run_with_privileges.return_value = (1, "", "Write error")

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=False):
            result = installer.install(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Write error" in result.message

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    def test_install_privilege_dialog_verification_failed(self, mock_dialog):
        """Test installation when file verification fails after write."""
        # Mock privilege dialog returning success but file doesn't exist after
        mock_dialog.run_with_privileges.return_value = (0, "", "")

        installer = LinuxUdevInstaller()

        # First exists check: False (not installed), second check: False (verification failed)
        with patch.object(Path, "exists", side_effect=[False, False]):
            result = installer.install(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "not created successfully" in result.message.lower()

    @patch("sys.platform", "linux")
    def test_install_direct_as_root_mkdir_failed(self):
        """Test direct installation when creating rules directory fails."""
        installer = LinuxUdevInstaller()

        with patch.object(
            Path, "exists", side_effect=[False, False]
        ):  # Not installed, rules dir doesn't exist
            with patch.object(Path, "mkdir", side_effect=OSError("Permission denied")):
                with patch.object(installer, "is_linux", return_value=True):
                    with patch(
                        "app.platform.linux.udev_installer.os.geteuid", return_value=0, create=True
                    ):
                        result = installer.install(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Failed to create rules directory" in result.message

    @patch("sys.platform", "linux")
    @patch("subprocess.run")
    def test_install_direct_write_failed(self, mock_subprocess):
        """Test direct installation when writing file fails."""
        installer = LinuxUdevInstaller()

        with patch.object(
            Path, "exists", side_effect=[False, True]
        ):  # Not installed, rules dir exists
            with patch.object(Path, "write_text", side_effect=OSError("Write error")):
                with patch.object(installer, "is_linux", return_value=True):
                    with patch(
                        "app.platform.linux.udev_installer.os.geteuid", return_value=0, create=True
                    ):
                        result = installer.install(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Failed to write rules file" in result.message

    @patch("sys.platform", "linux")
    @patch("subprocess.run")
    def test_install_direct_chmod_failed(self, mock_subprocess):
        """Test direct installation when chmod fails."""
        installer = LinuxUdevInstaller()

        with patch.object(
            Path, "exists", side_effect=[False, True]
        ):  # Not installed, rules dir exists
            with patch.object(Path, "write_text"):
                with patch.object(Path, "chmod", side_effect=Exception("chmod error")):
                    with patch.object(installer, "is_linux", return_value=True):
                        with patch(
                            "app.platform.linux.udev_installer.os.geteuid",
                            return_value=0,
                            create=True,
                        ):
                            result = installer.install(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Installation failed" in result.message

    @patch("sys.platform", "linux")
    @patch("subprocess.run", side_effect=FileNotFoundError)
    def test_install_direct_reload_failed(self, _mock_subprocess):  # noqa: PT019
        """Test direct installation when reload fails."""
        installer = LinuxUdevInstaller()

        with patch.object(
            Path, "exists", side_effect=[False, True]
        ):  # Not installed, rules dir exists
            with patch.object(Path, "write_text"):
                with patch.object(Path, "chmod"):
                    with patch.object(installer, "is_linux", return_value=True):
                        with patch(
                            "app.platform.linux.udev_installer.os.geteuid",
                            return_value=0,
                            create=True,
                        ):
                            result = installer.install(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.RELOAD_FAILED
        assert "failed to reload" in result.message.lower()
        assert result.rules_path is not None

    @patch("subprocess.run")
    def test_reload_timeout(self, mock_subprocess):
        """Test reload when udevadm times out."""
        import subprocess

        mock_subprocess.side_effect = subprocess.TimeoutExpired("udevadm", 10)

        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is False

    @patch("subprocess.run")
    def test_reload_called_process_error(self, mock_subprocess):
        """Test reload when udevadm returns non-zero exit code."""
        import subprocess

        mock_subprocess.side_effect = subprocess.CalledProcessError(1, "udevadm")

        installer = LinuxUdevInstaller()
        result = installer._reload_udev_rules()

        assert result is False

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    def test_uninstall_privilege_dialog_denied(self, mock_dialog):
        """Test uninstall when user denies privileges."""
        # Mock privilege dialog returning denial (pkexec returns 126 on cancel)
        mock_dialog.run_with_privileges.return_value = (126, "", "User cancelled")

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            result = installer.uninstall(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.PERMISSION_DENIED
        assert "User cancelled" in result.message

    @patch("sys.platform", "linux")
    @patch("app.platform.linux.udev_installer.LinuxPrivilegeDialog")
    def test_uninstall_privilege_dialog_failed(self, mock_dialog):
        """Test uninstall when removal command fails."""
        # Mock privilege dialog returning non-zero, non-126 exit code
        mock_dialog.run_with_privileges.return_value = (1, "", "Remove error")

        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            result = installer.uninstall(use_privilege_dialog=True)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Remove error" in result.message

    @patch("sys.platform", "linux")
    def test_uninstall_direct_without_root(self):
        """Test direct uninstall without root privileges."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(installer, "is_linux", return_value=True):
                with patch(
                    "app.platform.linux.udev_installer.os.geteuid", return_value=1000, create=True
                ):
                    result = installer.uninstall(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.PERMISSION_DENIED
        assert "root privileges" in result.message.lower()

    @patch("sys.platform", "linux")
    @patch("subprocess.run")
    def test_uninstall_direct_exception(self, mock_subprocess):
        """Test direct uninstall when exception occurs."""
        installer = LinuxUdevInstaller()

        with patch.object(Path, "exists", return_value=True):
            with patch.object(Path, "unlink", side_effect=Exception("Unlink error")):
                with patch.object(installer, "is_linux", return_value=True):
                    with patch(
                        "app.platform.linux.udev_installer.os.geteuid", return_value=0, create=True
                    ):
                        result = installer.uninstall(use_privilege_dialog=False)

        assert result.status == UdevInstallStatus.WRITE_FAILED
        assert "Uninstallation failed" in result.message
