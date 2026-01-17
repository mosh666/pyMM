"""Dialog for handling tool version mismatches.

Prompts user when a system tool is found but doesn't meet version requirements.
"""

from enum import Enum

from PySide6.QtWidgets import (
    QLabel,
    QPushButton,
    QWidget,
)
from qfluentwidgets import MessageBoxBase


class VersionChoice(str, Enum):
    """User's choice for handling version mismatch."""

    INSTALL_PORTABLE = "install_portable"
    USE_ANYWAY = "use_anyway"
    CANCEL = "cancel"


class ToolVersionDialog(MessageBoxBase):
    """Dialog for tool version mismatch resolution.

    Shows detected version, required version, and gives user choice to:
    - Install portable version (recommended)
    - Use system version anyway (may cause issues)
    - Cancel operation
    """

    def __init__(
        self,
        tool_name: str,
        detected_version: str,
        required_constraint: str,
        parent: QWidget | None = None,
    ):
        """Initialize tool version dialog.

        Args:
            tool_name: Name of the tool (e.g., "Git", "FFmpeg")
            detected_version: Version detected on system
            required_constraint: Required version constraint
            parent: Parent widget
        """
        super().__init__(parent)
        self.tool_name = tool_name
        self.detected_version = detected_version
        self.required_constraint = required_constraint
        self.choice = VersionChoice.CANCEL

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        # Title
        self.titleLabel = QLabel(f"{self.tool_name} Version Incompatible", self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 8px;")

        # Version info
        version_text = (
            f"<b>Detected Version:</b> {self.detected_version}<br>"
            f"<b>Required Version:</b> {self.required_constraint}<br><br>"
            f"The {self.tool_name} version on your system does not meet "
            f"the minimum requirements for pyMM."
        )
        self.versionLabel = QLabel(version_text, self)
        self.versionLabel.setWordWrap(True)

        # Warning text
        self.warningLabel = QLabel(
            "Using an incompatible version may cause errors or missing features. "
            "We recommend installing the portable version managed by pyMM.",
            self,
        )
        self.warningLabel.setWordWrap(True)
        self.warningLabel.setStyleSheet("color: #d97706;")  # Warning color

        # Add widgets to layout
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.versionLabel)
        self.viewLayout.addSpacing(10)
        self.viewLayout.addWidget(self.warningLabel)

        # Custom buttons
        self.yesButton.setText("Install Portable Version")
        self.yesButton.setStyleSheet("background-color: #0078d4;")  # Accent color
        self.cancelButton.setText("Cancel")

        # Add "Use Anyway" button
        self.useAnywayButton = QPushButton("Use System Version Anyway", self)
        self.useAnywayButton.setStyleSheet("background-color: #d97706;")  # Warning color
        self.useAnywayButton.clicked.connect(self._on_use_anyway)
        self.buttonLayout.insertWidget(1, self.useAnywayButton)

        # Connect signals
        self.yesButton.clicked.connect(self._on_install_portable)
        self.cancelButton.clicked.connect(self._on_cancel)

        # Set dialog properties
        self.widget.setMinimumWidth(450)

    def _on_install_portable(self) -> None:
        """Handle install portable button click."""
        self.choice = VersionChoice.INSTALL_PORTABLE
        self.accept()

    def _on_use_anyway(self) -> None:
        """Handle use anyway button click."""
        self.choice = VersionChoice.USE_ANYWAY
        self.accept()

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.choice = VersionChoice.CANCEL
        self.reject()

    @staticmethod
    def ask(
        tool_name: str,
        detected_version: str,
        required_constraint: str,
        parent: QWidget | None = None,
    ) -> VersionChoice:
        """Show dialog and return user's choice.

        Convenience static method for showing the dialog.

        Args:
            tool_name: Name of the tool
            detected_version: Detected version string
            required_constraint: Required version constraint
            parent: Parent widget

        Returns:
            VersionChoice indicating user's selection
        """
        dialog = ToolVersionDialog(tool_name, detected_version, required_constraint, parent)
        dialog.exec()
        return dialog.choice
