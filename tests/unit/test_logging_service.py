"""Tests for LoggingService."""

import logging

from app.core.logging_service import LoggingService
from app.core.services.file_system_service import FileSystemService


class TestLoggingService:
    """Test LoggingService initialization and configuration."""

    def test_init_defaults(self, tmp_path):
        """Test LoggingService initialization with defaults."""
        log_dir = tmp_path / "logs"
        service = LoggingService(log_dir=log_dir)

        assert service.app_name == "pyMediaManager"
        assert service.log_dir == log_dir
        assert service.level == logging.INFO
        assert service.console_enabled is True
        assert service.file_enabled is True
        assert service.max_file_size == 10485760
        assert service.backup_count == 5

    def test_init_custom_values(self, tmp_path):
        """Test LoggingService initialization with custom values."""
        log_dir = tmp_path / "custom_logs"
        service = LoggingService(
            app_name="TestApp",
            log_dir=log_dir,
            level="DEBUG",
            console_enabled=False,
            file_enabled=False,
            max_file_size=5242880,
            backup_count=3,
        )

        assert service.app_name == "TestApp"
        assert service.log_dir == log_dir
        assert service.level == logging.DEBUG
        assert service.console_enabled is False
        assert service.file_enabled is False
        assert service.max_file_size == 5242880
        assert service.backup_count == 3

    def test_init_with_file_system_service(self, tmp_path, monkeypatch):
        """Test LoggingService uses FileSystemService for portable logs."""
        fs_service = FileSystemService(app_root=tmp_path)

        # Mock drive root to use temp directory
        mock_drive_root = tmp_path / "mock_drive"
        mock_drive_root.mkdir()
        monkeypatch.setattr(fs_service, "get_drive_root", lambda: mock_drive_root)

        service = LoggingService(file_system_service=fs_service)

        expected_log_dir = mock_drive_root / "pyMM.Logs"
        assert service.log_dir == expected_log_dir

    def test_setup_console_only(self, tmp_path):
        """Test setup with console logging only."""
        service = LoggingService(
            log_dir=tmp_path / "logs",
            console_enabled=True,
            file_enabled=False,
        )
        logger = service.setup()

        assert logger is not None
        assert logger.name == "pyMediaManager"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
        assert service._console is not None

    def test_setup_file_only(self, tmp_path):
        """Test setup with file logging only."""
        log_dir = tmp_path / "logs"
        service = LoggingService(
            log_dir=log_dir,
            console_enabled=False,
            file_enabled=True,
        )
        logger = service.setup()

        assert logger is not None
        assert len(logger.handlers) == 1
        assert log_dir.exists()
        log_file = log_dir / "pymediamanager.log"
        assert log_file.exists()

    def test_setup_both_handlers(self, tmp_path):
        """Test setup with both console and file logging."""
        log_dir = tmp_path / "logs"
        service = LoggingService(
            log_dir=log_dir,
            console_enabled=True,
            file_enabled=True,
        )
        logger = service.setup()

        assert logger is not None
        assert len(logger.handlers) == 2  # Console + File
        assert log_dir.exists()

    def test_setup_no_log_dir_file_enabled(self):
        """Test setup with file logging enabled but no log directory."""
        service = LoggingService(
            log_dir=None,
            console_enabled=True,
            file_enabled=True,
        )
        logger = service.setup()

        assert logger is not None
        # Should only have console handler since no log_dir
        assert len(logger.handlers) == 1

    def test_setup_clears_existing_handlers(self, tmp_path):
        """Test that setup clears existing handlers."""
        service = LoggingService(log_dir=tmp_path / "logs")

        # Setup first time
        logger1 = service.setup()
        handler_count_1 = len(logger1.handlers)

        # Setup again - handlers should be cleared and recreated
        logger2 = service.setup()
        handler_count_2 = len(logger2.handlers)

        assert handler_count_1 == handler_count_2

    def test_get_logger_auto_setup(self, tmp_path):
        """Test get_logger automatically calls setup if needed."""
        service = LoggingService(log_dir=tmp_path / "logs")

        assert service._logger is None
        logger = service.get_logger()

        assert service._logger is not None
        assert logger is not None

    def test_get_logger_default_name(self, tmp_path):
        """Test get_logger returns app logger by default."""
        service = LoggingService(log_dir=tmp_path / "logs")
        logger = service.get_logger()

        assert logger.name == "pyMediaManager"

    def test_get_logger_custom_name(self, tmp_path):
        """Test get_logger with custom name creates child logger."""
        service = LoggingService(log_dir=tmp_path / "logs")
        logger = service.get_logger("module")

        assert logger.name == "pyMediaManager.module"

    def test_set_level(self, tmp_path):
        """Test changing logging level dynamically."""
        service = LoggingService(log_dir=tmp_path / "logs", level="INFO")
        logger = service.setup()

        assert logger.level == logging.INFO

        service.set_level("DEBUG")
        assert service.level == logging.DEBUG
        assert logger.level == logging.DEBUG
        for handler in logger.handlers:
            assert handler.level == logging.DEBUG

    def test_set_level_all_levels(self, tmp_path):
        """Test setting all valid log levels."""
        service = LoggingService(log_dir=tmp_path / "logs")
        service.setup()

        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level_name in levels:
            service.set_level(level_name)
            assert service.level == getattr(logging, level_name)

    def test_get_log_file_path_enabled(self, tmp_path):
        """Test get_log_file_path returns path when file logging enabled."""
        log_dir = tmp_path / "logs"
        service = LoggingService(log_dir=log_dir, file_enabled=True)

        expected = log_dir / "pymediamanager.log"
        assert service.get_log_file_path() == expected

    def test_get_log_file_path_disabled(self, tmp_path):
        """Test get_log_file_path returns None when file logging disabled."""
        service = LoggingService(
            log_dir=tmp_path / "logs",
            file_enabled=False,
        )

        assert service.get_log_file_path() is None

    def test_get_log_file_path_no_log_dir(self):
        """Test get_log_file_path returns None when no log directory."""
        service = LoggingService(log_dir=None, file_enabled=True)

        assert service.get_log_file_path() is None

    def test_get_all_log_files_empty(self, tmp_path):
        """Test get_all_log_files returns empty list for non-existent log dir."""
        log_dir = tmp_path / "nonexistent"
        service = LoggingService(log_dir=log_dir)

        assert service.get_all_log_files() == []

    def test_get_all_log_files_single(self, tmp_path):
        """Test get_all_log_files returns current log file."""
        log_dir = tmp_path / "logs"
        service = LoggingService(log_dir=log_dir, file_enabled=True)
        service.setup()

        log_files = service.get_all_log_files()
        assert len(log_files) == 1
        assert log_files[0].name == "pymediamanager.log"

    def test_get_all_log_files_with_rotations(self, tmp_path):
        """Test get_all_log_files returns all rotated files."""
        log_dir = tmp_path / "logs"
        log_dir.mkdir()

        # Create mock rotated log files
        (log_dir / "pymediamanager.log").touch()
        (log_dir / "pymediamanager.log.1").touch()
        (log_dir / "pymediamanager.log.2").touch()

        service = LoggingService(log_dir=log_dir, app_name="pyMediaManager")
        log_files = service.get_all_log_files()

        assert len(log_files) == 3
        assert all(f.name.startswith("pymediamanager.log") for f in log_files)

    def test_logging_actually_works(self, tmp_path):
        """Test that logging actually writes to file."""
        log_dir = tmp_path / "logs"
        service = LoggingService(
            log_dir=log_dir,
            console_enabled=False,
            file_enabled=True,
        )
        logger = service.get_logger()

        test_message = "Test log message"
        logger.info(test_message)

        log_file = log_dir / "pymediamanager.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert test_message in content

    def test_custom_app_name_log_file(self, tmp_path):
        """Test that custom app name creates correctly named log file."""
        log_dir = tmp_path / "logs"
        service = LoggingService(
            app_name="CustomApp",
            log_dir=log_dir,
            console_enabled=False,
            file_enabled=True,
        )
        service.setup()

        log_file = log_dir / "customapp.log"
        assert log_file.exists()

    def test_log_rotation_settings(self, tmp_path):
        """Test that rotation settings are properly configured."""
        log_dir = tmp_path / "logs"
        max_size = 1024
        backup_count = 2

        service = LoggingService(
            log_dir=log_dir,
            console_enabled=False,
            file_enabled=True,
            max_file_size=max_size,
            backup_count=backup_count,
        )
        logger = service.setup()

        # Find the rotating file handler
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                file_handler = handler
                break

        assert file_handler is not None
        assert file_handler.maxBytes == max_size
        assert file_handler.backupCount == backup_count
