"""
Test suite for plugin catalog automation (Phase 1).

Tests cover:
- Plugin YAML validation
- Schema compliance
- Category field presence
- Auto-generated markers
- Catalog generation
"""

from pathlib import Path
from typing import Any

import pytest
import yaml

# Adjust import path based on project structure
from app.plugins.plugin_schema import PluginManifestSchema

# Constants
PLUGINS_DIR = Path(__file__).parent.parent.parent / "plugins"
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"
PLUGIN_CATALOG_PATH = DOCS_DIR / "plugin-catalog.md"

# Expected categories
VALID_CATEGORIES = {
    "Version Control",
    "Media Processing",
    "Image Processing",
    "Database",
    "Development Tools",
    "Other",
}


def discover_plugins() -> list[Path]:
    """Discover all plugin.yaml files."""
    return list(PLUGINS_DIR.glob("*/plugin.yaml"))


def load_plugin_yaml(path: Path) -> dict[str, Any]:
    """Load and parse plugin YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.docs
class TestPluginYAMLValidity:
    """Test that all plugin YAML files are valid."""

    def test_all_plugins_have_valid_yaml(self):
        """All plugin directories must contain valid YAML."""
        plugins = discover_plugins()
        assert len(plugins) > 0, "No plugins found in plugins/ directory"

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            assert isinstance(data, dict), f"{plugin_path} is not a valid YAML dict"
            assert "name" in data, f"{plugin_path} missing 'name' field"
            assert "version" in data, f"{plugin_path} missing 'version' field"


@pytest.mark.docs
class TestPluginSchema:
    """Test Pydantic schema validation for all plugins."""

    def test_plugin_schema_validation(self):
        """All plugins must validate against PluginManifestSchema."""
        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            try:
                PluginManifestSchema(**data)
            except Exception as e:
                pytest.fail(f"{plugin_path} failed schema validation: {e}")

    def test_category_field_present(self):
        """All plugins must have a 'category' field (Phase 1 requirement)."""
        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            assert "category" in data, (
                f"{plugin_path} missing 'category' field. "
                "This is required for Phase 1 plugin categorization."
            )
            category = data["category"]
            assert category in VALID_CATEGORIES, (
                f"{plugin_path} has invalid category '{category}'. "
                f"Valid categories: {VALID_CATEGORIES}"
            )

    def test_schema_version(self):
        """All plugins should use schema_version 2."""
        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            if "schema_version" in data:
                assert data["schema_version"] == 2, f"{plugin_path} should use schema_version 2"


@pytest.mark.docs
class TestPluginCatalog:
    """Test plugin catalog markdown file."""

    def test_auto_generated_markers_exist(self):
        """plugin-catalog.md must contain AUTO-GENERATED markers."""
        content = PLUGIN_CATALOG_PATH.read_text(encoding="utf-8")

        assert "<!-- AUTO-GENERATED:PLUGIN_CATALOG:START -->" in content, (
            "Missing start marker for auto-generated content"
        )
        assert "<!-- AUTO-GENERATED:PLUGIN_CATALOG:END -->" in content, (
            "Missing end marker for auto-generated content"
        )

    def test_sphinx_label_exists(self):
        """plugin-catalog.md must have Sphinx reference label."""
        content = PLUGIN_CATALOG_PATH.read_text(encoding="utf-8")
        lines = content.splitlines()

        assert len(lines) > 0, "plugin-catalog.md is empty"
        assert lines[0].strip() == ".. _plugin-catalog:", (
            "First line must be Sphinx reference label '.. _plugin-catalog:'"
        )

    def test_no_manual_plugin_entries(self):
        """plugin-catalog.md should not contain manual plugin entries after cleanup."""
        content = PLUGIN_CATALOG_PATH.read_text(encoding="utf-8")

        # These patterns indicate manual plugin entries that should be removed
        forbidden_patterns = [
            "#### Git\n",
            "#### FFmpeg\n",
            "#### ExifTool\n",
            "**Plugin File:** [plugins/",
        ]

        for pattern in forbidden_patterns:
            assert pattern not in content, (
                f"Found forbidden pattern '{pattern}' - manual plugin entries should be removed"
            )


@pytest.mark.docs
class TestPluginCatalogGeneration:
    """Test the update_plugin_catalog.py script functionality."""

    def test_plugin_catalog_generation(self):
        """Test that plugin catalog can be generated successfully."""
        import subprocess
        import sys

        script_path = Path(__file__).parent.parent.parent / "scripts" / "update_plugin_catalog.py"
        result = subprocess.run(  # noqa: S603
            [sys.executable, str(script_path), "--dry-run"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )

        assert result.returncode == 0, f"Plugin catalog generation failed:\n{result.stderr}"
        assert (
            "SUCCESS" in result.stdout
            or "plugins found" in result.stdout
            or "Total Plugins:" in result.stdout
        ), "Script did not report success"

    def test_catalog_contains_all_plugins(self):
        """After generation, catalog should contain entries for all plugins."""
        # This test assumes the catalog has been generated
        # In CI, we'll run update_plugin_catalog.py before this test

        content = PLUGIN_CATALOG_PATH.read_text(encoding="utf-8")
        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            plugin_name = data["name"]

            # Check if plugin name appears in catalog
            # (case-insensitive search)
            assert plugin_name.lower() in content.lower(), (
                f"Plugin '{plugin_name}' not found in generated catalog"
            )

    def test_categories_not_empty(self):
        """Generated catalog should have plugins in each used category."""
        plugins = discover_plugins()
        categories_used = set()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            if "category" in data:
                categories_used.add(data["category"])

        content = PLUGIN_CATALOG_PATH.read_text(encoding="utf-8")

        for category in categories_used:
            # Check if category heading exists
            assert f"### {category}" in content or f"## {category}" in content, (
                f"Category '{category}' heading not found in catalog"
            )


@pytest.mark.docs
class TestPluginConsistency:
    """Test consistency across all plugins."""

    def test_unique_plugin_names(self):
        """All plugins must have unique names."""
        plugins = discover_plugins()
        names = []

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            names.append(data["name"])

        assert len(names) == len(set(names)), (
            f"Duplicate plugin names found: {[n for n in names if names.count(n) > 1]}"
        )

    def test_required_fields(self):
        """All plugins must have required fields."""
        required_fields = ["name", "version", "description", "category"]
        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            for field in required_fields:
                assert field in data, f"{plugin_path} missing required field '{field}'"

    def test_version_format(self):
        """Plugin versions should follow semantic versioning."""
        import re

        semver_pattern = re.compile(r"^\d+\.\d+\.\d+")

        plugins = discover_plugins()

        for plugin_path in plugins:
            data = load_plugin_yaml(plugin_path)
            version = data["version"]
            assert semver_pattern.match(version), (
                f"{plugin_path} has invalid version format '{version}'. "
                "Expected semantic versioning (e.g., 2.48.1)"
            )


# Pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "docs: marks tests as documentation-related (deselect with '-m \"not docs\"')"
    )
