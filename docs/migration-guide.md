# Migration Guide

> **Last Updated:** 2026-01-17 21:41 UTC
\nThis guide helps you migrate between different versions of pyMediaManager and upgrade project templates.

## Table of Contents

- [Breaking Changes](#breaking-changes)
- [Version Migrations](#version-migrations)
- [Template Migrations](#template-migrations)
- [Configuration Changes](#configuration-changes)
- [Plugin Updates](#plugin-updates)
- [Platform Migrations](#platform-migrations)
- [Rollback Procedures](#rollback-procedures)

---

(breaking-changes)=

## Breaking Changes

### January 15, 2026 - v0.7.0

**Removed Deprecated Features:**

1. **Legacy CONFIG Portable Mode**
   - **Removed:** `PortableMode.CONFIG` enum value
   - **Impact:** Config file-based portable mode detection no longer supported
   - **Migration:** Use `--portable` CLI flag or `PYMM_PORTABLE` environment variable
   - **Code Changes:** Update any code referencing `PortableMode.CONFIG`

2. **Platform Access Checking**
   - **Removed:** `check_plugin_platform_usage()` function, `PlatformCheckError` exception
   - **Impact:** No automatic detection of direct `sys.platform` usage in plugins
   - **Migration:** Plugins should already use `app.core.platform.Platform` API
   - **Code Changes:** Remove `strict_platform_checks` parameter from `PluginManager`

3. **V1 Plugin Schema Support**
   - **Removed:** Automatic v1 to v2 schema conversion in plugin manifests
   - **Impact:** V1 schema plugins (schema_version: 1) will no longer load
   - **Migration:** Convert all plugin.yaml files to v2 schema (see below)
   - **Removed Fields:** `source`, `command`, `checksum_sha256`, `file_size` (top-level)
   - **Required:** `schema_version: 2`, `platforms` dictionary with platform-specific configs

**V1 to V2 Plugin Schema Migration:**

Old V1 format:

```yaml
schema_version: 1
name: MyPlugin
version: "1.0.0"
mandatory: false
enabled: true
source:
  type: url
  base_uri: https://example.com/tool.zip
command:
  path: bin
  executable: tool.exe
```

New V2 format:

```yaml
schema_version: 2
name: MyPlugin
version: "1.0.0"
mandatory: false
enabled: true
platforms:
  windows:
    source:
      type: url
      base_uri: https://example.com/tool-win.zip
    command:
      path: bin
      executable: tool.exe
    system_package: null
  linux:
    source:
      type: url
      base_uri: https://example.com/tool-linux.tar.gz
    command:
      path: ""
      executable: tool
    system_package: tool
  macos:
    source:
      type: url
      base_uri: https://example.com/tool-macos.tar.gz
    command:
      path: ""
      executable: tool
    system_package: tool
```

**Code Migration Examples:**

Before:

```python
# Removed - no longer available
from app.core.platform import check_plugin_platform_usage, PlatformCheckError

manager = PluginManager(
    plugins_dir=Path("plugins"),
    manifests_dir=Path("manifests"),
    strict_platform_checks=True  # Removed parameter
)

# Removed method
check_plugin_platform_usage(plugin_path, strict=True)
```

After:

```python
from app.plugins.plugin_manager import PluginManager

manager = PluginManager(
    plugins_dir=Path("plugins"),
    manifests_dir=Path("manifests"),
    # strict_platform_checks parameter removed
)

# Platform checking removed - plugins should use app.core.platform API directly
```

---

(version-migrations)=

## Version Migrations

### Migrating from v0.x to v1.0

**Release Date:** January 7, 2026

**Breaking Changes:**

1. **Python Version Requirement**
   - **Old:** Python 3.10+
   - **New:** Python 3.12+
   - **Action:** Upgrade Python before updating pyMM

2. **Configuration Structure**
   - **Old:** Single `config.yaml`
   - **New:** Separate `app.yaml` (defaults) and `user.yaml` (overrides)
   - **Action:** Migration automatic on first run, review `config/user.yaml`

3. **Plugin System**
   - **Old:** Python-based plugins
   - **New:** YAML manifest-based plugins
   - **Action:** Remove old plugins, install new versions from plugin catalog

4. **Project Structure**
   - **Old:** `.pyMediaManager/` metadata folder
   - **New:** `.pymm/` metadata folder
   - **Action:** Automatic migration on project open

**Migration Steps:**

1. **Backup your data:**

   ```bash
   # Backup entire projects directory
   cp -r pyMM.Projects pyMM.Projects.backup

   # Backup configuration
   cp config/config.yaml config/config.yaml.backup
   ```

2. **Update Python:**

   ```bash
   python --version  # Check current version
   # If < 3.12, install Python 3.13 (recommended)
   ```

3. **Update pyMM:**

   ```bash
   git pull origin main
   uv sync --all-extras
   ```

4. **Run migration tool:**

   ```bash
   python -m app --migrate-from v0.x
   ```

5. **Verify configuration:**
   - Review `config/user.yaml`
   - Test project opening
   - Check plugin detection

**New Features in v1.0:**

- Enhanced plugin system with YAML manifests
- Improved cross-platform USB drive detection
- Modern Fluent UI with QFluentWidgets
- Type-safe codebase with Python 3.12+ generics
- 193 tests, 73% code coverage
- Automated GitHub workflows

---

### Migrating to Python 3.14

**Release Date:** Python 3.14.0 released October 1, 2024 (stable)

**Status:** Fully supported by pyMM with complete CI/CD testing across all platforms.

**Why Upgrade to Python 3.14?**

1. **JIT Compiler (Experimental)** - PEP 744 experimental JIT for improved runtime performance
2. **Improved Error Messages** - Enhanced traceback readability and debugging
3. **Performance Improvements** - Native optimizations for async/await and generator expressions
4. **Better Type Checking** - Refined support for modern type hints and generics
5. **Free-threaded Mode** - PEP 703 experimental support (GIL-free Python)

**Compatibility Notes:**

- ✅ All 193 pyMM tests pass on Python 3.14
- ✅ Full CI/CD testing across Windows, Linux (x64/ARM64), and macOS (Intel/Apple Silicon)
- ✅ All plugins and dependencies compatible
- ✅ Portable distributions available for Windows (ZIP/MSI), Linux (AppImage), macOS (DMG)

**Migration Steps:**

1. **Install Python 3.14:**

   **Windows:**

   ```powershell
   # Download from python.org or use winget
   winget install Python.Python.3.14
   ```

   **Linux:**

   ```bash
   # Ubuntu/Debian (if available in repos)
   sudo apt update && sudo apt install python3.14 python3.14-venv

   # Or use deadsnakes PPA
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt update && sudo apt install python3.14 python3.14-venv
   ```

   **macOS:**

   ```bash
   # Using Homebrew
   brew install python@3.14
   ```

2. **Verify Installation:**

   ```bash
   python3.14 --version
   # Should output: Python 3.14.x
   ```

3. **Recreate Virtual Environment:**

   ```bash
   # Remove old environment
   rm -rf .venv  # Linux/macOS
   Remove-Item -Recurse -Force .venv  # Windows PowerShell

   # Create new environment with Python 3.14
   uv venv --python 3.14

   # Activate environment
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

4. **Reinstall Dependencies:**

   ```bash
   uv sync --all-extras --frozen
   ```

5. **Verify pyMM Functionality:**

   ```bash
   # Run tests
   uv run pytest

   # Launch application
   python launcher.py
   ```

**Known Issues:**

- **Free-threaded mode:** Not tested with pyMM—use standard build
- **JIT compiler:** Experimental feature, may not provide benefits for GUI applications

**Rollback:**

If you encounter issues, revert to Python 3.13 (recommended) or 3.12:

```bash
# Recreate environment with Python 3.13
uv venv --python 3.13
source .venv/bin/activate  # or .venv\Scripts\Activate.ps1 on Windows
uv sync --all-extras --frozen
```

---

(template-migrations)=

## Template Migrations

### Why Migrate Templates?

- **Project structure changes:** New templates may have improved folder layouts
- **Plugin updates:** New templates support updated plugins
- **Feature additions:** Access new features available in newer templates

### Using the Template Migration Tool

**Access:** Tools → Migrate Template

**Steps:**

1. **Open the project** you want to migrate
2. **Select source template** (current template)
3. **Select destination template** (new template)
4. **Review changes:**
   - Added folders
   - Removed folders
   - Modified configuration files
   - Plugin changes
5. **Apply migration**
6. **Verify:** Check that all files are intact

**Supported Migrations:**

| From | To | Notes |
| ------ | ----- | ------- |
| `base` | `default` | Adds standard media project structure |
| `base` | `photo-management` | Adds photo-specific folders and plugins |
| `base` | `video-editing` | Adds video-specific folders and plugins |
| `default` | `photo-management` | Specializes for photography |
| `default` | `video-editing` | Specializes for video editing |
| `photo-management` | `video-editing` | Cross-migration (manual review needed) |
| Any | `base` | Simplifies structure (removes specialized folders) |

### Manual Template Migration

If the migration tool doesn't support your scenario:

1. **Create new project with target template:**

   ```bash
   # Create test project
   python -m app create-project --template video-editing --name TestMigration
   ```

2. **Compare structures:**

   ```bash
   # Windows
   tree /F OldProject > old.txt
   tree /F TestMigration > new.txt
   fc old.txt new.txt

   # Linux/macOS
   tree OldProject > old.txt
   tree TestMigration > new.txt
   diff old.txt new.txt
   ```

3. **Copy needed folders/files:**
   - Manually create missing folders
   - Copy `.pymm/template.yaml` from new project
   - Update `.pymm/project.yaml` to reference new template

4. **Update plugins:**
   - Check required plugins in new template
   - Install missing plugins

5. **Test thoroughly:**
   - Open project in pyMM
   - Verify all features work
   - Check that files are accessible

---

(configuration-changes)=

## Configuration Changes

### v0.x → v1.0 Configuration Migration

**Old Format (config.yaml):**

```yaml
app:
  name: pyMediaManager
  version: 0.9.0

paths:
  projects: pyMM.Projects
  logs: pyMM.Logs

logging:
  level: INFO
```

**New Format (config/app.yaml + config/user.yaml):**

```yaml
# config/app.yaml (defaults, don't edit)
app_name: pyMediaManager
paths:
  projects_dir: pyMM.Projects
  logs_dir: pyMM.Logs
logging:
  level: INFO

# config/user.yaml (your overrides)
paths:
  projects_dir: D:\MediaProjects  # Custom path
logging:
  level: DEBUG  # Custom log level
```

**Migration Script:**

```python
# Automatic migration on first v1.0 startup
# Manual migration:
import yaml

# Read old config
with open('config/config.yaml') as f:
    old = yaml.safe_load(f)

# Write user overrides
user_config = {
    'paths': {
        'projects_dir': old['paths']['projects']
    },
    'logging': {
        'level': old['logging']['level']
    }
}

with open('config/user.yaml', 'w') as f:
    yaml.dump(user_config, f)
```

### Platform Configuration Changes

**Windows Drive Detection (v1.0+):**

- Now uses WMI for better USB drive detection
- Supports persistent volume tracking (drive letter changes handled)

**Linux udev Rules (v1.0+):**

- Enhanced udev integration
- Auto-mount improvements
- See [docs/linux-udev-installer.md](linux-udev-installer.md)

**macOS DiskArbitration (v1.0+):**

- Native macOS disk event handling
- Better external drive support

---

(plugin-updates)=

## Plugin Updates

### Plugin System Changes (v1.0)

**Old System:**

- Python plugins in `plugins/*.py`
- Loaded as Python modules
- Security concerns with arbitrary code execution

**New System:**

- YAML manifests in `plugins/*/plugin.yaml`
- Sandboxed execution
- SHA-256 verification for downloads
- No arbitrary code execution

### Migrating Custom Plugins

**If you have custom v0.x plugins:**

1. **Review plugin functionality**
2. **Create YAML manifest:**

   ```yaml
   # plugins/my-plugin/plugin.yaml
   name: My Custom Plugin
   version: 1.0.0
   description: Custom plugin for X

   tool:
     name: mytool
     platforms:
       windows:
         executable: mytool.exe
         download_url: https://example.com/mytool-win.zip
         sha256: abc123...
       linux:
         executable: mytool
         install_command: apt install mytool
       macos:
         executable: mytool
         install_command: brew install mytool
   ```

3. **Remove old `.py` plugin files**
4. **Test plugin detection:** Settings → Plugins → Refresh

**Official Plugin Migrations:**

All bundled plugins have been converted:

- ✅ Git → `plugins/git/plugin.yaml`
- ✅ Git LFS → `plugins/gitlfs/plugin.yaml`
- ✅ FFmpeg → `plugins/ffmpeg/plugin.yaml`
- ✅ ExifTool → `plugins/exiftool/plugin.yaml`
- ✅ ImageMagick → `plugins/imagemagick/plugin.yaml`
- ✅ MKVToolNix → `plugins/mkvtoolnix/plugin.yaml`

---

(platform-migrations)=

## Platform Migrations

### Moving from Windows to Linux

**Scenario:** You have a portable pyMM installation on USB, moving from Windows PC to Linux laptop

**Steps:**

1. **Ensure Python 3.12+ is installed on Linux:**

   ```bash
   sudo apt update
   sudo apt install python3.13 python3.13-venv python3-pip
   ```

2. **Install Qt dependencies:**

   ```bash
   sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0
   ```

3. **Plug in USB drive:**

   ```bash
   # Check mount point
   lsblk
   # Drive should auto-mount to /media/$USER/DriveName
   ```

4. **Navigate to pyMM:**

   ```bash
   cd /media/$USER/YourUSBDrive/pyMM
   ```

5. **Create fresh virtual environment:**

   ```bash
   # Remove old Windows venv
   rm -rf .venv

   # Create new Linux venv and install
   uv venv --python 3.13
   uv sync --all-extras
   ```

6. **Run pyMM:**

   ```bash
   python launcher.py
   ```

**Configuration:** No changes needed for portable mode!

### Moving from macOS to Windows

**Scenario:** Portable installation moving from Mac to Windows PC

**Steps:**

1. **Install Python 3.12+ on Windows:**
   - Download from [python.org](https://www.python.org/downloads/)
   - Check "Add to PATH" during installation

2. **Install Visual C++ Redistributables:**
   - Required for PySide6
   - Download: <https://aka.ms/vs/17/release/vc_redist.x64.exe>

3. **Plug in USB drive:**
   - Note drive letter (e.g., E:)

4. **Open PowerShell and navigate:**

   ```powershell
   cd E:\pyMM
   ```

5. **Recreate virtual environment:**

   ```powershell
   # Remove macOS venv
   Remove-Item -Recurse -Force .venv

   # Create Windows venv with uv
   uv venv
   uv sync --all-extras
   ```

6. **Run pyMM:**

   ```powershell
   python launcher.py
   ```

### Cross-Platform Path Handling

**pyMM automatically handles path differences:**

- Windows: `D:\pyMM.Projects\Project1`
- Linux: `/media/user/USB/pyMM.Projects/Project1`
- macOS: `/Volumes/USB/pyMM.Projects/Project1`

**No manual configuration needed for portable installations!**

---

(rollback-procedures)=

## Rollback Procedures

### Rolling Back to Previous Version

**Scenario:** v1.0 has issues, need to revert to v0.9

**Steps:**

1. **Backup current state:**

   ```bash
   cp -r pyMM.Projects pyMM.Projects.v1.0.backup
   cp -r config config.v1.0.backup
   ```

2. **Checkout previous version:**

   ```bash
   git fetch --tags
   git checkout v0.9.5  # or desired version
   ```

3. **Restore old Python environment:**

   ```bash
   rm -rf .venv
   # Use uv with appropriate Python version
   uv venv --python 3.10  # v0.x used Python 3.10+
   uv sync --all-extras
   ```

4. **Restore old configuration:**

   ```bash
   # If you backed up old config
   cp config.yaml.backup config/config.yaml
   ```

5. **Test thoroughly:**
   - Open existing projects
   - Verify data integrity
   - Check plugin functionality

**Note:** Project metadata may have been updated to v1.0 format. If projects don't open:

```bash
# Manually fix .pymm/project.yaml
cd pyMM.Projects/YourProject/.pymm
# Change "version: 1.0.0" back to "version: 0.9.0"
```

### Emergency Recovery

**If pyMM won't start after update:**

1. **Use backup:**

   ```bash
   mv pyMM pyMM.broken
   mv pyMM.backup pyMM
   ```

2. **Fresh install:**

   ```bash
   git clone https://github.com/mosh666/pyMM.git pyMM.fresh
   cd pyMM.fresh
   uv venv
   uv sync --all-extras

   # Copy your data
   cp -r ../pyMM.broken/pyMM.Projects ./
   cp ../pyMM.broken/config/user.yaml ./config/
   ```

---

## Post-Migration Checklist

After any migration:

- [ ] All projects open successfully
- [ ] Plugins are detected correctly
- [ ] Git integration works (if used)
- [ ] Templates are available
- [ ] Configuration settings preserved
- [ ] Logs directory accessible
- [ ] Performance is acceptable
- [ ] No error messages in logs
- [ ] Recent projects list intact
- [ ] USB drive detection works (portable mode)

---

## Getting Help with Migrations

- **Issues:** [GitHub Issues](https://github.com/mosh666/pyMM/issues)
- **Documentation:** [Installation](installation.md), [Features](features.md), [Configuration](configuration.md), [Troubleshooting](troubleshooting.md)

---

**Document Version:** 1.0
**Last Updated:** January 8, 2026
**Compatible with:** pyMediaManager v1.0+
