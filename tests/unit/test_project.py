"""
Tests for Project model and ProjectService.
"""

import pytest
import shutil
from pathlib import Path
from datetime import datetime

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
        assert project.git_enabled is True
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
    
    def test_project_is_git_repo_property(self, sample_project_path):
        """Test the is_git_repo property."""
        sample_project_path.mkdir(parents=True)
        project = Project(name="Test", path=sample_project_path)
        
        assert not project.is_git_repo
        
        (sample_project_path / ".git").mkdir()
        assert project.is_git_repo
    
    def test_project_to_dict(self, sample_project_path):
        """Test project serialization."""
        project = Project(
            name="Test Project",
            path=sample_project_path,
            description="Test",
            git_enabled=True,
        )
        
        data = project.to_dict()
        
        assert data["name"] == "Test Project"
        assert data["path"] == str(sample_project_path)
        assert data["description"] == "Test"
        assert data["git_enabled"] is True
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
            "git_enabled": True,
            "settings": {"key": "value"},
        }
        
        project = Project.from_dict(data)
        
        assert project.name == "Test Project"
        assert project.path == sample_project_path
        assert project.description == "Test"
        assert project.git_enabled is True
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
            git_enabled=False,
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
