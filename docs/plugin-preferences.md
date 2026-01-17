# Plugin Preferences System

> **Last Updated:** 2026-01-17 21:41 UTC


## Overview

The plugin preferences system allows users to override default plugin
execution behavior on a per-plugin basis. Users can choose whether each plugin
should prefer system packages, portable binaries, or follow the plugin's
default setting.

## Architecture

### Data Model

**ExecutionPreference Enum** (`config_service.py`):

- `AUTO` - Use plugin's `prefer_system` setting (default)
- `SYSTEM` - Always try system packages first
- `PORTABLE` - Always use portable binaries

**PluginPreferences Model** (`config_service.py`):

```python
class PluginPreferences(BaseModel):
    execution_preference: ExecutionPreference = ExecutionPreference.AUTO
    enabled: bool = True  # Whether plugin is active
    notes: str = ""  # User notes about this plugin
```

**AppConfig** includes:

```python
plugin_preferences: dict[str, PluginPreferences]  # plugin_id -> preferences
```

### Storage

Plugin preferences are stored separately from main configuration in `plugins.yaml`:

```yaml
git:
  execution_preference: system
  enabled: true
  notes: Use system git for better integration

ffmpeg:
  execution_preference: portable
  enabled: true
  notes: Portable version ensures consistency

imagemagick:
  execution_preference: auto
  enabled: false
  notes: Not needed for current workflow
```

**Location**:

- **Windows**: `%APPDATA%\pyMediaManager\plugins.yaml`
- **Linux**: `~/.config/pymediamanager/plugins.yaml`
- **macOS**: `~/Library/Application Support/pyMediaManager/plugins.yaml`

## API Usage

### Loading Preferences

```python
from app.core.services.config_service import ConfigService

config_service = ConfigService()
config = config_service.load()

# Access all preferences
all_prefs = config.plugin_preferences

# Get preference for specific plugin
git_pref = config_service.get_plugin_preference("git")
print(f"Git preference: {git_pref.execution_preference}")
print(f"Enabled: {git_pref.enabled}")
```

### Setting Preferences

```python
from app.core.services.config_service import (
    ConfigService,
    ExecutionPreference,
    PluginPreferences,
)

config_service = ConfigService()
config_service.load()

# Method 1: Using PluginPreferences object
pref = PluginPreferences(
    execution_preference=ExecutionPreference.SYSTEM,
    enabled=True,
    notes="Use system package for better integration"
)
config_service.set_plugin_preference("git", pref)

# Method 2: Using kwargs (updates only specified fields)
config_service.set_plugin_preference(
    "ffmpeg",
    execution_preference=ExecutionPreference.PORTABLE,
    notes="Portable version for consistency"
)

# Method 3: Disable a plugin
config_service.set_plugin_preference(
    "imagemagick",
    enabled=False,
    notes="Not needed currently"
)
```

### Direct File Management

```python
# Load from file (returns dict[str, PluginPreferences])
preferences = config_service.load_plugin_preferences()

# Modify
preferences["git"] = PluginPreferences(
    execution_preference=ExecutionPreference.SYSTEM,
    enabled=True
)

# Save back to file
config_service.save_plugin_preferences(preferences)
```

## Integration with Plugin System

The plugin execution system respects user preferences:

```python
from app.plugins.plugin_base import PluginBase

class MyPlugin(PluginBase):
    def get_executable_info(self):
        # Check user preference from config
        pref = self.config_service.get_plugin_preference(self.plugin_id)

        if not pref.enabled:
            raise RuntimeError(f"Plugin {self.plugin_id} is disabled")

        # Apply preference
        if pref.execution_preference == ExecutionPreference.SYSTEM:
            # Force system tool usage
            return self._try_system_tool()
        elif pref.execution_preference == ExecutionPreference.PORTABLE:
            # Force portable binary
            return self._get_portable_executable()
        else:  # AUTO
            # Use plugin's prefer_system setting
            return super().get_executable_info()
```

## UI Integration

Settings dialog provides UI for managing preferences:

```python
from app.ui.dialogs.settings_dialog import SettingsDialog

# Settings dialog automatically loads preferences
dialog = SettingsDialog(config_service)

# User can:
# - Set execution preference (Auto/System/Portable) via radio buttons
# - Enable/disable plugins via toggle switches
# - Add notes via text fields
# - See system package availability status
```

