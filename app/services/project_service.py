"""
Project service for managing projects.

This module provides the ProjectService class for creating, loading,
saving, and managing media management projects.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.models.project import Project


class ProjectService:
    """
    Service for managing project lifecycle.
    
    Handles project creation, loading, saving, deletion, and listing.
    Projects are stored as JSON files in the projects directory.
    """
    
    def __init__(self, projects_dir: Path):
        """
        Initialize the project service.
        
        Args:
            projects_dir: Directory where project metadata files are stored
        """
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)
    
    def create_project(
        self,
        name: str,
        path: Path,
        description: Optional[str] = None,
        git_enabled: bool = True,
        use_template: Optional[str] = None,
    ) -> Project:
        """
        Create a new project.
        
        Args:
            name: Project name
            path: Project directory path
            description: Optional project description
            git_enabled: Whether to enable Git integration
            use_template: Optional template name to use
        
        Returns:
            Created Project instance
        
        Raises:
            ValueError: If project already exists or path is invalid
        """
        # Convert to Path if string
        if isinstance(path, str):
            path = Path(path)
        
        # Ensure path is absolute
        if not path.is_absolute():
            raise ValueError(f"Project path must be absolute: {path}")
        
        # Check if project already exists
        if path.exists():
            raise ValueError(f"Directory already exists: {path}")
        
        # Create project directory
        path.mkdir(parents=True, exist_ok=True)
        
        # Apply template if specified
        if use_template:
            self._apply_template(path, use_template)
        
        # Create project instance
        project = Project(
            name=name,
            path=path,
            description=description,
            git_enabled=git_enabled,
        )
        
        # Save project metadata
        self.save_project(project)
        
        return project
    
    def load_project(self, project_path: Path) -> Optional[Project]:
        """
        Load a project from its directory.
        
        Args:
            project_path: Path to the project directory
        
        Returns:
            Project instance or None if not found
        """
        metadata_file = self._get_metadata_file(project_path)
        
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Project.from_dict(data)
        except Exception as e:
            print(f"Error loading project metadata: {e}")
            return None
    
    def save_project(self, project: Project) -> None:
        """
        Save project metadata.
        
        Args:
            project: Project to save
        """
        # Update modified timestamp
        project.modified = datetime.now()
        
        # Get metadata file path
        metadata_file = self._get_metadata_file(project.path)
        
        # Save metadata
        try:
            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(project.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving project metadata: {e}")
            raise
    
    def delete_project(self, project: Project, delete_files: bool = False) -> None:
        """
        Delete a project.
        
        Args:
            project: Project to delete
            delete_files: Whether to delete project files (default: False)
        """
        metadata_file = self._get_metadata_file(project.path)
        
        # Remove metadata file
        if metadata_file.exists():
            metadata_file.unlink()
        
        # Optionally delete project directory
        if delete_files and project.path.exists():
            shutil.rmtree(project.path)
    
    def list_projects(self) -> List[Project]:
        """
        List all known projects.
        
        Returns:
            List of Project instances
        """
        projects = []
        
        # Find all .pyMM.json metadata files in the projects directory
        for metadata_file in self.projects_dir.glob("*.pyMM.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                project = Project.from_dict(data)
                projects.append(project)
            except Exception as e:
                print(f"Error loading project {metadata_file}: {e}")
        
        # Sort by modified date (most recent first)
        projects.sort(key=lambda p: p.modified, reverse=True)
        
        return projects
    
    def _get_metadata_file(self, project_path: Path) -> Path:
        """
        Get the path to the project metadata file.
        
        Args:
            project_path: Path to the project directory
        
        Returns:
            Path to metadata file in projects directory
        """
        # Use a sanitized version of the project path as the filename
        # Replace path separators with underscores
        filename = str(project_path).replace(":", "").replace("\\", "_").replace("/", "_")
        return self.projects_dir / f"{filename}.pyMM.json"
    
    def _apply_template(self, project_path: Path, template_name: str) -> None:
        """
        Apply a project template.
        
        Args:
            project_path: Path to the project directory
            template_name: Name of the template to apply
        """
        # TODO: Implement template system
        # For now, just create basic directory structure
        (project_path / "media").mkdir(exist_ok=True)
        (project_path / "exports").mkdir(exist_ok=True)
        (project_path / "cache").mkdir(exist_ok=True)
        
        # Create a basic README
        readme = project_path / "README.md"
        readme.write_text(f"# {project_path.name}\n\nMedia management project.\n")
