"""Linux udev rules installer for automatic USB device detection.

This module provides functionality to install and manage udev rules
for pyMediaManager on Linux systems. The rules enable automatic detection
and handling of USB storage devices.
"""

import contextlib
from dataclasses import dataclass
from enum import Enum
import logging
import os
from pathlib import Path
from stat import S_IRGRP, S_IROTH, S_IRUSR, S_IWUSR
import subprocess
import sys
import tempfile
from typing import ClassVar

try:
    from app.ui.dialogs.privilege_dialog import LinuxPrivilegeDialog
except ImportError:
    LinuxPrivilegeDialog = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


class UdevInstallStatus(str, Enum):
    """Status of udev rules installation."""

    SUCCESS = "success"
    ALREADY_INSTALLED = "already_installed"
    PERMISSION_DENIED = "permission_denied"
    WRITE_FAILED = "write_failed"
    RELOAD_FAILED = "reload_failed"
    NOT_LINUX = "not_linux"


@dataclass
class UdevInstallResult:
    """Result of udev rules installation."""

    status: UdevInstallStatus
    message: str
    rules_path: Path | None = None


class LinuxUdevInstaller:
    """Installer for pyMediaManager udev rules on Linux systems.

    Manages installation, removal, and verification of udev rules that enable
    automatic USB device detection. Requires elevated privileges for system-level
    changes.
    """

    RULES_FILENAME: ClassVar[str] = "99-pymm-usb.rules"
    RULES_DIR: ClassVar[Path] = Path("/etc/udev/rules.d")

    # udev rules for USB storage detection
    UDEV_RULES: ClassVar[str] = """# pyMediaManager USB Storage Detection Rules
# Automatically trigger pyMediaManager notifications for USB storage devices

# Match USB storage devices (block devices)
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="disk", \\
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

# Match USB storage devices (partitions)
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="partition", \\
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

# Set ownership and permissions for pyMediaManager access
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", \\
    GROUP="plugdev", MODE="0660"
"""

    def __init__(self) -> None:
        """Initialize the udev installer."""
        self.logger = logging.getLogger(__name__)
        self.rules_path = self.RULES_DIR / self.RULES_FILENAME

    def is_linux(self) -> bool:
        """Check if running on Linux."""
        return sys.platform.startswith("linux")

    def is_installed(self) -> bool:
        """Check if udev rules are already installed.

        Returns:
            True if rules file exists, False otherwise
        """
        if not self.is_linux():
            return False
        return self.rules_path.exists()

    def get_rules_content(self) -> str:
        """Get the udev rules content to be installed.

        Returns:
            String containing udev rules
        """
        return self.UDEV_RULES

    def install(self, use_privilege_dialog: bool = True) -> UdevInstallResult:
        """Install udev rules for USB device detection.

        Args:
            use_privilege_dialog: If True, use GUI privilege dialog for elevation.
                                 If False, attempt direct installation (requires running as root)

        Returns:
            UdevInstallResult with status and message
        """
        # Check if running on Linux
        if not self.is_linux():
            return UdevInstallResult(
                status=UdevInstallStatus.NOT_LINUX,
                message="udev rules are only supported on Linux systems",
            )

        # Check if already installed
        if self.is_installed():
            return UdevInstallResult(
                status=UdevInstallStatus.ALREADY_INSTALLED,
                message=f"udev rules already installed at {self.rules_path}",
                rules_path=self.rules_path,
            )

        # Get rules content
        rules_content = self.get_rules_content()

        try:
            if use_privilege_dialog:
                # Use privilege dialog for elevated access
                result = self._install_with_privilege_dialog(rules_content)
            else:
                # Direct installation (requires root)
                result = self._install_direct(rules_content)

            return result

        except Exception as e:
            self.logger.exception("Failed to install udev rules")
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message=f"Installation failed: {e}",
            )

    def _install_with_privilege_dialog(self, rules_content: str) -> UdevInstallResult:  # noqa: PLR0911
        """Install udev rules using privilege dialog for elevation.

        Args:
            rules_content: Content of udev rules file

        Returns:
            UdevInstallResult with status
        """
        if LinuxPrivilegeDialog is None:
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message="LinuxPrivilegeDialog not available",
            )

        self.logger.info("Installing udev rules to %s with pkexec", self.rules_path)

        # Write rules content to temp file first
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".rules") as tmp:
                tmp.write(rules_content)
                tmp_path = tmp.name

            # Use pkexec to copy temp file to rules location
            returncode, _, stderr = LinuxPrivilegeDialog.run_with_privileges(
                command=["cp", tmp_path, str(self.rules_path)],
                timeout=30,
            )

            # Clean up temp file
            with contextlib.suppress(Exception):
                Path(tmp_path).unlink()

            # Check return code
            # pkexec returns 126 when user cancels, 127 when command not found
            if returncode == 126:
                return UdevInstallResult(
                    status=UdevInstallStatus.PERMISSION_DENIED,
                    message="Permission denied: User cancelled privilege request",
                )

            if returncode != 0:
                return UdevInstallResult(
                    status=UdevInstallStatus.WRITE_FAILED,
                    message=f"Failed to write rules file: {stderr}",
                )

            # Verify file was created
            if not self.rules_path.exists():
                return UdevInstallResult(
                    status=UdevInstallStatus.WRITE_FAILED,
                    message="Rules file was not created successfully",
                )

            self.logger.info("Successfully wrote rules to %s", self.rules_path)

            # Reload udev rules
            reload_result = self._reload_udev_rules()
            if not reload_result:
                return UdevInstallResult(
                    status=UdevInstallStatus.RELOAD_FAILED,
                    message="Rules installed but failed to reload udev. Reboot may be required.",
                    rules_path=self.rules_path,
                )

            return UdevInstallResult(
                status=UdevInstallStatus.SUCCESS,
                message="udev rules installed and activated successfully",
                rules_path=self.rules_path,
            )

        except Exception as e:
            self.logger.exception("Failed during privilege elevation")
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message=f"Installation failed: {e}",
            )

    def _install_direct(self, rules_content: str) -> UdevInstallResult:
        """Install udev rules directly (requires root privileges).

        Args:
            rules_content: Content of udev rules file

        Returns:
            UdevInstallResult with status
        """
        # Check if running as root (Linux only)
        if hasattr(os, "geteuid") and os.geteuid() != 0:
            return UdevInstallResult(
                status=UdevInstallStatus.PERMISSION_DENIED,
                message="Direct installation requires root privileges. Run with sudo or use privilege dialog.",
            )

        # Ensure rules directory exists
        if not self.RULES_DIR.exists():
            try:
                self.RULES_DIR.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                return UdevInstallResult(
                    status=UdevInstallStatus.WRITE_FAILED,
                    message=f"Failed to create rules directory: {e}",
                )

        # Write rules file
        try:
            self.rules_path.write_text(rules_content, encoding="utf-8")
            # Set proper permissions (readable by all, writable by owner)
            self.rules_path.chmod(S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH)
            self.logger.info("Successfully wrote rules to %s", self.rules_path)

            # Reload udev rules
            reload_result = self._reload_udev_rules()
            if not reload_result:
                return UdevInstallResult(
                    status=UdevInstallStatus.RELOAD_FAILED,
                    message="Rules installed but failed to reload udev. Reboot may be required.",
                    rules_path=self.rules_path,
                )

            return UdevInstallResult(
                status=UdevInstallStatus.SUCCESS,
                message="udev rules installed and activated successfully",
                rules_path=self.rules_path,
            )

        except OSError as e:
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message=f"Failed to write rules file: {e}",
            )
        except Exception as e:
            self.logger.exception("Unexpected error during installation")
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message=f"Installation failed: {e}",
            )

    def _reload_udev_rules(self) -> bool:
        """Reload udev rules to apply changes.

        Returns:
            True if reload successful, False otherwise
        """
        try:
            # Reload udev rules database
            subprocess.run(
                ["udevadm", "control", "--reload-rules"],
                check=True,
                capture_output=True,
                timeout=10,
            )

            # Trigger udev to process existing devices
            subprocess.run(
                ["udevadm", "trigger"],
                check=True,
                capture_output=True,
                timeout=10,
            )

            self.logger.info("Successfully reloaded udev rules")
            return True

        except FileNotFoundError:
            self.logger.warning("udevadm command not found")
            return False
        except subprocess.TimeoutExpired:
            self.logger.warning("udevadm command timed out")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.warning("Failed to reload udev rules: %s", e)
            return False
        except Exception as e:  # noqa: BLE001
            self.logger.warning("Error reloading udev rules: %s", e)
            return False

    def uninstall(self, use_privilege_dialog: bool = True) -> UdevInstallResult:  # noqa: PLR0911
        """Uninstall udev rules.

        Args:
            use_privilege_dialog: If True, use GUI privilege dialog for elevation.
                                 If False, attempt direct removal (requires running as root)

        Returns:
            UdevInstallResult with status and message
        """
        # Check if running on Linux
        if not self.is_linux():
            return UdevInstallResult(
                status=UdevInstallStatus.NOT_LINUX,
                message="udev rules are only supported on Linux systems",
            )

        # Check if installed
        if not self.is_installed():
            return UdevInstallResult(
                status=UdevInstallStatus.SUCCESS,
                message="udev rules are not installed",
            )

        try:
            if use_privilege_dialog:
                if LinuxPrivilegeDialog is None:
                    return UdevInstallResult(
                        status=UdevInstallStatus.WRITE_FAILED,
                        message="LinuxPrivilegeDialog not available",
                    )

                # Use pkexec to remove file
                returncode, _, stderr = LinuxPrivilegeDialog.run_with_privileges(
                    command=["rm", "-f", str(self.rules_path)],
                    timeout=30,
                )

                if returncode == 126:
                    return UdevInstallResult(
                        status=UdevInstallStatus.PERMISSION_DENIED,
                        message="Permission denied: User cancelled privilege request",
                    )

                if returncode != 0:
                    return UdevInstallResult(
                        status=UdevInstallStatus.WRITE_FAILED,
                        message=f"Failed to remove rules file: {stderr}",
                    )

            else:
                # Direct removal (requires root)
                if hasattr(os, "geteuid") and os.geteuid() != 0:
                    return UdevInstallResult(
                        status=UdevInstallStatus.PERMISSION_DENIED,
                        message="Direct removal requires root privileges. Run with sudo or use privilege dialog.",
                    )

                self.rules_path.unlink()

            # Reload udev rules
            self._reload_udev_rules()

            return UdevInstallResult(
                status=UdevInstallStatus.SUCCESS,
                message="udev rules uninstalled successfully",
            )

        except Exception as e:
            self.logger.exception("Failed to uninstall udev rules")
            return UdevInstallResult(
                status=UdevInstallStatus.WRITE_FAILED,
                message=f"Uninstallation failed: {e}",
            )

    def verify_installation(self) -> dict[str, bool]:
        """Verify udev rules installation status.

        Returns:
            Dictionary with verification results:
            - rules_installed: True if rules file exists
            - rules_readable: True if rules file is readable
            - udevadm_available: True if udevadm command is available
            - correct_permissions: True if file has correct permissions
        """
        results = {
            "rules_installed": False,
            "rules_readable": False,
            "udevadm_available": False,
            "correct_permissions": False,
        }

        # Check if not Linux
        if not self.is_linux():
            return results

        # Check if rules file exists
        results["rules_installed"] = self.rules_path.exists()

        if results["rules_installed"]:
            # Check if rules file is readable
            try:
                self.rules_path.read_text(encoding="utf-8")
                results["rules_readable"] = True
            except Exception:  # noqa: BLE001
                results["rules_readable"] = False

            # Check permissions
            try:
                stat_info = self.rules_path.stat()
                # Check if file is readable by others (should be)
                results["correct_permissions"] = bool(stat_info.st_mode & S_IROTH)
            except Exception:  # noqa: BLE001
                results["correct_permissions"] = False

        # Check if udevadm is available
        try:
            subprocess.run(
                ["udevadm", "--version"],
                check=True,
                capture_output=True,
                timeout=5,
            )
            results["udevadm_available"] = True
        except Exception:  # noqa: BLE001
            results["udevadm_available"] = False

        return results
