# Platform-Specific Directory Support

## Overview

pyMediaManager now follows platform conventions for configuration, data, and cache directories. This ensures compliance with operating system standards and improves integration with system-level tools.

## Directory Structure

### Windows
- **Config/Data**: `%APPDATA%\pyMediaManager` (e.g., `C:\Users\John\AppData\Roaming\pyMediaManager`)
- **Cache**: `%LOCALAPPDATA%\pyMediaManager\Cache` (e.g., `C:\Users\John\AppData\Local\pyMediaManager\Cache`)

### macOS
- **Config/Data**: `~/Library/Application Support/pyMediaManager`
- **Logs**: `~/Library/Logs/pyMediaManager` (future enhancement)
- **Cache**: `~/Library/Caches/pyMediaManager`

### Linux
Follows [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html):

- **Config**: `$XDG_CONFIG_HOME/pymediamanager` or `~/.config/pymediamanager`
- **Data**: `$XDG_DATA_HOME/pymediamanager` or `~/.local/share/pymediamanager`
- **Cache**: `$XDG_CACHE_HOME/pymediamanager` or `~/.cache/pymediamanager`

## API

### Functions

```python
from app.core.services.config_service import (
    get_platform_config_dir,
    get_platform_data_dir,
    get_platform_cache_dir,
)

# Get platform-specific configuration directory
config_dir = get_platform_config_dir()  # Path to config directory
config_dir = get_platform_config_dir("MyApp")  # Custom app name

# Get platform-specific data directory
data_dir = get_platform_data_dir()

# Get platform-specific cache directory
cache_dir = get_platform_cache_dir()
```

### ConfigService

```python
from app.core.services.config_service import ConfigService

# Uses platform-specific directory by default
config_service = ConfigService()

# Override with custom directory (for testing or portable installations)
config_service = ConfigService(config_dir="/custom/path")
```

## Migration

### Automatic Migration

When `ConfigService` initializes, it automatically migrates configuration files from the legacy location (`app_root/config`) to the platform-specific directory if:

1. The platform-specific directory is empty (no `user.yaml` exists)
2. Files exist in the legacy location (`app_root/config`)

Migration copies:
- `user.yaml` - User configuration overrides
- `app.yaml` - Default application configuration

### Manual Migration

If you need to manually migrate configuration:

```bash
# Linux
mkdir -p ~/.config/pymediamanager
cp -r config/* ~/.config/pymediamanager/

# macOS
mkdir -p ~/Library/Application\ Support/pyMediaManager
cp -r config/* ~/Library/Application\ Support/pyMediaManager/

# Windows (PowerShell)
mkdir "$env:APPDATA\pyMediaManager"
Copy-Item -Recurse config\* "$env:APPDATA\pyMediaManager\"
```

## Testing

Tests use explicit `config_dir` parameters to avoid platform-specific behavior:

```python
import pytest
from pathlib import Path
from app.core.services.config_service import ConfigService

@pytest.fixture
def config_service(tmp_path):
    """Create ConfigService with explicit test directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return ConfigService(config_dir=config_dir)
```

## Backward Compatibility

- Legacy installations continue to work through automatic migration
- Custom `config_dir` can be specified to override platform defaults
- Tests explicitly specify `config_dir` for consistent behavior

## Platform Detection

Platform detection uses `sys.platform`:
- `"win32"` → Windows
- `"darwin"` → macOS
- `"linux"` → Linux (and other Unix-like systems)

## Environment Variables

### Linux (XDG)

Override default XDG directories:

```bash
export XDG_CONFIG_HOME="/custom/config"
export XDG_DATA_HOME="/custom/data"
export XDG_CACHE_HOME="/custom/cache"
```

### Windows

Override default AppData locations:

```powershell
$env:APPDATA = "C:\CustomAppData"
$env:LOCALAPPDATA = "C:\CustomLocalAppData"
```

### macOS

macOS uses hardcoded `~/Library` paths and does not support environment variable overrides (as per macOS conventions).

## Benefits

1. **Standards Compliance**: Follows OS-specific conventions for file organization
2. **Better Integration**: Works with system backup tools, sync services, and package managers
3. **User Familiarity**: Users expect config files in standard locations
4. **Packaging**: Simplifies creation of system packages (apt, homebrew, chocolatey)
5. **Isolation**: Separates config, data, and cache for better management

## Future Enhancements

- Support for `XDG_STATE_HOME` (Linux) for runtime state
- macOS-specific log directory (`~/Library/Logs/pyMediaManager`)
- System-wide configuration in `/etc/pymediamanager` (Linux)
- Windows registry integration for advanced settings

## References

- [XDG Base Directory Specification](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html)
- [Apple File System Basics](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/FileSystemProgrammingGuide/FileSystemOverview/FileSystemOverview.html)
- [Windows Known Folders](https://docs.microsoft.com/en-us/windows/win32/shell/knownfolderid)
