#!/usr/bin/env python3
"""Create a new media project.

This example demonstrates:
- Using ProjectService to create projects
- Setting project metadata
- Understanding project structure
"""

import logging
from pathlib import Path

from app.services.file_system_service import FileSystemService
from app.services.project_service import ProjectService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Create a new project in a test directory."""
    # Set up services
    # In a real app, these would come from dependency injection
    file_system_service = FileSystemService()
    project_service = ProjectService(file_system_service)

    # Define project parameters
    project_name = "MyMediaProject"
    project_path = Path("test_projects") / project_name

    # Create test_projects directory if it doesn't exist
    test_dir = Path("test_projects")
    test_dir.mkdir(exist_ok=True)

    try:
        # Create the project
        project_service.create_project(
            name=project_name,
            path=project_path,
            template="basic",  # Use basic template
            description="Example media project for demonstration",
        )

        # Check project structure
        if project_path.exists():
            for item in sorted(project_path.rglob("*")):
                if item.is_file():
                    item.relative_to(project_path)

    except Exception as e:
        logger.exception(f"Failed to create project: {e}")


if __name__ == "__main__":
    main()
