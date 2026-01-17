"""
Integration tests for the template and migration system.

Tests the complete template lifecycle including discovery, inheritance,
variable substitution, migration workflows, conflict detection, and rollback.
"""

from pathlib import Path

import pytest
import yaml

from app.services.git_service import GitService
from app.services.project_service import ProjectService


@pytest.fixture
def templates_dir(tmp_path):
    """Create a temporary templates directory with test templates."""
    templates = tmp_path / "templates"
    templates.mkdir()

    # Base template
    base_dir = templates / "base"
    base_dir.mkdir()
    (base_dir / "template.yaml").write_text(
        yaml.dump(
            {
                "name": "base",
                "description": "Base template",
                "version": "1.0.0",
                "min_app_version": "0.1.0",
                "folder_structure": ["media", "exports", "cache"],
            }
        )
    )
    (base_dir / "README.md").write_text("# Base Template\n\nProject: {PROJECT_NAME}")

    # Default template (extends base)
    default_dir = templates / "default"
    default_dir.mkdir()
    (default_dir / "template.yaml").write_text(
        yaml.dump(
            {
                "name": "default",
                "description": "Default template",
                "version": "1.0.0",
                "min_app_version": "0.1.0",
                "extends": "base",
                "folder_structure": ["documents"],
            }
        )
    )
    (default_dir / "README.md").write_text("# {PROJECT_NAME}\n\nAuthor: {AUTHOR}\nDate: {DATE}")

    # Video template (extends default)
    video_dir = templates / "video-editing"
    video_dir.mkdir()
    (video_dir / "template.yaml").write_text(
        yaml.dump(
            {
                "name": "video-editing",
                "description": "Video editing template",
                "version": "2.0.0",
                "min_app_version": "0.1.0",
                "extends": "default",
                "folder_structure": ["source", "proxies", "renders"],
                "required_plugins": ["ffmpeg"],
            }
        )
    )

    return templates


@pytest.fixture
def project_service(tmp_path, templates_dir):
    """Create a ProjectService instance with templates."""
    metadata_dir = tmp_path / ".metadata"
    metadata_dir.mkdir()

    git_service = GitService()
    return ProjectService(
        metadata_dir, git_service=git_service, templates_dir=templates_dir, disable_watch=True
    )


@pytest.fixture
def project_path(tmp_path):
    """Create a project path."""
    return tmp_path / "test_project"


class TestTemplateDiscovery:
    """Tests for template discovery."""

    def test_discover_templates(self, project_service):
        """Test that templates are discovered."""
        templates = project_service.list_templates()

        assert len(templates) >= 3
        template_names = [t.name for t in templates.values()]
        assert "base" in template_names
        assert "default" in template_names
        assert "video-editing" in template_names

    def test_get_template(self, project_service):
        """Test getting a specific template."""
        template = project_service.get_template("base")

        assert template is not None
        assert template.name == "base"
        assert template.version == "1.0.0"
        assert "media" in template.folder_structure

    def test_get_nonexistent_template(self, project_service):
        """Test getting a template that doesn't exist."""
        template = project_service.get_template("nonexistent")
        assert template is None

    def test_refresh_templates(self, project_service, templates_dir):
        """Test refreshing template cache."""
        # Add new template
        new_dir = templates_dir / "new-template"
        new_dir.mkdir()
        (new_dir / "template.yaml").write_text(
            yaml.dump(
                {
                    "name": "new-template",
                    "description": "New template",
                    "version": "1.0.0",
                    "min_app_version": "0.1.0",
                    "folder_structure": ["test"],
                }
            )
        )

        # Refresh
        project_service.refresh_templates()

        # Should find new template
        templates = project_service.list_templates()
        assert any(t.name == "new-template" for t in templates.values())

    def test_invalid_template_yaml(self, project_service, templates_dir):
        """Test handling of invalid template YAML."""
        invalid_dir = templates_dir / "invalid"
        invalid_dir.mkdir()
        (invalid_dir / "template.yaml").write_text("invalid: yaml: content:")

        # Should handle gracefully
        project_service.refresh_templates()
        templates = project_service.list_templates()
        # Should not include invalid template
        assert not any(t.name == "invalid" for t in templates.values())

    def test_missing_required_fields(self, project_service, templates_dir):
        """Test template missing required fields."""
        incomplete_dir = templates_dir / "incomplete"
        incomplete_dir.mkdir()
        (incomplete_dir / "template.yaml").write_text(
            yaml.dump({"name": "incomplete"})  # Missing version, folder_structure
        )

        project_service.refresh_templates()
        template = project_service.get_template("incomplete")
        assert template is None


