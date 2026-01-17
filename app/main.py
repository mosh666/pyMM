"""
Main application entry point for pyMediaManager.
Initializes services and launches the PySide6 GUI.
"""

from __future__ import annotations

# ruff: noqa: I001 - Platform import must be first to prevent shadowing (Python 3.12)
import argparse
import platform  # Must be imported before app modules
import sys
from pathlib import Path
from typing import Any

sys.modules["platform"] = platform  # Force stdlib platform into sys.modules before app imports
del platform  # Don't pollute namespace

from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from app.core.platform import PortableConfig  # noqa: E402
from app.core.services.storage_group_service import StorageGroupService  # noqa: E402


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
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
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
    log_level: str | None = None,
) -> dict[str, Any]:
    """
    Initialize all application services.

    Args:
        app_root: Root directory of the application
        config: Configuration object
        portable_config: Resolved portable configuration
        templates_dir: Optional custom templates directory
        disable_template_watch: Whether to disable template filesystem watching
        log_level: Optional log level override (DEBUG, INFO, WARNING, ERROR, CRITICAL)

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
    # Use CLI log level if provided, otherwise use config value
    effective_log_level = log_level if log_level else config.logging.level.value
    logging_service = LoggingService(
        app_name=config.app_name,
        level=effective_log_level,
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

    # Storage group service - use same config directory as ConfigService
    from app.core.services.config_service import get_platform_config_dir

    storage_groups_config_path = get_platform_config_dir() / "storage_groups.yaml"
    storage_group_service = StorageGroupService(
        config_path=storage_groups_config_path,
        storage_service=storage_service,
    )
    logger.info(
        "Storage group service initialized: %s",
        storage_groups_config_path,
    )

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
        "storage_group_service": storage_group_service,
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

    # Enable High DPI scaling (Qt6 enables by default, only set rounding policy)
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    # Note: AA_EnableHighDpiScaling and AA_UseHighDpiPixmaps are deprecated in Qt6
    # and enabled by default, so no need to set them explicitly

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
        log_level=args.log_level if hasattr(args, "log_level") else None,
    )

    # Extract services
    logger = services["logger"]
    file_system_service = services["file_system_service"]
    plugin_manager = services["plugin_manager"]
    project_service = services["project_service"]
    storage_group_service = services["storage_group_service"]

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
            storage_group_service=storage_group_service,
        )
        main_window.show()

        # Store reference to prevent garbage collection
        app.main_window = main_window

    # Check first-run state
    if config.ui.show_first_run:
        logger.info("Showing first-run wizard")

        from app.ui.components.first_run_wizard import FirstRunWizard

        optional_plugins = [p.manifest.name for p in plugin_manager.get_optional_plugins()]

        wizard = FirstRunWizard(
            storage_service,
            optional_plugins,
            storage_group_service=storage_group_service,
        )

        def on_wizard_finished(data: dict[str, Any]) -> None:
            """Handle wizard completion and update configuration.

            Args:
                data: Wizard data including dont_show_again flag.

            Examples:
                >>> on_wizard_finished({'dont_show_again': True})
                # Updates config and shows main window
            """
            logger.info("First-run wizard completed: %s", data)

            # Create storage group if configured
            if data.get("storage_group"):
                try:
                    group_data = data["storage_group"]
                    master = group_data["master_drive"]
                    backup = group_data["backup_drive"]
                    name = group_data["name"]

                    logger.info(
                        "Creating storage group '%s': %s ↔ %s",
                        name,
                        master.drive_letter,
                        backup.drive_letter,
                    )

                    # Create the storage group
                    from app.models.storage_group import DriveIdentity

                    master_identity = DriveIdentity(
                        serial_number=master.serial_number,
                        label=master.label,
                        total_size=master.total_size,
                    )

                    backup_identity = DriveIdentity(
                        serial_number=backup.serial_number,
                        label=backup.label,
                        total_size=backup.total_size,
                    )

                    storage_group_service.create_group(
                        name=name,
                        master_identity=master_identity,
                        backup_identity=backup_identity,
                        description="Created during first-run setup",
                    )

                    logger.info("Storage group '%s' created successfully", name)
                except Exception:
                    logger.exception("Failed to create storage group")

            # Update config to not show wizard again
            if data.get("dont_show_again"):
                config_service.update_config(ui={"show_first_run": False})

            # Show main window
            show_main_window()

        def on_wizard_cancelled() -> None:
            """Handle wizard cancellation and proceed to main window.

            Examples:
                >>> on_wizard_cancelled()
                # Shows main window even when wizard is cancelled
            """
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
