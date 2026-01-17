"""
Plugin manifest migrator for converting v1 to v2 schema.

Provides tools to migrate plugin manifests with dry-run preview and rollback capabilities.
"""

import difflib
from pathlib import Path
import shutil
import sys
from typing import Any

import yaml


class MigrationError(Exception):
    """Exception raised when migration fails."""


def detect_schema_version(manifest_data: dict[str, Any]) -> int:
    """Detect schema version of plugin manifest.

    Args:
        manifest_data: Parsed YAML manifest data

    Returns:
        Schema version (1 or 2)
    """
    if "schema_version" in manifest_data:
        return int(manifest_data["schema_version"])

    # v1 schema has 'source' and 'command' at root level
    if "source" in manifest_data and "command" in manifest_data:
        return 1

    return 1  # Default to v1


def convert_v1_to_v2(manifest_data: dict[str, Any]) -> dict[str, Any]:
    """Convert v1 manifest to v2 format.

    Args:
        manifest_data: v1 manifest data

    Returns:
        v2 manifest data
    """
    # Extract v1 fields
    name = manifest_data.get("name", "Unknown")
    version = manifest_data.get("version", "0.0.0")
    mandatory = manifest_data.get("mandatory", False)
    enabled = manifest_data.get("enabled", False)
    description = manifest_data.get("description", "")
    register_to_path = manifest_data.get("register_to_path", False)
    dependencies = manifest_data.get("dependencies", [])

    source = manifest_data.get("source", {})
    command = manifest_data.get("command", {})

    # Build platform config
    platform_config = {
        "source": source.get("type", "url"),
        "download_url": source.get("base_uri", ""),
        "checksum_sha256": source.get("checksum_sha256", ""),
        "file_size": source.get("file_size"),
        "command_path": command.get("path", ""),
        "command_executable": command.get("executable", ""),
    }

    # Determine system package name (heuristic based on plugin name)
    system_package_map = {
        "Git": "git",
        "FFmpeg": "ffmpeg",
        "ExifTool": "exiftool",
        "ImageMagick": "imagemagick",
        "MariaDB": "mariadb",
        "MKVToolNix": "mkvtoolnix",
        "DigiKam": None,  # No common system package
        "GitLFS": "git-lfs",
        "GitVersion": None,  # No common system package
    }

    system_package = system_package_map.get(name)
    if system_package:
        platform_config["system_package"] = system_package
        platform_config["version_constraint"] = f">={version.split('.')[0]}.0"

    # Create v2 manifest
    v2_manifest = {
        "schema_version": 2,
        "name": name,
        "version": version,
        "mandatory": mandatory,
        "enabled": enabled,
        "description": description,
        "prefer_system": True,  # Default to preferring system packages
        "register_to_path": register_to_path,
        "dependencies": dependencies,
        "platforms": {
            "windows": platform_config.copy(),
            "linux": platform_config.copy(),
            "macos": platform_config.copy(),
        },
    }

    # Platform-specific adjustments
    # Windows: Keep download URLs as-is
    # Linux: Usually has system packages available
    # macOS: May need Homebrew packages

    # For Linux, if system package exists, clear download_url to prefer system
    if system_package:
        v2_manifest["platforms"]["linux"]["download_url"] = ""
        v2_manifest["platforms"]["macos"]["download_url"] = ""

    return v2_manifest


def generate_diff(original: str, migrated: str, filename: str) -> str:
    """Generate unified diff between original and migrated content.

    Args:
        original: Original file content
        migrated: Migrated file content
        filename: Name of file for diff header

    Returns:
        Unified diff string
    """
    original_lines = original.splitlines(keepends=True)
    migrated_lines = migrated.splitlines(keepends=True)

    diff = difflib.unified_diff(
        original_lines,
        migrated_lines,
        fromfile=f"{filename} (v1)",
        tofile=f"{filename} (v2)",
        lineterm="",
    )

    return "".join(diff)


def migrate_manifest(
    yaml_path: Path, dry_run: bool = True, backup: bool = True
) -> tuple[bool, str]:
    """Migrate a plugin manifest from v1 to v2 schema.

    Args:
        yaml_path: Path to plugin.yaml file
        dry_run: If True, only show what would change (default: True)
        backup: If True, create .bak backup before migrating (default: True)

    Returns:
        Tuple of (success, message/diff)
    """
    if not yaml_path.exists():
        return (False, f"File not found: {yaml_path}")

    try:
        # Read original file
        original_content = yaml_path.read_text(encoding="utf-8")
        manifest_data = yaml.safe_load(original_content)

        # Detect version
        version = detect_schema_version(manifest_data)

        if version == 2:
            return (True, f"Already using schema v2: {yaml_path.name}")

        # Convert to v2
        v2_manifest = convert_v1_to_v2(manifest_data)

        # Generate new YAML with nice formatting
        migrated_content = yaml.dump(
            v2_manifest,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=120,
        )

        # Add header comment
        plugin_name = v2_manifest.get("name", "Unknown")
        migrated_content = f"# {plugin_name} Plugin Manifest (Schema v2)\n\n{migrated_content}"

        # Generate diff
        diff = generate_diff(original_content, migrated_content, yaml_path.name)

        if dry_run:
            return (True, diff)

        # Create backup
        if backup:
            backup_path = yaml_path.with_suffix(".yaml.bak")
            shutil.copy2(yaml_path, backup_path)

        # Write migrated file
        yaml_path.write_text(migrated_content, encoding="utf-8")

        return (True, f"Migrated successfully: {yaml_path.name}\n{diff}")

    except Exception as e:
        return (False, f"Migration failed for {yaml_path.name}: {e}")