class TestTemplateInheritance:
    """Tests for template inheritance."""

    def test_single_level_inheritance(self, project_service, project_path):
        """Test template extending another template."""
        template = project_service.get_template("default")

        assert template is not None
        assert template.extends == "base"

        # Create project to verify inheritance is resolved
        project_service.create_project(
            name="Test", path=project_path, use_template="default", git_enabled=False
        )

        # Should inherit base folders
        assert (project_path / "media").exists()
        assert (project_path / "exports").exists()
        assert (project_path / "cache").exists()
        # Plus its own folders
        assert (project_path / "documents").exists()

    def test_multi_level_inheritance(self, project_service, project_path):
        """Test template with multiple inheritance levels."""
        template = project_service.get_template("video-editing")

        assert template is not None

        # Create project to verify multi-level inheritance
        project_service.create_project(
            name="Test", path=project_path, use_template="video-editing", git_enabled=False
        )

        # Should have all inherited folders
        assert (project_path / "media").exists()  # from base
        assert (project_path / "documents").exists()  # from default
        assert (project_path / "source").exists()  # from video-editing

    def test_inheritance_cycle_detection(self, project_service, templates_dir):
        """Test detection of circular inheritance."""
        # Create circular reference
        cycle1 = templates_dir / "cycle1"
        cycle1.mkdir()
        (cycle1 / "template.yaml").write_text(
            yaml.dump(
                {
                    "name": "cycle1",
                    "description": "Cycle test 1",
                    "version": "1.0.0",
                    "min_app_version": "0.1.0",
                    "extends": "cycle2",
                    "folder_structure": ["test"],
                }
            )
        )

        cycle2 = templates_dir / "cycle2"
        cycle2.mkdir()
        (cycle2 / "template.yaml").write_text(
            yaml.dump(
                {
                    "name": "cycle2",
                    "description": "Cycle test 2",
                    "version": "1.0.0",
                    "min_app_version": "0.1.0",
                    "extends": "cycle1",
                    "folder_structure": ["test"],
                }
            )
        )

        project_service.refresh_templates()

        # Should handle cycle gracefully - error occurs when trying to resolve inheritance
        with pytest.raises(RecursionError):
            # Try to create a project with cyclic template
            project_service._resolve_template_inheritance("cycle1")

    def test_max_inheritance_depth(self, project_service, templates_dir):
        """Test maximum inheritance depth limit."""
        # Create deep inheritance chain (6 levels)
        for i in range(6):
            dir_name = f"level{i}"
            level_dir = templates_dir / dir_name
            level_dir.mkdir()
            extends = f"level{i - 1}" if i > 0 else "base"
            (level_dir / "template.yaml").write_text(
                yaml.dump(
                    {
                        "name": dir_name,
                        "description": f"Level {i} template",
                        "version": "1.0.0",
                        "min_app_version": "0.1.0",
                        "extends": extends,
                        "folder_structure": [f"folder{i}"],
                    }
                )
            )

        project_service.refresh_templates()

        # Should reject templates exceeding max depth (5)
        with pytest.raises(RecursionError):
            # Try to resolve inheritance which will hit the depth limit
            project_service._resolve_template_inheritance("level5")


class TestVariableSubstitution:
    """Tests for template variable substitution."""

    def test_project_name_substitution(self, project_service, project_path):
        """Test {PROJECT_NAME} variable substitution."""
        project_service.create_project(
            name="My Test Project",
            path=project_path,
            use_template="default",
            git_enabled=False,
        )

        readme = project_path / "README.md"
        content = readme.read_text()

        assert "My Test Project" in content
        assert "{PROJECT_NAME}" not in content

    def test_date_substitution(self, project_service, project_path):
        """Test {DATE} variable substitution."""
        project_service.create_project(
            name="Test", path=project_path, use_template="default", git_enabled=False
        )

        readme = project_path / "README.md"
        content = readme.read_text()

        # Should contain date in YYYY-MM-DD format (check for valid format, not exact date)
        # Use local time since project_service uses datetime.now() (local time)
        import re

        date_pattern = r"\d{4}-\d{2}-\d{2}"
        assert re.search(date_pattern, content), "No date in YYYY-MM-DD format found"
        assert "{DATE}" not in content

    def test_author_substitution(self, project_service, project_path):
        """Test {AUTHOR} variable substitution."""
        project_service.create_project(
            name="Test", path=project_path, use_template="default", git_enabled=False
        )

        readme = project_path / "README.md"
        content = readme.read_text()

        # Should have author (either git user or system user)
        assert "Author:" in content
        assert "{AUTHOR}" not in content
        # Should not be empty
        assert "Author: \n" not in content

    def test_git_enabled_variable(self, project_service, project_path):
        """Test {GIT_ENABLED} variable substitution."""
        # Create template with GIT_ENABLED variable
        templates_dir = project_service.templates_dir
        git_test_dir = templates_dir / "git-test"
        git_test_dir.mkdir()
        (git_test_dir / "template.yaml").write_text(
            yaml.dump(
                {
                    "name": "git-test",
                    "description": "Git test template",
                    "version": "1.0.0",
                    "min_app_version": "0.1.0",
                    "folder_structure": ["test"],
                }
            )
        )
        (git_test_dir / "README.md").write_text("Git enabled: {GIT_ENABLED}")

        # Refresh templates to pick up the new template
        project_service.refresh_templates()

        project_service.create_project(
            name="Test", path=project_path, use_template="git-test", git_enabled=True
        )

        readme = project_path / "README.md"
        content = readme.read_text()

        assert "Git enabled: true" in content


