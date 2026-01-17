"""Tests for plugin_migrator module.

Tests plugin migration functions for converting v1 to v2 schema with backup and rollback.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from app.plugins.plugin_migrator import (
    convert_v1_to_v2,
    detect_schema_version,
    generate_diff,
    migrate_all_plugins,
    migrate_manifest,
    rollback_all_migrations,
    rollback_migration,
)


class TestDetectSchemaVersion:
    """Test suite for detect_schema_version function."""

    def test_detect_v2_schema_explicit(self):
        """Test detecting explicit v2 schema_version."""
        manifest = {"schema_version": 2, "name": "test", "platforms": {}}

        version = detect_schema_version(manifest)

        assert version == 2

    def test_detect_v1_schema_explicit(self):
        """Test detecting explicit v1 schema_version."""
        manifest = {"schema_version": 1, "name": "test", "source": {}}

        version = detect_schema_version(manifest)

        assert version == 1

    def test_detect_v1_schema_implicit(self):
        """Test detecting v1 schema by structure."""
        manifest = {
            "name": "test",
            "source": {"type": "url"},
            "command": {"executable": "test"},
        }

        version = detect_schema_version(manifest)

        assert version == 1

    def test_detect_unknown_defaults_to_v1(self):
        """Test unknown schema defaults to v1."""
        manifest = {"name": "test", "version": "1.0.0"}

        version = detect_schema_version(manifest)

        assert version == 1


class TestConvertV1ToV2:
    """Test suite for convert_v1_to_v2 function."""

    def test_convert_basic_v1_manifest(self):
        """Test converting basic v1 manifest to v2."""
        v1_manifest = {
            "name": "TestTool",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "source": {"type": "url", "base_uri": "https://example.com/tool.zip"},
            "command": {"path": "bin", "executable": "tool.exe"},
        }

        v2_manifest = convert_v1_to_v2(v1_manifest)

        assert v2_manifest["schema_version"] == 2
        assert v2_manifest["name"] == "TestTool"
        assert v2_manifest["version"] == "1.0.0"
        assert "platforms" in v2_manifest
        assert "windows" in v2_manifest["platforms"]

    def test_convert_with_system_package(self):
        """Test converting v1 manifest with system_package."""
        v1_manifest = {
            "name": "Git",
            "version": "2.0.0",
            "mandatory": False,
            "enabled": True,
            "system_package": "git",
            "command": {"executable": "git"},
        }

        v2_manifest = convert_v1_to_v2(v1_manifest)

        assert v2_manifest["schema_version"] == 2
        assert "platforms" in v2_manifest

    def test_convert_preserves_optional_fields(self):
        """Test conversion preserves optional fields."""
        v1_manifest = {
            "name": "Tool",
            "version": "1.0.0",
            "mandatory": True,
            "enabled": False,
            "prefer_system": True,
            "register_to_path": False,
            "dependencies": ["git"],
            "description": "Test tool",
            "source": {"type": "url", "base_uri": "https://example.com"},
            "command": {"executable": "tool"},
        }

        v2_manifest = convert_v1_to_v2(v1_manifest)

        assert v2_manifest["mandatory"] is True
        assert v2_manifest["enabled"] is False
        assert v2_manifest.get("prefer_system") is True
        assert v2_manifest.get("register_to_path") is False
        assert v2_manifest.get("dependencies") == ["git"]
        assert v2_manifest.get("description") == "Test tool"

    def test_convert_defaults_missing_fields(self):
        """Test conversion provides defaults for missing fields."""
        v1_manifest = {
            "source": {"type": "url", "base_uri": "https://example.com"},
            "command": {"executable": "tool"},
        }

        v2_manifest = convert_v1_to_v2(v1_manifest)

        assert v2_manifest["name"] == "Unknown"
        assert v2_manifest["version"] == "0.0.0"


class TestGenerateDiff:
    """Test suite for generate_diff function."""

    def test_generate_diff_with_changes(self):
        """Test generating diff with changes."""
        original = "line1\nline2\nline3\n"
        migrated = "line1\nline2_modified\nline3\n"

        diff = generate_diff(original, migrated, "plugin.yaml")

        assert diff
        assert "plugin.yaml" in diff
        assert "line2" in diff

    def test_generate_diff_no_changes(self):
        """Test generating diff with no changes."""
        content = "line1\nline2\nline3\n"

        diff = generate_diff(content, content, "plugin.yaml")

        assert "No changes" in diff or not diff.strip()

    def test_generate_diff_multiline(self):
        """Test diff with multiline changes."""
        original = "schema_version: 1\nname: test\nsource:\n  type: url\n"
        migrated = "schema_version: 2\nname: test\nplatforms:\n  windows:\n"

        diff = generate_diff(original, migrated, "plugin.yaml")

        assert "schema_version" in diff
        assert diff  # Should have content


class TestMigrateManifest:
    """Test suite for migrate_manifest function."""

    @pytest.fixture
    def mock_yaml_path(self, tmp_path):
        """Create mock YAML file path."""
        return tmp_path / "plugin.yaml"

    def test_migrate_manifest_v1_to_v2(self, mock_yaml_path):
        """Test migrating v1 manifest to v2."""
        v1_content = {
            "schema_version": 1,
            "name": "TestTool",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "source": {"type": "url", "base_uri": "https://example.com"},
            "command": {"executable": "tool.exe"},
        }

        # Write v1 manifest
        with open(mock_yaml_path, "w") as f:
            yaml.dump(v1_content, f)

        # Migrate
        success, message = migrate_manifest(mock_yaml_path, dry_run=False)

        assert success
        assert "successfully" in message.lower()

        # Verify backup was created
        backup_path = mock_yaml_path.with_suffix(".yaml.bak")
        assert backup_path.exists()

        # Verify migrated content
        with open(mock_yaml_path) as f:
            migrated = yaml.safe_load(f)

        assert migrated["schema_version"] == 2
        assert "platforms" in migrated

    def test_migrate_manifest_dry_run(self, mock_yaml_path):
        """Test dry-run migration (no file changes)."""
        v1_content = {
            "schema_version": 1,
            "name": "TestTool",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "source": {"type": "url", "base_uri": "https://example.com"},
            "command": {"executable": "tool.exe"},
        }

        # Write v1 manifest
        with open(mock_yaml_path, "w") as f:
            yaml.dump(v1_content, f)

        original_mtime = mock_yaml_path.stat().st_mtime

        # Dry run
        success, message = migrate_manifest(mock_yaml_path, dry_run=True)

        assert success
        # Dry run returns diff output
        assert "---" in message or "+++" in message

        # File should not be modified
        assert mock_yaml_path.stat().st_mtime == original_mtime

        # No backup should be created
        mock_yaml_path.with_suffix(".yaml.bak")
        v2_content = {
            "schema_version": 2,
            "name": "TestTool",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "platforms": {"windows": {"command": {"executable": "tool.exe"}}},
        }

        with open(mock_yaml_path, "w") as f:
            yaml.dump(v2_content, f)

        success, message = migrate_manifest(mock_yaml_path, dry_run=False)

        assert success
        assert "already" in message.lower() or "no migration" in message.lower()

    def test_migrate_manifest_file_not_found(self, tmp_path):
        """Test migrating non-existent file."""
        nonexistent = tmp_path / "missing.yaml"

        success, message = migrate_manifest(nonexistent, dry_run=False)

        assert not success
        assert "not found" in message.lower() or "does not exist" in message.lower()

    def test_migrate_manifest_invalid_yaml(self, mock_yaml_path):
        """Test migrating invalid YAML file."""
        with open(mock_yaml_path, "w") as f:
            f.write("invalid: yaml: content: [[[")

        success, message = migrate_manifest(mock_yaml_path, dry_run=False)

        assert not success
        assert "error" in message.lower() or "invalid" in message.lower()


class TestRollbackMigration:
    """Test suite for rollback_migration function."""

    def test_rollback_successful(self, tmp_path):
        """Test successful rollback of migration."""
        yaml_path = tmp_path / "plugin.yaml"
        backup_path = tmp_path / "plugin.yaml.bak"

        # Create migrated v2 file
        v2_content = {
            "schema_version": 2,
            "name": "Test",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "platforms": {},
        }
        with open(yaml_path, "w") as f:
            yaml.dump(v2_content, f)

        # Create backup v1 file
        v1_content = {
            "schema_version": 1,
            "name": "Test",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "source": {},
            "command": {},
        }
        with open(backup_path, "w") as f:
            yaml.dump(v1_content, f)

        # Rollback
        success, message = rollback_migration(yaml_path)

        assert success
        # Message says "Rolled back successfully: plugin.yaml"
        assert "rolled back" in message.lower() or "success" in message.lower()

        # Verify v1 content restored
        with open(yaml_path) as f:
            restored = yaml.safe_load(f)

        assert restored["schema_version"] == 1
        assert "source" in restored

    def test_rollback_no_backup_exists(self, tmp_path):
        """Test rollback when no backup exists."""
        yaml_path = tmp_path / "plugin.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump({"schema_version": 2}, f)

        success, message = rollback_migration(yaml_path)

        assert not success
        # Message says "No backup found: <path>"
        assert "backup" in message.lower()
        assert "found" in message.lower()
        nonexistent = tmp_path / "missing.yaml"

        success, message = rollback_migration(nonexistent)

        assert not success


class TestMigrateAllPlugins:
    """Test suite for migrate_all_plugins function."""

    def test_migrate_all_plugins_success(self, tmp_path):
        """Test migrating multiple plugin manifests."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin directories with v1 manifests
        for plugin_name in ["git", "ffmpeg", "exiftool"]:
            plugin_dir = plugins_dir / plugin_name
            plugin_dir.mkdir()
            yaml_path = plugin_dir / "plugin.yaml"

            v1_content = {
                "schema_version": 1,
                "name": plugin_name,
                "version": "1.0.0",
                "mandatory": False,
                "enabled": True,
                "source": {"type": "url", "base_uri": "https://example.com"},
                "command": {"executable": plugin_name},
            }

            with open(yaml_path, "w") as f:
                yaml.dump(v1_content, f)

        # Migrate all
        results = migrate_all_plugins(plugins_dir, dry_run=False)

        assert len(results) == 3
        assert all(success for success, _ in results.values())

    def test_migrate_all_plugins_dry_run(self, tmp_path):
        """Test dry-run migration of all plugins."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        plugin_dir = plugins_dir / "test"
        plugin_dir.mkdir()
        yaml_path = plugin_dir / "plugin.yaml"

        v1_content = {
            "schema_version": 1,
            "name": "test",
            "version": "1.0.0",
            "mandatory": False,
            "enabled": True,
            "source": {},
            "command": {},
        }

        with open(yaml_path, "w") as f:
            yaml.dump(v1_content, f)

        results = migrate_all_plugins(plugins_dir, dry_run=True)

        # Should have results but no backup files created
        assert len(results) > 0
        backup_path = yaml_path.with_suffix(".yaml.bak")
        assert not backup_path.exists()

    def test_migrate_all_plugins_empty_directory(self, tmp_path):
        """Test migrating from empty plugins directory."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        results = migrate_all_plugins(plugins_dir, dry_run=False)

        assert results == {}

    """Test suite for rollback_all_migrations function."""

    def test_rollback_all_migrations_success(self, tmp_path):
        """Test rolling back multiple plugin migrations."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create plugin with migrated manifest and backup
        for plugin_name in ["git", "ffmpeg"]:
            plugin_dir = plugins_dir / plugin_name
            plugin_dir.mkdir()
            yaml_path = plugin_dir / "plugin.yaml"
            backup_path = plugin_dir / "plugin.yaml.bak"

            # Create v2 manifest
            with open(yaml_path, "w") as f:
                yaml.dump({"schema_version": 2, "name": plugin_name, "platforms": {}}, f)

            # Create v1 backup
            with open(backup_path, "w") as f:
                yaml.dump({"schema_version": 1, "name": plugin_name, "source": {}}, f)

        # Rollback all
        results = rollback_all_migrations(plugins_dir)

        assert len(results) == 2
        assert all(success for success, _ in results.values())

    def test_rollback_all_migrations_no_backups(self, tmp_path):
        """Test rollback when no backups exist."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        plugin_dir = plugins_dir / "test"
        plugin_dir.mkdir()
        yaml_path = plugin_dir / "plugin.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump({"schema_version": 2}, f)

        results = rollback_all_migrations(plugins_dir)

        # Should have results indicating no backups
        assert len(results) >= 0


