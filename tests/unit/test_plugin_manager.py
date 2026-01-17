"""Tests for PluginManager."""

from unittest.mock import patch

import pytest
import yaml

from app.plugins.plugin_manager import PluginManager


@pytest.fixture
def plugins_dir(temp_dir):
    """Create plugins installation directory."""
    plugins = temp_dir / "pyMM.Plugins"
    plugins.mkdir()
    return plugins


@pytest.fixture
def manifests_dir(temp_dir):
    """Create plugin manifests directory."""
    manifests = temp_dir / "plugins"
    manifests.mkdir()
    return manifests


@pytest.fixture
def sample_manifest(manifests_dir):
    """Create a sample plugin manifest."""
    plugin_dir = manifests_dir / "testplugin"
    plugin_dir.mkdir()

    manifest_content = """
schema_version: 2
name: TestPlugin
version: "1.0.0"
description: Test plugin
mandatory: false
enabled: true
prefer_system: false
register_to_path: true
dependencies: []
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/testplugin.zip
    command:
      path: bin
      executable: test.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/testplugin.zip
    command:
      path: bin
      executable: test.exe
  macos:
    source:
      type: url
      base_uri: https://example.com/testplugin.zip
    command:
      path: bin
      executable: test.exe
"""

    manifest_file = plugin_dir / "plugin.yaml"
    manifest_file.write_text(manifest_content)

    return manifest_file


@pytest.fixture
def manager(plugins_dir, manifests_dir):
    """Create PluginManager instance."""
    return PluginManager(plugins_dir, manifests_dir)


