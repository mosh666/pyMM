"""
Platform-specific privilege escalation dialogs for system operations.
"""

from enum import Enum
import subprocess
import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QLabel, QWidget
from qfluentwidgets import MessageBoxBase, PushButton

# Module-level privilege cache for session persistence
_privilege_cache: dict[str, bool] = {}


class PrivilegeStatus(str, Enum):
    """Status of privilege elevation."""

    GRANTED = "granted"  # User granted privileges
    DENIED = "denied"  # User denied privileges
    FAILED = "failed"  # Privilege elevation failed
    CACHED = "cached"  # Previously granted (session cache)


class LinuxPrivilegeDialog(MessageBoxBase):
    """Dialog for Linux privilege escalation using pkexec."""

    def __init__(self, operation: str, reason: str, parent: QWidget | None = None):
        """Initialize Linux privilege dialog.

        Args:
            operation: Name of operation requiring privileges
            reason: Explanation of why privileges are needed
            parent: Parent widget
        """
        super().__init__(parent)
        self.operation = operation
        self.reason = reason
        self.status = PrivilegeStatus.DENIED

        self.titleLabel = QLabel("Administrator Access Required")
        self.contentLabel = QLabel(
            f"The operation '{operation}' requires administrator privileges.\n\n"
            f"{reason}\n\n"
            f"You will be prompted to enter your password using PolicyKit."
        )

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)

        self.yesButton = PushButton("Grant Access")
        self.cancelButton = PushButton("Cancel")

        self.yesButton.clicked.connect(self._on_grant)
        self.cancelButton.clicked.connect(self._on_cancel)

        self.widget.setMinimumWidth(400)

    def _on_grant(self) -> None:
        """Handle grant button click."""
        self.status = PrivilegeStatus.GRANTED
        self.accept()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.status = PrivilegeStatus.DENIED
        self.reject()

    @staticmethod
    def ask(operation: str, reason: str, parent: QWidget | None = None) -> PrivilegeStatus:
        """Show dialog and return privilege status.

        Args:
            operation: Name of operation requiring privileges
            reason: Explanation of why privileges are needed
            parent: Parent widget

        Returns:
            PrivilegeStatus indicating result
        """
        # Check cache first
        cache_key = f"linux:{operation}"
        if _privilege_cache.get(cache_key):
            return PrivilegeStatus.CACHED

        dialog = LinuxPrivilegeDialog(operation, reason, parent)
        dialog.exec()

        if dialog.status == PrivilegeStatus.GRANTED:
            # Cache successful grant
            _privilege_cache[cache_key] = True

        return dialog.status

    @staticmethod
    def run_with_privileges(command: list[str], timeout: int = 30) -> tuple[int, str, str]:
        """Run command with pkexec elevation.

        Args:
            command: Command and arguments to run
            timeout: Timeout in seconds

        Returns:
            Tuple of (returncode, stdout, stderr)
        """
        try:
            result = subprocess.run(  # noqa: S603
                ["pkexec", *command],  # noqa: S607
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return (result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired:
            return (-1, "", "Command timed out")
        except Exception as e:
            return (-1, "", str(e))


class MacOSPermissionDialog(MessageBoxBase):
    """Dialog for macOS Full Disk Access permission instructions."""

    def __init__(self, reason: str, parent: QWidget | None = None):
        """Initialize macOS permission dialog.

        Args:
            reason: Explanation of why Full Disk Access is needed
            parent: Parent widget
        """
        super().__init__(parent)
        self.reason = reason
        self.status = PrivilegeStatus.DENIED

        self.titleLabel = QLabel("Full Disk Access Required")
        self.contentLabel = QLabel(
            f"{reason}\n\n"
            f"To grant Full Disk Access:\n"
            f"1. Click 'Open System Settings' below\n"
            f"2. Navigate to Privacy & Security → Full Disk Access\n"
            f"3. Enable access for this application\n"
            f"4. Restart the application"
        )

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)

        self.openSettingsButton = PushButton("Open System Settings")
        self.laterButton = PushButton("Later")

        self.openSettingsButton.clicked.connect(self._on_open_settings)
        self.laterButton.clicked.connect(self._on_later)

        self.widget.setMinimumWidth(450)

    def _on_open_settings(self) -> None:
        """Open macOS System Settings."""
        # Open Privacy & Security settings
        url = QUrl("x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles")
        if not QDesktopServices.openUrl(url):
            # Fallback to general System Settings
            QDesktopServices.openUrl(QUrl("x-apple.systempreferences:"))

        self.status = PrivilegeStatus.GRANTED
        self.accept()

    def _on_later(self) -> None:
        """Handle later button click."""
        self.status = PrivilegeStatus.DENIED
        self.reject()

    @staticmethod
    def ask(reason: str, parent: QWidget | None = None) -> PrivilegeStatus:
        """Show dialog and return privilege status.

        Args:
            reason: Explanation of why Full Disk Access is needed
            parent: Parent widget

        Returns:
            PrivilegeStatus indicating result
        """
        # Check cache first
        cache_key = "macos:full_disk_access"
        if _privilege_cache.get(cache_key):
            return PrivilegeStatus.CACHED

        dialog = MacOSPermissionDialog(reason, parent)
        dialog.exec()

        if dialog.status == PrivilegeStatus.GRANTED:
            # Cache successful grant (user opened settings)
            _privilege_cache[cache_key] = True

        return dialog.status


def request_privileges(
    operation: str, reason: str, parent: QWidget | None = None
) -> PrivilegeStatus:
    """Request platform-specific privileges.

    Args:
        operation: Name of operation requiring privileges
        reason: Explanation of why privileges are needed
        parent: Parent widget

    Returns:
        PrivilegeStatus indicating result
    """
    if sys.platform == "linux":
        return LinuxPrivilegeDialog.ask(operation, reason, parent)
    if sys.platform == "darwin":
        return MacOSPermissionDialog.ask(reason, parent)
    if sys.platform == "win32":
        # Windows UAC is handled automatically by system
        return PrivilegeStatus.GRANTED
    return PrivilegeStatus.DENIED


def clear_privilege_cache() -> None:
    """Clear the privilege cache (useful for testing or logout)."""
    _privilege_cache.clear()
