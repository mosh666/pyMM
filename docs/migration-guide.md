# Migration Guide

> **Last Updated:** January 8, 2026

This guide helps you migrate between different versions of pyMediaManager and upgrade project templates.

## Table of Contents

- [Version Migrations](#version-migrations)
- [Template Migrations](#template-migrations)
- [Configuration Changes](#configuration-changes)
- [Plugin Updates](#plugin-updates)
- [Platform Migrations](#platform-migrations)
- [Rollback Procedures](#rollback-procedures)

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
   # If < 3.12, install Python 3.13 or 3.14
   ```

3. **Update pyMM:**

   ```bash
   git pull origin main
   pip install -e ".[dev]"
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

   # Create new Linux venv
   python3.13 -m venv .venv
   source .venv/bin/activate
   pip install -e ".[dev]"
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

   # Create Windows venv
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -e ".[dev]"
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
   python3.10 -m venv .venv  # v0.x used Python 3.10+
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -e .
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
   python -m venv .venv
   # ... install dependencies ...

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
- **Documentation:** [User Guide](user-guide.md), [Troubleshooting](troubleshooting.md)

---

**Document Version:** 1.0
**Last Updated:** January 8, 2026
**Compatible with:** pyMediaManager v1.0+
