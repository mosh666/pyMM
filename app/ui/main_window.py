"""
Main window for pyMediaManager application.
Uses Fluent Design with navigation interface.
"""
import logging
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon

try:
    from qfluentwidgets import (
        FluentWindow,
        NavigationItemPosition,
        FluentIcon,
        Theme,
        setTheme,
    )

    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    # Fallback to standard Qt widgets
    from PySide6.QtWidgets import QMainWindow as FluentWindow

from app.core.services.config_service import ConfigService
from app.core.services.storage_service import StorageService
from app.plugins.plugin_manager import PluginManager
from app.services.project_service import ProjectService


class MainWindow(FluentWindow if FLUENT_AVAILABLE else QWidget):
    """Main application window with Fluent Design interface."""

    def __init__(
        self,
        config_service: ConfigService,
        storage_service: StorageService,
        plugin_manager: PluginManager,
        project_service: ProjectService,
    ):
        super().__init__()
        
        self.logger = logging.getLogger(__name__)

        self.config_service = config_service
        self.storage_service = storage_service
        self.plugin_manager = plugin_manager
        self.project_service = project_service
        self.current_project = None

        self._init_window()
        self._init_navigation()
        self._apply_theme()

    def _init_window(self) -> None:
        """Initialize window properties."""
        config = self.config_service.get_config()

        self.setWindowTitle(config.app_name)
        self.resize(config.ui.window_width, config.ui.window_height)

    def _init_navigation(self) -> None:
        """Initialize navigation interface."""
        if not FLUENT_AVAILABLE:
            self._init_fallback_ui()
            return

        # Home/Dashboard
        self.home_interface = self._create_home_interface()
        self.addSubInterface(
            self.home_interface, FluentIcon.HOME, "Home", NavigationItemPosition.TOP
        )

        # Storage Management
        from app.ui.views.storage_view import StorageView

        self.storage_view = StorageView(self.storage_service)
        self.addSubInterface(
            self.storage_view, FluentIcon.FOLDER, "Storage", NavigationItemPosition.TOP
        )

        # Plugin Management
        from app.ui.views.plugin_view import PluginView

        self.plugin_view = PluginView(self.plugin_manager)
        self.addSubInterface(
            self.plugin_view, FluentIcon.APPLICATION, "Plugins", NavigationItemPosition.TOP
        )

        # Project Management
        from app.ui.views.project_view import ProjectView

        self.project_view = ProjectView(self.project_service)
        self.project_view.project_opened.connect(self._on_project_opened)
        self.addSubInterface(
            self.project_view, FluentIcon.FOLDER_ADD, "Projects", NavigationItemPosition.TOP
        )

        # Settings
        self.settings_interface = self._create_settings_interface()
        self.addSubInterface(
            self.settings_interface,
            FluentIcon.SETTING,
            "Settings",
            NavigationItemPosition.BOTTOM,
        )

    def _create_home_interface(self) -> QWidget:
        """Create home/dashboard interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Welcome message
        welcome = QLabel("Welcome to pyMediaManager")
        welcome_font = welcome.font()
        welcome_font.setPointSize(24)
        welcome_font.setBold(True)
        welcome.setFont(welcome_font)
        layout.addWidget(welcome)

        # Quick stats
        stats = QLabel(
            "Your portable media management solution<br><br>"
            "Use the navigation menu to:<br>"
            "• Manage storage drives<br>"
            "• Install and configure plugins<br>"
            "• Create and organize projects<br>"
            "• Adjust application settings"
        )
        stats.setWordWrap(True)
        layout.addWidget(stats)

        layout.addStretch()

        return widget

    def _create_settings_interface(self) -> QWidget:
        """Create settings interface."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)

        title = QLabel("Settings")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        description = QLabel(
            "Configure application settings, theme, plugins, and more.\n\n"
            "Click the button below to open the settings dialog."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Open settings button
        open_settings_btn = QPushButton("Open Settings")
        open_settings_btn.clicked.connect(self._open_settings_dialog)
        open_settings_btn.setMaximumWidth(200)
        layout.addWidget(open_settings_btn)

        layout.addStretch()

        return widget
    
    def _open_settings_dialog(self) -> None:
        """Open the settings dialog."""
        from app.ui.dialogs.settings_dialog import SettingsDialog
        
        dialog = SettingsDialog(self.config_service, self)
        dialog.exec()

    def _init_fallback_ui(self) -> None:
        """Initialize fallback UI when Fluent Widgets not available."""
        layout = QVBoxLayout(self)

        warning = QLabel(
            "⚠️ PySide6-Fluent-Widgets not installed\n\n"
            "Install with: pip install PySide6-Fluent-Widgets\n\n"
            "Running in fallback mode..."
        )
        warning.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning)

    def _apply_theme(self) -> None:
        """Apply theme based on configuration."""
        if not FLUENT_AVAILABLE:
            return

        config = self.config_service.get_config()

        if config.ui.theme == "dark":
            setTheme(Theme.DARK)
        elif config.ui.theme == "light":
            setTheme(Theme.LIGHT)
        else:
            # Auto mode - use system theme
            setTheme(Theme.AUTO)
    
    def _on_project_opened(self, project) -> None:
        """Handle project opened event."""
        from PySide6.QtWidgets import QMessageBox
        
        self.current_project = project
        
        # Update window title
        config = self.config_service.get_config()
        self.setWindowTitle(f"{config.app_name} - {project.name}")
        
        # Show notification
        QMessageBox.information(
            self,
            "Project Opened",
            f"Successfully opened project: {project.name}\n\nPath: {project.path}",
        )
