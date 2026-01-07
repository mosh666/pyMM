"""
Main application entry point for pyMediaManager.
Initializes services and launches the PySide6 GUI.
"""

from pathlib import Path
import sys
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def get_app_root() -> Path:
    """Get the application root directory."""
    # APP_ROOT is parent of app/ directory
    return Path(__file__).parent.parent.resolve()


def initialize_services(
    app_root: Path,
    config: Any,
    templates_dir: Path | None = None,
    disable_template_watch: bool = False,
) -> dict[str, Any]:
    """
    Initialize all application services.

    Args:
        app_root: Root directory of the application
        config: Configuration object
        templates_dir: Optional custom templates directory
        disable_template_watch: Whether to disable template filesystem watching

    Returns:
        Dictionary with initialized services and components
    """
    from app.core.logging_service import LoggingService
    from app.core.services.config_service import ConfigService
    from app.core.services.file_system_service import FileSystemService
    from app.core.services.storage_service import StorageService
    from app.plugins.plugin_manager import PluginManager
    from app.services.git_service import GitService
    from app.services.project_service import ProjectService

    # File system service
    file_system_service = FileSystemService(app_root)

    # Ensure portable folders exist at drive root
    portable_folders = file_system_service.ensure_portable_folders()

    # Logging service - uses portable logs folder automatically
    logging_service = LoggingService(
        app_name=config.app_name,
        level=config.logging.level.value,
        console_enabled=config.logging.console_enabled,
        file_enabled=config.logging.file_enabled,
        file_system_service=file_system_service,
    )
    logger = logging_service.setup()
    logger.info(f"Starting {config.app_name} v{config.app_version}")
    logger.info(f"App root: {app_root}")
    logger.info(f"Drive root: {file_system_service.get_drive_root()}")
    logger.info(
        f"Portable folders: Projects={portable_folders['projects']}, Logs={portable_folders['logs']}"
    )

    # Storage service
    storage_service = StorageService()

    # Plugin manager
    plugins_dir = app_root.parent / config.paths.plugins_dir
    manifests_dir = app_root / "plugins"
    plugin_manager = PluginManager(plugins_dir, manifests_dir)
    plugin_manager.discover_plugins()

    logger.info(f"Discovered {len(plugin_manager.get_all_plugins())} plugins")

    # Git service
    git_service = GitService()

    # Project service with template support
    projects_metadata_dir = portable_folders["projects"] / ".metadata"
    project_service = ProjectService(
        projects_metadata_dir,
        git_service=git_service,
        templates_dir=templates_dir,
        disable_watch=disable_template_watch,
    )
    logger.info(f"Project service initialized: {projects_metadata_dir}")
    logger.info(f"Discovered {len(project_service.list_templates())} templates")

    return {
        "file_system_service": file_system_service,
        "config_service": None,  # Would need to pass this in or refactor
        "logging_service": logging_service,
        "logger": logger,
        "storage_service": storage_service,
        "plugin_manager": plugin_manager,
        "git_service": git_service,
        "project_service": project_service,
        "portable_folders": portable_folders,
    }


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

    from app import __version__

    app = QApplication(sys.argv)
    app.setApplicationName("pyMediaManager")
    app.setOrganizationName("mosh666")
    app.setApplicationVersion(__version__)

    # Get app root and load config
    app_root = get_app_root()

    from app.core.services.config_service import ConfigService

    config_service = ConfigService(app_root)
    config = config_service.load()

    # Check if template watching should be disabled
    import os

    disable_watch = os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"

    # Initialize services
    services = initialize_services(
        app_root, config, templates_dir=None, disable_template_watch=disable_watch
    )

    # Extract services
    file_system_service = services["file_system_service"]
    logger = services["logger"]
    storage_service = services["storage_service"]
    plugin_manager = services["plugin_manager"]
    project_service = services["project_service"]
    portable_folders = services["portable_folders"]

    # Define show_main_window function
    def show_main_window() -> None:
        """Create and show the main window."""
        from app.ui.main_window import MainWindow

        main_window = MainWindow(config_service, storage_service, plugin_manager, project_service)
        main_window.show()

        # Store reference to prevent garbage collection
        app.main_window = main_window

    # Check first-run state
    if config.ui.show_first_run:
        logger.info("Showing first-run wizard")

        from app.ui.components.first_run_wizard import FirstRunWizard

        optional_plugins = [p.manifest.name for p in plugin_manager.get_optional_plugins()]

        wizard = FirstRunWizard(storage_service, optional_plugins)

        def on_wizard_finished(data: dict[str, Any]) -> None:
            logger.info(f"First-run wizard completed: {data}")
            # Update config to not show wizard again
            if data.get("dont_show_again"):
                config_service.update_config(ui={"show_first_run": False})

            # Show main window
            show_main_window()

        def on_wizard_cancelled() -> None:
            logger.info("First-run wizard cancelled")
            # Still show main window
            show_main_window()

        wizard.finished.connect(on_wizard_finished)
        wizard.cancelled.connect(on_wizard_cancelled)
        wizard.show()
    else:
        # Show main window directly
        show_main_window()

    return int(app.exec())


if __name__ == "__main__":
    sys.exit(run_application())
