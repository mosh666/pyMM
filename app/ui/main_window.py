"""
Main window for pyMediaManager application.
Uses Fluent Design with navigation interface.
"""

import logging
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

try:
    from qfluentwidgets import FluentIcon, FluentWindow, NavigationItemPosition, Theme, setTheme

    FLUENT_AVAILABLE = True
except ImportError:
    FLUENT_AVAILABLE = False
    # Fallback to standard Qt widgets
    from PySide6.QtWidgets import QMainWindow as FluentWindow

from app.core.platform import PortableConfig
from app.core.services.config_service import ConfigService
from app.core.services.storage_group_service import StorageGroupService
from app.core.services.storage_service import StorageService
from app.plugins.plugin_manager import PluginManager
from app.services.project_service import ProjectService
from app.ui.components.migration_banner import MigrationBanner
from app.ui.dialogs.rollback_dialog import MigrationHistoryDialog, RollbackDialog


class MainWindow(FluentWindow if FLUENT_AVAILABLE else QWidget):
    """Main application window with Fluent Design interface."""

    def __init__(
        self,
        config_service: ConfigService,
        storage_service: StorageService,
        plugin_manager: PluginManager,
        project_service: ProjectService,
        portable_config: PortableConfig | None = None,
        storage_group_service: StorageGroupService | None = None,
    ):
        """Initialize main application window.

        Args:
            config_service: Configuration service instance.
            storage_service: Storage and drive detection service.
            plugin_manager: Plugin management instance.
            project_service: Project management service.
            portable_config: Portable mode configuration (optional).
            storage_group_service: Storage group service for managing drive pairs (optional).

        Examples:
            >>> main_window = MainWindow(
            ...     config_service, storage_service,
            ...     plugin_manager, project_service
            ... )
        """
        super().__init__()

        self.logger = logging.getLogger(__name__)

        self.config_service = config_service
        self.storage_service = storage_service
        self.plugin_manager = plugin_manager
        self.project_service = project_service
        self.portable_config = portable_config
        self.storage_group_service = storage_group_service
        self.current_project = None
        self._pending_migration_count = 0
        self._portable_status_label: QLabel | None = None

        self._init_window()
        self._init_navigation()
        self._init_status_bar()
        self._apply_theme()
        self._check_pending_migrations()

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

        self.storage_view = StorageView(
            self.storage_service,
            storage_group_service=self.storage_group_service,
        )
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

        # Migrations (with badge if pending)
        self.migrations_interface = self._create_migrations_interface()
        self.addSubInterface(
            self.migrations_interface,
            FluentIcon.UPDATE,
            "Migrations",
            NavigationItemPosition.TOP,
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
        widget.setObjectName("homeInterface")
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
        widget.setObjectName("settingsInterface")
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
            "Install with: uv pip install PySide6-Fluent-Widgets\n\n"
            "Running in fallback mode..."
        )
        warning.setAlignment(Qt.AlignCenter)
        layout.addWidget(warning)

    def _init_status_bar(self) -> None:
        """Initialize the status bar with portable mode indicator."""
        if not FLUENT_AVAILABLE:
            return

        # Get or create status bar
        # FluentWindow uses a custom status area, we'll add to the title bar area
        if self.portable_config is not None:
            # Create portable status label
            self._portable_status_label = QLabel()
            self._update_portable_status_display()

            # Style the label
            self._portable_status_label.setStyleSheet(
                """
                QLabel {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                }
                """
            )

            # Add to window - for FluentWindow, add to the title bar
            try:
                if hasattr(self, "titleBar") and self.titleBar is not None:
                    # Insert before the close button area
                    self.titleBar.hBoxLayout.insertWidget(
                        self.titleBar.hBoxLayout.count() - 3,
                        self._portable_status_label,
                    )
            except (AttributeError, RuntimeError):
                # Fallback: just keep the label reference for later use
                self.logger.debug("Could not add portable status to title bar")

    def _update_portable_status_display(self) -> None:
        """Update the portable status label display."""
        if self._portable_status_label is None or self.portable_config is None:
            return

        icon = self.portable_config.status_icon
        text = self.portable_config.status_text
        self._portable_status_label.setText(f"{icon} {text}")

        # Set color based on portable mode
        if self.portable_config.enabled:
            # Green tint for portable
            self._portable_status_label.setStyleSheet(
                """
                QLabel {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    background-color: rgba(76, 175, 80, 0.2);
                    color: #4CAF50;
                }
                """
            )
        else:
            # Neutral gray for installed
            self._portable_status_label.setStyleSheet(
                """
                QLabel {
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    background-color: rgba(158, 158, 158, 0.2);
                    color: #9E9E9E;
                }
                """
            )

        # Set tooltip with full details
        self._portable_status_label.setToolTip(str(self.portable_config))

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

    def _on_project_opened(self, project: Any) -> None:
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

    def _create_migrations_interface(self) -> QWidget:
        """Create migrations management interface."""
        widget = QWidget()
        widget.setObjectName("migrationsInterface")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title = QLabel("Template Migrations")
        title_font = title.font()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Description
        description = QLabel(
            "Manage template updates for your projects.\n\n"
            "Check for available updates, preview changes, apply migrations, or rollback."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

        # Check for updates button
        check_btn = QPushButton("🔍 Check for Updates")
        check_btn.clicked.connect(self._check_migrations)
        check_btn.setMaximumWidth(250)
        layout.addWidget(check_btn)

        # Apply pending migrations button
        apply_pending_btn = QPushButton("⚡ Apply Pending Migrations")
        apply_pending_btn.clicked.connect(self._apply_pending_migrations)
        apply_pending_btn.setMaximumWidth(250)
        layout.addWidget(apply_pending_btn)

        # Rollback button
        rollback_btn = QPushButton("↩️  Rollback Migrations")
        rollback_btn.clicked.connect(self._show_rollback_dialog)
        rollback_btn.setMaximumWidth(250)
        layout.addWidget(rollback_btn)

        # View migration history button
        if self.current_project:
            history_btn = QPushButton("📜 View Migration History")
            history_btn.clicked.connect(self._show_migration_history)
            history_btn.setMaximumWidth(250)
            layout.addWidget(history_btn)

        layout.addStretch()

        return widget

    def _check_pending_migrations(self) -> None:
        """Check for projects with pending migrations and update badge."""
        try:
            pending_projects = self.project_service.list_projects_with_pending_migrations()
            self._pending_migration_count = len(pending_projects)

            # Update badge on Migrations menu item
            if FLUENT_AVAILABLE and self._pending_migration_count > 0:
                # Note: Badge update would require QFluentWidgets API support
                # This is a placeholder for the badge update logic
                self.logger.info(
                    f"{self._pending_migration_count} project(s) have pending migrations"
                )

                # Show toast notification on startup if there are pending migrations
                MigrationBanner.show_info_bar(
                    f"📢 {self._pending_migration_count} project(s) have pending migrations",
                    parent=self,
                )
        except Exception:
            self.logger.exception("Failed to check pending migrations")

    def _check_migrations(self) -> None:
        """Check all projects for available template updates.

        Scans all projects to identify those with pending migrations,
        displaying appropriate UI notifications and migration dialogs.

        Examples:
            >>> main_window._check_migrations()
            # Shows info bar if migrations available or all up to date

        .. versionadded:: dev
        """
        try:
            migratable_projects = self.project_service.list_migratable_projects()

            if not migratable_projects:
                MigrationBanner.show_info_bar(
                    "✅ All projects are up to date",
                    parent=self,
                )
                return

            # Show summary
            project_names = [p.name for p in migratable_projects]
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "Updates Available",
                f"Found {len(migratable_projects)} project(s) with available updates:\n\n"
                + "\n".join(f"• {name}" for name in project_names[:10])
                + (f"\n... and {len(project_names) - 10} more" if len(project_names) > 10 else ""),
            )

            # Switch to projects view
            self.switchTo(self.project_view)

        except Exception as e:
            self.logger.exception("Failed to check migrations")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to check for migrations:\n{e!s}",
            )

    def _apply_pending_migrations(self) -> None:
        """Apply all pending (deferred) migrations."""
        try:
            pending_projects = self.project_service.list_projects_with_pending_migrations()

            if not pending_projects:
                MigrationBanner.show_info_bar(
                    "ℹ️  No pending migrations to apply",
                    parent=self,
                )
                return

            # Confirm action
            from PySide6.QtWidgets import QMessageBox

            reply = QMessageBox.question(
                self,
                "Apply Pending Migrations",
                f"Apply {len(pending_projects)} pending migration(s)?\n\n"
                "This will migrate all projects that were previously deferred.",
                QMessageBox.Yes | QMessageBox.No,
            )

            if reply != QMessageBox.Yes:
                return

            # Apply migrations
            results = self.project_service.apply_pending_migrations()

            # Count successes and failures
            successes = sum(1 for _, success, _ in results if success)
            failures = len(results) - successes

            # Show results
            if failures == 0:
                MigrationBanner.show_info_bar(
                    f"✅ Successfully applied {successes} migration(s)",
                    parent=self,
                )
            else:
                error_msgs = [msg for _, success, msg in results if not success]
                QMessageBox.warning(
                    self,
                    "Migration Results",
                    f"Applied {successes} migration(s) successfully.\n"
                    f"Failed: {failures}\n\n" + "\n".join(error_msgs[:5]),
                )

            # Refresh pending count
            self._check_pending_migrations()

            # Refresh project view
            if hasattr(self.project_view, "refresh_projects"):
                self.project_view.refresh_projects()

        except Exception as e:
            self.logger.exception("Failed to apply pending migrations")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to apply pending migrations:\n{e!s}",
            )

    def _show_rollback_dialog(self) -> None:
        """Show rollback dialog for reverting migrations."""
        try:
            # Get all projects
            all_projects = self.project_service.list_projects()

            # Filter projects with migration backups
            projects_with_backups = [
                p
                for p in all_projects
                if p.migration_history and any(m.get("backup_path") for m in p.migration_history)
            ]

            if not projects_with_backups:
                from PySide6.QtWidgets import QMessageBox

                QMessageBox.information(
                    self,
                    "No Rollbacks Available",
                    "No projects have migration backups available for rollback.",
                )
                return

            # Show rollback dialog
            dialog = RollbackDialog(projects_with_backups, self.project_service, self)
            if dialog.exec():
                # Refresh project view after rollback
                if hasattr(self.project_view, "refresh_projects"):
                    self.project_view.refresh_projects()

                MigrationBanner.show_info_bar(
                    "✅ Rollback completed successfully",
                    parent=self,
                )

        except Exception as e:
            self.logger.exception("Failed to show rollback dialog")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open rollback dialog:\n{e!s}",
            )

    def _show_migration_history(self) -> None:
        """Show migration history for current project."""
        if not self.current_project:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self,
                "No Project Selected",
                "Please open a project first to view its migration history.",
            )
            return

        try:
            dialog = MigrationHistoryDialog(self.current_project, self)
            dialog.exec()
        except Exception as e:
            self.logger.exception("Failed to show migration history")
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open migration history:\n{e!s}",
            )