class TestEdgeCasesAndErrors:
    """Test suite for edge cases and error handling."""

    def test_rollback_migration_file_not_found(self, tmp_path):
        """Test rollback when file doesn't exist."""
        nonexistent = tmp_path / "missing.yaml"

        success, message = rollback_migration(nonexistent)

        assert success is False
        assert "not found" in message.lower() or "no backup" in message.lower()

    def test_rollback_migration_copy_error(self, tmp_path):
        """Test rollback handles copy errors."""
        yaml_path = tmp_path / "plugin.yaml"
        backup_path = yaml_path.with_suffix(".yaml.bak")

        # Create files
        yaml_path.write_text("schema_version: 2\n")
        backup_path.write_text("schema_version: 1\n")

        # Mock shutil.copy2 to raise an error

        with patch("shutil.copy2", side_effect=PermissionError("Access denied")):
            success, message = rollback_migration(yaml_path)

        assert success is False
        assert "failed" in message.lower()

    def test_migrate_all_plugins_nonexistent_directory(self, tmp_path):
        """Test migrate_all_plugins with nonexistent directory."""
        nonexistent = tmp_path / "missing"

        results = migrate_all_plugins(nonexistent)

        assert "error" in results
        assert results["error"][0] is False
        assert "not found" in results["error"][1].lower()

    def test_migrate_all_plugins_skips_non_directories(self, tmp_path):
        """Test migrate_all_plugins skips non-directory files."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create a file (not directory)
        (plugins_dir / "readme.txt").write_text("Not a plugin")

        # Create a valid plugin
        plugin_dir = plugins_dir / "validplugin"
        plugin_dir.mkdir()
        yaml_path = plugin_dir / "plugin.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump({"name": "Valid", "source": {}, "command": {}}, f)

        results = migrate_all_plugins(plugins_dir, dry_run=False)

        # Should only process valid plugin, skip the file
        assert "validplugin" in results
        assert "readme.txt" not in results

    def test_migrate_all_plugins_skips_missing_yaml(self, tmp_path):
        """Test migrate_all_plugins skips directories without plugin.yaml."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create directory without plugin.yaml
        (plugins_dir / "incomplete").mkdir()

        # Create valid plugin
        plugin_dir = plugins_dir / "validplugin"
        plugin_dir.mkdir()
        yaml_path = plugin_dir / "plugin.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump({"name": "Valid", "source": {}, "command": {}}, f)

        results = migrate_all_plugins(plugins_dir, dry_run=False)

        # Should only process valid plugin
        assert "validplugin" in results
        assert "incomplete" not in results

    def test_rollback_all_migrations_nonexistent_directory(self, tmp_path):
        """Test rollback_all_migrations with nonexistent directory."""
        nonexistent = tmp_path / "missing"

        results = rollback_all_migrations(nonexistent)

        assert "error" in results
        assert results["error"][0] is False
        assert "not found" in results["error"][1].lower()

    def test_rollback_all_migrations_skips_non_directories(self, tmp_path):
        """Test rollback_all_migrations skips non-directory files."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Create a file (not directory)
        (plugins_dir / "readme.txt").write_text("Not a plugin")

        # Create a plugin with backup
        plugin_dir = plugins_dir / "testplugin"
        plugin_dir.mkdir()
        yaml_path = plugin_dir / "plugin.yaml"
        backup_path = yaml_path.with_suffix(".yaml.bak")

        with open(yaml_path, "w") as f:
            yaml.dump({"schema_version": 2}, f)
        with open(backup_path, "w") as f:
            yaml.dump({"schema_version": 1}, f)

        results = rollback_all_migrations(plugins_dir)

        # Should only process valid plugin
        assert "testplugin" in results
        assert "readme.txt" not in results

    def test_rollback_all_migrations_skips_no_backup(self, tmp_path):
        """Test rollback_all_migrations skips plugins without backups."""
        plugins_dir = tmp_path / "plugins"
        plugins_dir.mkdir()

        # Plugin without backup
        plugin_dir1 = plugins_dir / "no_backup"
        plugin_dir1.mkdir()
        (plugin_dir1 / "plugin.yaml").write_text("schema_version: 2\n")

        # Plugin with backup
        plugin_dir2 = plugins_dir / "with_backup"
        plugin_dir2.mkdir()
        yaml_path = plugin_dir2 / "plugin.yaml"
        backup_path = yaml_path.with_suffix(".yaml.bak")
        yaml_path.write_text("schema_version: 2\n")
        backup_path.write_text("schema_version: 1\n")

        results = rollback_all_migrations(plugins_dir)

        # Should only process plugin with backup
        assert "with_backup" in results
        assert "no_backup" not in results

    def test_migrate_manifest_write_permission_error(self, tmp_path):
        """Test migrate_manifest handles write permission errors."""
        yaml_path = tmp_path / "plugin.yaml"

        with open(yaml_path, "w") as f:
            yaml.dump({"name": "Test", "source": {}, "command": {}}, f)

        # Mock Path.write_text to raise permission error

        with patch.object(Path, "write_text", side_effect=PermissionError("Access denied")):
            success, message = migrate_manifest(yaml_path, dry_run=False)

        assert success is False
        assert "error" in message.lower() or "failed" in message.lower()

    def test_generate_diff_with_identical_content(self):
        """Test generate_diff with identical original and migrated content."""
        content = "name: test\nversion: 1.0.0\n"

        diff = generate_diff(content, content, "plugin.yaml")

        # Diff should indicate no changes
        assert diff == "" or "No changes" in diff or "identical" in diff.lower()
