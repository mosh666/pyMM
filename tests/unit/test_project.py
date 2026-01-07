"""
Tests for Project model and ProjectService.
"""

from datetime import datetime
from pathlib import Path

import pytest

from app.models.project import Project
from app.services.project_service import ProjectService


@pytest.fixture
def test_projects_dir(tmp_path):
    """Create a temporary projects directory."""
    projects_dir = tmp_path / ".metadata"
    projects_dir.mkdir(parents=True)
    return projects_dir


@pytest.fixture
def project_service(test_projects_dir):
    """Create a ProjectService instance."""
    return ProjectService(test_projects_dir)


@pytest.fixture
def sample_project_path(tmp_path):
    """Create a sample project path."""
    return tmp_path / "test_project"


class TestProject:
    """Tests for Project model."""

    def test_project_creation(self, sample_project_path):
        """Test creating a Project instance."""
        project = Project(
            name="Test Project",
            path=sample_project_path,
            description="A test project",
        )

        assert project.name == "Test Project"
        assert project.path == sample_project_path
        assert project.description == "A test project"
        assert isinstance(project.created, datetime)
        assert isinstance(project.modified, datetime)

    def test_project_path_validation(self):
        """Test that relative paths are rejected."""
        with pytest.raises(ValueError, match="must be absolute"):
            Project(name="Test", path=Path("relative/path"))

    def test_project_exists_property(self, sample_project_path):
        """Test the exists property."""
        project = Project(name="Test", path=sample_project_path)

        assert not project.exists

        sample_project_path.mkdir(parents=True)
        assert project.exists

    def test_project_to_dict(self, sample_project_path):
        """Test project serialization."""
        project = Project(
            name="Test Project",
            path=sample_project_path,
            description="Test",
        )

        data = project.to_dict()

        assert data["name"] == "Test Project"
        assert data["path"] == str(sample_project_path)
        assert data["description"] == "Test"
        assert "created" in data
        assert "modified" in data
        assert "settings" in data

    def test_project_from_dict(self, sample_project_path):
        """Test project deserialization."""
        data = {
            "name": "Test Project",
            "path": str(sample_project_path),
            "created": "2024-01-01T12:00:00",
            "modified": "2024-01-02T12:00:00",
            "description": "Test",
            "settings": {"key": "value"},
        }

        project = Project.from_dict(data)

        assert project.name == "Test Project"
        assert project.path == sample_project_path
        assert project.description == "Test"
        assert project.settings == {"key": "value"}


class TestProjectService:
    """Tests for ProjectService."""

    def test_service_initialization(self, test_projects_dir):
        """Test ProjectService initialization."""
        service = ProjectService(test_projects_dir)

        assert service.projects_dir == test_projects_dir
        assert test_projects_dir.exists()

    def test_create_project(self, project_service, sample_project_path):
        """Test creating a new project."""
        project = project_service.create_project(
            name="Test Project",
            path=sample_project_path,
            description="A test project",
        )

        assert project.name == "Test Project"
        assert project.path == sample_project_path
        assert project.exists
        assert sample_project_path.exists()

    def test_create_project_with_template(self, project_service, sample_project_path):
        """Test creating a project with template."""
        project = project_service.create_project(
            name="Test Project",
            path=sample_project_path,
            use_template="default",
        )

        assert project.exists
        assert (sample_project_path / "media").exists()
        assert (sample_project_path / "exports").exists()
        assert (sample_project_path / "cache").exists()
        assert (sample_project_path / "README.md").exists()

    def test_create_project_existing_path(self, project_service, sample_project_path):
        """Test that creating project with existing path raises error."""
        sample_project_path.mkdir(parents=True)

        with pytest.raises(ValueError, match="already exists"):
            project_service.create_project(
                name="Test",
                path=sample_project_path,
            )

    def test_save_and_load_project(self, project_service, sample_project_path):
        """Test saving and loading a project."""
        sample_project_path.mkdir(parents=True)

        original = Project(
            name="Test Project",
            path=sample_project_path,
            description="Test",
        )

        project_service.save_project(original)

        loaded = project_service.load_project(sample_project_path)

        assert loaded is not None
        assert loaded.name == original.name
        assert loaded.path == original.path
        assert loaded.description == original.description

    def test_load_nonexistent_project(self, project_service, sample_project_path):
        """Test loading a project that doesn't exist."""
        loaded = project_service.load_project(sample_project_path)
        assert loaded is None

    def test_list_projects(self, project_service, tmp_path):
        """Test listing projects."""
        # Create multiple projects
        for i in range(3):
            path = tmp_path / f"project_{i}"
            project_service.create_project(
                name=f"Project {i}",
                path=path,
            )

        projects = project_service.list_projects()

        assert len(projects) == 3
        assert all(isinstance(p, Project) for p in projects)
        # Should be sorted by modified date (most recent first)
        assert projects[0].name == "Project 2"

    def test_delete_project(self, project_service, sample_project_path):
        """Test deleting a project."""
        project = project_service.create_project(
            name="Test",
            path=sample_project_path,
        )

        metadata_file = project_service._get_metadata_file(sample_project_path)
        assert metadata_file.exists()

        project_service.delete_project(project, delete_files=False)

        assert not metadata_file.exists()
        assert sample_project_path.exists()  # Files not deleted

    def test_delete_project_with_files(self, project_service, sample_project_path):
        """Test deleting a project with files."""
        project = project_service.create_project(
            name="Test",
            path=sample_project_path,
        )

        project_service.delete_project(project, delete_files=True)

        metadata_file = project_service._get_metadata_file(sample_project_path)
        assert not metadata_file.exists()
        assert not sample_project_path.exists()  # Files deleted

    def test_metadata_file_naming(self, project_service):
        """Test metadata file naming convention."""
        test_path = Path("D:/Test/Project")

        metadata_file = project_service._get_metadata_file(test_path)

        # Should sanitize path for filename
        assert metadata_file.name.endswith(".pyMM.json")
        assert ":" not in metadata_file.name
        assert "\\" not in metadata_file.name
        assert "/" not in metadata_file.name


