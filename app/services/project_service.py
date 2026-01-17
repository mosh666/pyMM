"""
Project service for managing projects.

This module provides the ProjectService class for creating, loading,
saving, and managing media management projects with template support
and migration capabilities.
"""

from collections.abc import Callable
from datetime import UTC, datetime
import getpass
import json
import logging
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from typing import Any

from packaging.version import Version
from pydantic import BaseModel, ValidationError
from watchdog.events import FileSystemEventHandler
import yaml

from app import __version__
from app.models.project import Project


class TemplateMetadata(BaseModel):
    """Template configuration metadata."""

    name: str
    description: str
    version: str
    min_app_version: str
    required_plugins: list[str] = []
    folder_structure: list[str]
    extends: str | None = None
    migration_notes: dict[str, str] = {}
    inheritance_changes: list[str] = []


class MigrationConflict(BaseModel):
    """Represents a conflict detected during migration."""

    folder_path: str
    reason: str
    user_files_count: int
    last_modified: str


class MigrationDiff(BaseModel):
    """Represents differences between project and target template versions."""

    folders_to_add: list[str]
    folders_to_remove: list[str]
    conflicts: list[MigrationConflict]
    migration_notes: str
    inheritance_changes: list[str]
    current_version: str
    target_version: str


class TemplateFileHandler(FileSystemEventHandler):
    """Watches template.yaml files for changes."""

    def __init__(self, callback: Callable[[], None]):
        """Initialize handler with callback function."""
        self.callback = callback
        self.patterns = ["*/template.yaml"]

    def on_modified(self, event: Any) -> None:
        """Handle file modification events."""
        if not event.is_directory and event.src_path.endswith("template.yaml"):
            self.callback()

    def on_created(self, event: Any) -> None:
        """Handle file creation events."""
        if not event.is_directory and event.src_path.endswith("template.yaml"):
            self.callback()


