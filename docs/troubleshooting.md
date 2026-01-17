# Troubleshooting Guide

> **Last Updated:** 2026-01-17 21:41 UTC


>
> **Test Coverage:** 193 tests passing (73% coverage, ⚠️ sync engine: 0%)
> **Python Support:** 3.12, 3.13, 3.14 (3.13 recommended, 3.14 fully supported)
> **Build System:** uv (10-100x faster) + Hatchling + hatch-vcs
> **Latest Fixes:** Windows UV bundling improvements, dependabot-uv-lock-update workflow
> (Version references in examples are not current version - check releases for your actual version)

This guide covers common issues, error messages, and solutions for pyMediaManager.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Startup Problems](#startup-problems)
- [Plugin Issues](#plugin-issues)
- {ref}`troubleshooting-project-management`
- [Git Integration](#git-integration)
- [UI and Display Issues](#ui-and-display-issues)
- [Performance Problems](#performance-problems)
- [Platform-Specific Issues](#platform-specific-issues)
- [Log File Analysis](#log-file-analysis)
- [Getting Additional Help](#getting-additional-help)

---

(installation-issues)=

## Installation Issues

### Python Version Not Supported

**Error:** `Python 3.12 or higher is required`

**Solution:**

- Install Python 3.12, 3.13 (recommended), or 3.14 from [python.org](https://www.python.org/downloads/)
- **Windows (recommended):** Download the MSI installer for Python 3.13 from GitHub Releases for seamless desktop integration
- **Windows (portable):** Use the ZIP package for USB drive scenarios
- On Windows: Use the official installer and check "Add to PATH"
- On Linux: Use your package manager (e.g., `sudo apt install python3.13`)
- On macOS: Use Homebrew (`brew install python@3.13`) or the official installer

### PySide6 Installation Fails

**Error:** `Failed building wheel for PySide6` or `Qt platform plugin not found`

**Solutions:**

**Windows:**

```powershell
# Install Visual C++ Redistributables
# Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Then reinstall PySide6
uv pip install --force-reinstall PySide6
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3-dev libxcb-xinerama0 libxcb-cursor0 \
                 libxkbcommon-x11-0 libegl1-mesa libglib2.0-0
uv pip install --force-reinstall PySide6
```

**macOS:**

```bash
# Ensure Xcode Command Line Tools are installed
xcode-select --install

uv pip install --force-reinstall PySide6
```

### Missing Dependencies

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**

```bash
# Reinstall all dependencies with UV
uv sync --all-extras

# Or use frozen lockfile for reproducible install
uv sync --frozen --all-extras

# If uv not installed, install it first:
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/macOS: curl -LsSf https://astral.sh/uv/install.sh | sh
```

### UV Not Found

**Error:** `command not found: uv` or `uv is not recognized`

**Solutions:**

**Install UV:**

```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Reload PATH:**

```bash
# Windows PowerShell
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")

# Linux/macOS
source ~/.bashrc  # or ~/.zshrc
```

**For Portable Installations:**

Portable ZIP distributions include a bundled UV executable. Run `launcher.py` to automatically add UV to PATH.

> **Migration Note:** If you're upgrading from an older version that used pip (pre-2026), see
> {ref}`migrating-from-pip` for migration steps.

---

(startup-problems)=

## Startup Problems

### Application Won't Start

**Symptoms:** Double-clicking launcher.py or running from terminal produces no window

**Diagnostics:**

1. Check if Python is correctly installed:

   ```bash
   python --version  # Should show 3.12+
   ```

2. Try running with verbose logging:

   ```bash
   python -m app --log-level DEBUG
   ```

3. Check for conflicting Qt installations:

   ```bash
   python -c "from PySide6 import QtCore; print(QtCore.__version__)"
   ```

**Solutions:**

- **Virtual environment issues:** Recreate your venv

  ```bash
  rm -rf .venv  # or Remove-Item -Recurse .venv on Windows
  uv venv
  uv sync --all-extras
  ```

- **Permission issues:** Run as administrator (Windows) or with appropriate permissions

### Portable Mode Not Working

**Symptoms:** Application creates files in system directories instead of on USB drive

**Solution:**

- Ensure `portable.flag` file exists in the application root directory
- Check that the drive is writable (not read-only)
- On Windows: Right-click drive → Properties → uncheck "Read-only"
- Verify directory paths in logs: Check `pyMM.Logs/app.log`

### Configuration File Errors

**Error:** `YAML parsing error in config/user.yaml`

**Solution:**

1. Validate YAML syntax: <https://www.yamllint.com/>
2. Common issues:
   - Incorrect indentation (must use spaces, not tabs)
   - Missing quotes around special characters
   - Incorrect Windows path escaping (use `\\` or `/`)

3. Reset to default:

   ```bash
   mv config/user.yaml config/user.yaml.backup
   # Restart application to regenerate default config
   ```

---

(plugin-issues)=

## Plugin Issues

### Plugin Not Detected

**Symptoms:** System tool (Git, FFmpeg, etc.) is installed but not showing in pyMM

**Solutions:**

1. **Refresh plugin list:**
   - Settings → Plugins → Refresh System Tools
   - Or restart the application

2. **Check PATH environment variable:**

   ```bash
   # Windows
   where git

   # Linux/macOS
   which git
   ```

3. **Manually specify plugin path:**
   - Go to Settings → Plugins → [Plugin Name]
   - Click "Locate Manually" and browse to executable
   - Windows: Usually `C:\Program Files\Git\bin\git.exe`
   - Linux: Usually `/usr/bin/git`
   - macOS: Usually `/usr/local/bin/git` or `/opt/homebrew/bin/git`

### Plugin Download Fails

**Error:** `SHA-256 checksum mismatch` or `Download failed`

**Solutions:**

1. **Checksum mismatch:**
   - File may be corrupted during download
   - Delete cached file: `pyMM.Plugins/.cache/[plugin_name]`
   - Try downloading again

2. **Network issues:**
   - Check internet connection
   - Try disabling VPN or proxy temporarily
   - Check firewall settings

3. **Manual installation:**
   - Download tool from official website
   - Install normally
   - Let pyMM auto-detect (Settings → Plugins → Refresh)

### Plugin Version Incompatible

**Error:** `Plugin requires version X.X but found Y.Y`

**Solutions:**

- Update the tool to the required version
- Or disable version checking (not recommended):

  ```yaml
  # config/user.yaml
  plugins:
    strict_version_check: false
  ```

---

(troubleshooting-project-management)=

## Project Management

### Cannot Create Project

**Error:** `Permission denied` or `Path not accessible`

**Solutions:**

1. **Check write permissions:**
   - Windows: Right-click folder → Properties → Security
   - Linux/macOS: `chmod +w /path/to/projects`

2. **Drive not mounted:**
   - Ensure external drive is properly connected and mounted
   - Check drive letter/mount point in File Explorer/Finder

3. **Path too long (Windows):**
   - Windows has 260 character path limit
   - Use shorter project names or move projects directory closer to root
   - Or enable long path support (Windows 10 1607+):

     ```powershell
     # Run as Administrator
     New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
       -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
     ```

### Project Won't Open

**Symptoms:** Double-clicking project shows error or nothing happens

**Diagnostics:**

1. Check project metadata file: `.pymm/project.yaml`
2. Verify project structure integrity
3. Check logs: `pyMM.Logs/app.log`

**Solutions:**

- **Corrupted metadata:** Delete `.pymm` folder and re-add project
- **Missing template:** Install required template or migrate to different template
- **Drive letter changed (Windows):** Update project path in recent projects list

### Upgrade pyMediaManager

**To upgrade to the latest version:**

```bash
# Recommended: Using uv (fast)
uv pip install --upgrade pymediamanager

# Using uv tool (for global installations)
uv tool upgrade pymediamanager
```

### Template Not Found

**Error:** `Template 'X' not found`

**Solutions:**

1. **Reinstall templates:**

   ```bash
   # Templates are bundled with application
   # Verify templates/ directory exists in app root
   ls templates/  # Linux/macOS
   dir templates\  # Windows
   ```

2. **Use migration tool:**
   - Tools → Migrate Template
   - Select old template and new template
   - Apply migration

---

(git-integration)=

## Git Integration

### Git Not Initialized

**Symptoms:** Git features disabled or greyed out

**Solutions:**

1. **Initialize Git for project:**
   - Open project
   - Project → Enable Git
   - Or manually: `cd /path/to/project && git init`

2. **Check Git installation:**

   ```bash
   git --version  # Should show 2.40+
   ```

### Git Conflicts

**Error:** `Merge conflict in file X`

**Solutions:**

1. **Resolve manually:**
   - Open conflicted files in text editor
   - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
   - Edit to resolve conflicts
   - Remove conflict markers
   - Save and commit

2. **Use external merge tool:**

   ```bash
   cd /path/to/project
   git mergetool
   ```

3. **Abort merge:**

   ```bash
   git merge --abort
   ```

### Git LFS Issues

**Error:** `Git LFS: filter 'lfs' failed` or large files not tracked

**Solutions:**

1. **Install Git LFS:**

   ```bash
   # Windows: Download from https://git-lfs.github.com/
   # Linux: sudo apt install git-lfs
   # macOS: brew install git-lfs

   git lfs install
   ```

2. **Track large files:**

   ```bash
   cd /path/to/project
   git lfs track "*.psd"
   git lfs track "*.mp4"
   git add .gitattributes
   git commit -m "Track large files with LFS"
   ```

---

(ui-and-display-issues)=

## UI and Display Issues

### Blurry Text (Windows)

**Symptoms:** Text appears blurry or scaled incorrectly on high-DPI displays

**Solutions:**

1. **Enable high-DPI support:**
   - Right-click `launcher.py` → Properties → Compatibility
   - Check "Override high DPI scaling behavior"
   - Select "Application" in dropdown

2. **Adjust Windows scaling:**
   - Settings → Display → Scale and layout
   - Try 100%, 125%, or 150%

### Dark Theme Issues

**Symptoms:** Text unreadable or incorrect colors

**Solutions:**

- Switch theme: Settings → Appearance → Theme → Light/Dark/Auto
- Check Qt style settings:

  ```yaml
  # config/user.yaml
  ui:
    theme: auto  # or light, dark
  ```

### Window Won't Maximize

**Symptoms:** Window size incorrect or maximized state not saved

**Solutions:**

1. **Reset window geometry:**

   ```yaml
   # Delete from config/user.yaml
   # ui:
   #   window:
   #     maximized: true
   ```

2. **Check multi-monitor setup:**
   - Disconnect external monitors temporarily
   - Reset window position: Settings → Reset Window Layout

---

(performance-problems)=

## Performance Problems

### Slow Startup

**Symptoms:** Application takes 10+ seconds to start

**Diagnostics:**

- Check startup time in logs
- Monitor CPU/RAM usage

**Solutions:**

1. **Disable auto-detection:**

   ```yaml
   # config/user.yaml
   plugins:
     auto_detect: false  # Manually refresh when needed
   ```

2. **Reduce recent projects:**
   - Clear old projects from recent list
   - Settings → Privacy → Clear Recent Projects

3. **Check disk health:**
   - Run disk check utility (especially for external drives)
   - Windows: `chkdsk D: /f`
   - Linux: `sudo fsck /dev/sdX`
   - macOS: Disk Utility → First Aid

### High Memory Usage

**Symptoms:** Application uses excessive RAM (500+ MB)

**Solutions:**

1. **Reduce thread pool size:**

   ```yaml
   # config/user.yaml
   advanced:
     thread_pool_size: 2  # Default: 4
     max_concurrent_operations: 2  # Default: 3
   ```

2. **Clear cache:**
   - Settings → Advanced → Clear Cache
   - Or manually delete: `pyMM.Plugins/.cache/`

### Slow Project Loading

**Symptoms:** Opening large projects takes minutes

**Solutions:**

1. **Optimize project structure:**
   - Limit files per directory to < 10,000
   - Use subdirectories for organization

2. **Disable file watchers temporarily:**

   ```yaml
   # config/user.yaml
   advanced:
     file_watcher_delay: 2000  # Increase debounce (ms)
   ```

---

(platform-specific-issues)=

## Platform-Specific Issues

### Windows

#### UAC Prompts

**Issue:** Repeated User Account Control prompts

**Solution:**

- Don't install to `C:\Program Files\` (requires admin)
- Use user directory: `C:\Users\<YourName>\pyMM\`
- Or create portable installation on external drive

#### Drive Letter Changes

**Issue:** USB drive gets different letter (D: → E:), projects not found

**Solution:**

1. **Assign permanent drive letter:**
   - Open Disk Management (`diskmgmt.msc`)
   - Right-click drive → Change Drive Letter
   - Assign fixed letter (e.g., M: for Media)

2. **Use volume label instead:** (pyMM v1.3+)
   - Projects tracked by volume GUID, not drive letter

### Linux

#### USB Drive Auto-Mount Issues

**Issue:** USB drive not auto-mounting or wrong permissions

**Solution:**

1. **Check udev rules:**

   ```bash
   # See docs/linux-udev-installer.md for complete guide
   sudo nano /etc/udev/rules.d/99-pymm-usb.rules
   ```

2. **Manual mount:**

   ```bash
   sudo mkdir /mnt/pymm
   sudo mount /dev/sdX1 /mnt/pymm
   sudo chown $USER:$USER /mnt/pymm
   ```

#### Qt Platform Plugin Missing

**Error:** `Could not load the Qt platform plugin "xcb"`

**Solution:**

```bash
# Install missing Qt dependencies
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0
```

### macOS

#### Gatekeeper Blocks Application

**Issue:** "pyMM cannot be opened because it is from an unidentified developer"

**Solution:**

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /path/to/launcher.py

# Or: Right-click → Open (hold Control key)
```

#### Apple Silicon (M1/M2/M3) Issues

**Issue:** Performance problems or compatibility warnings

**Solution:**

- Install native ARM64 Python 3.13+

  ```bash
  # Check architecture
  python -c "import platform; print(platform.machine())"
  # Should show "arm64" not "x86_64"

  # Install native Python
  brew install python@3.13
  ```

---

(log-file-analysis)=

## Log File Analysis

### Finding Logs

**Location:**

- **Portable mode:** `pyMM.Logs/app.log` (in application root)
- **Installed mode:**
  - Windows: `%LOCALAPPDATA%\pyMediaManager\logs\`
  - Linux: `~/.local/share/pyMediaManager/logs/`
  - macOS: `~/Library/Application Support/pyMediaManager/logs/`

### Understanding Log Levels

```text
DEBUG - Detailed diagnostic information (verbose)
INFO - Normal application events
WARNING - Something unexpected but not critical
ERROR - Functionality affected but app continues
CRITICAL - Severe error, app may crash
```

### Common Error Patterns

**Pattern:** `PermissionError: [Errno 13]`

- **Meaning:** Cannot access file/directory due to permissions
- **Check:** File permissions, antivirus, drive lock status

**Pattern:** `FileNotFoundError: [Errno 2]`

- **Meaning:** Expected file doesn't exist
- **Check:** Path spelling, drive mounted, file deleted

**Pattern:** `yaml.scanner.ScannerError`

- **Meaning:** YAML syntax error in configuration
- **Check:** config/user.yaml for syntax errors

**Pattern:** `RuntimeError: Platform not supported`

- **Meaning:** Feature not available on current OS
- **Check:** Platform-specific documentation

### Increasing Log Verbosity

```yaml
# config/user.yaml
logging:
  level: DEBUG  # Show all diagnostic information
  console_enabled: true  # Print to terminal
  file_enabled: true
```

Or temporary override:

```bash
python -m app --log-level DEBUG
```

---

(getting-additional-help)=

## Getting Additional Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Search [existing issues](https://github.com/mosh666/pyMM/issues)
3. ✅ Review [installation guide](installation.md), [features guide](features.md), and [documentation](https://github.com/mosh666/pyMM/blob/main/README.md)
4. ✅ Collect diagnostic information (see below)

### Diagnostic Information to Provide

When reporting issues, include:

```bash
# System information
python --version
uv pip list | grep -i pyside  # or Select-String on Windows

# pyMM version
python -m app --version

# Operating system
# Windows: winver
# Linux: uname -a && lsb_release -a
# macOS: sw_vers

# Relevant log excerpts (last 50 lines)
# Windows: Get-Content pyMM.Logs\app.log -Tail 50
# Linux/macOS: tail -50 pyMM.Logs/app.log
```

---

## Release Automation Issues

### Failed Automated Release

**Symptom:** Daily scheduled release did not run or failed

**Common Causes:**

1. **No commits since last release** - This is expected behavior. Check workflow summary for "No changes to release."
2. **Workflow permissions** - Ensure `GITHUB_TOKEN` has `contents: write` permission
3. **Branch protection** - Release commits may be blocked by branch protection rules
4. **Conventional commits** - Invalid commit format prevents version calculation

**Solutions:**

**Check workflow run logs:**

```bash
# View recent workflow runs
gh run list --workflow=semantic-release.yml --limit 5

# View specific run details
gh run view <run-id> --log
```

**Verify commit format:**

```bash
# Check recent commits follow conventional format
git log --oneline -10

# Valid examples:
# ✅ feat(plugins): add new feature
# ✅ fix(ui): resolve button alignment
# ❌ Fixed the bug (missing type)
```

**Manual trigger:**

If you need to force a release:

1. Go to [Actions → Semantic Release](https://github.com/mosh666/pyMM/actions/workflows/semantic-release.yml)
2. Click "Run workflow"
3. Select branch (`dev` or `main`)
4. Enable "force" if no new commits exist
5. Click "Run workflow"

### Beta Release Not Created

**Symptom:** Expected daily beta release was not created

**Diagnostic Steps:**

1. **Check if commits exist:**

   ```bash
   # Get latest tag
   git describe --tags --abbrev=0

   # Count commits since last tag (example: v0.2.0-beta.1)
   git rev-list v0.2.0-beta.1..HEAD --count
   ```

   If count is 0, no release is needed.

2. **Check workflow schedule:**

   - Daily releases run at 00:00 UTC
   - Check your timezone: UTC = GMT
   - Verify in [Actions tab](https://github.com/mosh666/pyMM/actions)

3. **Review excluded commits:**

   Commits with these types are excluded from releases:
   - `chore`, `ci`, `refactor`, `style`, `test`, `docs`, `build` (non-deps)

   If ALL commits since last tag are excluded types, no version bump occurs.

**Solution:**

To trigger a beta release manually:

```bash
# Option 1: Via GitHub UI (recommended)
# Go to Actions → Semantic Release → Run workflow → Select 'dev' branch

# Option 2: Create a version bump commit
git commit --allow-empty -m "chore(release): trigger beta release"
git push origin dev
```

### Version Number Issues

**Symptom:** Version doesn't match expectations (e.g., 0.1.0-beta.1 instead of 0.2.0-beta.1)

**Explanation:**

- **`feat` commits** → Minor bump (0.1.0 → 0.2.0)
- **`fix` commits** → Patch bump (0.1.0 → 0.1.1)
- **Breaking changes (`!` or `BREAKING CHANGE:`)** → Minor bump in v0.x (0.1.0 → 0.2.0)
- **All versions stay in `0.y.z` format** until deliberate v1.0.0 release process

**v0.y.z Enforcement:**

The project has 5 protection layers preventing accidental v1.0.0 releases:

1. **hatch-vcs `tag_regex`** - Rejects v1+ at build time
2. **GitHub Actions workflow** - Fails CI if version exceeds v0.y.z
3. **Pre-commit hook** - Blocks v1+ tags at git push
4. **PR checklist** - Manual verification for v1.0.0 release
5. **Documentation** - Clear process in CONTRIBUTING.md

This ensures v1.0.0 is a conscious, deliberate decision by maintainers.

**Important:** Branch-specific semantic-release configurations require explicit `major_on_zero = false`
settings - they don't inherit from the root configuration. Both `branches.main` and `branches.dev`
sections must have this setting to ensure consistent v0.y.z enforcement.

**Check what version would be calculated:**

```bash
# Preview next version without creating release
just release-preview

# Or using python-semantic-release directly
semantic-release version --print
```

### Release Assets Missing

**Symptom:** GitHub release exists but no ZIP/AppImage/DMG files attached

**Common Causes:**

1. **Build workflow failed** - Check build.yml workflow logs
2. **Upload step failed** - Check semantic-release.yml upload-assets job
3. **Artifact retention** - Artifacts expire after 90 days

**Solutions:**

**Check build status:**

```bash
gh run list --workflow=build.yml --limit 5
gh run view <run-id> --log
```

**Re-upload assets manually:**

If build succeeded but upload failed:

1. Download artifacts from build workflow run
2. Upload to release manually (replace version with your actual release):

   ```bash
   gh release upload v0.3.0-beta.1 \
     pyMM-Windows-3.13-x64.zip \
     pyMM-Linux-3.13-x86_64.AppImage \
     pyMM-macOS-3.13-x86_64.dmg \
     SHA256SUMS.txt
   ```

### Changelog Not Updated

**Symptom:** CHANGELOG.md not updated after release

**Common Causes:**

1. **All commits excluded** - Only `feat`, `fix`, and `perf` types appear in changelog
2. **Merge conflicts** - CHANGELOG.md has conflicts from manual edits
3. **Configuration error** - `changelog.mode = "update"` setting incorrect

**Solutions:**

**Verify changelog configuration:**

```bash
# Check pyproject.toml
grep -A 10 "\[tool.semantic_release.changelog\]" pyproject.toml
```

**Manually update if needed:**

```bash
# Generate changelog without committing
semantic-release changelog --unreleased

# Or view what would be generated
semantic-release version --changelog --no-commit
```

### Permission Denied Errors

**Symptom:** `refusing to allow a GitHub App to create or update workflow` or `Resource not accessible by integration`

**Cause:** `GITHUB_TOKEN` permissions insufficient for scheduled workflows

**Solution:**

Repository settings must allow GitHub Actions to:

1. Go to repository **Settings → Actions → General**
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"
3. Save changes

**Note:** This is required for automated releases triggered by schedule or workflow_dispatch.

---

### Where to Get Help

- **🐛 Bug Reports:** [GitHub Issues](<https://github.com/mosh666/pyMM/issues/new?template=bug_report.yml>)
- **💡 Feature Requests:** [GitHub Issues](<https://github.com/mosh666/pyMM/issues/new?template=feature_request.yml>)
- **📖 Documentation:** [Installation](installation.md), [Getting Started](getting-started.md),
  [Features](features.md), [Architecture](architecture.md)
- **🔒 Security Issues:** See [Security Policy](<https://github.com/mosh666/pyMM/blob/main/.github/SECURITY.md>)

---

**Document Version:** 2.0
**Last Updated:** January 8, 2026
**Compatible with:** pyMediaManager v0.1+