class TestProjectTemplateFields:
    """Tests for template-related fields in Project model."""

    def test_project_with_template_fields(self, sample_project_path):
        """Test creating project with template metadata."""
        project = Project(
            name="Test",
            path=sample_project_path,
            template_name="default",
            template_version="1.0.0",
        )

        assert project.template_name == "default"
        assert project.template_version == "1.0.0"
        assert project.pending_migration is None
        assert project.migration_history == []

    def test_template_fields_in_serialization(self, sample_project_path):
        """Test template fields are serialized correctly."""
        project = Project(
            name="Test",
            path=sample_project_path,
            template_name="video-editing",
            template_version="2.1.0",
        )

        data = project.to_dict()

        assert data["template_name"] == "video-editing"
        assert data["template_version"] == "2.1.0"
        assert data["pending_migration"] is None
        assert data["migration_history"] == []

    def test_template_fields_in_deserialization(self, sample_project_path):
        """Test template fields are deserialized correctly."""
        data = {
            "name": "Test",
            "path": str(sample_project_path),
            "created": "2024-01-01T12:00:00",
            "modified": "2024-01-02T12:00:00",
            "template_name": "photo-management",
            "template_version": "1.5.2",
        }

        project = Project.from_dict(data)

        assert project.template_name == "photo-management"
        assert project.template_version == "1.5.2"

    def test_optional_template_fields(self, sample_project_path):
        """Test that template fields are optional."""
        project = Project(name="Test", path=sample_project_path)

        assert project.template_name is None
        assert project.template_version is None

        # Should serialize without errors
        data = project.to_dict()
        assert "template_name" in data
        assert data["template_name"] is None


class TestProjectMigrationFields:
    """Tests for migration-related fields in Project model."""

    def test_pending_migration_field(self, sample_project_path):
        """Test pending_migration field."""
        pending = {
            "target_version": "2.0.0",
            "scheduled_at": "2024-01-01T12:00:00",
            "reason": "Deferred by user",
        }

        project = Project(
            name="Test",
            path=sample_project_path,
            pending_migration=pending,
        )

        assert project.pending_migration == pending
        assert project.pending_migration["target_version"] == "2.0.0"

    def test_migration_history_field(self, sample_project_path):
        """Test migration_history field."""
        history = [
            {
                "from_version": "1.0.0",
                "to_version": "1.1.0",
                "timestamp": "2024-01-01T12:00:00",
                "backup_path": "/backups/project_backup_20240101",
            },
            {
                "from_version": "1.1.0",
                "to_version": "2.0.0",
                "timestamp": "2024-01-02T12:00:00",
                "backup_path": "/backups/project_backup_20240102",
            },
        ]

        project = Project(
            name="Test",
            path=sample_project_path,
            migration_history=history,
        )

        assert len(project.migration_history) == 2
        assert project.migration_history[0]["from_version"] == "1.0.0"
        assert project.migration_history[1]["to_version"] == "2.0.0"

    def test_migration_fields_serialization(self, sample_project_path):
        """Test migration fields are serialized correctly."""
        project = Project(
            name="Test",
            path=sample_project_path,
            pending_migration={"target_version": "3.0.0"},
            migration_history=[
                {"from_version": "1.0.0", "to_version": "2.0.0"}
            ],
        )

        data = project.to_dict()

        assert data["pending_migration"]["target_version"] == "3.0.0"
        assert len(data["migration_history"]) == 1
        assert data["migration_history"][0]["from_version"] == "1.0.0"

    def test_migration_fields_deserialization(self, sample_project_path):
        """Test migration fields are deserialized correctly."""
        data = {
            "name": "Test",
            "path": str(sample_project_path),
            "created": "2024-01-01T12:00:00",
            "modified": "2024-01-02T12:00:00",
            "pending_migration": {
                "target_version": "2.5.0",
                "reason": "Auto-detected update",
            },
            "migration_history": [
                {
                    "from_version": "1.0.0",
                    "to_version": "2.0.0",
                    "timestamp": "2024-01-01T10:00:00",
                }
            ],
        }

        project = Project.from_dict(data)

        assert project.pending_migration["target_version"] == "2.5.0"
        assert len(project.migration_history) == 1
        assert project.migration_history[0]["to_version"] == "2.0.0"

    def test_empty_migration_history(self, sample_project_path):
        """Test default empty migration history."""
        project = Project(name="Test", path=sample_project_path)

        assert project.migration_history == []
        assert isinstance(project.migration_history, list)

    def test_none_pending_migration(self, sample_project_path):
        """Test default None pending_migration."""
        project = Project(name="Test", path=sample_project_path)

        assert project.pending_migration is None