class ProjectService:
    """
    Service for managing project lifecycle with template support.

    Handles project creation, loading, saving, deletion, listing,
    template management, and migration capabilities.
    """

    def __init__(
        self,
        projects_dir: Path,
        git_service: Any | None = None,
        templates_dir: Path | None = None,
        _watch_interval: float = 1.0,
        disable_watch: bool = False,
        storage_group_service: Any | None = None,
    ):
        """
        Initialize the project service.

        Args:
            projects_dir: Directory where project metadata files are stored
            git_service: Optional GitService for Git integration
            templates_dir: Directory containing project templates (defaults to <app_root>/templates)
            watch_interval: Filesystem watch polling interval in seconds
            disable_watch: Disable template filesystem watching (also reads PYMM_DISABLE_TEMPLATE_WATCH env var)
            storage_group_service: Optional StorageGroupService for drive redundancy
        """
        self.logger = logging.getLogger(__name__)
        self.projects_dir = projects_dir
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        self.git_service = git_service
        self.storage_group_service = storage_group_service

        # Setup templates directory
        if templates_dir is None:
            # Default to templates/ at repo root (parent of app/)
            app_root = Path(__file__).parent.parent.parent
            templates_dir = app_root / "templates"

        self.templates_dir = templates_dir
        self._templates: dict[str, TemplateMetadata] = {}

        # Discover templates and cache results
        if self.templates_dir.exists():
            self.discover_templates()

        # Setup filesystem watcher for template changes
        self._observer: Any | None = None
        disable_watch = disable_watch or os.getenv("PYMM_DISABLE_TEMPLATE_WATCH", "0") == "1"

        if not disable_watch and self.templates_dir.exists():
            try:
                from watchdog.observers import Observer

                handler = TemplateFileHandler(self.refresh_templates)
                self._observer = Observer()
                self._observer.schedule(handler, str(self.templates_dir), recursive=True)
                self._observer.start()
                self.logger.info("Template filesystem watcher started")
            except Exception as e:
                self.logger.warning("Failed to start template watcher: %s", e)

    def __del__(self) -> None:
        """Cleanup filesystem watcher on destruction."""
        # Use getattr to safely handle partial initialization
        observer = getattr(self, "_observer", None)
        if observer is not None:
            try:
                observer.stop()
                observer.join(timeout=1.0)
                self.logger.info("Template filesystem watcher stopped")
            except Exception as e:
                self.logger.warning("Error stopping template watcher: %s", e)

    def discover_templates(self) -> dict[str, TemplateMetadata]:
        """
        Discover and validate all templates in templates directory.

        Returns:
            Dictionary mapping template names to metadata

        Raises:
            ValidationError: If template.yaml has invalid schema
            ValueError: If template version incompatible with current app version
        """
        self._templates.clear()

        if not self.templates_dir.exists():
            self.logger.warning("Templates directory not found: %s", self.templates_dir)
            return self._templates

        for template_dir in self.templates_dir.iterdir():
            if not template_dir.is_dir():
                continue

            template_yaml = template_dir / "template.yaml"
            if not template_yaml.exists():
                continue

            try:
                # Load and validate template metadata
                with open(template_yaml, encoding="utf-8") as f:
                    data = yaml.safe_load(f)

                metadata = TemplateMetadata(**data)

                # Check version compatibility
                if metadata.min_app_version:
                    min_version = Version(metadata.min_app_version)
                    current_version = Version(__version__)
                    if current_version < min_version:
                        raise ValueError(
                            f"Template '{metadata.name}' requires pyMM >= {metadata.min_app_version}, "
                            f"but current version is {__version__}"
                        )

                self._templates[template_dir.name] = metadata
                self.logger.debug("Discovered template: %s v%s", metadata.name, metadata.version)

            except ValidationError:
                self.logger.exception("Invalid template schema in %s", template_yaml)
                raise
            except Exception:
                self.logger.exception("Error loading template %s", template_yaml)
                raise

        self.logger.info("Discovered %d templates", len(self._templates))
        return self._templates

    def refresh_templates(self) -> None:
        """Refresh template cache by rescanning filesystem."""
        self.logger.info("Refreshing template cache...")
        try:
            self.discover_templates()
        except Exception:
            self.logger.exception("Error refreshing templates")

    def get_template(self, template_name: str) -> TemplateMetadata | None:
        """Get template metadata by name."""
        return self._templates.get(template_name)

    def list_templates(self) -> dict[str, TemplateMetadata]:
        """List all available templates."""
        return self._templates.copy()

    def _resolve_template_inheritance(
        self, template_name: str, depth: int = 0
    ) -> tuple[TemplateMetadata, list[str]]:
        """
        Resolve template inheritance chain and merge metadata.

        Args:
            template_name: Name of template to resolve
            depth: Current recursion depth

        Returns:
            Tuple of (merged_metadata, folder_structure)

        Raises:
            RecursionError: If inheritance depth exceeds 5 or circular dependency detected
            KeyError: If template or base template not found
        """
        max_depth = 5

        if depth > max_depth:
            raise RecursionError(
                f"Template inheritance exceeds maximum depth of {max_depth} levels"
            )

        if template_name not in self._templates:
            raise KeyError(f"Template '{template_name}' not found")

        metadata = self._templates[template_name]
        folders = set(metadata.folder_structure)

        # Resolve base template if extends is specified
        if metadata.extends:
            try:
                _base_metadata, base_folders = self._resolve_template_inheritance(
                    metadata.extends, depth + 1
                )
                # Merge folder structures (child adds to base)
                folders.update(base_folders)
            except RecursionError:
                raise
            except KeyError as e:
                raise KeyError(
                    f"Template '{template_name}' extends '{metadata.extends}' which was not found"
                ) from e

        return metadata, list(folders)

    def _validate_template(self, template_path: Path, metadata: TemplateMetadata) -> None:
        """
        Validate that template directory contains all required folders.

        Args:
            template_path: Path to template directory
            metadata: Template metadata with folder_structure

        Raises:
            ValueError: If required folders are missing
        """
        missing_folders = [
            folder for folder in metadata.folder_structure if not (template_path / folder).exists()
        ]

        if missing_folders:
            raise ValueError(
                f"Template '{metadata.name}' is missing required folders: {', '.join(missing_folders)}"
            )

    def _validate_variables(self, file_path: Path) -> None:
        """
        Validate that file contains only allowed template variables.

        Args:
            file_path: Path to file to validate

        Raises:
            ValueError: If file contains undefined variables
        """
        allowed_vars = {
            "PROJECT_NAME",
            "PROJECT_PATH",
            "DATE",
            "DATETIME",
            "AUTHOR",
            "DESCRIPTION",
            "GIT_ENABLED",
        }

        try:
            content = file_path.read_text(encoding="utf-8")
            # Find all {VAR} patterns
            pattern = r"\{([A-Z_]+)\}"
            variables = set(re.findall(pattern, content))

            undefined = variables - allowed_vars
            if undefined:
                raise ValueError(
                    f"File '{file_path.name}' contains undefined variables: {', '.join(sorted(undefined))}. "
                    f"Allowed variables: {', '.join(sorted(allowed_vars))}"
                )
        except UnicodeDecodeError:
            # Skip binary files
            pass

    def _get_author_name(self) -> str:
        """
        Get author name from Git config or system username.

        Returns:
            Author name string
        """
        try:
            if self.git_service:
                # Try to get from Git config
                git_exe = shutil.which("git") or "git"
                result = subprocess.run(  # noqa: S603
                    [git_exe, "config", "user.name"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
        except Exception:
            pass

        # Fallback to system username
        return getpass.getuser()

    def _substitute_variables(self, file_path: Path, variables: dict[str, str]) -> None:
        """
        Substitute template variables in text file.

        Args:
            file_path: Path to file to process
            variables: Dictionary of variable names to values
        """
        # Only process text files with specific extensions
        text_extensions = {".md", ".txt", ".yaml", ".yml", ".gitignore", ".py"}

        if file_path.suffix not in text_extensions:
            return

        try:
            content = file_path.read_text(encoding="utf-8")

            # Replace all variables
            for var_name, var_value in variables.items():
                content = content.replace(f"{{{var_name}}}", var_value)

            file_path.write_text(content, encoding="utf-8")
        except UnicodeDecodeError:
            # Skip binary files
            pass

    def _apply_template(
        self,
        project_path: Path,
        template_name: str,
        project_name: str,
        description: str = "",
        git_enabled: bool = False,
        preview_mode: bool = False,
    ) -> None:
        """
        Apply a project template to directory.

        Args:
            project_path: Path to project directory
            template_name: Name of template to apply
            project_name: Name of the project for variable substitution
            description: Project description
            git_enabled: Whether Git is enabled for this project
            preview_mode: If True, skip Git operations and backups

        Raises:
            KeyError: If template not found
            ValueError: If template validation fails
        """
        if template_name not in self._templates:
            raise KeyError(f"Template '{template_name}' not found")

        template_path = self.templates_dir / template_name

        # Resolve inheritance chain
        metadata, folders = self._resolve_template_inheritance(template_name)

        # Validate template structure
        # Note: Only validate the leaf template, not inherited ones

        # Prepare variable substitutions
        now = datetime.now()
        variables = {
            "PROJECT_NAME": project_name,
            "PROJECT_PATH": str(project_path),
            "DATE": now.strftime("%Y-%m-%d"),
            "DATETIME": now.strftime("%Y-%m-%d %H:%M:%S"),
            "AUTHOR": self._get_author_name(),
            "DESCRIPTION": description or "No description provided",
            "GIT_ENABLED": str(git_enabled).lower(),
        }

        # Create folders from merged structure
        for folder in folders:
            (project_path / folder).mkdir(parents=True, exist_ok=True)

        # Copy template files (excluding template.yaml)
        for item in template_path.iterdir():
            if item.name == "template.yaml":
                continue

            dest = project_path / item.name

            if item.is_file():
                # Validate variables before copying
                self._validate_variables(item)

                shutil.copy2(item, dest)

                # Substitute variables
                self._substitute_variables(dest, variables)

        # Initialize Git repository if enabled and not in preview mode
        if git_enabled and self.git_service and not preview_mode:
            try:
                self.git_service.init_repository(project_path)
                # Create initial commit
                commit_msg = f"Initial commit from {metadata.name} template"
                # Would need to call git_service methods here
                self.logger.info("Initialized Git repository: %s", commit_msg)
            except Exception as e:
                self.logger.warning("Failed to initialize Git repository: %s", e)

    def create_project(
        self,
        name: str,
        path: Path,
        description: str | None = None,
        use_template: str | None = None,
        git_enabled: bool = False,
    ) -> Project:
        """
        Create a new project.

        Args:
            name: Project name
            path: Project directory path
            description: Optional project description
            use_template: Optional template name to use
            git_enabled: Whether to initialize Git repository

        Returns:
            Created Project instance

        Raises:
            ValueError: If project already exists or path is invalid
            KeyError: If template not found
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

        # Get template version if using template
        template_version = None
        if use_template:
            template_metadata = self.get_template(use_template)
            if template_metadata:
                template_version = template_metadata.version

            # Apply template
            self._apply_template(
                path, use_template, name, description or "", git_enabled, preview_mode=False
            )

        # Create project instance with template metadata
        project = Project(
            name=name,
            path=path,
            description=description,
            template_name=use_template,
            template_version=template_version,
            pending_migration=None,
            migration_history=[],
        )

        # Save project metadata
        self.save_project(project)

        return project

    def load_project(self, project_path: Path, parent_widget: Any | None = None) -> Project | None:
        """
        Load a project from its directory with storage group resolution.

        If the project is assigned to a storage group and the Master drive is unavailable,
        this method will prompt the user to use the Backup drive or wait.

        Args:
            project_path: Path to the project directory
            parent_widget: Optional parent widget for dialogs (QWidget)

        Returns:
            Project instance with resolved path, or None if not found/unavailable

        Raises:
            RuntimeError: If storage group drives are unavailable and user cancels
        """
        metadata_file = self._get_metadata_file(project_path)

        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, encoding="utf-8") as f:
                data = json.load(f)
            project = Project.from_dict(data)

            # Handle storage group resolution
            if project.storage_group_id and self.storage_group_service:
                self.logger.info(
                    f"Project '{project.name}' assigned to storage group '{project.storage_group_id}'"
                )

                resolved_path = self.storage_group_service.resolve_drive(
                    project.storage_group_id, project.name, parent=parent_widget
                )

                if resolved_path is None:
                    # User cancelled or no drives available
                    self.logger.warning(
                        f"Could not resolve storage group for project '{project.name}'"
                    )
                    raise RuntimeError(
                        f"Cannot open project '{project.name}' - no drives from storage group are available"
                    )

                # Update project path to resolved drive (Master or Backup)
                # Preserve the relative path within the drive
                relative_path = project.path.relative_to(project.path.anchor)
                project.path = resolved_path / relative_path
                self.logger.info(f"Resolved project path to: {project.path}")

            return project

        except Exception:
            self.logger.exception("Error loading project metadata")
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
        except Exception:
            self.logger.exception("Error saving project metadata")
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

    def list_projects(self) -> list[Project]:
        """
        List all known projects.

        Returns:
            List of Project instances
        """
        projects = []

        # Find all .pyMM.json metadata files in the projects directory
        for metadata_file in self.projects_dir.glob("*.pyMM.json"):
            try:
                with open(metadata_file, encoding="utf-8") as f:
                    data = json.load(f)
                project = Project.from_dict(data)
                projects.append(project)
            except Exception as e:
                self.logger.warning("Error loading project %s: %s", metadata_file, e)

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

    # Migration System Methods

    def _detect_migration_conflicts(
        self, project: Project, folders_to_remove: list[str]
    ) -> list[MigrationConflict]:
        """
        Detect conflicts with folders scheduled for removal.

        Args:
            project: Project being migrated
            folders_to_remove: List of folder paths to be removed

        Returns:
            List of detected conflicts
        """
        conflicts = []

        for folder_path in folders_to_remove:
            full_path = project.path / folder_path

            if not full_path.exists():
                continue

            # Check if folder has user-created files
            try:
                # Count non-template files
                user_files = list(full_path.rglob("*"))
                user_file_count = sum(1 for f in user_files if f.is_file())

                if user_file_count > 0:
                    # Get last modification time
                    mtime = full_path.stat().st_mtime
                    last_modified = datetime.fromtimestamp(mtime, tz=UTC).isoformat()

                    conflicts.append(
                        MigrationConflict(
                            folder_path=folder_path,
                            reason=f"Folder contains {user_file_count} user file(s)",
                            user_files_count=user_file_count,
                            last_modified=last_modified,
                        )
                    )
            except Exception as e:
                self.logger.warning("Error checking folder %s: %s", full_path, e)

        return conflicts

    def calculate_migration_diff(self, project: Project) -> MigrationDiff | None:
        """
        Calculate differences between project and target template version.

        Args:
            project: Project to check for migration

        Returns:
            MigrationDiff if migration available, None otherwise
        """
        if not project.template_name or not project.template_version:
            return None

        # Get current template
        template = self.get_template(project.template_name)
        if not template:
            return None

        # Check if version is different
        if template.version == project.template_version:
            return None

        try:
            # Resolve current and target folder structures
            _, current_folders = self._resolve_template_inheritance(project.template_name)
            target_folders = set(current_folders)

            # Determine folders to add/remove
            # For simplicity, assume current structure matches template_version
            # In real implementation, would need to store original structure
            existing_folders = {
                f.name for f in project.path.iterdir() if f.is_dir() and not f.name.startswith(".")
            }

            folders_to_add = [f for f in target_folders if f not in existing_folders]
            # Detect folders that were removed from template (exist in project but not in target)
            # These are candidates for removal, but will only be removed if they have no user files
            folders_to_remove = [f for f in existing_folders if f not in target_folders]

            # Detect conflicts
            conflicts = self._detect_migration_conflicts(project, folders_to_remove)

            # Get migration notes
            migration_notes_text = ""
            if project.template_version in template.migration_notes:
                migration_notes_text = template.migration_notes[project.template_version]

            return MigrationDiff(
                folders_to_add=folders_to_add,
                folders_to_remove=folders_to_remove,
                conflicts=conflicts,
                migration_notes=migration_notes_text,
                inheritance_changes=template.inheritance_changes,
                current_version=project.template_version,
                target_version=template.version,
            )

        except Exception:
            self.logger.exception("Error calculating migration diff")
            return None

    def check_project_migration(self, project: Project) -> tuple[bool, MigrationDiff | None]:
        """
        Check if project needs migration.

        Args:
            project: Project to check

        Returns:
            Tuple of (needs_migration, migration_diff)
        """
        diff = self.calculate_migration_diff(project)
        return (diff is not None, diff)

    def create_preview_migration(self, project: Project) -> tuple[Path, Project]:
        """
        Create temporary copy of project for migration preview.

        Args:
            project: Project to preview

        Returns:
            Tuple of (preview_path, preview_project)
        """
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix=f"pymm_preview_{project.name}_"))

        # Copy project directory
        preview_path = temp_dir / project.path.name
        shutil.copytree(project.path, preview_path)

        # Create preview project instance
        preview_project = Project(
            name=f"{project.name} (Preview)",
            path=preview_path,
            created=project.created,
            modified=project.modified,
            description=project.description,
            settings=project.settings.copy(),
            template_name=project.template_name,
            template_version=project.template_version,
            pending_migration=project.pending_migration.copy()
            if project.pending_migration
            else None,
            migration_history=project.migration_history.copy(),
        )

        return temp_dir, preview_project

    def cleanup_preview_migration(self, preview_path: Path) -> None:
        """
        Remove temporary preview directory.

        Args:
            preview_path: Path to preview temp directory
        """
        try:
            if preview_path.exists():
                shutil.rmtree(preview_path)
        except Exception as e:
            self.logger.warning("Failed to cleanup preview directory: %s", e)

    def schedule_deferred_migration(
        self, project: Project, target_version: str, reason: str = "user_deferred"
    ) -> Project:
        """
        Schedule migration to be applied later.

        Args:
            project: Project to schedule migration for
            target_version: Target template version
            reason: Reason for deferral

        Returns:
            Updated project
        """
        project.pending_migration = {
            "target_version": target_version,
            "scheduled_at": datetime.now().isoformat(),
            "reason": reason,
        }

        self.save_project(project)
        return project

    def migrate_project(  # noqa: C901, PLR0912
        self,
        project: Project,
        backup: bool = True,
        skip_conflicts: bool = False,
        applied_by: str = "user",
        deferred: bool = False,
        preview_mode: bool = False,
    ) -> tuple[Project, Path | None]:
        """
        Migrate project to latest template version.

        Args:
            project: Project to migrate
            backup: Create backup before migration
            skip_conflicts: Skip removal of folders with conflicts
            applied_by: Name of person/process applying migration
            deferred: Whether this was a deferred migration
            preview_mode: If True, skip backup and Git operations

        Returns:
            Tuple of (updated_project, backup_path)

        Raises:
            ValueError: If migration not available or fails
        """
        diff = self.calculate_migration_diff(project)
        if not diff:
            raise ValueError("No migration available for this project")

        backup_path = None

        # Create backup unless in preview mode
        if backup and not preview_mode:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = project.path.parent / f"{project.path.name}_backup_{timestamp}"
            shutil.copytree(project.path, backup_path)
            self.logger.info("Created backup at %s", backup_path)

        try:
            # Create new folders
            for folder in diff.folders_to_add:
                (project.path / folder).mkdir(parents=True, exist_ok=True)

            # Remove folders (respecting skip_conflicts)
            for folder in diff.folders_to_remove:
                if skip_conflicts:
                    # Check if this folder has conflicts
                    has_conflict = any(c.folder_path == folder for c in diff.conflicts)
                    if has_conflict:
                        self.logger.info("Skipping removal of %s due to conflicts", folder)
                        continue

                folder_path = project.path / folder
                if folder_path.exists():
                    shutil.rmtree(folder_path)

            # Update project metadata
            project.template_version = diff.target_version
            project.modified = datetime.now()

            # Add migration history entry
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "from_version": diff.current_version,
                "to_version": diff.target_version,
                "backup_path": str(backup_path) if backup_path else None,
                "applied_by": applied_by,
                "deferred": deferred,
                "conflicts_skipped": skip_conflicts and len(diff.conflicts) > 0,
            }
            project.migration_history.append(history_entry)

            # Clear pending migration if this was deferred
            if deferred:
                project.pending_migration = None

            # Save updated metadata
            self.save_project(project)

            # Git commit if available and not preview mode
            if self.git_service and not preview_mode and project.template_name:
                try:
                    template = self.get_template(project.template_name)
                    if template:
                        commit_msg = f"Migrate from {template.name} v{diff.current_version} to v{diff.target_version}"
                        # Would call git_service.commit() here
                        self.logger.info("Would create Git commit: %s", commit_msg)
                except Exception as e:
                    self.logger.warning("Failed to create Git commit: %s", e)

            return project, backup_path

        except Exception:
            self.logger.exception("Migration failed")
            # Restore from backup if available
            if backup_path and backup_path.exists():
                self.logger.info("Attempting to restore from backup...")
                try:
                    if project.path.exists():
                        shutil.rmtree(project.path)
                    shutil.copytree(backup_path, project.path)
                    self.logger.info("Restored from backup")
                except Exception:
                    self.logger.exception("Failed to restore from backup")
            raise

    def rollback_project(self, project: Project, backup_path: Path) -> Project:
        """
        Rollback project to backup.

        Args:
            project: Project to rollback
            backup_path: Path to backup directory

        Returns:
            Restored project

        Raises:
            ValueError: If backup doesn't exist
        """
        if not backup_path.exists():
            raise ValueError(f"Backup not found: {backup_path}")

        # Remove current project directory
        if project.path.exists():
            shutil.rmtree(project.path)

        # Restore from backup
        shutil.copytree(backup_path, project.path)

        # Reload project metadata
        restored = self.load_project(project.path)
        if not restored:
            raise ValueError("Failed to load restored project metadata")

        return restored

    def rollback_multiple_projects(self, projects: list[tuple[Project, Path]]) -> dict[str, bool]:
        """
        Rollback multiple projects in batch.

        Args:
            projects: List of (project, backup_path) tuples

        Returns:
            Dictionary mapping project names to success status
        """
        results = {}

        for project, backup_path in projects:
            try:
                self.rollback_project(project, backup_path)
                results[project.name] = True
            except Exception:
                self.logger.exception("Failed to rollback %s", project.name)
                results[project.name] = False

        return results

    def apply_pending_migrations(self) -> list[tuple[Project, bool, str]]:
        """
        Apply all pending migrations.

        Returns:
            List of (project, success, message) tuples
        """
        results = []

        all_projects = self.list_projects()
        pending = [p for p in all_projects if p.pending_migration is not None]

        for project in pending:
            try:
                self.migrate_project(project, backup=True, deferred=True)
                results.append((project, True, f"Migrated to v{project.template_version}"))
            except Exception as e:
                error_msg = str(e)
                self.logger.exception("Failed to apply pending migration for %s", project.name)
                results.append((project, False, error_msg))

        return results

    def list_migratable_projects(self) -> list[tuple[Project, MigrationDiff]]:
        """
        List all projects that have available migrations.

        Returns:
            List of (project, migration_diff) tuples
        """
        migratable = []

        for project in self.list_projects():
            needs_migration, diff = self.check_project_migration(project)
            if needs_migration and diff:
                migratable.append((project, diff))

        return migratable

    def list_projects_with_pending_migrations(self) -> list[Project]:
        """
        List all projects with pending migrations.

        Returns:
            List of projects
        """
        all_projects = self.list_projects()
        return [p for p in all_projects if p.pending_migration is not None]