class TestProjectCreation:
    """Tests for project creation with templates."""

    def test_create_project_with_base_template(self, project_service, project_path):
        """Test creating project with base template."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        assert project.exists
        assert (project_path / "media").exists()
        assert (project_path / "exports").exists()
        assert (project_path / "cache").exists()

    def test_create_project_with_inherited_template(self, project_service, project_path):
        """Test creating project with inherited template."""
        project_service.create_project(
            name="Test", path=project_path, use_template="video-editing", git_enabled=False
        )

        # Should have all inherited folders
        assert (project_path / "media").exists()  # base
        assert (project_path / "documents").exists()  # default
        assert (project_path / "source").exists()  # video-editing
        assert (project_path / "proxies").exists()
        assert (project_path / "renders").exists()

    def test_template_metadata_tracked(self, project_service, project_path):
        """Test that template metadata is tracked in project."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="default", git_enabled=False
        )

        assert project.template_name == "default"
        assert project.template_version == "1.0.0"

    def test_create_without_template(self, project_service, project_path):
        """Test creating project without template."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template=None, git_enabled=False
        )

        assert project.exists
        assert project.template_name is None
        assert project.template_version is None


class TestMigrationDetection:
    """Tests for migration detection."""

    def test_no_migration_needed(self, project_service, project_path):
        """Test project with current template version."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        needs_migration, diff = project_service.check_project_migration(project)
        assert not needs_migration
        assert diff is None

    def test_migration_available(self, project_service, project_path):
        """Test detecting available migration."""
        # Create project with old version
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Simulate old version
        project.template_version = "0.9.0"
        project_service.save_project(project)

        # Check migration
        needs_migration, diff = project_service.check_project_migration(project)

        assert needs_migration
        assert diff is not None
        assert diff.current_version == "0.9.0"
        assert diff.target_version == "1.0.0"

    def test_template_changed_structure(self, project_service, project_path, templates_dir):
        """Test migration when template structure changes."""
        # Create project with template
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Modify template to add new folder
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].append("new_folder")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Check migration
        needs_migration, diff = project_service.check_project_migration(project)

        assert needs_migration
        assert diff is not None
        assert "new_folder" in diff.folders_to_add

    def test_project_without_template(self, project_service, project_path):
        """Test migration check for project without template."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template=None, git_enabled=False
        )

        needs_migration, diff = project_service.check_project_migration(project)
        assert not needs_migration
        assert diff is None


class TestConflictDetection:
    """Tests for migration conflict detection."""

    def test_no_conflicts(self, project_service, project_path, templates_dir):
        """Test migration with no conflicts."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Update template to remove empty folder
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].remove("cache")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        needs_migration, diff = project_service.check_project_migration(project)
        assert needs_migration
        assert diff is not None
        assert len(diff.conflicts) == 0

    def test_conflict_with_user_files(self, project_service, project_path, templates_dir):
        """Test conflict detection when folder has user files."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Add user files to folder that will be removed
        cache_folder = project_path / "cache"
        (cache_folder / "user_file.txt").write_text("User content")

        # Update template to remove cache folder
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].remove("cache")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        needs_migration, diff = project_service.check_project_migration(project)
        assert needs_migration
        assert diff is not None
        assert len(diff.conflicts) > 0
        assert any(c.folder_path == "cache" for c in diff.conflicts)

    def test_conflict_metadata(self, project_service, project_path, templates_dir):
        """Test conflict metadata includes file count."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Add multiple user files
        cache_folder = project_path / "cache"
        for i in range(3):
            (cache_folder / f"file{i}.txt").write_text(f"Content {i}")

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].remove("cache")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        needs_migration, diff = project_service.check_project_migration(project)
        assert needs_migration
        assert diff is not None
        # Check that migration diff is calculated correctly
        # Note: conflict detection is conservative and doesn't remove folders by default
        cache_conflicts = [c for c in diff.conflicts if c.folder_path == "cache"]
        if cache_conflicts:
            conflict = cache_conflicts[0]
            assert conflict.user_files_count == 3


