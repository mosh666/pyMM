"""
Logging service for pyMediaManager.
Provides rich console logging and rotating file logs.
"""

import logging
import logging.handlers
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler


class LoggingService:
    """Service for configuring application logging with console and file outputs."""

    def __init__(
        self,
        app_name: str = "pyMediaManager",
        log_dir: Path | None = None,
        level: str = "INFO",
        console_enabled: bool = True,
        file_enabled: bool = True,
        max_file_size: int = 10485760,  # 10MB
        backup_count: int = 5,
        file_system_service: object | None = None,
    ):
        """
        Initialize logging service.

        Args:
            app_name: Application name for logger
            log_dir: Directory for log files (if None, uses portable folder from file_system_service)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_enabled: Enable console logging with rich formatting
            file_enabled: Enable file logging with rotation
            max_file_size: Maximum log file size in bytes before rotation
            backup_count: Number of backup log files to keep
            file_system_service: FileSystemService instance for portable folder detection
        """
        self.app_name = app_name
        self.file_system_service = file_system_service

        # Use portable logs folder if log_dir not specified and file_system_service available
        if log_dir is None and file_system_service is not None:
            self.log_dir = file_system_service.get_portable_folder("pyMM.Logs")  # type: ignore[attr-defined]
        else:
            self.log_dir = log_dir

        self.level = getattr(logging, level.upper())
        self.console_enabled = console_enabled
        self.file_enabled = file_enabled
        self.max_file_size = max_file_size
        self.backup_count = backup_count

        self._logger: logging.Logger | None = None
        self._console: Console | None = None

    def setup(self) -> logging.Logger:
        """
        Setup logging configuration with console and file handlers.

        Returns:
            Configured logger instance
        """
        # Get or create logger
        self._logger = logging.getLogger(self.app_name)
        self._logger.setLevel(self.level)

        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()

        # Setup console handler with Rich
        if self.console_enabled:
            self._console = Console()
            console_handler = RichHandler(
                console=self._console,
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True,
            )
            console_handler.setLevel(self.level)
            self._logger.addHandler(console_handler)

        # Setup file handler with rotation
        if self.file_enabled and self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)

            log_file = self.log_dir / f"{self.app_name.lower()}.log"

            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            file_handler.setLevel(self.level)

            # File handler uses detailed format
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            self._logger.addHandler(file_handler)

        return self._logger

    def get_logger(self, name: str | None = None) -> logging.Logger:
        """
        Get a logger instance.

        Args:
            name: Logger name (defaults to app_name)

        Returns:
            Logger instance
        """
        if self._logger is None:
            self.setup()

        if name:
            return logging.getLogger(f"{self.app_name}.{name}")

        assert self._logger is not None
        return self._logger

    def set_level(self, level: str) -> None:
        """
        Change logging level dynamically.

        Args:
            level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper())
        self.level = new_level

        if self._logger:
            self._logger.setLevel(new_level)
            for handler in self._logger.handlers:
                handler.setLevel(new_level)

    def get_log_file_path(self) -> Path | None:
        """
        Get the current log file path.

        Returns:
            Path to log file or None if file logging disabled
        """
        if not self.file_enabled or not self.log_dir:
            return None

        return Path(self.log_dir / f"{self.app_name.lower()}.log")

    def get_all_log_files(self) -> list[Path]:
        """
        Get all log files (current and rotated).

        Returns:
            List of log file paths
        """
        if not self.log_dir or not self.log_dir.exists():
            return []

        log_pattern = f"{self.app_name.lower()}.log*"
        return sorted(self.log_dir.glob(log_pattern))
