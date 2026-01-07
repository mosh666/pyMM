"""Unit tests for plugin preferences functionality."""

import pytest
import yaml

from app.core.services.config_service import (
    ConfigService,
    ExecutionPreference,
    PluginPreferences,
)


class TestPluginPreferences:
    """Test suite for plugin preferences."""

    @pytest.fixture
    def config_service(self, tmp_path):
        """Create ConfigService instance with temp directory."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        return ConfigService(config_dir=config_dir)

    @pytest.fixture
    def sample_preferences(self):
        """Sample plugin preferences for testing."""
        return {
            "git": PluginPreferences(
                execution_preference=ExecutionPreference.SYSTEM,
                enabled=True,
                notes="Use system git package",
            ),
            "ffmpeg": PluginPreferences(
                execution_preference=ExecutionPreference.PORTABLE,
                enabled=True,
                notes="Portable version for consistency",
            ),
            "imagemagick": PluginPreferences(
                execution_preference=ExecutionPreference.AUTO,
                enabled=False,
                notes="Disabled for now",
            ),
        }

    def test_default_plugin_preference(self):
        """Test default PluginPreferences values."""
        pref = PluginPreferences()

        assert pref.execution_preference == ExecutionPreference.AUTO
        assert pref.enabled is True
        assert pref.notes == ""

    def test_plugin_preference_with_values(self):
        """Test PluginPreferences with custom values."""
        pref = PluginPreferences(
            execution_preference=ExecutionPreference.SYSTEM, enabled=False, notes="Test note"
        )

        assert pref.execution_preference == ExecutionPreference.SYSTEM
        assert pref.enabled is False
        assert pref.notes == "Test note"

    def test_save_plugin_preferences(self, config_service, sample_preferences):
        """Test saving plugin preferences to file."""
        config_service.save_plugin_preferences(sample_preferences)

        # Verify file was created
        prefs_file = config_service._plugin_preferences_path
        assert prefs_file.exists()

        # Verify file contents
        with open(prefs_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "git" in data
        assert data["git"]["execution_preference"] == "system"
        assert data["git"]["enabled"] is True
        assert data["git"]["notes"] == "Use system git package"

        assert "ffmpeg" in data
        assert data["ffmpeg"]["execution_preference"] == "portable"

        assert "imagemagick" in data
        assert data["imagemagick"]["enabled"] is False

    def test_load_plugin_preferences(self, config_service, sample_preferences):
        """Test loading plugin preferences from file."""
        # Save first
        config_service.save_plugin_preferences(sample_preferences)

        # Load
        loaded_prefs = config_service.load_plugin_preferences()

        assert len(loaded_prefs) == 3
        assert "git" in loaded_prefs
        assert loaded_prefs["git"].execution_preference == ExecutionPreference.SYSTEM
        assert loaded_prefs["git"].enabled is True

        assert "ffmpeg" in loaded_prefs
        assert loaded_prefs["ffmpeg"].execution_preference == ExecutionPreference.PORTABLE

        assert "imagemagick" in loaded_prefs
        assert loaded_prefs["imagemagick"].enabled is False

    def test_load_empty_preferences(self, config_service):
        """Test loading when no preferences file exists."""
        loaded_prefs = config_service.load_plugin_preferences()

        assert loaded_prefs == {}

    def test_load_preferences_with_config(self, config_service, sample_preferences):
        """Test that preferences are loaded with main config."""
        # Save preferences
        config_service.save_plugin_preferences(sample_preferences)

        # Load config (should also load preferences)
        config = config_service.load()

        assert len(config.plugin_preferences) == 3
        assert "git" in config.plugin_preferences
        assert config.plugin_preferences["git"].execution_preference == ExecutionPreference.SYSTEM

    def test_get_plugin_preference(self, config_service, sample_preferences):
        """Test getting preference for specific plugin."""
        config_service.save_plugin_preferences(sample_preferences)
        config_service.load()

        # Get existing preference
        git_pref = config_service.get_plugin_preference("git")
        assert git_pref.execution_preference == ExecutionPreference.SYSTEM
        assert git_pref.notes == "Use system git package"

        # Get non-existent preference (should return default)
        unknown_pref = config_service.get_plugin_preference("unknown")
        assert unknown_pref.execution_preference == ExecutionPreference.AUTO
        assert unknown_pref.enabled is True

    def test_set_plugin_preference_new(self, config_service):
        """Test setting preference for new plugin."""
        config_service.load()

        new_pref = PluginPreferences(
            execution_preference=ExecutionPreference.SYSTEM,
            enabled=True,
            notes="New plugin preference",
        )

        config_service.set_plugin_preference("newplugin", new_pref)

        # Verify in memory
        config = config_service.get_config()
        assert "newplugin" in config.plugin_preferences
        assert (
            config.plugin_preferences["newplugin"].execution_preference
            == ExecutionPreference.SYSTEM
        )

        # Verify persisted
        loaded_prefs = config_service.load_plugin_preferences()
        assert "newplugin" in loaded_prefs
        assert loaded_prefs["newplugin"].notes == "New plugin preference"

    def test_set_plugin_preference_with_kwargs(self, config_service):
        """Test setting preference using kwargs."""
        config_service.load()

        config_service.set_plugin_preference(
            "testplugin",
            execution_preference=ExecutionPreference.PORTABLE,
            enabled=False,
            notes="Test via kwargs",
        )

        # Verify
        pref = config_service.get_plugin_preference("testplugin")
        assert pref.execution_preference == ExecutionPreference.PORTABLE
        assert pref.enabled is False
        assert pref.notes == "Test via kwargs"

    def test_set_plugin_preference_update_existing(self, config_service, sample_preferences):
        """Test updating existing preference."""
        config_service.save_plugin_preferences(sample_preferences)
        config_service.load()

        # Update git preference
        config_service.set_plugin_preference(
            "git", execution_preference=ExecutionPreference.PORTABLE, notes="Changed to portable"
        )

        # Verify update
        pref = config_service.get_plugin_preference("git")
        assert pref.execution_preference == ExecutionPreference.PORTABLE
        assert pref.notes == "Changed to portable"
        assert pref.enabled is True  # Should retain original value

    def test_malformed_preferences_file(self, config_service):
        """Test handling of malformed preferences file."""
        # Create malformed preferences file
        prefs_file = config_service._plugin_preferences_path
        prefs_file.parent.mkdir(parents=True, exist_ok=True)

        with open(prefs_file, "w", encoding="utf-8") as f:
            f.write("git:\n  invalid_field: value\n  execution_preference: invalid_value\n")

        # Should handle gracefully and skip invalid entries
        loaded_prefs = config_service.load_plugin_preferences()

        # Should not crash and may skip invalid entry
        assert isinstance(loaded_prefs, dict)

    def test_execution_preference_enum_values(self):
        """Test ExecutionPreference enum values."""
        assert ExecutionPreference.AUTO.value == "auto"
        assert ExecutionPreference.SYSTEM.value == "system"
        assert ExecutionPreference.PORTABLE.value == "portable"

        # Test all values are valid
        for pref in ExecutionPreference:
            assert pref.value in ["auto", "system", "portable"]