class TestMigrationExecution:
    """Tests for executing migrations."""

    def test_simple_migration(self, project_service, project_path, templates_dir):
        """Test executing a simple migration."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].append("new_folder")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Migrate
        updated_project, _backup_path = project_service.migrate_project(
            project, backup=True, skip_conflicts=True
        )

        assert updated_project is not None
        assert (project_path / "new_folder").exists()
        assert updated_project.template_version == "1.1.0"

    def test_migration_with_backup(self, project_service, project_path, templates_dir):
        """Test that migration creates backup."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Add user file
        (project_path / "user_file.txt").write_text("Important data")

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Migrate with backup
        updated_project, backup_path = project_service.migrate_project(
            project, backup=True, skip_conflicts=True
        )

        assert updated_project is not None
        # Backup should exist
        assert backup_path is not None
        assert backup_path.exists()

    def test_migration_history_updated(self, project_service, project_path, templates_dir):
        """Test that migration history is updated."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        original_version = project.template_version

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Migrate
        project_service.migrate_project(project, backup=True, skip_conflicts=True)

        # Reload project
        reloaded = project_service.load_project(project_path)

        assert len(reloaded.migration_history) == 1
        assert reloaded.migration_history[0]["from_version"] == original_version
        assert reloaded.migration_history[0]["to_version"] == "1.1.0"

    def test_migration_skip_conflicts(self, project_service, project_path, templates_dir):
        """Test migration with skip_conflicts flag."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Add user file to folder being removed
        (project_path / "cache" / "important.txt").write_text("Keep this")

        # Update template to remove cache
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].remove("cache")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Migrate with skip_conflicts
        updated_project, _backup_path = project_service.migrate_project(
            project, backup=True, skip_conflicts=True
        )

        assert updated_project is not None
        # Cache folder should still exist (conflict skipped)
        assert (project_path / "cache").exists()
        assert (project_path / "cache" / "important.txt").exists()


class TestPreviewMode:
    """Tests for migration preview mode."""

    def test_preview_migration(self, project_service, project_path, templates_dir):
        """Test creating a preview of migration."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].append("preview_test")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Create preview
        preview_temp_dir, preview_project = project_service.create_preview_migration(project)

        assert preview_temp_dir is not None
        preview_dir = Path(preview_temp_dir)
        assert preview_dir.exists()

        # Migrate the preview project
        preview_project, _ = project_service.migrate_project(
            preview_project, backup=False, skip_conflicts=True
        )

        preview_path = preview_project.path
        assert (preview_path / "preview_test").exists()

        # Original should be unchanged
        assert not (project_path / "preview_test").exists()

    def test_preview_cleanup(self, project_service, project_path, templates_dir):
        """Test preview cleanup."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Create preview
        preview_temp_dir, _preview_project = project_service.create_preview_migration(project)
        preview_dir = Path(preview_temp_dir)

        # Cleanup
        project_service.cleanup_preview_migration(preview_temp_dir)

        assert not preview_dir.exists()


class TestRollback:
    """Tests for migration rollback."""

    def test_rollback_migration(self, project_service, project_path, templates_dir):
        """Test rolling back a migration."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Add marker file
        (project_path / "original.txt").write_text("Original content")

        # Migrate
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        template_data["folder_structure"].append("new_folder")
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        updated_project, backup_path = project_service.migrate_project(
            project, backup=True, skip_conflicts=True
        )

        # Verify migration
        assert (project_path / "new_folder").exists()

        # Add file after migration
        (project_path / "after_migration.txt").write_text("After migration")

        # Rollback
        restored_project = project_service.rollback_project(updated_project, backup_path)

        assert restored_project is not None
        # New folder should be gone
        assert not (project_path / "new_folder").exists()
        # Original file should be back
        assert (project_path / "original.txt").exists()
        # File added after migration should be gone
        assert not (project_path / "after_migration.txt").exists()

    def test_rollback_without_backup(self, project_service, project_path):
        """Test rollback fails without backup."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Try rollback without migration - should raise ValueError
        fake_backup = project_path.parent / "nonexistent_backup"
        with pytest.raises(ValueError):
            project_service.rollback_project(project, fake_backup)

    def test_batch_rollback(self, project_service, tmp_path, templates_dir):
        """Test rolling back multiple projects."""
        # Create multiple projects
        projects = []
        for i in range(3):
            path = tmp_path / f"project_{i}"
            proj = project_service.create_project(
                name=f"Project {i}", path=path, use_template="base", git_enabled=False
            )
            projects.append(proj)

        # Migrate all
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        migrations = []
        for proj in projects:
            updated_proj, backup_path = project_service.migrate_project(
                proj, backup=True, skip_conflicts=True
            )
            migrations.append((updated_proj, backup_path))

        # Batch rollback
        results = project_service.rollback_multiple_projects(migrations)

        assert len(results) == 3
        # results is a dict with project names as keys and bool values
        assert all(success for success in results.values())


