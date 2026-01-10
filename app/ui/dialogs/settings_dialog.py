"""
Settings dialog for pyMediaManager.

Provides a tabbed interface for configuring:
- General settings (theme, logging)
- Plugin settings (auto-update, timeouts)
- Storage settings (default locations)
- Git settings (user name, email)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.services.config_service import ConfigService, ExecutionPreference
from app.plugins.system_tool_detector import SystemToolDetector

if TYPE_CHECKING:
    from app.plugins.plugin_base import PluginManifest


class SettingsDialog(QDialog):
    """
    Main settings dialog with tabbed interface.

    Allows users to configure:
    - Application appearance and behavior
    - Plugin management settings
    - Storage and path preferences
    - Git integration settings
    """

    def __init__(self, config_service: ConfigService, parent: QWidget | None = None) -> None:
        """Initialize settings dialog.

        Args:
            config_service: Configuration service instance.
            parent: Parent widget (optional).

        Examples:
            >>> dialog = SettingsDialog(config_service)
        """
        super().__init__(parent)

        self.logger = logging.getLogger(__name__)
        self.config_service = config_service
        self.config = config_service.get_config()

        self._init_ui()
        self._load_settings()

    def _init_ui(self) -> None:
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

        self.plugin_prefs_tab = self._create_plugin_preferences_tab()
        self.tabs.addTab(self.plugin_prefs_tab, "Plugin Preferences")

        self.storage_tab = self._create_storage_tab()
        self.tabs.addTab(self.storage_tab, "Storage")

        self.git_tab = self._create_git_tab()
        self.tabs.addTab(self.git_tab, "Git")

        self.about_tab = self._create_about_tab()
        self.tabs.addTab(self.about_tab, "About")

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

    def _create_plugin_preferences_tab(self) -> QWidget:
        """Create the Plugin Preferences settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Info label
        info_label = QLabel(
            "Configure execution preferences for each plugin.\n"
            "Auto: Use plugin's default | System: Prefer system packages | Portable: Use portable binaries"
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # Scroll area for plugin preferences
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)

        # Create preference widget for each plugin
        self.plugin_pref_widgets = {}

        try:
            # Get available plugins
            plugins = self._get_available_plugins()

            if plugins:
                for plugin_name, manifest in plugins.items():
                    pref_widget = self._create_plugin_preference_widget(plugin_name, manifest)
                    self.plugin_pref_widgets[plugin_name] = pref_widget
                    scroll_layout.addWidget(pref_widget)
            else:
                placeholder = QLabel("No plugins available. Discover plugins from main window.")
                placeholder.setStyleSheet("color: gray; font-style: italic;")
                scroll_layout.addWidget(placeholder)
        except Exception as e:
            self.logger.warning(f"Could not load plugin list: {e}")
            placeholder = QLabel(f"Error loading plugins: {e}")
            placeholder.setStyleSheet("color: red;")
            scroll_layout.addWidget(placeholder)

        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        return widget

    def _get_available_plugins(self) -> dict[str, PluginManifest]:
        """Get available plugins from discovered manifests."""
        # Try to get from parent window's plugin manager
        if hasattr(self.parent(), "plugin_manager"):
            return self.parent().plugin_manager.manifests

        # Fallback: create temporary plugin manager to discover plugins
        from pathlib import Path

        plugins_dir = Path(self.config.paths.plugins_dir)
        manifests_dir = Path(__file__).parent.parent.parent.parent / "plugins"

        if manifests_dir.exists():
            from app.plugins.plugin_manager import PluginManager

            temp_manager = PluginManager(plugins_dir, manifests_dir)
            temp_manager.discover_plugins()
            return temp_manager.manifests

        return {}

    def _create_plugin_preference_widget(
        self, plugin_name: str, manifest: PluginManifest
    ) -> QGroupBox:
        """Create a preference widget for a single plugin."""
        group = QGroupBox(manifest.name)
        layout = QVBoxLayout(group)

        # Plugin info
        info_layout = QHBoxLayout()
        info_label = QLabel(f"v{manifest.version} - {manifest.description}")
        info_label.setStyleSheet("color: gray; font-style: italic;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)

        # Execution preference radio buttons
        pref_layout = QHBoxLayout()
        pref_label = QLabel("Execution Mode:")
        pref_layout.addWidget(pref_label)

        button_group = QButtonGroup(group)
        button_group.setObjectName(f"pref_group_{plugin_name}")

        auto_radio = QRadioButton("Auto")
        auto_radio.setToolTip("Use plugin's default prefer_system setting")
        button_group.addButton(auto_radio, 0)
        pref_layout.addWidget(auto_radio)

        system_radio = QRadioButton("System Package")
        system_radio.setToolTip("Prefer system-installed package")
        button_group.addButton(system_radio, 1)
        pref_layout.addWidget(system_radio)

        portable_radio = QRadioButton("Portable Binary")
        portable_radio.setToolTip("Use portable binary distribution")
        button_group.addButton(portable_radio, 2)
        pref_layout.addWidget(portable_radio)

        pref_layout.addStretch()
        layout.addLayout(pref_layout)

        # System availability status
        status_layout = QHBoxLayout()
        status_label = QLabel("System Status:")
        status_layout.addWidget(status_label)

        system_status = self._check_system_availability(plugin_name, manifest)
        status_value = QLabel(system_status)
        if "Available" in system_status:
            status_value.setStyleSheet("color: green; font-weight: bold;")
        elif "Not found" in system_status:
            status_value.setStyleSheet("color: orange;")
        else:
            status_value.setStyleSheet("color: gray;")
        status_layout.addWidget(status_value)
        status_layout.addStretch()
        layout.addLayout(status_layout)

        # Enabled checkbox
        enabled_layout = QHBoxLayout()
        enabled_check = QCheckBox("Plugin Enabled")
        enabled_check.setObjectName(f"enabled_{plugin_name}")
        enabled_check.setChecked(True)
        enabled_layout.addWidget(enabled_check)
        enabled_layout.addStretch()
        layout.addLayout(enabled_layout)

        # Notes field
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)

        notes_edit = QTextEdit()
        notes_edit.setObjectName(f"notes_{plugin_name}")
        notes_edit.setMaximumHeight(60)
        notes_edit.setPlaceholderText("Optional notes about this plugin...")
        layout.addWidget(notes_edit)

        # Store references for later access
        group.setProperty("button_group", button_group)
        group.setProperty("enabled_check", enabled_check)
        group.setProperty("notes_edit", notes_edit)
        group.setProperty("plugin_id", plugin_name)

        return group

    def _check_system_availability(self, plugin_name: str, manifest: PluginManifest) -> str:  # noqa: PLR0911
        """Check if system package is available for this plugin."""
        import sys

        # Get platform config
        platform_key = (
            "windows"
            if sys.platform == "win32"
            else ("macos" if sys.platform == "darwin" else "linux")
        )

        # Check if manifest has platform configs (v2 schema)
        if not hasattr(manifest, "platforms") or not manifest.platforms:
            return "Legacy plugin (no platform config)"

        platform_config = manifest.platforms.get(platform_key)
        if not platform_config:
            return f"Not supported on {platform_key}"

        # Check if has system package info
        if not hasattr(platform_config, "system_package") or not platform_config.system_package:
            return "No system package available"

        # Try to detect system tool
        try:
            detector = SystemToolDetector()
            tool_info = detector.find_system_tool(
                platform_config.system_package, platform_config.version_constraint
            )

            if tool_info and tool_info.status.value == "found_valid":
                return f"Available: {platform_config.system_package} v{tool_info.version}"
            if tool_info and tool_info.status.value == "found_invalid":
                return f"Found but wrong version: v{tool_info.version}"
            return f"Not found: {platform_config.system_package}"
        except Exception:
            return "Error checking system"

    def _create_storage_tab(self) -> QWidget:
        """Create the Storage settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Paths section
        paths_group = QGroupBox("Default Paths")
        paths_layout = QFormLayout(paths_group)

        info_label = QLabel(
            "These paths are relative to the drive root.\nChanges require application restart."
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

    def _load_settings(self) -> None:
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
            self.git_user_name_edit.setText(str(config.get_value("user", "name", "")))
            self.git_user_email_edit.setText(str(config.get_value("user", "email", "")))
        except (ImportError, Exception):
            # Git not available or config error - use empty values
            pass

        # Plugin Preferences tab
        self._load_plugin_preferences()

    def _load_plugin_preferences(self) -> None:
        """Load plugin preferences into UI widgets."""
        for plugin_id, widget in self.plugin_pref_widgets.items():
            # Get preference from config
            pref = self.config_service.get_plugin_preference(plugin_id)

            # Set radio button based on execution_preference
            button_group = widget.property("button_group")
            if pref.execution_preference == ExecutionPreference.AUTO:
                button_group.button(0).setChecked(True)
            elif pref.execution_preference == ExecutionPreference.SYSTEM:
                button_group.button(1).setChecked(True)
            elif pref.execution_preference == ExecutionPreference.PORTABLE:
                button_group.button(2).setChecked(True)

            # Set enabled checkbox
            enabled_check = widget.property("enabled_check")
            enabled_check.setChecked(pref.enabled)

            # Set notes
            notes_edit = widget.property("notes_edit")
            notes_edit.setPlainText(pref.notes)

    def _save_plugin_preferences(self) -> None:
        """Save plugin preferences from UI widgets."""
        from app.core.services.config_service import PluginPreferences

        for plugin_id, widget in self.plugin_pref_widgets.items():
            # Get values from UI
            button_group = widget.property("button_group")
            checked_id = button_group.checkedId()

            # Map button ID to ExecutionPreference
            if checked_id == 0:
                exec_pref = ExecutionPreference.AUTO
            elif checked_id == 1:
                exec_pref = ExecutionPreference.SYSTEM
            elif checked_id == 2:
                exec_pref = ExecutionPreference.PORTABLE
            else:
                exec_pref = ExecutionPreference.AUTO

            # Get enabled state
            enabled_check = widget.property("enabled_check")
            enabled = enabled_check.isChecked()

            # Get notes
            notes_edit = widget.property("notes_edit")
            notes = notes_edit.toPlainText()

            # Create and save preference
            pref = PluginPreferences(execution_preference=exec_pref, enabled=enabled, notes=notes)
            self.config_service.set_plugin_preference(plugin_id, pref)

    def _apply_settings(self) -> None:
        """Apply settings without closing dialog."""
        try:
            # Build update dictionary
            updates: dict[str, Any] = {}

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

            # Save plugin preferences
            self._save_plugin_preferences()

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
                f"Failed to save settings:\n{e!s}",
            )

    def _update_git_config(self) -> None:
        """Update global Git configuration with user identity.

        Saves user name and email to Git global config for use in
        project initialization and commits.

        Examples:
            >>> settings_dialog._update_git_config()
            # Updates ~/.gitconfig with user identity

        .. versionadded:: dev
        """
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
            self.logger.warning(f"Could not update Git config: {e}")

    def _ok_clicked(self) -> None:
        """Handle OK button click."""
        self._apply_settings()
        self.accept()

    def _create_about_tab(self) -> QWidget:
        """Create the About tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # App Info
        info_group = QGroupBox("Application Information")
        info_layout = QFormLayout(info_group)

        info_layout.addRow("Name:", QLabel(self.config.app_name))
        info_layout.addRow("Version:", QLabel(self.config.app_version))

        if self.config.app_commit:
            info_layout.addRow("Commit:", QLabel(self.config.app_commit))

        layout.addWidget(info_group)
        layout.addStretch()

        return widget
