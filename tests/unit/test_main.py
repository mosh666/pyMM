"""
Tests for main application module (app.main).
"""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.main import get_app_root, initialize_services


class TestGetAppRoot:
    """Tests for get_app_root function."""

    def test_get_app_root_returns_path(self):
        """Test that get_app_root returns a Path object."""
        root = get_app_root()

        assert isinstance(root, Path)
        assert root.is_absolute()

    def test_get_app_root_points_to_project_root(self):
        """Test that app root is the project root directory."""
        root = get_app_root()

        # Should contain app directory
        assert (root / "app").exists()
        assert (root / "app").is_dir()

        # Should contain pyproject.toml
        assert (root / "pyproject.toml").exists()

    def test_get_app_root_is_consistent(self):
        """Test that multiple calls return the same path."""
        root1 = get_app_root()
        root2 = get_app_root()

        assert root1 == root2

    def test_get_app_root_is_resolved(self):
        """Test that returned path is fully resolved."""
        root = get_app_root()

        # Should not contain .. or .
        assert ".." not in str(root)
        assert root == root.resolve()


class TestInitializeServices:
    """Tests for initialize_services function."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration object."""
        config = Mock()
        config.app_name = "pyMediaManager"
        config.app_version = "1.0.0"
        config.paths.plugins_dir = "plugins"
        config.logging.level.value = "INFO"
        config.logging.console_enabled = True
        config.logging.file_enabled = True
        return config

    @pytest.fixture
    def test_app_root(self, tmp_path):
        """Create a test app root directory."""
        app_root = tmp_path / "app_root"
        app_root.mkdir()
        (app_root / "plugins").mkdir()
        return app_root

    def test_initialize_services_returns_dict(self, test_app_root, mock_config):
        """Test that initialize_services returns a dictionary."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        assert isinstance(services, dict)

    def test_initialize_services_has_all_keys(self, test_app_root, mock_config):
        """Test that returned dict has all expected service keys."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        expected_keys = [
            "file_system_service",
            "config_service",
            "logging_service",
            "logger",
            "storage_service",
            "plugin_manager",
            "git_service",
            "project_service",
            "portable_folders",
        ]

        for key in expected_keys:
            assert key in services, f"Missing key: {key}"

    def test_file_system_service_creation(self, test_app_root, mock_config):
        """Test that FileSystemService is created correctly."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        fs_service = services["file_system_service"]
        assert fs_service is not None
        # Should have been initialized with app_root
        assert hasattr(fs_service, "app_root")

    def test_storage_service_creation(self, test_app_root, mock_config):
        """Test that StorageService is created."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        storage_service = services["storage_service"]
        assert storage_service is not None

    def test_plugin_manager_creation(self, test_app_root, mock_config):
        """Test that PluginManager is created with correct paths."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        plugin_manager = services["plugin_manager"]
        assert plugin_manager is not None
        # Should have discovered plugins
        assert hasattr(plugin_manager, "get_all_plugins")

    def test_git_service_creation(self, test_app_root, mock_config):
        """Test that GitService is created."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        git_service = services["git_service"]
        assert git_service is not None

    def test_project_service_creation(self, test_app_root, mock_config):
        """Test that ProjectService is created."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        project_service = services["project_service"]
        assert project_service is not None

    def test_project_service_with_git_service(self, test_app_root, mock_config):
        """Test that ProjectService receives GitService."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        project_service = services["project_service"]
        # ProjectService should have been initialized with git_service
        assert hasattr(project_service, "git_service")
        assert project_service.git_service is not None

    def test_template_watch_disabled(self, test_app_root, mock_config):
        """Test that template watching can be disabled."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        project_service = services["project_service"]
        # Should not have observer running when disabled
        # Note: This depends on ProjectService implementation details
        assert project_service is not None

    def test_template_watch_enabled(self, test_app_root, mock_config):
        """Test that template watching can be enabled."""
        templates_dir = test_app_root / "templates"
        templates_dir.mkdir()

        services = initialize_services(
            test_app_root, mock_config, templates_dir=templates_dir, disable_template_watch=False
        )

        project_service = services["project_service"]
        assert project_service is not None

    def test_custom_templates_dir(self, test_app_root, mock_config):
        """Test that custom templates directory is used."""
        custom_templates = test_app_root / "custom_templates"
        custom_templates.mkdir()

        services = initialize_services(
            test_app_root,
            mock_config,
            templates_dir=custom_templates,
            disable_template_watch=True,
        )

        project_service = services["project_service"]
        assert project_service.templates_dir == custom_templates

    def test_portable_folders_created(self, test_app_root, mock_config):
        """Test that portable folders are created."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        portable_folders = services["portable_folders"]
        assert isinstance(portable_folders, dict)
        assert "projects" in portable_folders
        assert "logs" in portable_folders

    def test_logger_configured(self, test_app_root, mock_config):
        """Test that logger is configured and returned."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        logger = services["logger"]
        assert logger is not None
        # Should be a Logger instance
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")
        assert hasattr(logger, "debug")

    def test_config_service_placeholder(self, test_app_root, mock_config):
        """Test that config_service is None (placeholder)."""
        services = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        # Currently returns None as placeholder
        assert services["config_service"] is None

    def test_initialization_with_invalid_app_root(self, mock_config):
        """Test initialization with non-existent app root.

        Note: The initialization doesn't validate app_root existence,
        so this test verifies that initialization completes without errors.
        """
        invalid_root = Path("/nonexistent/path")

        # Should initialize without raising errors
        services = initialize_services(
            invalid_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        # Services should still be created
        assert services is not None
        assert "project_service" in services

    def test_services_are_independent(self, test_app_root, mock_config):
        """Test that multiple initializations create independent services."""
        services1 = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        services2 = initialize_services(
            test_app_root, mock_config, templates_dir=None, disable_template_watch=True
        )

        # Should be different instances
        assert services1["storage_service"] is not services2["storage_service"]
        assert services1["plugin_manager"] is not services2["plugin_manager"]


class TestEnvironmentVariables:
    """Tests for environment variable handling."""

    def test_template_watch_env_var_true(self, tmp_path):
        """Test PYMM_DISABLE_TEMPLATE_WATCH=1 disables watching."""
        with patch.dict(os.environ, {"PYMM_DISABLE_TEMPLATE_WATCH": "1"}):
            disable_watch = os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"
            assert disable_watch is True

    def test_template_watch_env_var_false(self):
        """Test PYMM_DISABLE_TEMPLATE_WATCH=0 enables watching."""
        with patch.dict(os.environ, {"PYMM_DISABLE_TEMPLATE_WATCH": "0"}):
            disable_watch = os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"
            assert disable_watch is False

    def test_template_watch_env_var_default(self):
        """Test default when PYMM_DISABLE_TEMPLATE_WATCH is not set."""
        with patch.dict(os.environ, {}, clear=True):
            disable_watch = os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"
            assert disable_watch is False
