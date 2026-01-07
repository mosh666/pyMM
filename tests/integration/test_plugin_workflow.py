"""
Integration tests for plugin download and installation workflow.
"""

from pathlib import Path

import pytest

from app.plugins.plugin_manager import PluginManager

# Mark all tests in this module as integration tests
pytestmark = pytest.mark.integration


@pytest.fixture
def test_plugins_dir(tmp_path):
    """Create a temporary plugins directory."""
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    return plugins_dir


@pytest.fixture
def manifests_dir():
    """Get the real manifests directory."""
    # Use actual plugin manifests from the project
    return Path(__file__).parent.parent.parent / "plugins"


@pytest.fixture
def plugin_manager(test_plugins_dir, manifests_dir):
    """Create a PluginManager with test directories."""
    return PluginManager(test_plugins_dir, manifests_dir)


class TestPluginDownload:
    """Integration tests for plugin download and installation."""

    def test_plugin_discovery(self, plugin_manager):
        """Test discovering plugins from manifests."""
        plugin_manager.discover_plugins()

        plugins = plugin_manager.get_all_plugins()
        assert len(plugins) > 0

        # Check for known plugins (use cross-platform compatible ones)
        plugin_names = [p.manifest.name for p in plugins]
        assert "Git-LFS" in plugin_names or "GitVersion" in plugin_names

    def test_plugin_status_before_install(self, plugin_manager):
        """Test plugin status before installation."""
        plugin_manager.discover_plugins()

        plugins = plugin_manager.get_all_plugins()
        assert len(plugins) > 0

        # None should be installed initially
        for plugin in plugins:
            assert not plugin.is_installed()

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_install_small_plugin(self, plugin_manager):
        """Test installing a small plugin (Git-LFS).

        This test downloads from the internet and may be slow.
        """
        plugin_manager.discover_plugins()

        # Track progress
        progress_updates = []

        def progress_callback(current, total):
            if total > 0:
                percent = (current / total) * 100
                progress_updates.append(percent)

        # Install Git-LFS (relatively small download, works cross-platform)
        success = await plugin_manager.install_plugin("Git-LFS", progress_callback)

        assert success is True
        assert len(progress_updates) > 0

        # Verify installation
        gitlfs = next(p for p in plugin_manager.get_all_plugins() if p.manifest.name == "Git-LFS")

        assert gitlfs.is_installed()

        exe_path = gitlfs.get_executable_path()
        assert exe_path is not None
        assert exe_path.exists()

        version = gitlfs.get_version()
        assert version is not None
        assert len(version) > 0

    @pytest.mark.asyncio
    async def test_install_nonexistent_plugin(self, plugin_manager):
        """Test installing a plugin that doesn't exist."""
        plugin_manager.discover_plugins()

        success = await plugin_manager.install_plugin("NonexistentPlugin")

        assert success is False

    def test_get_plugin_status(self, plugin_manager):
        """Test getting status for specific plugin."""
        plugin_manager.discover_plugins()

        plugins = plugin_manager.get_all_plugins()
        if len(plugins) > 0:
            plugin = plugins[0]
            status = plugin_manager.get_plugin_status(plugin.manifest.name)

            assert status is not None
            assert "installed" in status
            assert "enabled" in status

    def test_mandatory_vs_optional_plugins(self, plugin_manager):
        """Test filtering mandatory and optional plugins."""
        plugin_manager.discover_plugins()

        mandatory = plugin_manager.get_mandatory_plugins()
        optional = plugin_manager.get_optional_plugins()

        # Should have at least some plugins
        assert len(mandatory) + len(optional) > 0

        # No overlap
        mandatory_names = {p.manifest.name for p in mandatory}
        optional_names = {p.manifest.name for p in optional}
        assert len(mandatory_names & optional_names) == 0
