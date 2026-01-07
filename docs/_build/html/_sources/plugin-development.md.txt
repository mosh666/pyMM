# Plugin Development Guide

This guide explains how to create and configure plugins for pyMediaManager (pyMM).

## Table of Contents

- [Overview](#overview)
- [Plugin Architecture](#plugin-architecture)
- [Creating a Plugin](#creating-a-plugin)
- [Plugin YAML Schema](#plugin-yaml-schema)
- [Implementing Plugin Logic](#implementing-plugin-logic)
- [Testing Your Plugin](#testing-your-plugin)
- [Best Practices](#best-practices)

## Overview

pyMM uses a plugin system to manage external tools and dependencies. Each plugin
represents a third-party tool (like Git, FFmpeg, or ExifTool) that pyMM can
download, install, and manage automatically.

Plugins are defined by:

1. A YAML manifest file (`plugin.yaml`) defining metadata and download
   information
2. An optional Python implementation extending `PluginBase` for custom behavior

## Plugin Architecture

### Plugin Base Class

All plugins inherit from `app.plugins.plugin_base.PluginBase`, which provides:

- **`download_and_extract_binary()`**: Built-in download and extraction with retry
  logic, checksum verification, and progress callbacks
- **Archive extraction**: Automatic handling of ZIP, 7z, and self-extracting .exe
  archives
- **Directory flattening**: Removes unnecessary nested directories after extraction
- **Special case handling**: Custom logic for specific tools (e.g., ExifTool renaming)

### Abstract Methods

Plugins must implement these methods:

```python
@abstractmethod
def check_installed(self) -> bool:
    """Check if the plugin is properly installed."""
    pass

@abstractmethod
def install(self, progress_callback: Callable[[str], None] | None = None) -> bool:
    """Install the plugin."""
    pass

@abstractmethod
def uninstall(self) -> bool:
    """Uninstall the plugin."""
    pass

@abstractmethod
def get_version(self) -> str | None:
    """Get the installed version of the plugin."""
    pass
```

### Simple Plugin Implementation

Most plugins use `SimplePluginImplementation`, which provides default behavior:

```python
from app.plugins.plugin_base import SimplePluginImplementation

class MyToolPlugin(SimplePluginImplementation):
    """Plugin for MyTool."""
    pass  # Uses default implementation
```

For custom behavior, override specific methods:

```python
class CustomPlugin(SimplePluginImplementation):
    def check_installed(self) -> bool:
        """Custom installation check."""
        # Your custom logic here
        return super().check_installed()

    def get_version(self) -> str | None:
        """Custom version detection."""
        # Parse version from tool output
        return "1.0.0"
```

## Creating a Plugin

### Step 1: Create Plugin Directory

Create a directory in `plugins/` with your tool name:

```text
plugins/
  mytool/
    plugin.yaml
```

### Step 2: Define Plugin Manifest

Create `plugin.yaml` with your plugin configuration (see [Plugin YAML Schema](#plugin-yaml-schema) below).

### Step 3: (Optional) Create Custom Implementation

If you need custom behavior beyond `SimplePluginImplementation`, create a Python module:

```python
# plugins/mytool/mytool_plugin.py
from app.plugins.plugin_base import PluginBase, PluginManifest

class MyToolPlugin(PluginBase):
    def __init__(self, manifest: PluginManifest, install_dir: Path):
        super().__init__(manifest, install_dir)

    def check_installed(self) -> bool:
        # Custom check logic
        pass

    def install(self, progress_callback=None) -> bool:
        # Custom install logic
        return self.download_and_extract_binary(progress_callback)

    def uninstall(self) -> bool:
        # Custom uninstall logic
        pass

    def get_version(self) -> str | None:
        # Custom version detection
        pass
```

## Plugin YAML Schema

### Required Fields

```yaml
name: string
  # Display name of the plugin
  # Example: "Git"

version: string
  # Version of the plugin/tool
  # Example: "2.43.0"

mandatory: boolean
  # true = Required for pyMM to function
  # false = Optional plugin
  # Example: true

enabled: boolean
  # true = Plugin is active
  # false = Plugin is disabled
  # Example: true

source:
  type: string
    # Download method (currently only "url" supported)
    # Example: "url"

  base_uri: string
    # Download URL for the plugin archive
    # Example: "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe"

command:
  path: string
    # Relative path to executable directory from plugin root
    # Use empty string ("") if executable is in root
    # Example: "bin" or ""

  executable: string
    # Filename of the executable
    # Example: "git.exe"

register_to_path: boolean
  # true = Add executable directory to PATH
  # false = Don't modify PATH
  # Example: true
```

### Optional Fields

```yaml
description: string
  # Human-readable description of the plugin
  # Example: "Distributed version control system"

dependencies: list[string]
  # List of plugin names this plugin depends on
  # Example: ["git", "mariadb"]

source:
  checksum_sha256: string
    # SHA-256 hash (uppercase hex) for integrity verification
    # Example: "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855"

  file_size: integer
    # Expected file size in bytes (for progress tracking)
    # Example: 52428800

  asset_pattern: string
    # Pattern for GitHub release assets (not yet implemented)
    # Example: "PortableGit-.*-64-bit\\.7z\\.exe"
```

## Complete Example

### Basic Plugin: FFmpeg

```yaml
name: "FFmpeg"
version: "7.0.1"
description: "Complete multimedia framework for video/audio processing"
mandatory: false
enabled: true

source:
  type: "url"
  base_uri: "https://github.com/GyanD/codexffmpeg/releases/download/7.0.1/ffmpeg-7.0.1-full_build.7z"
  checksum_sha256: "1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF"
  file_size: 123456789

command:
  path: "bin"
  executable: "ffmpeg.exe"

register_to_path: true
```

### Advanced Plugin: digiKam (with dependencies)

```yaml
name: "digiKam"
version: "8.5.0"
description: "Professional photo management application"
mandatory: false
enabled: false

dependencies:
  - "mariadb"
  - "exiftool"

source:
  type: "url"
  base_uri: "https://download.kde.org/stable/digikam/8.5.0/digiKam-8.5.0-Win64.exe"
  file_size: 387654321

command:
  path: ""
  executable: "digikam.exe"

register_to_path: true
```

## Implementing Plugin Logic

### Using Default Implementation

Most plugins can use `SimplePluginImplementation` which provides:

1. **Installation**: Downloads and extracts to `<storage_dir>/plugins/<plugin_name>/`
2. **Version Check**: Runs `<executable> --version` and parses output
3. **Installation Check**: Verifies executable exists and can run
4. **Uninstallation**: Removes plugin directory

### Custom Installation Logic

Override the `install()` method for custom behavior:

```python
def install(self, progress_callback=None) -> bool:
    """Custom installation with post-processing."""
    # Download and extract
    if not self.download_and_extract_binary(progress_callback):
        return False

    # Post-install configuration
    config_file = self.install_dir / "config.ini"
    config_file.write_text("[Settings]\nkey=value")

    # Create symlinks or shortcuts
    self._create_shortcuts()

    return True
```

### Custom Version Detection

Override `get_version()` for non-standard version output:

```python
def get_version(self) -> str | None:
    """Parse version from tool-specific output."""
    try:
        result = subprocess.run(
            [self.executable_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Parse version with regex
        import re
        match = re.search(r"v(\d+\.\d+\.\d+)", result.stdout)
        return match.group(1) if match else None
    except Exception:
        return None
```

### Custom Installation Check

Override `check_installed()` for complex verification:

```python
def check_installed(self) -> bool:
    """Verify installation with multiple checks."""
    # Check executable exists
    if not self.executable_path.exists():
        return False

    # Check required files
    required_files = ["lib/library.dll", "config/default.cfg"]
    if not all((self.install_dir / f).exists() for f in required_files):
        return False

    # Verify executable runs
    try:
        subprocess.run(
            [self.executable_path, "--help"],
            capture_output=True,
            timeout=5,
            check=True
        )
        return True
    except Exception:
        return False
```

## Testing Your Plugin

### Manual Testing

1. **Place your plugin in the plugins directory**:

   ```text
   plugins/
     mytool/
       plugin.yaml
   ```

2. **Launch pyMM** and check the Plugin Manager view

3. **Verify plugin is discovered**:
   - Should appear in the plugin list
   - Check mandatory/enabled status
   - Verify dependencies are shown

4. **Test installation**:
   - Click Install button
   - Monitor progress callback
   - Verify files are extracted to `<storage>/plugins/mytool/`
   - Check executable is registered to PATH

5. **Test version detection**:
   - Should display version after installation
   - Verify version string is parsed correctly

6. **Test uninstallation**:
   - Click Uninstall button
   - Verify all files are removed
   - Check PATH is cleaned up

### Automated Testing

Create a test file in `tests/unit/test_mytool_plugin.py`:

```python
"""Tests for MyTool plugin."""
import pytest
from pathlib import Path
from app.plugins.plugin_manager import PluginManager

def test_mytool_discovery(temp_dir):
    """Test MyTool plugin is discovered."""
    plugin_dir = temp_dir / "plugins"
    plugin_dir.mkdir()

    # Create test plugin.yaml
    mytool_dir = plugin_dir / "mytool"
    mytool_dir.mkdir()
    (mytool_dir / "plugin.yaml").write_text("""
name: "MyTool"
version: "1.0.0"
mandatory: false
enabled: true
source:
  type: "url"
  base_uri: "https://example.com/mytool.zip"
command:
  path: ""
  executable: "mytool.exe"
register_to_path: true
""")

    # Test discovery
    manager = PluginManager(temp_dir)
    plugins = manager.get_all_plugins()

    assert "mytool" in plugins
    assert plugins["mytool"].manifest.name == "MyTool"
    assert plugins["mytool"].manifest.version == "1.0.0"

def test_mytool_installation(temp_dir, mock_download):
    """Test MyTool installation."""
    # Set up plugin
    manager = PluginManager(temp_dir)
    plugin = manager.get_plugin("mytool")

    # Mock download and install
    assert plugin.install() is True
    assert plugin.check_installed() is True
    assert plugin.get_version() == "1.0.0"
```

## Best Practices

### 1. Always Provide Checksums

Include SHA-256 checksums for security and integrity verification:

```yaml
source:
  checksum_sha256: "ABC123..."  # Generate with: certutil -hashfile file.exe SHA256
```

### 2. Use Semantic Versioning

Follow [semver.org](https://semver.org) for version numbers:

```yaml
version: "2.1.3"  # MAJOR.MINOR.PATCH
```

### 3. Specify File Sizes

Include file sizes for accurate progress tracking:

```yaml
source:
  file_size: 52428800  # 50 MB in bytes
```

### 4. Document Dependencies

Explicitly list dependencies to ensure correct installation order:

```yaml
dependencies:
  - "git"
  - "git-lfs"
```

### 5. Test on Clean Installs

Always test plugin installation on a machine without the tool pre-installed to verify:

- Download URLs are accessible
- Archive extraction works correctly
- Executable paths are correct
- Version detection works
- PATH registration is functional

### 6. Handle Installation Failures Gracefully

Implement proper error handling in custom implementations:

```python
def install(self, progress_callback=None) -> bool:
    """Install with error handling."""
    try:
        if not self.download_and_extract_binary(progress_callback):
            logger.error(f"Failed to download {self.manifest.name}")
            return False

        # Post-install steps
        self._configure()

        if not self.check_installed():
            logger.error(f"{self.manifest.name} installation verification failed")
            return False

        return True
    except Exception as e:
        logger.exception(f"Installation failed for {self.manifest.name}: {e}")
        return False
```

### 7. Use Portable Versions

Prefer portable/standalone versions of tools that don't require system installation:

- PortableGit instead of Git installer
- Portable FFmpeg builds
- Standalone executables

### 8. Document Platform Requirements

If your plugin is platform-specific, document it:

```yaml
description: "Windows-only photo management tool"
# Or implement platform checks in code
```

### 9. Keep Plugins Updated

Regularly update plugin versions and checksums:

- Monitor upstream releases
- Test new versions before updating
- Update CHANGELOG.md when bumping versions

### 10. Follow Security Best Practices

- Only download from official sources (GitHub releases, official websites)
- Always verify checksums
- Use HTTPS URLs
- Scan downloaded files for malware before extraction (if implementing custom logic)

## Plugin Lifecycle

### Discovery Phase

1. `PluginManager` scans `plugins/` directory
2. Reads all `plugin.yaml` files
3. Validates schema (strict validation - fails fast on errors)
4. Creates `PluginManifest` objects
5. Instantiates plugin implementations

### Installation Phase

1. User clicks Install in UI
2. `PluginManager.install_plugin()` called
3. Plugin's `install()` method executes:
   - Downloads archive from `base_uri`
   - Verifies checksum (if provided)
   - Extracts to `<storage>/plugins/<name>/`
   - Flattens directory structure
   - Handles special cases (ExifTool renaming, etc.)
4. Executable registered to PATH
5. Version verification
6. UI updates installation status

### Runtime Phase

1. Application checks plugin status via `check_installed()`
2. Gets version via `get_version()`
3. Executes plugin commands with executable path
4. Monitors plugin health

### Uninstallation Phase

1. User clicks Uninstall in UI
2. `plugin.uninstall()` removes installation directory
3. PATH registration cleaned up
4. UI updates status

## Troubleshooting

### Plugin Not Discovered

- **Check YAML syntax**: Ensure valid YAML formatting
- **Verify required fields**: All required fields must be present
- **Check directory structure**: `plugins/<name>/plugin.yaml`
- **Review logs**: Check `logs/` for validation errors

### Download Fails

- **Verify URL**: Ensure `base_uri` is accessible
- **Check network**: Firewall or proxy issues
- **Validate SSL**: Some corporate networks block certain certificates
- **Try manual download**: Test URL in browser

### Extraction Fails

- **Check archive format**: ZIP, 7z, or self-extracting .exe supported
- **Verify file integrity**: Checksum mismatch indicates corruption
- **Check disk space**: Ensure sufficient space for extraction
- **Review permissions**: Write permissions in storage directory

### Executable Not Found

- **Verify path**: Check `command.path` is correct relative to archive root
- **Check extraction**: Ensure archive extracted properly
- **Verify executable name**: Ensure `command.executable` matches actual filename
- **Test manually**: Navigate to plugin directory and try running executable

### Version Detection Fails

- **Check executable output**: Run `<executable> --version` manually
- **Implement custom parser**: Override `get_version()` for non-standard output
- **Verify executable works**: Ensure tool runs correctly

## Advanced Topics

### GitHub Release Asset Pattern (Future Feature)

The `asset_pattern` field is defined but not yet implemented. Future versions will support:

```yaml
source:
  type: "github-release"
  repository: "owner/repo"
  asset_pattern: "mytool-.*-windows-x64\\.zip"
```

This will automatically fetch the latest matching asset from GitHub releases.

### Multi-Platform Support

To support multiple platforms, you can implement platform detection:

```python
import platform

class CrossPlatformPlugin(PluginBase):
    def __init__(self, manifest: PluginManifest, install_dir: Path):
        super().__init__(manifest, install_dir)

        # Platform-specific configuration
        self.system = platform.system()
        if self.system == "Windows":
            self.executable_name = "tool.exe"
        elif self.system == "Linux":
            self.executable_name = "tool"
        elif self.system == "Darwin":
            self.executable_name = "tool"
```

### Custom Progress Callbacks

Implement detailed progress reporting:

```python
def install(self, progress_callback=None) -> bool:
    """Install with detailed progress."""
    if progress_callback:
        progress_callback("Starting download...")

    # Download with progress
    result = self.download_and_extract_binary(progress_callback)

    if progress_callback:
        progress_callback("Configuring plugin...")

    self._configure()

    if progress_callback:
        progress_callback("Installation complete!")

    return result
```

## Contributing

When contributing new plugins to pyMM:

1. Follow this guide for plugin structure
2. Include checksums for all downloads
3. Test thoroughly on clean installations
4. Update `docs/architecture.md` if adding new patterns
5. Add tests in `tests/unit/test_<plugin>_plugin.py`
6. Update `CHANGELOG.md` with plugin addition
7. Submit PR with plugin manifest and implementation

## Resources

- **Plugin Base Implementation**: `app/plugins/plugin_base.py`
- **Plugin Manager**: `app/plugins/plugin_manager.py`
- **Existing Plugins**: `plugins/` directory
- **Architecture Documentation**: `docs/architecture.md`
- **Contributing Guide**: `CONTRIBUTING.md`

## Support

For questions or issues with plugin development:

1. Check existing plugin implementations in `plugins/`
2. Review architecture documentation in `docs/architecture.md`
3. Open an issue on GitHub with the `plugin` label
4. Join discussions in the pyMM community

---

**Last Updated**: January 2026
**Version**: 1.0.0