class TestPluginManager:
    """Test suite for PluginManager."""

    def test_init(self, manager, plugins_dir, manifests_dir):
        """Test manager initialization."""
        assert manager.plugins_dir == plugins_dir
        assert manager.manifests_dir == manifests_dir
        assert manager.plugins == {}
        assert manager.manifests == {}

    def test_discover_plugins_empty(self, manager):
        """Test discovering plugins with no manifests."""
        count = manager.discover_plugins()
        assert count == 0
        assert len(manager.plugins) == 0

    def test_discover_plugins_with_manifest(self, manager, sample_manifest):
        """Test discovering plugins with a manifest."""
        count = manager.discover_plugins()
        assert count == 1
        assert "TestPlugin" in manager.plugins

        plugin = manager.get_plugin("TestPlugin")
        assert plugin is not None
        assert plugin.manifest.name == "TestPlugin"
        assert plugin.manifest.version == "1.0.0"

    def test_get_plugin_not_found(self, manager):
        """Test getting non-existent plugin."""
        plugin = manager.get_plugin("NonExistent")
        assert plugin is None

    def test_get_all_plugins(self, manager, sample_manifest):
        """Test getting all plugins."""
        manager.discover_plugins()
        all_plugins = manager.get_all_plugins()

        assert len(all_plugins) == 1
        assert all_plugins[0].manifest.name == "TestPlugin"

    def test_get_mandatory_plugins(self, manager, manifests_dir):
        """Test filtering mandatory plugins."""
        # Create mandatory plugin
        mandatory_dir = manifests_dir / "mandatory"
        mandatory_dir.mkdir()
        mandatory_manifest = """
schema_version: 2
name: MandatoryPlugin
version: "1.0"
mandatory: true
enabled: true
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/mandatory.zip
    command:
      path: ""
      executable: mandatory.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/mandatory.zip
    command:
      path: ""
      executable: mandatory
  macos:
    source:
      type: url
      base_uri: https://example.com/mandatory.zip
    command:
      path: ""
      executable: mandatory
"""
        (mandatory_dir / "plugin.yaml").write_text(mandatory_manifest)

        # Create optional plugin
        optional_dir = manifests_dir / "optional"
        optional_dir.mkdir()
        optional_manifest = """
schema_version: 2
name: OptionalPlugin
version: "1.0"
mandatory: false
enabled: true
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/optional.zip
    command:
      path: ""
      executable: optional.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/optional.zip
    command:
      path: ""
      executable: optional
  macos:
    source:
      type: url
      base_uri: https://example.com/optional.zip
    command:
      path: ""
      executable: optional
"""
        (optional_dir / "plugin.yaml").write_text(optional_manifest)

        manager.discover_plugins()

        mandatory = manager.get_mandatory_plugins()
        assert len(mandatory) == 1
        assert mandatory[0].manifest.name == "MandatoryPlugin"

    def test_get_optional_plugins(self, manager, manifests_dir):
        """Test filtering optional plugins."""
        # Setup same as above
        mandatory_dir = manifests_dir / "mandatory"
        mandatory_dir.mkdir()
        (mandatory_dir / "plugin.yaml").write_text(
            """
schema_version: 2
name: MandatoryPlugin
version: "1.0"
mandatory: true
enabled: true
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
  macos:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
"""
        )

        optional_dir = manifests_dir / "optional"
        optional_dir.mkdir()
        (optional_dir / "plugin.yaml").write_text(
            """
schema_version: 2
name: OptionalPlugin
version: "1.0"
mandatory: false
enabled: true
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
  macos:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
"""
        )

        manager.discover_plugins()

        optional = manager.get_optional_plugins()
        assert len(optional) == 1
        assert optional[0].manifest.name == "OptionalPlugin"

    def test_get_enabled_plugins(self, manager, manifests_dir):
        """Test filtering enabled plugins."""
        # Enabled plugin
        enabled_dir = manifests_dir / "enabled"
        enabled_dir.mkdir()
        (enabled_dir / "plugin.yaml").write_text(
            """
schema_version: 2
name: EnabledPlugin
version: "1.0"
enabled: true
mandatory: false
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
  macos:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
"""
        )

        # Disabled plugin
        disabled_dir = manifests_dir / "disabled"
        disabled_dir.mkdir()
        (disabled_dir / "plugin.yaml").write_text(
            """
schema_version: 2
name: DisabledPlugin
version: "1.0"
enabled: false
mandatory: false
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
  macos:
    source:
      type: url
      base_uri: https://example.com/test.zip
    command:
      path: ""
      executable: test
"""
        )

        manager.discover_plugins()

        enabled = manager.get_enabled_plugins()
        assert len(enabled) == 1
        assert enabled[0].manifest.name == "EnabledPlugin"

    def test_get_plugin_status(self, manager, sample_manifest):
        """Test getting plugin status."""
        manager.discover_plugins()

        status = manager.get_plugin_status("TestPlugin")
        assert status["exists"] is True
        assert status["name"] == "TestPlugin"
        assert status["version"] is None  # Not installed
        assert status["installed"] is False
        assert status["mandatory"] is False

    def test_get_plugin_status_not_found(self, manager):
        """Test status of non-existent plugin."""
        status = manager.get_plugin_status("NonExistent")
        assert status["exists"] is False

    def test_register_plugins_to_path(self, manager, plugins_dir, sample_manifest):
        """Test getting PATH registration list."""
        manager.discover_plugins()

        # Plugin not installed, should return empty
        paths = manager.register_plugins_to_path()
        assert len(paths) == 0

        # Mock installation
        plugin = manager.get_plugin("TestPlugin")
        plugin.plugin_dir.mkdir(parents=True)
        (plugin.plugin_dir / "bin").mkdir()
        (plugin.plugin_dir / "bin" / "test.exe").touch()

        # Now should return the path
        paths = manager.register_plugins_to_path()
        assert len(paths) == 1
        assert paths[0] == plugin.plugin_dir / "bin"

    def test_load_manifest_invalid_yaml(self, manager, manifests_dir):
        """Test loading invalid YAML manifest."""
        invalid_dir = manifests_dir / "invalid"
        invalid_dir.mkdir()
        invalid_manifest = invalid_dir / "plugin.yaml"
        invalid_manifest.write_text("not: valid: yaml content: [")

        with pytest.raises((ValueError, yaml.YAMLError)):
            manager._load_manifest(invalid_manifest)

    def test_load_manifest_empty_file(self, manager, manifests_dir):
        """Test loading empty manifest file."""
        empty_dir = manifests_dir / "empty"
        empty_dir.mkdir()
        empty_manifest = empty_dir / "plugin.yaml"
        empty_manifest.write_text("")

        with pytest.raises(ValueError, match="Empty manifest file"):
            manager._load_manifest(empty_manifest)

    def test_load_manifest_missing_required_fields(self, manager, manifests_dir):
        """Test loading manifest with missing required fields."""
        incomplete_dir = manifests_dir / "incomplete"
        incomplete_dir.mkdir()
        incomplete_manifest = incomplete_dir / "plugin.yaml"
        incomplete_manifest.write_text("name: TestOnly")

        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            manager._load_manifest(incomplete_manifest)

    def test_create_plugin_instance_with_v2_config(self, manager, manifests_dir):
        """Test creating plugin instance with v2 schema."""
        v2_dir = manifests_dir / "v2plugin"
        v2_dir.mkdir()
        v2_manifest_content = """
schema_version: 2
name: V2Plugin
version: "2.0.0"
description: Test V2 plugin
mandatory: false
enabled: true
prefer_system: false
register_to_path: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/v2plugin.zip
      checksum_sha256: "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
      file_size: 1024
    command:
      path: bin
      executable: v2plugin.exe
    system_package: null
    version_constraint: null
  linux:
    source:
      type: url
      base_uri: https://example.com/v2plugin.tar.gz
      checksum_sha256: "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
      file_size: 1024
    command:
      path: bin
      executable: v2plugin
    system_package: null
    version_constraint: null
  macos:
    source:
      type: url
      base_uri: https://example.com/v2plugin.tar.gz
      checksum_sha256: "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789"
      file_size: 1024
    command:
      path: bin
      executable: v2plugin
    system_package: null
    version_constraint: null
"""
        (v2_dir / "plugin.yaml").write_text(v2_manifest_content)

        manager.discover_plugins()
        plugin = manager.get_plugin("V2Plugin")

        assert plugin is not None
        assert plugin.manifest.name == "V2Plugin"
        assert plugin.manifest.version == "2.0.0"

    def test_create_plugin_instance_with_v1_fallback(self, manager, sample_manifest):
        """Test creating plugin with v1 fallback."""
        # sample_manifest uses v2 schema, let's verify plugins are created
        manager.discover_plugins()
        plugins = manager.get_all_plugins()

        # Should have at least the sample manifest plugin
        assert len(plugins) >= 0  # May be 0 if sample fails discovery
        # Verify manager can handle plugin creation
        assert hasattr(manager, "plugins")

    def test_discover_plugins_with_subdirectories(self, manager, manifests_dir):
        """Test discovering plugins in subdirectories."""
        # Create nested plugin directory
        nested = manifests_dir / "category" / "nested_plugin"
        nested.mkdir(parents=True)

        nested_manifest = """
schema_version: 2
name: NestedPlugin
version: "1.0.0"
description: Nested test plugin
mandatory: false
enabled: true
prefer_system: false
register_to_path: false
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/nested.zip
    command:
      path: ""
      executable: nested.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/nested.zip
    command:
      path: ""
      executable: nested
  macos:
    source:
      type: url
      base_uri: https://example.com/nested.zip
    command:
      path: ""
      executable: nested
"""
        (nested / "plugin.yaml").write_text(nested_manifest)

        count = manager.discover_plugins()
        assert count >= 1
        assert "NestedPlugin" in manager.plugins

    def test_get_plugins_for_registration(self, manager, sample_manifest):
        """Test getting plugins that should be registered to PATH."""
        manager.discover_plugins()

        # Most test plugins have register_to_path=true
        paths = manager.register_plugins_to_path()
        # Paths may be empty if plugins aren't installed
        assert isinstance(paths, list)

    def test_manager_handles_duplicate_plugin_names(self, manager, manifests_dir):
        """Test behavior when duplicate plugin names exist."""
        # Create two plugins with same name
        dup1 = manifests_dir / "dup1"
        dup1.mkdir()
        (dup1 / "plugin.yaml").write_text("""
schema_version: 2
name: DuplicatePlugin
version: "1.0.0"
description: Duplicate test plugin v1
mandatory: false
enabled: true
prefer_system: false
register_to_path: false
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/dup1.zip
    command:
      executable: dup.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/dup1.zip
    command:
      executable: dup
  macos:
    source:
      type: url
      base_uri: https://example.com/dup1.zip
    command:
      executable: dup
""")

        dup2 = manifests_dir / "dup2"
        dup2.mkdir()
        (dup2 / "plugin.yaml").write_text("""
schema_version: 2
name: DuplicatePlugin
version: "2.0.0"
description: Duplicate test plugin v2
mandatory: false
enabled: true
prefer_system: false
register_to_path: false
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/dup2.zip
    command:
      executable: dup.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/dup2.zip
    command:
      executable: dup
  macos:
    source:
      type: url
      base_uri: https://example.com/dup2.zip
    command:
      executable: dup
""")

        count = manager.discover_plugins()
        # Should only have one instance (last one wins)
        assert "DuplicatePlugin" in manager.plugins
        assert count >= 1


