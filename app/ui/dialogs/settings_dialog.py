"""
Settings dialog for pyMediaManager.

Provides a tabbed interface for configuring:
- General settings (theme, logging)
- Plugin settings (auto-update, timeouts)
- Storage settings (default locations)
- Git settings (user name, email)
"""

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QPushButton,
    QWidget,
    QLabel,
    QComboBox,
    QCheckBox,
    QSpinBox,
    QLineEdit,
    QFormLayout,
    QGroupBox,
    QMessageBox,
)
from PySide6.QtCore import Qt

from app.core.services.config_service import ConfigService, LogLevel


class SettingsDialog(QDialog):
    """
    Main settings dialog with tabbed interface.
    
    Allows users to configure:
    - Application appearance and behavior
    - Plugin management settings
    - Storage and path preferences
    - Git integration settings
    """
    
    def __init__(self, config_service: ConfigService, parent=None):
        super().__init__(parent)
        self.config_service = config_service
        self.config = config_service.get_config()
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumSize(700, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.general_tab = self._create_general_tab()
        self.tabs.addTab(self.general_tab, "General")
        
        self.plugins_tab = self._create_plugins_tab()
        self.tabs.addTab(self.plugins_tab, "Plugins")
        
        self.storage_tab = self._create_storage_tab()
        self.tabs.addTab(self.storage_tab, "Storage")
        
        self.git_tab = self._create_git_tab()
        self.tabs.addTab(self.git_tab, "Git")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self._apply_settings)
        button_layout.addWidget(self.apply_button)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._ok_clicked)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _create_general_tab(self) -> QWidget:
        """Create the General settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Appearance section
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Auto", "Light", "Dark"])
        appearance_layout.addRow("Theme:", self.theme_combo)
        
        layout.addWidget(appearance_group)
        
        # Window section
        window_group = QGroupBox("Window")
        window_layout = QFormLayout(window_group)
        
        self.window_width_spin = QSpinBox()
        self.window_width_spin.setRange(800, 3840)
        self.window_width_spin.setSingleStep(100)
        window_layout.addRow("Default Width:", self.window_width_spin)
        
        self.window_height_spin = QSpinBox()
        self.window_height_spin.setRange(600, 2160)
        self.window_height_spin.setSingleStep(100)
        window_layout.addRow("Default Height:", self.window_height_spin)
        
        layout.addWidget(window_group)
        
        # Logging section
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        self.console_logging_check = QCheckBox("Enable console logging")
        logging_layout.addRow("", self.console_logging_check)
        
        self.file_logging_check = QCheckBox("Enable file logging")
        logging_layout.addRow("", self.file_logging_check)
        
        layout.addWidget(logging_group)
        
        # Startup section
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.show_first_run_check = QCheckBox("Show first-run wizard on next startup")
        startup_layout.addWidget(self.show_first_run_check)
        
        layout.addWidget(startup_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_plugins_tab(self) -> QWidget:
        """Create the Plugins settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Updates section
        updates_group = QGroupBox("Updates")
        updates_layout = QVBoxLayout(updates_group)
        
        self.auto_update_check = QCheckBox("Automatically check for plugin updates")
        updates_layout.addWidget(self.auto_update_check)
        
        layout.addWidget(updates_group)
        
        # Downloads section
        downloads_group = QGroupBox("Downloads")
        downloads_layout = QFormLayout(downloads_group)
        
        self.download_timeout_spin = QSpinBox()
        self.download_timeout_spin.setRange(30, 3600)
        self.download_timeout_spin.setSingleStep(30)
        self.download_timeout_spin.setSuffix(" seconds")
        downloads_layout.addRow("Timeout:", self.download_timeout_spin)
        
        self.parallel_downloads_spin = QSpinBox()
        self.parallel_downloads_spin.setRange(1, 10)
        downloads_layout.addRow("Parallel Downloads:", self.parallel_downloads_spin)
        
        layout.addWidget(downloads_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_storage_tab(self) -> QWidget:
        """Create the Storage settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Paths section
        paths_group = QGroupBox("Default Paths")
        paths_layout = QFormLayout(paths_group)
        
        info_label = QLabel(
            "These paths are relative to the drive root.\n"
            "Changes require application restart."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        paths_layout.addRow("", info_label)
        
        self.projects_dir_edit = QLineEdit()
        paths_layout.addRow("Projects Directory:", self.projects_dir_edit)
        
        self.plugins_dir_edit = QLineEdit()
        paths_layout.addRow("Plugins Directory:", self.plugins_dir_edit)
        
        self.logs_dir_edit = QLineEdit()
        paths_layout.addRow("Logs Directory:", self.logs_dir_edit)
        
        layout.addWidget(paths_group)
        
        layout.addStretch()
        
        return widget
    
    def _create_git_tab(self) -> QWidget:
        """Create the Git settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # User section
        user_group = QGroupBox("User Identity")
        user_layout = QFormLayout(user_group)
        
        info_label = QLabel(
            "Configure your Git identity for project commits.\n"
            "These settings are used when initializing new projects."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        user_layout.addRow("", info_label)
        
        self.git_user_name_edit = QLineEdit()
        self.git_user_name_edit.setPlaceholderText("John Doe")
        user_layout.addRow("Name:", self.git_user_name_edit)
        
        self.git_user_email_edit = QLineEdit()
        self.git_user_email_edit.setPlaceholderText("john.doe@example.com")
        user_layout.addRow("Email:", self.git_user_email_edit)
        
        layout.addWidget(user_group)
        
        # Behavior section
        behavior_group = QGroupBox("Behavior")
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.auto_init_git_check = QCheckBox("Automatically initialize Git for new projects")
        self.auto_init_git_check.setChecked(True)
        behavior_layout.addWidget(self.auto_init_git_check)
        
        layout.addWidget(behavior_group)
        
        layout.addStretch()
        
        return widget
    
    def _load_settings(self):
        """Load current settings into the UI."""
        # General tab
        theme_map = {"auto": 0, "light": 1, "dark": 2}
        self.theme_combo.setCurrentIndex(theme_map.get(self.config.ui.theme.lower(), 0))
        self.window_width_spin.setValue(self.config.ui.window_width)
        self.window_height_spin.setValue(self.config.ui.window_height)
        self.log_level_combo.setCurrentText(self.config.logging.level.value)
        self.console_logging_check.setChecked(self.config.logging.console_enabled)
        self.file_logging_check.setChecked(self.config.logging.file_enabled)
        self.show_first_run_check.setChecked(self.config.ui.show_first_run)
        
        # Plugins tab
        self.auto_update_check.setChecked(self.config.plugins.auto_update_check)
        self.download_timeout_spin.setValue(self.config.plugins.download_timeout)
        self.parallel_downloads_spin.setValue(self.config.plugins.parallel_downloads)
        
        # Storage tab
        self.projects_dir_edit.setText(self.config.paths.projects_dir)
        self.plugins_dir_edit.setText(self.config.paths.plugins_dir)
        self.logs_dir_edit.setText(self.config.paths.logs_dir)
        
        # Git tab - load from git config if available
        try:
            import git
            config = git.GitConfigParser()
            self.git_user_name_edit.setText(config.get_value("user", "name", ""))
            self.git_user_email_edit.setText(config.get_value("user", "email", ""))
        except:
            pass
    
    def _apply_settings(self):
        """Apply settings without closing dialog."""
        try:
            # Build update dictionary
            updates = {}
            
            # UI settings
            theme_values = ["auto", "light", "dark"]
            ui_updates = {
                "theme": theme_values[self.theme_combo.currentIndex()],
                "window_width": self.window_width_spin.value(),
                "window_height": self.window_height_spin.value(),
                "show_first_run": self.show_first_run_check.isChecked(),
            }
            updates["ui"] = ui_updates
            
            # Logging settings
            logging_updates = {
                "level": self.log_level_combo.currentText(),
                "console_enabled": self.console_logging_check.isChecked(),
                "file_enabled": self.file_logging_check.isChecked(),
            }
            updates["logging"] = logging_updates
            
            # Plugin settings
            plugins_updates = {
                "auto_update_check": self.auto_update_check.isChecked(),
                "download_timeout": self.download_timeout_spin.value(),
                "parallel_downloads": self.parallel_downloads_spin.value(),
            }
            updates["plugins"] = plugins_updates
            
            # Path settings
            paths_updates = {
                "projects_dir": self.projects_dir_edit.text(),
                "plugins_dir": self.plugins_dir_edit.text(),
                "logs_dir": self.logs_dir_edit.text(),
            }
            updates["paths"] = paths_updates
            
            # Save configuration
            self.config_service.update_config(**updates)
            
            # Update Git config
            self._update_git_config()
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved successfully.\n\n"
                "Some changes may require restarting the application.",
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings:\n{str(e)}",
            )
    
    def _update_git_config(self):
        """Update global Git configuration."""
        try:
            import git
            
            name = self.git_user_name_edit.text().strip()
            email = self.git_user_email_edit.text().strip()
            
            if name or email:
                config = git.GitConfigParser()
                
                if name:
                    config.set_value("user", "name", name)
                
                if email:
                    config.set_value("user", "email", email)
                
                config.release()
        except Exception as e:
            print(f"Warning: Could not update Git config: {e}")
    
    def _ok_clicked(self):
        """Handle OK button click."""
        self._apply_settings()
        self.accept()
