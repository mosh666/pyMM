"""
Integration tests for project workflow.

Tests the complete lifecycle of a project from creation to deletion.
"""

import pytest

from app.services.project_service import ProjectService

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
        """Test creating a basic project."""
        project_path = test_projects_dir / "basic_project"

        project = project_service.create_project(
            name="Basic Project",
            path=project_path,
            description="A test project",
        )

        assert project is not None
        assert project.name == "Basic Project"
        assert project.path == project_path
        assert project.exists is True

        # Verify directory was created
        assert project_path.exists()
        assert project_path.is_dir()

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