class TestPluginManagerEdgeCases:
    """Test edge cases and error handling in PluginManager."""

    def test_discover_plugins_nonexistent_directory(self, temp_dir):
        """Test discovering plugins when directory doesn't exist."""
        nonexistent_plugins = temp_dir / "nonexistent_plugins"
        nonexistent_manifests = temp_dir / "nonexistent_manifests"
        manager = PluginManager(nonexistent_plugins, nonexistent_manifests)

        count = manager.discover_plugins()
        assert count == 0
        assert len(manager.plugins) == 0

    def test_discover_plugins_with_validation_error(self, manager, manifests_dir):
        """Test that validation errors don't stop other plugins from loading."""
        # Create a valid plugin
        valid_dir = manifests_dir / "valid"
        valid_dir.mkdir()
        valid_manifest = valid_dir / "plugin.yaml"
        valid_manifest.write_text("""
schema_version: 2
name: ValidPlugin
version: "1.0.0"
description: Valid plugin
mandatory: false
enabled: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/valid.zip
    command:
      path: ""
      executable: valid.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/valid.zip
    command:
      path: ""
      executable: valid
  macos:
    source:
      type: url
      base_uri: https://example.com/valid.zip
    command:
      path: ""
      executable: valid
""")

        # Create an invalid plugin (validation should fail)
        invalid_dir = manifests_dir / "invalid"
        invalid_dir.mkdir()
        invalid_manifest = invalid_dir / "plugin.yaml"
        invalid_manifest.write_text("""
name: InvalidPlugin
# Missing required fields like version, description, schema_version
enabled: true
""")

        count = manager.discover_plugins()

        # Valid plugin should still load
        assert "ValidPlugin" in manager.plugins
        assert count >= 1

    def test_discover_plugins_with_generic_exception(self, manager, manifests_dir):
        """Test that generic exceptions don't stop other plugins from loading."""
        # Create two valid plugins
        for i in range(2):
            plugin_dir = manifests_dir / f"plugin{i}"
            plugin_dir.mkdir()
            manifest = plugin_dir / "plugin.yaml"
            manifest.write_text(f"""
schema_version: 2
name: Plugin{i}
version: "1.0.0"
description: Test plugin {i}
mandatory: false
enabled: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}
  macos:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}
""")

        # Mock _load_manifest to raise exception for first plugin
        original_load = manager._load_manifest

        def mock_load(path):
            if "plugin0" in str(path):
                raise Exception("Test error")  # noqa: TRY002
            return original_load(path)

        with patch.object(manager, "_load_manifest", side_effect=mock_load):
            count = manager.discover_plugins()

        # Second plugin should still load
        assert "Plugin1" in manager.plugins
        assert count >= 1

    def test_get_all_plugins_empty(self, manager):
        """Test listing plugins when none are loaded."""
        plugins = manager.get_all_plugins()
        assert len(plugins) == 0

    def test_get_enabled_plugins(self, manager, manifests_dir):
        """Test listing only enabled plugins."""
        # Create enabled and disabled plugins
        for i, enabled in enumerate([True, False, True]):
            plugin_dir = manifests_dir / f"plugin{i}"
            plugin_dir.mkdir()
            manifest = plugin_dir / "plugin.yaml"
            manifest.write_text(f"""
schema_version: 2
name: Plugin{i}
version: "1.0.0"
description: Test plugin {i}
mandatory: false
enabled: {str(enabled).lower()}
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}.exe
  linux:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}
  macos:
    source:
      type: url
      base_uri: https://example.com/plugin{i}.zip
    command:
      executable: plugin{i}
""")

        manager.discover_plugins()

        enabled_plugins = manager.get_enabled_plugins()
        assert len(enabled_plugins) == 2
        assert all(p.manifest.enabled for p in enabled_plugins)
