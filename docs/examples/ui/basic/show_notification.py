#!/usr/bin/env python3
"""Simple notification example.

This example demonstrates:
- Showing info messages
- Displaying warnings
- Error notifications
- Success messages

Note: Requires a display environment (not headless).
"""

import sys

from PySide6.QtWidgets import QApplication, QMessageBox, QPushButton, QVBoxLayout, QWidget


class NotificationDemo(QWidget):
    """Simple notification demonstration window."""

    def __init__(self) -> None:
        """Initialize notification demo window."""
        super().__init__()
        self.setWindowTitle("pyMM Notification Examples")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Create buttons for each notification type
        info_btn = QPushButton("Show Info Message")
        info_btn.clicked.connect(self.show_info)
        layout.addWidget(info_btn)

        warning_btn = QPushButton("Show Warning")
        warning_btn.clicked.connect(self.show_warning)
        layout.addWidget(warning_btn)

        error_btn = QPushButton("Show Error")
        error_btn.clicked.connect(self.show_error)
        layout.addWidget(error_btn)

        success_btn = QPushButton("Show Success")
        success_btn.clicked.connect(self.show_success)
        layout.addWidget(success_btn)

        question_btn = QPushButton("Ask Question")
        question_btn.clicked.connect(self.show_question)
        layout.addWidget(question_btn)

        self.setLayout(layout)

    def show_info(self) -> None:
        """Show information message."""
        QMessageBox.information(
            self,
            "Information",
            "This is an informational message.\n\nUsed for general notifications.",
        )

    def show_warning(self) -> None:
        """Show warning message."""
        QMessageBox.warning(
            self,
            "Warning",
            "This is a warning message.\n\nUsed to alert users about potential issues.",
        )

    def show_error(self) -> None:
        """Show error message."""
        QMessageBox.critical(
            self, "Error", "This is an error message.\n\nUsed when operations fail."
        )

    def show_success(self) -> None:
        """Show success message (using info with custom title)."""
        QMessageBox.information(
            self, "Success", "Operation completed successfully!\n\nProject created and initialized."
        )

    def show_question(self) -> None:
        """Show question dialog and handle response."""
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            "Do you want to delete this project?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,  # Default button
        )

        if reply == QMessageBox.Yes:
            QMessageBox.information(self, "Result", "User clicked Yes")
        else:
            QMessageBox.information(self, "Result", "User clicked No")


def main() -> None:
    """Run the notification demo application."""
    app = QApplication(sys.argv)

    window = NotificationDemo()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
