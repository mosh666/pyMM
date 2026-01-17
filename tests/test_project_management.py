"""
Test project management functionality.

This test script verifies:
- Project model creation and validation
- ProjectService CRUD operations
- Project serialization/deserialization
"""

from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))


from app.models.project import Project
from app.services.project_service import ProjectService


def test_project_model(tmp_path):
    """Test Project model."""

    # Create test project
    test_path = (tmp_path / "my_project").resolve()
    project = Project(
        name="My Test Project",
        path=test_path,
        description="A test project for media management",
    )

    # Test serialization
    project_dict = project.to_dict()

    # Test deserialization
    restored_project = Project.from_dict(project_dict)

    assert restored_project.name == project.name
    assert restored_project.path == project.path
    assert restored_project.description == project.description


def test_project_service(tmp_path):
    """Test ProjectService."""

    # Create service
    projects_dir = (tmp_path / ".metadata").resolve()
    projects_dir.mkdir(parents=True, exist_ok=True)
    service = ProjectService(projects_dir)

    # Create a test project
    project_path = (tmp_path / "service_test_project").resolve()

    metadata_file = service._get_metadata_file(project_path)

    try:
        # Create project
        project = service.create_project(
            name="Service Test Project",
            path=project_path,
            description="Testing project service",
        )

        # Load project
        loaded_project = service.load_project(project_path)
        assert loaded_project is not None
        assert loaded_project.name == project.name

        # List projects
        service.list_projects()

        # Update project
        project.description = "Updated description"
        service.save_project(project)

        # Reload and verify
        reloaded = service.load_project(project_path)
        assert reloaded.description == "Updated description"

        # Delete project
        service.delete_project(project, delete_files=True)

        # Verify deletion
        assert not project_path.exists()
        assert not metadata_file.exists()

    except Exception:
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    try:
        test_project_model()
        test_project_service()

    except Exception:
        sys.exit(1)
