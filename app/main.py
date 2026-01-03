"""
Main application entry point for pyMediaManager.
Initializes services and launches the PySide6 GUI.
"""
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def get_app_root() -> Path:
    """Get the application root directory."""
    # APP_ROOT is parent of app/ directory
    return Path(__file__).parent.parent.resolve()


def run_application() -> int:
    """
    Initialize and run the pyMediaManager application.
    
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    app.setApplicationName("pyMediaManager")
    app.setOrganizationName("mosh666")
    app.setApplicationVersion("0.0.1")

    # TODO: Initialize services (config, logging, storage, plugins)
    # TODO: Check first-run state and show wizard if needed
    # TODO: Create and show main window

    # Temporary placeholder
    from PySide6.QtWidgets import QMessageBox

    msg = QMessageBox()
    msg.setWindowTitle("pyMediaManager")
    msg.setText(
        f"pyMediaManager v0.0.1\n\n"
        f"Application Root: {get_app_root()}\n\n"
        f"Framework initialized successfully!\n"
        f"GUI implementation in progress..."
    )
    msg.exec()

    return 0


if __name__ == "__main__":
    sys.exit(run_application())
