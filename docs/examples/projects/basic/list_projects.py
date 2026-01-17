#!/usr/bin/env python3
"""List all projects in a storage location.

This example demonstrates:
- Scanning for projects
- Reading project metadata
- Filtering and sorting projects
"""

import logging
from pathlib import Path

from app.services.file_system_service import FileSystemService
from app.services.project_service import ProjectService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """List all projects in test_projects directory."""
    # Set up services
    file_system_service = FileSystemService()
    project_service = ProjectService(file_system_service)

    # Storage location to scan
    storage_path = Path("test_projects")

    if not storage_path.exists():
        return

    try:
        # Discover all projects
        projects = project_service.discover_projects(storage_path)

        if not projects:
            return

        for project in sorted(projects, key=lambda p: p.name):
            # Check if project needs migration
            try:
                if project_service.needs_migration(project):
                    pass
            except:
                pass

        # Group by template
        templates = {}
        for project in projects:
            templates[project.template] = templates.get(project.template, 0) + 1

        if len(templates) > 1:
            for _template, _count in sorted(templates.items()):
                pass

    except Exception as e:
        logger.exception(f"Error listing projects: {e}")


if __name__ == "__main__":
    main()
