"""Tests for PluginManager."""

import pytest

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
name: TestPlugin
version: "1.0.0"
mandatory: false
enabled: true

source:
  type: url
  base_uri: https://example.com/testplugin.zip

command:
  path: bin
  executable: test.exe

register_to_path: true
dependencies: []
"""

    manifest_file = plugin_dir / "plugin.yaml"
    manifest_file.write_text(manifest_content)

    return manifest_file


class TestPluginManager:
    """Test suite for PluginManager."""

    @pytest.fixture
    def manager(self, plugins_dir, manifests_dir):
        """Create PluginManager instance."""
        return PluginManager(plugins_dir, manifests_dir)

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
name: MandatoryPlugin
version: "1.0"
mandatory: true
enabled: true
source:
  type: url
  base_uri: https://example.com/mandatory.zip
command:
  path: ""
  executable: mandatory.exe
"""
        (mandatory_dir / "plugin.yaml").write_text(mandatory_manifest)

        # Create optional plugin
        optional_dir = manifests_dir / "optional"
        optional_dir.mkdir()
        optional_manifest = """
name: OptionalPlugin
version: "1.0"
mandatory: false
enabled: true
source:
  type: url
  base_uri: https://example.com/optional.zip
command:
  path: ""
  executable: optional.exe
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
name: MandatoryPlugin
mandatory: true
enabled: true
source: {type: url, base_uri: "https://example.com"}
command: {path: "", executable: "test.exe"}
"""
        )

        optional_dir = manifests_dir / "optional"
        optional_dir.mkdir()
        (optional_dir / "plugin.yaml").write_text(
            """
name: OptionalPlugin
mandatory: false
enabled: true
source: {type: url, base_uri: "https://example.com"}
command: {path: "", executable: "test.exe"}
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
name: EnabledPlugin
enabled: true
mandatory: false
source: {type: url, base_uri: "https://example.com"}
command: {path: "", executable: "test.exe"}
"""
        )

        # Disabled plugin
        disabled_dir = manifests_dir / "disabled"
        disabled_dir.mkdir()
        (disabled_dir / "plugin.yaml").write_text(
            """
name: DisabledPlugin
enabled: false
mandatory: false
source: {type: url, base_uri: "https://example.com"}
command: {path: "", executable: "test.exe"}
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
