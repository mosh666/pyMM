"""
Plugin view for managing application plugins.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QProgressDialog,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.plugins.plugin_manager import PluginManager


class PluginInstallThread(QThread):
    """Thread for installing plugins asynchronously."""

    progress = Signal(int, int)  # current, total
    finished = Signal(bool, str)  # success, message

    def __init__(self, plugin_manager: PluginManager, plugin_name: str) -> None:
        """Initialize plugin installation thread.

        Args:
            plugin_manager: Plugin manager instance.
            plugin_name: Name of plugin to install.

        Examples:
            >>> thread = PluginInstallThread(plugin_manager, 'git')
        """
        super().__init__()
        self.plugin_manager = plugin_manager
        self.plugin_name = plugin_name

    def run(self) -> None:
        """Run plugin installation."""
        import asyncio

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            success = loop.run_until_complete(
                self.plugin_manager.install_plugin(
                    self.plugin_name, progress_callback=self._progress_callback
                )
            )

            if success:
                self.finished.emit(True, f"{self.plugin_name} installed successfully")
            else:
                self.finished.emit(False, f"Failed to install {self.plugin_name}")

        except Exception as e:
            self.finished.emit(False, f"Error: {e!s}")

    def _progress_callback(self, current: int, total: int) -> None:
        """Update progress."""
        self.progress.emit(current, total)


class PluginView(QWidget):
    """View for managing plugins."""

    def __init__(self, plugin_manager: PluginManager, parent: QWidget | None = None) -> None:
        """Initialize plugin management view.

        Args:
            plugin_manager: Plugin manager instance.
            parent: Parent widget (optional).

        Examples:
            >>> view = PluginView(plugin_manager)
        """
        super().__init__(parent)
        self.setObjectName("pluginView")

        self.logger = logging.getLogger(__name__)
        self.plugin_manager = plugin_manager
        self.install_thread: PluginInstallThread | None = None

        self._init_ui()
        self.refresh_plugins()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Plugin Management")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        desc = QLabel(
            "Manage external tools and plugins. Mandatory plugins are required for core functionality. "
            "Optional plugins can be installed as needed."
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Plugins table
        self.plugins_table = QTableWidget()
        self.plugins_table.setColumnCount(5)
        self.plugins_table.setHorizontalHeaderLabels(
            ["Plugin", "Version", "Type", "Status", "Actions"]
        )
        self.plugins_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.plugins_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.plugins_table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_plugins)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

    def refresh_plugins(self) -> None:
        """Refresh the plugins table."""
        # Discover plugins
        self.plugin_manager.discover_plugins()

        plugins = self.plugin_manager.get_all_plugins()
        self.plugins_table.setRowCount(len(plugins))

        for row, plugin in enumerate(plugins):
            # Plugin name
            self.plugins_table.setItem(row, 0, QTableWidgetItem(plugin.manifest.name))

            # Version
            version = plugin.get_version() or plugin.manifest.version
            self.plugins_table.setItem(row, 1, QTableWidgetItem(version))

            # Type
            plugin_type = "Mandatory" if plugin.manifest.mandatory else "Optional"
            self.plugins_table.setItem(row, 2, QTableWidgetItem(plugin_type))

            # Status
            status = "✓ Installed" if plugin.is_installed() else "Not Installed"
            status_item = QTableWidgetItem(status)
            if plugin.is_installed():
                status_item.setForeground(Qt.GlobalColor.darkGreen)
            self.plugins_table.setItem(row, 3, status_item)

            # Actions
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            if plugin.is_installed():
                update_btn = QPushButton("Update")
                update_btn.clicked.connect(lambda checked, p=plugin: self._update_plugin(p))
                action_layout.addWidget(update_btn)

                uninstall_btn = QPushButton("Uninstall")
                uninstall_btn.clicked.connect(lambda checked, p=plugin: self._uninstall_plugin(p))
                action_layout.addWidget(uninstall_btn)
            else:
                install_btn = QPushButton("Install")
                install_btn.clicked.connect(lambda checked, p=plugin: self._install_plugin(p))
                action_layout.addWidget(install_btn)

            self.plugins_table.setCellWidget(row, 4, action_widget)

    def _install_plugin(self, plugin: Any) -> None:
        """Install a plugin."""
        # Show confirmation
        reply = QMessageBox.question(
            self,
            "Install Plugin",
            f"Install {plugin.manifest.name}?\n\nThis will download and extract the plugin binaries.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Show progress dialog
        progress = QProgressDialog(f"Installing {plugin.manifest.name}...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        # Start installation thread
        self.install_thread = PluginInstallThread(self.plugin_manager, plugin.manifest.name)
        self.install_thread.progress.connect(
            lambda cur, total: progress.setValue(int((cur / total) * 100) if total > 0 else 0)
        )
        self.install_thread.finished.connect(
            lambda success, msg: self._on_install_finished(success, msg, progress)
        )
        self.install_thread.start()

    def _on_install_finished(self, success: bool, message: str, progress: QProgressDialog) -> None:
        """Handle installation completion and show results.

        Args:
            success: Whether installation succeeded.
            message: Result message to display.
            progress: Progress dialog to close.

        Examples:
            >>> view._on_install_finished(True, 'Installed successfully', progress_dlg)
            # Closes dialog and shows success message
        """
        progress.close()

        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.warning(self, "Failed", message)

        self.refresh_plugins()

    def _update_plugin(self, plugin: Any) -> None:
        """Update a plugin."""
        QMessageBox.information(
            self, "Update", f"Update functionality for {plugin.manifest.name} coming soon!"
        )

    def _uninstall_plugin(self, plugin: Any) -> None:
        """Uninstall a plugin."""
        reply = QMessageBox.question(
            self,
            "Uninstall Plugin",
            f"Uninstall {plugin.manifest.name}?\n\nThis will remove all plugin files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            import asyncio

            loop = asyncio.new_event_loop()
            success = loop.run_until_complete(
                self.plugin_manager.uninstall_plugin(plugin.manifest.name)
            )

            if success:
                QMessageBox.information(self, "Success", f"{plugin.manifest.name} uninstalled")
            else:
                QMessageBox.warning(self, "Failed", f"Failed to uninstall {plugin.manifest.name}")

            self.refresh_plugins()
