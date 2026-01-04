"""
Integration tests for project workflow.

Tests the complete lifecycle of a project from creation to deletion.
"""

import pytest
import shutil
from pathlib import Path

from app.models.project import Project
from app.services.project_service import ProjectService
from app.services.git_service import GitService

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def test_projects_dir(tmp_path):
    """Create a temporary projects directory."""
    return tmp_path / "projects"


@pytest.fixture
def project_service(test_projects_dir):
    """Create a ProjectService with test directory."""
    metadata_dir = test_projects_dir / ".metadata"
    return ProjectService(metadata_dir)


class TestProjectWorkflow:
    """Integration tests for complete project workflows."""
    
    def test_create_basic_project(self, project_service, test_projects_dir):
        """Test creating a basic project without Git."""
        project_path = test_projects_dir / "basic_project"
        
        project = project_service.create_project(
            name="Basic Project",
            path=project_path,
            description="A test project",
            git_enabled=False,
        )
        
        assert project is not None
        assert project.name == "Basic Project"
        assert project.path == project_path
        assert project.exists is True
        assert project.is_git_repo is False
        
        # Verify directory was created
        assert project_path.exists()
        assert project_path.is_dir()
    
    def test_create_project_with_git(self, project_service, test_projects_dir):
        """Test creating a project with Git initialization."""
        project_path = test_projects_dir / "git_project"
        
        project = project_service.create_project(
            name="Git Project",
            path=project_path,
            description="A project with Git",
            git_enabled=True,
        )
        
        assert project.git_enabled is True
        
        # Initialize Git
        success = project_service.init_git_repository(project, initial_commit=True)
        assert success is True
        
        # Reload project and check Git status
        project = project_service.load_project(project_path)
        assert project.is_git_repo is True
        
        # Verify .git directory exists
        assert (project_path / ".git").exists()
    
    def test_project_lifecycle(self, project_service, test_projects_dir):
        """Test complete project lifecycle: create → modify → delete."""
        project_path = test_projects_dir / "lifecycle_project"
        
        # Create
        project = project_service.create_project(
            name="Lifecycle Project",
            path=project_path,
        )
        assert project.exists is True
        
        # Modify metadata
        project.description = "Updated description"
        project_service.save_project(project)
        
        # Reload and verify changes
        reloaded = project_service.load_project(project_path)
        assert reloaded.description == "Updated description"
        
        # List projects
        projects = project_service.list_projects()
        assert len(projects) >= 1
        assert any(p.name == "Lifecycle Project" for p in projects)
        
        # Delete
        project_service.delete_project(project, delete_files=True)
        assert not project_path.exists()
        
        # Verify metadata is gone
        loaded = project_service.load_project(project_path)
        assert loaded is None
    
    def test_git_operations_workflow(self, project_service, test_projects_dir):
        """Test Git operations within a project."""
        project_path = test_projects_dir / "git_workflow"
        
        # Create project with Git
        project = project_service.create_project(
            name="Git Workflow Project",
            path=project_path,
            git_enabled=True,
        )
        
        # Initialize Git
        success = project_service.init_git_repository(project, initial_commit=True)
        assert success is True
        
        # Create a file in the project
        test_file = project_path / "README.md"
        test_file.write_text("# Git Workflow Project\n\nTesting Git integration.")
        
        # Check status
        status = project_service.get_git_status(project)
        assert status is not None
        assert status["is_dirty"] is True
        assert len(status["untracked"]) == 1
        assert "README.md" in status["untracked"]
        
        # Commit the file
        success = project_service.commit_changes(
            project,
            "Add README",
            add_all=True,
        )
        assert success is True
        
        # Check status is clean
        status = project_service.get_git_status(project)
        assert status["is_dirty"] is False
        assert status["total_changes"] == 0
        
        # Get commit log
        log = project_service.get_git_log(project, max_count=5)
        assert len(log) >= 1
        assert any("Add README" in commit["message"] for commit in log)
    
    def test_multiple_projects(self, project_service, test_projects_dir):
        """Test managing multiple projects simultaneously."""
        project_count = 3
        projects = []
        
        # Create multiple projects
        for i in range(project_count):
            project_path = test_projects_dir / f"project_{i}"
            project = project_service.create_project(
                name=f"Project {i}",
                path=project_path,
                description=f"Test project number {i}",
            )
            projects.append(project)
        
        # List all projects
        all_projects = project_service.list_projects()
        assert len(all_projects) >= project_count
        
        # Verify each project
        for i, project in enumerate(projects):
            loaded = project_service.load_project(project.path)
            assert loaded is not None
            assert loaded.name == f"Project {i}"
            assert loaded.description == f"Test project number {i}"
        
        # Delete all test projects
        for project in projects:
            project_service.delete_project(project, delete_files=True)
        
        # Verify deletion
        for project in projects:
            assert not project.path.exists()
    
    def test_project_with_subdirectories(self, project_service, test_projects_dir):
        """Test project with nested directory structure."""
        project_path = test_projects_dir / "structured_project"
        
        project = project_service.create_project(
            name="Structured Project",
            path=project_path,
        )
        
        # Create subdirectories
        (project_path / "media" / "videos").mkdir(parents=True)
        (project_path / "media" / "images").mkdir(parents=True)
        (project_path / "exports").mkdir()
        
        # Create some files
        (project_path / "media" / "videos" / "clip1.mp4").touch()
        (project_path / "media" / "images" / "photo1.jpg").touch()
        
        # Initialize Git
        success = project_service.init_git_repository(project, initial_commit=True)
        assert success is True
        
        # Commit the structure
        success = project_service.commit_changes(
            project,
            "Initial project structure",
            add_all=True,
        )
        assert success is True
        
        # Verify project still loads correctly
        loaded = project_service.load_project(project_path)
        assert loaded is not None
        assert loaded.is_git_repo is True