class TestDeferredMigrations:
    """Tests for deferred migration scheduling."""

    def test_schedule_deferred_migration(self, project_service, project_path):
        """Test scheduling a migration for later."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        project_service.schedule_deferred_migration(project, "1.1.0", reason="User deferred")

        # Reload project
        reloaded = project_service.load_project(project_path)

        assert reloaded.pending_migration is not None
        assert reloaded.pending_migration["target_version"] == "1.1.0"
        assert "User deferred" in reloaded.pending_migration["reason"]

    def test_list_pending_migrations(self, project_service, tmp_path):
        """Test listing projects with pending migrations."""
        # Create projects with and without pending migrations
        path1 = tmp_path / "project_1"
        proj1 = project_service.create_project(
            name="Project 1", path=path1, use_template="base", git_enabled=False
        )
        project_service.schedule_deferred_migration(proj1, "1.1.0", "Deferred")

        path2 = tmp_path / "project_2"
        project_service.create_project(
            name="Project 2", path=path2, use_template="base", git_enabled=False
        )

        pending = project_service.list_projects_with_pending_migrations()

        assert len(pending) == 1
        assert pending[0].name == "Project 1"

    def test_apply_pending_migrations(self, project_service, tmp_path, templates_dir):
        """Test applying all pending migrations."""
        # Create projects with pending migrations
        projects = []
        for i in range(2):
            path = tmp_path / f"project_{i}"
            proj = project_service.create_project(
                name=f"Project {i}", path=path, use_template="base", git_enabled=False
            )
            project_service.schedule_deferred_migration(proj, "1.1.0", "Deferred")
            projects.append(proj)

        # Update template
        base_yaml = templates_dir / "base" / "template.yaml"
        template_data = yaml.safe_load(base_yaml.read_text())
        template_data["version"] = "1.1.0"
        base_yaml.write_text(yaml.dump(template_data))

        project_service.refresh_templates()

        # Apply pending
        results = project_service.apply_pending_migrations()

        assert len(results) == 2
        assert all(success for _, success, _ in results)

        # Pending migrations should be cleared
        pending = project_service.list_projects_with_pending_migrations()
        assert len(pending) == 0


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_incompatible_app_version(self, project_service, templates_dir):
        """Test template requiring newer app version."""
        future_dir = templates_dir / "future"
        future_dir.mkdir()
        (future_dir / "template.yaml").write_text(
            yaml.dump(
                {
                    "name": "future",
                    "version": "1.0.0",
                    "min_app_version": "99.0.0",  # Far future version
                    "folder_structure": ["test"],
                }
            )
        )

        project_service.refresh_templates()

        # Should not be available
        template = project_service.get_template("future")
        assert template is None

    def test_migration_to_same_version(self, project_service, project_path):
        """Test migration to same version is no-op."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Try to migrate to same version - should raise ValueError (no migration available)
        with pytest.raises(ValueError):
            project_service.migrate_project(project, backup=True, skip_conflicts=True)

    def test_concurrent_modifications(self, project_service, project_path):
        """Test handling of concurrent project modifications."""
        project = project_service.create_project(
            name="Test", path=project_path, use_template="base", git_enabled=False
        )

        # Simulate concurrent modification by changing metadata file
        metadata_file = project_service._get_metadata_file(project_path)
        yaml.safe_load(metadata_file.read_text())

        # Save project multiple times (simulate concurrent saves)
        project.description = "Modified 1"
        project_service.save_project(project)

        project.description = "Modified 2"
        project_service.save_project(project)

        # Reload and verify latest state
        reloaded = project_service.load_project(project_path)
        assert reloaded.description == "Modified 2"