class TestProjectValidation:
    """Tests for Project model validation."""

    def test_name_validation_empty(self, tmp_path):
        """Test that empty name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Project(name="", path=tmp_path)

    def test_name_validation_whitespace(self, tmp_path):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValueError, match="cannot be empty"):
            Project(name="   ", path=tmp_path)

    def test_path_validation_relative(self):
        """Test that relative paths are rejected."""
        with pytest.raises(ValueError, match="must be absolute"):
            Project(name="Test", path=Path("relative/path"))

    def test_complex_migration_history(self, sample_project_path):
        """Test project with complex migration history."""
        history = [
            {
                "from_version": "1.0.0",
                "to_version": "1.1.0",
                "timestamp": "2024-01-01T12:00:00",
                "backup_path": "/backup1",
                "folders_added": ["source", "proxies"],
                "folders_removed": [],
                "conflicts": 0,
            },
            {
                "from_version": "1.1.0",
                "to_version": "2.0.0",
                "timestamp": "2024-01-02T12:00:00",
                "backup_path": "/backup2",
                "folders_added": ["renders"],
                "folders_removed": ["cache"],
                "conflicts": 1,
            },
        ]

        project = Project(
            name="Test",
            path=sample_project_path,
            template_name="video-editing",
            template_version="2.0.0",
            migration_history=history,
        )

        # Should serialize and deserialize correctly
        data = project.to_dict()
        restored = Project.from_dict(data)

        assert len(restored.migration_history) == 2
        assert restored.migration_history[1]["conflicts"] == 1
        assert "renders" in restored.migration_history[1]["folders_added"]

    def test_project_with_all_fields(self, sample_project_path):
        """Test project with all possible fields set."""
        project = Project(
            name="Complete Project",
            path=sample_project_path,
            description="Full test",
            template_name="photo-management",
            template_version="1.5.0",
            pending_migration={
                "target_version": "2.0.0",
                "scheduled_at": "2024-01-05T12:00:00",
            },
            migration_history=[
                {
                    "from_version": "1.0.0",
                    "to_version": "1.5.0",
                    "timestamp": "2024-01-01T12:00:00",
                }
            ],
            settings={"custom_key": "custom_value"},
        )

        # Full round-trip test
        data = project.to_dict()
        restored = Project.from_dict(data)

        assert restored.name == "Complete Project"
        assert restored.template_name == "photo-management"
        assert restored.template_version == "1.5.0"
        assert restored.pending_migration["target_version"] == "2.0.0"
        assert len(restored.migration_history) == 1
        assert restored.settings["custom_key"] == "custom_value"

    def test_backwards_compatibility(self, sample_project_path):
        """Test that old projects without template fields still work."""
        # Old project data without template fields
        data = {
            "name": "Old Project",
            "path": str(sample_project_path),
            "created": "2023-01-01T12:00:00",
            "modified": "2023-01-01T12:00:00",
            "description": "Legacy project",
            "settings": {},
        }

        project = Project.from_dict(data)

        assert project.name == "Old Project"
        assert project.template_name is None
        assert project.template_version is None
        assert project.pending_migration is None
        assert project.migration_history == []
