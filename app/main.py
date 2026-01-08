"""
Main application entry point for pyMediaManager.
Initializes services and launches the PySide6 GUI.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from app.core.platform import PortableConfig


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="pyMediaManager",
        description="Portable Python-based media management application",
    )
    portable_group = parser.add_mutually_exclusive_group()
    portable_group.add_argument(
        "--portable",
        action="store_true",
        default=None,
        help="Enable portable mode (store data relative to executable)",
    )
    portable_group.add_argument(
        "--no-portable",
        action="store_true",
        default=None,
        help="Disable portable mode (use platform-specific directories)",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version information and exit",
    )
    return parser.parse_args()


def get_cli_portable_setting(args: argparse.Namespace) -> bool | None:
    """
    Extract portable setting from CLI args.

    Returns:
        True if --portable, False if --no-portable, None if neither specified
    """
    if args.portable:
        return True
    if args.no_portable:
        return False
    return None


def get_app_root() -> Path:
    """Get the application root directory."""
    # APP_ROOT is parent of app/ directory
    return Path(__file__).parent.parent.resolve()


def initialize_services(
    app_root: Path,
    config: Any,
    portable_config: PortableConfig | None = None,
    templates_dir: Path | None = None,
    disable_template_watch: bool = False,
) -> dict[str, Any]:
    """
    Initialize all application services.

    Args:
        app_root: Root directory of the application
        config: Configuration object
        portable_config: Resolved portable configuration
        templates_dir: Optional custom templates directory
        disable_template_watch: Whether to disable template filesystem watching

    Returns:
        Dictionary with initialized services and components
    """
    from app.core.logging_service import LoggingService
    from app.core.services.file_system_service import FileSystemService
    from app.core.services.storage_service import StorageService
    from app.plugins.plugin_manager import PluginManager
    from app.services.git_service import GitService
    from app.services.project_service import ProjectService

    # File system service with portable config
    file_system_service = FileSystemService(app_root, portable_config=portable_config)

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
    logger.info("Starting %s v%s", config.app_name, config.app_version)
    logger.info("App root: %s", app_root)
    logger.info("Drive root: %s", file_system_service.get_drive_root())
    logger.info("Portable mode: %s", file_system_service.portable_config)
    logger.info(
        "Portable folders: Projects=%s, Logs=%s",
        portable_folders["projects"],
        portable_folders["logs"],
    )

    # Storage service
    storage_service = StorageService()

    # Plugin manager
    plugins_dir = app_root.parent / config.paths.plugins_dir
    manifests_dir = app_root / "plugins"
    plugin_manager = PluginManager(plugins_dir, manifests_dir)
    plugin_manager.discover_plugins()

    logger.info("Discovered %d plugins", len(plugin_manager.get_all_plugins()))

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
    logger.info("Project service initialized: %s", projects_metadata_dir)
    logger.info("Discovered %d templates", len(project_service.list_templates()))

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


def run_application(args: argparse.Namespace | None = None) -> int:
    """
    Initialize and run the pyMediaManager application.

    Args:
        args: Parsed command line arguments. If None, parses sys.argv.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    if args is None:
        args = parse_args()

    # Handle --version flag
    if args.version:
        from app import __version__

        # Print to stdout for version query
        sys.stdout.write(f"pyMediaManager {__version__}\n")
        return 0

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

    # Get app root (for resources) and load config from platform-specific location
    app_root = get_app_root()

    from app.core.services.config_service import ConfigService
    from app.core.services.file_system_service import resolve_portable_config
    from app.core.services.storage_service import StorageService

    # ConfigService now uses platform-specific directories by default
    # Pass app_root for legacy config migration fallback
    config_service = ConfigService(app_root=app_root)
    config = config_service.load()

    # Resolve portable configuration with cascade: CLI > env > auto-detect
    storage_service = StorageService()
    cli_portable = get_cli_portable_setting(args)
    portable_config = resolve_portable_config(
        cli_portable=cli_portable,
        storage_service=storage_service,
    )

    # Check if template watching should be disabled
    import os

    disable_watch = os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"

    # Initialize services with resolved portable config
    services = initialize_services(
        app_root,
        config,
        portable_config=portable_config,
        templates_dir=None,
        disable_template_watch=disable_watch,
    )

    # Extract services
    logger = services["logger"]
    file_system_service = services["file_system_service"]
    plugin_manager = services["plugin_manager"]
    project_service = services["project_service"]

    # Define show_main_window function
    def show_main_window() -> None:
        """Create and show the main window."""
        from app.ui.main_window import MainWindow

        main_window = MainWindow(
            config_service,
            storage_service,
            plugin_manager,
            project_service,
            portable_config=file_system_service.portable_config,
        )
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
            logger.info("First-run wizard completed: %s", data)
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
