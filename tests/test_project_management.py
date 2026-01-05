"""
Test project management functionality.

This test script verifies:
- Project model creation and validation
- ProjectService CRUD operations
- Project serialization/deserialization
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.project import Project
from app.services.project_service import ProjectService


def test_project_model():
    """Test Project model."""
    print("=" * 60)
    print("Testing Project Model")
    print("=" * 60)

    # Create test project
    test_path = Path("D:/pyMM/test_projects/my_project")
    project = Project(
        name="My Test Project",
        path=test_path,
        description="A test project for media management",
    )

    print(f"\n✓ Created project: {project.name}")
    print(f"  Path: {project.path}")
    print(f"  Created: {project.created}")

    # Test serialization
    project_dict = project.to_dict()
    print(f"\n✓ Serialized to dict: {len(project_dict)} keys")

    # Test deserialization
    restored_project = Project.from_dict(project_dict)
    print(f"✓ Deserialized from dict: {restored_project.name}")

    assert restored_project.name == project.name
    assert restored_project.path == project.path
    assert restored_project.description == project.description

    print("\n✅ Project model tests passed!")


def test_project_service():
    """Test ProjectService."""
    print("\n" + "=" * 60)
    print("Testing Project Service")
    print("=" * 60)

    # Create service
    projects_dir = Path("D:/pyMM/test_projects/.metadata")
    service = ProjectService(projects_dir)

    print("\n✓ Created ProjectService")
    print(f"  Metadata directory: {projects_dir}")

    # Create a test project
    project_path = Path("D:/pyMM/test_projects/service_test_project")

    # Clean up if exists
    if project_path.exists():
        import shutil

        shutil.rmtree(project_path)

    metadata_file = service._get_metadata_file(project_path)
    if metadata_file.exists():
        metadata_file.unlink()

    try:
        # Create project
        project = service.create_project(
            name="Service Test Project",
            path=project_path,
            description="Testing project service",
        )

        print(f"\n✓ Created project: {project.name}")
        print(f"  Path exists: {project.exists}")
        print(f"  Metadata file: {metadata_file}")

        # Load project
        loaded_project = service.load_project(project_path)
        assert loaded_project is not None
        assert loaded_project.name == project.name
        print(f"✓ Loaded project: {loaded_project.name}")

        # List projects
        projects = service.list_projects()
        print(f"✓ Listed {len(projects)} project(s)")

        # Update project
        project.description = "Updated description"
        service.save_project(project)
        print("✓ Updated project description")

        # Reload and verify
        reloaded = service.load_project(project_path)
        assert reloaded.description == "Updated description"
        print("✓ Verified updated description")

        # Delete project
        service.delete_project(project, delete_files=True)
        print("✓ Deleted project")

        # Verify deletion
        assert not project_path.exists()
        assert not metadata_file.exists()
        print("✓ Verified project deletion")

        print("\n✅ Project service tests passed!")

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        # Clean up
        if project_path.exists():
            import shutil

            shutil.rmtree(project_path)
        if metadata_file.exists():
            metadata_file.unlink()


if __name__ == "__main__":
    print("=" * 60)
    print("Project Management Test")
    print("=" * 60)

    try:
        test_project_model()
        test_project_service()

        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