def rollback_migration(yaml_path: Path) -> tuple[bool, str]:
    """Rollback a migration by restoring from .bak file.

    Args:
        yaml_path: Path to plugin.yaml file

    Returns:
        Tuple of (success, message)
    """
    backup_path = yaml_path.with_suffix(".yaml.bak")

    if not backup_path.exists():
        return (False, f"No backup found: {backup_path}")

    try:
        shutil.copy2(backup_path, yaml_path)
        backup_path.unlink()  # Remove backup after successful rollback
        return (True, f"Rolled back successfully: {yaml_path.name}")
    except Exception as e:
        return (False, f"Rollback failed for {yaml_path.name}: {e}")


def migrate_all_plugins(
    plugins_dir: Path, dry_run: bool = True, backup: bool = True
) -> dict[str, tuple[bool, str]]:
    """Migrate all plugin manifests in a directory.

    Args:
        plugins_dir: Path to plugins directory
        dry_run: If True, only show what would change
        backup: If True, create .bak backups

    Returns:
        Dictionary mapping plugin names to (success, message) tuples
    """
    results = {}

    if not plugins_dir.exists():
        return {"error": (False, f"Plugins directory not found: {plugins_dir}")}

    # Find all plugin.yaml files
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        yaml_path = plugin_dir / "plugin.yaml"
        if not yaml_path.exists():
            continue

        plugin_name = plugin_dir.name
        success, message = migrate_manifest(yaml_path, dry_run=dry_run, backup=backup)
        results[plugin_name] = (success, message)

    return results


def rollback_all_migrations(plugins_dir: Path) -> dict[str, tuple[bool, str]]:
    """Rollback all plugin migrations in a directory.

    Args:
        plugins_dir: Path to plugins directory

    Returns:
        Dictionary mapping plugin names to (success, message) tuples
    """
    results = {}

    if not plugins_dir.exists():
        return {"error": (False, f"Plugins directory not found: {plugins_dir}")}

    # Find all plugin.yaml.bak files
    for plugin_dir in plugins_dir.iterdir():
        if not plugin_dir.is_dir():
            continue

        yaml_path = plugin_dir / "plugin.yaml"
        backup_path = yaml_path.with_suffix(".yaml.bak")

        if not backup_path.exists():
            continue

        plugin_name = plugin_dir.name
        success, message = rollback_migration(yaml_path)
        results[plugin_name] = (success, message)

    return results


def main() -> None:
    """CLI entry point for plugin migrator."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate plugin manifests to v2 schema")
    parser.add_argument(
        "command", choices=["migrate", "rollback", "dry-run"], help="Command to execute"
    )
    parser.add_argument(
        "--plugins-dir",
        type=Path,
        default=Path("plugins"),
        help="Path to plugins directory (default: plugins)",
    )
    parser.add_argument(
        "--plugin",
        type=str,
        help="Migrate specific plugin only",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup files",
    )

    args = parser.parse_args()

    plugins_dir = args.plugins_dir.resolve()

    if args.command == "rollback":
        print("Rolling back migrations...\n")  # noqa: T201
        if args.plugin:
            yaml_path = plugins_dir / args.plugin / "plugin.yaml"
            success, message = rollback_migration(yaml_path)
            print(message)  # noqa: T201
            sys.exit(0 if success else 1)
        else:
            results = rollback_all_migrations(plugins_dir)
    else:
        dry_run = args.command == "dry-run"
        backup = not args.no_backup

        if dry_run:
            print("DRY RUN: Showing what would change (no files modified)\n")  # noqa: T201
            print("=" * 80 + "\n")  # noqa: T201

        if args.plugin:
            yaml_path = plugins_dir / args.plugin / "plugin.yaml"
            success, message = migrate_manifest(yaml_path, dry_run=dry_run, backup=backup)
            print(message)  # noqa: T201
            sys.exit(0 if success else 1)
        else:
            results = migrate_all_plugins(plugins_dir, dry_run=dry_run, backup=backup)

    # Print results
    for plugin_name, (success, message) in results.items():
        status = "✓" if success else "✗"
        print(f"{status} {plugin_name}")  # noqa: T201
        if message:
            print(f"  {message}\n")  # noqa: T201

    # Exit with error if any migration failed
    all_success = all(success for success, _ in results.values())
    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