## Examples

### Example 1: Prefer System Tools on Linux

```python
# User prefers system packages on Linux for better integration
config_service.set_plugin_preference("git", execution_preference=ExecutionPreference.SYSTEM)
config_service.set_plugin_preference("ffmpeg", execution_preference=ExecutionPreference.SYSTEM)
config_service.set_plugin_preference("imagemagick", execution_preference=ExecutionPreference.SYSTEM)
```

### Example 2: Portable Installation

```python
# User wants fully portable installation
for plugin_id in ["git", "ffmpeg", "imagemagick", "exiftool"]:
    config_service.set_plugin_preference(
        plugin_id,
        execution_preference=ExecutionPreference.PORTABLE,
        notes="Portable installation"
    )
```

### Example 3: Disable Unused Plugins

```python
# Disable plugins not needed for current workflow
unused = ["imagemagick", "mkvtoolnix", "mariadb"]
for plugin_id in unused:
    config_service.set_plugin_preference(
        plugin_id,
        enabled=False,
        notes="Not needed for photo management workflow"
    )
```

### Example 4: Mixed Configuration

```python
# Git: use system (better integration with OS)
config_service.set_plugin_preference(
    "git",
    execution_preference=ExecutionPreference.SYSTEM,
    notes="System git has SSH key integration"
)

# FFmpeg: use portable (version-specific features)
config_service.set_plugin_preference(
    "ffmpeg",
    execution_preference=ExecutionPreference.PORTABLE,
    notes="Need specific version for codec support"
)

# Others: auto (use plugin defaults)
config_service.set_plugin_preference(
    "exiftool",
    execution_preference=ExecutionPreference.AUTO,
    notes="Default behavior is fine"
)
```

## Validation

The system validates preferences:

```python
# ExecutionPreference enum ensures only valid values
try:
    pref = PluginPreferences(execution_preference="invalid")
except ValidationError:
    # Pydantic validation fails for invalid enum values
    pass

# Boolean validation for enabled field
pref = PluginPreferences(enabled=True)  # OK
pref = PluginPreferences(enabled="yes")  # Validation error
```

## Migration

The system handles missing preferences gracefully:

```python
# If plugins.yaml doesn't exist, defaults are used
pref = config_service.get_plugin_preference("unknown_plugin")
assert pref.execution_preference == ExecutionPreference.AUTO
assert pref.enabled is True
assert pref.notes == ""

# If specific plugin not in plugins.yaml, returns default
pref = config_service.get_plugin_preference("new_plugin")
# Returns PluginPreferences() with defaults
```

## Testing

```python
import pytest
from app.core.services.config_service import (
    ConfigService,
    ExecutionPreference,
    PluginPreferences,
)

def test_plugin_preferences(tmp_path):
    config_service = ConfigService(config_dir=tmp_path)
    config_service.load()

    # Set preference
    config_service.set_plugin_preference(
        "test_plugin",
        execution_preference=ExecutionPreference.SYSTEM,
        enabled=True,
        notes="Test note"
    )

    # Verify
    pref = config_service.get_plugin_preference("test_plugin")
    assert pref.execution_preference == ExecutionPreference.SYSTEM
    assert pref.enabled is True
    assert pref.notes == "Test note"

    # Verify persistence
    prefs_file = tmp_path / "plugins.yaml"
    assert prefs_file.exists()
```

## Benefits

1. **User Control**: Fine-grained control over each plugin's execution
2. **Flexibility**: Mix system and portable tools as needed
3. **Documentation**: Notes field for explaining decisions
4. **Persistence**: Preferences survive app restarts
5. **Validation**: Pydantic ensures data integrity
6. **Separation**: Preferences stored separately from main config
7. **Default Behavior**: Missing preferences use safe defaults
8. **Platform-Aware**: Follows XDG/macOS standards for storage

## Future Enhancements

- **Profiles**: Save/load preference profiles (e.g., "Portable", "System", "Development")
- **Import/Export**: Share preferences between machines
- **Version Pinning**: Specify preferred versions in preferences
- **Auto-detection**: Suggest preferences based on available tools
- **Conflict Resolution**: Warn about incompatible preferences
- **UI Presets**: One-click preset configurations
