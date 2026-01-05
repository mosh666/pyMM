# pyMediaManager User Guide

**Version:** Auto-detected from Git using setuptools_scm (v1.0.0 stable, latest-beta for dev)
**Last Updated:** January 5, 2026
**Test Suite:** 193 tests with 73% coverage (all passing with automatic isolation)
**Python Support:** 3.12, 3.13, 3.14 (embedded Python 3.13 runtime included for portability)
**Quality:** 15+ pre-commit hooks, Ruff linting, MyPy type checking, Bandit security scanning
**Security:** Daily OpenSSF Scorecard metrics, CodeQL analysis, Dependabot updates

> **See also:** [CHANGELOG.md](../CHANGELOG.md) for detailed version history and new features
> **See also:** [Architecture Guide](architecture.md) for technical details
> **See also:** [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines

## Table of Contents

1. [Getting Started](#getting-started)
2. [First-Time Setup](#first-time-setup)
3. [Project Management](#project-management)
4. [Plugin Management](#plugin-management)
5. [Storage & Portability](#storage--portability)
6. [Settings & Configuration](#settings--configuration)
7. [Troubleshooting](#troubleshooting)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Support & Resources](#support--resources)
10. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### System Requirements

- **Operating System:** Windows 10/11 (64-bit)
- **Python:** 3.12, 3.13, or 3.14 (3.13 recommended) - Embedded runtime included
- **Storage:** Minimum 500MB free space (more for plugins and projects)
- **Recommended:** USB 3.0+ or SSD for portable installation
- **Reliability:** 193 tests ensuring stability and quality

### Installation

pyMediaManager is designed to be fully portable with no system installation required:

1. **Download** the latest release:
   - **Stable releases:** Download from releases page
   - **Latest beta:** Download the `latest-beta` tag for newest features
   - Version is automatically managed using Git tags and setuptools_scm
2. **Extract** to your desired location:
   - USB drive: `E:\pyMM\`
   - External SSD: `D:\pyMM\`
   - Local drive: `C:\Apps\pyMM\`
3. **Run** `launcher.py` to start the application

The application includes an embedded Python 3.13 runtime and all dependencies.
Version information is automatically managed from Git tags and displayed in
the Settings → About tab.

The application will automatically detect the drive root and configure portable folders.

---

## First-Time Setup

### Initial Launch

When you first launch pyMediaManager, the First Run Wizard will guide you through setup:

1. **Welcome Screen** - Introduction to pyMediaManager and key features
2. **Storage Page** - Select your portable drive and confirm installation location
   - **Enhanced Drive Detection**: The wizard now detects all external drives including:
     - USB flash drives and SD cards
     - External USB HDDs and SSDs
     - Thunderbolt/USB-C external drives
     - Portable drives even when Windows shows them as "fixed" drives
   - The application uses Windows Management Instrumentation (WMI) for accurate detection
   - Simply select your preferred external drive from the list
3. **Plugin Page** - Choose optional plugins to install (mandatory plugins installed automatically)
4. **Complete Page** - Setup summary with option to skip wizard on future launches

### Storage Drive Selection

The application's intelligent drive detection identifies:

- **True Removable Drives**: USB flash drives, SD cards, memory sticks
- **External Storage**: USB HDDs, external SSDs, portable drives
- **Interface Detection**: USB, USB-C, Thunderbolt connections
- **Media Type Recognition**: Devices marked as "External hard disk media" by Windows

All external drives are suitable for portable pyMediaManager installation.

### Recommended First Steps

1. **Install Core Plugins** (Essential tools):
   - ExifTool - Media metadata extraction
   - FFmpeg - Video processing
   - Git - Version control system (available as plugin)

2. **Create Your First Project**:
   - Click "New Project" in the toolbar
   - Choose a name and location
   - Select optional project template

3. **Configure Settings**:
   - Open Settings (gear icon)
   - Set your preferred theme
   - Configure storage preferences

---

## Project Management

### Creating a Project

Projects are the primary way to organize your media work in pyMediaManager.

**To create a new project:**

1. Click the **"New Project"** button (or `Ctrl+N`)
2. Enter project details:
   - **Name:** Project identifier (e.g., "vacation-2026")
   - **Location:** Where to store project files
   - **Template:** Optional starter structure
3. Click **"Create"**

**Project Structure:**

```text
D:\pyMM.Projects\vacation-2026\
├── photos\            # Organized media
├── videos\
└── exports\
```

**Note:** Git integration has been decoupled from project management. If you want to use
version control, you can initialize a Git repository manually using the Git plugin.

### Managing Projects

**Open Recent Project:**

- Projects appear in the "Recent Projects" list
- Double-click to open
- Recently used projects stay at the top

**Project Browser:**

- Click "Browse Projects" to see all projects
- Search and filter projects
- View project metadata (created date, size, Git status)

**Delete Project:**

- Right-click project in browser
- Select "Delete Project"
- Choose whether to delete files or just metadata

### Project Workflows

**Basic Workflow:**

1. Create project
2. Add media files to project folders
3. Use plugins to process media
4. Commit changes to Git
5. Export final results

**Git-Enabled Workflow:**

1. Create project with Git
2. Add files and make changes
3. Review status: `View > Git Status`
4. Commit changes with message
5. View history: `View > Git Log`

---

## Plugin Management

### Understanding Plugins

Plugins are external tools integrated into pyMediaManager:

- **Mandatory Plugins:** Required for core functionality (Git, 7-Zip)
- **Optional Plugins:** Add features (FFmpeg, ExifTool, digiKam)
- **Status Indicators:**
  - ✅ Green: Installed and ready
  - ⚠️ Yellow: Available but not installed
  - ❌ Red: Error or missing

### Installing Plugins

**Auto-Install (Recommended):**

1. Navigate to **Plugin View** (tab or `Ctrl+P`)
2. Find the plugin you need
3. Click **"Install"** button
4. Wait for download and extraction
5. Status changes to "Installed" when ready

**Download Details:**

- Plugins download from official sources
- SHA256 checksum verification for security
- Automatic retry on network errors (up to 3 attempts)
- Progress bar shows download status

**Manual Install:**

For plugins not in the catalog:

1. Download plugin binary
2. Extract to `D:\pyMM.Plugins\plugin-name\`
3. Ensure executable is at correct path
4. Restart pyMediaManager

### Plugin Status

**Check Plugin Status:**

```text
Plugin View → Select Plugin → View Status
```

Shows:

- Installation status (Installed/Not Installed)
- Version detected
- Executable path
- Installation date

**Common Plugin Actions:**

- **Install:** Download and set up plugin
- **Uninstall:** Remove plugin files
- **Refresh:** Re-check installation status
- **View Info:** See plugin details and homepage

### Available Plugins

|Plugin|Type|Description|Size|
|---|---|---|---|
|Git|Mandatory|Version control system|~61MB|
|Git-LFS|Mandatory|Git extension for large files|~5MB|
|GitVersion|Mandatory|Semantic versioning tool|~3MB|
|digiKam|Mandatory|Photo management|~300MB+|
|MariaDB|Mandatory|Database backend for digiKam|~200MB+|
|ExifTool|Mandatory|Metadata extraction|~11MB|
|FFmpeg|Optional|Video/audio processing|~202MB|
|ImageMagick|Optional|Image manipulation|~21MB|
|MKVToolNix|Optional|MKV video tools|~20MB+|

---

## Storage & Portability

### Portable Folders

pyMediaManager uses drive-root folders for maximum portability:

```text
K:\                              # Your removable/external drive root
├── pyMM\                        # Application (contains embedded Python 3.13)
│   ├── python313\               # Embedded Python 3.13 runtime
│   ├── lib-py313\               # Python dependencies
│   ├── app\                     # Application code
│   └── launcher.py              # Entry point
├── pyMM.Projects\               # Your media projects
├── pyMM.Logs\                   # Application logs
└── pyMM.Plugins\                # Installed plugin binaries
```

### Supported Drive Types

The application automatically detects and works with:

**True Removable Media:**

- USB flash drives (any capacity)
- SD cards and memory sticks
- Other media marked as "DRIVE_REMOVABLE" by Windows

**External Storage Devices:**

- External USB HDDs (any size, any filesystem)
- External USB SSDs (NTFS, FAT32, exFAT)
- Portable drives connected via USB-C or Thunderbolt
- Drives with "External hard disk media" designation

**Detection Technology:**

- **Primary**: Windows `GetDriveTypeW` API for removable drives
- **Enhanced**: WMI queries for USB interface and external media type
- **Automatic**: Detects drives regardless of Windows classification
- **Reliable**: Works with both consumer and professional storage devices

### Moving Between Computers

pyMediaManager is designed to move seamlessly:

```text
├── pyMM.Plugins\                # Installed plugin binaries
├── pyMM.Logs\                   # Application logs
└── pyMM.Config\                 # User settings (optional)
```

### Drive Management

**Storage View** shows:

- Available drives and their status
- Free space on each drive
- Whether drive is removable
- Current application location

**Best Practices:**

- Install on fast drive (USB 3.0+, SSD)
- Keep 500MB+ free space for plugins
- Regular backups of `pyMM.Projects\`
- Consider using Git plugin for project version control if needed

### Moving Between Drives

pyMediaManager is fully portable:

1. **Copy** entire `pyMM` folder to new drive (includes Python 3.13 runtime)
2. **Copy** `pyMM.Projects`, `pyMM.Plugins`, and `pyMM.Config` folders if desired
3. **Run** `launcher.py` - automatic drive detection on launch
4. Projects and plugins remain accessible

**Note:** The embedded Python runtime moves with the application, ensuring consistency.
If moving projects separately, they will be auto-detected in the new drive root.

---

## Git Integration

### Git Repository Basics

Projects can optionally use Git for version control:

- Track all changes to project files
- Commit snapshots with descriptive messages
- View complete history of modifications
- Collaborate with team members
- Git LFS support for large media files

### Using Git

**Initialize Repository:**

- Enable "Initialize Git" when creating project
- Or: `Project > Initialize Git` on existing project
- Automatically creates `.gitignore` with media-friendly defaults

**Check Status:**

```text
View > Git Status
```

Shows:

- Modified files (yellow)
- New files (green)
- Deleted files (red)
- Untracked files
- Current branch name

**Commit Changes:**

1. Make changes to project files
2. Open Git Status view
3. Review changed files
4. Click **"Commit"**
5. Enter descriptive commit message
6. Confirm commit

**View History:**

```text
View > Git Log
```

Shows:

- Commit messages with full descriptions
- Author name and email
- Commit date and time
- Files changed per commit
- Commit hash for reference

**Git Configuration:**

Git is available as a standalone plugin and can be configured independently
for your project workflows. Use external Git tools or command line for
repository management.

### Version Control Best Practices

**Good Commit Messages:**

```text
✅ Good: "Add raw photos from beach shoot"
✅ Good: "Export final video in 4K"
❌ Bad: "changes"
❌ Bad: "update"
```

**What to Commit:**

- ✅ Raw source files (photos, videos)
- ✅ Project configurations
- ✅ Export settings
- ❌ Large temporary files
- ❌ Cache directories
- ❌ Final exports (optional)

**Using .gitignore:**

Recommended `.gitignore` entries:

- `*.tmp`, `*.cache`
- `__pycache__/`
- `.DS_Store`, `Thumbs.db`
- `exports/` (optional)

---

## Settings & Configuration

### Opening Settings

Access settings via:

- Menu: `Edit > Settings`
- Keyboard: `Ctrl+,`
- Toolbar: Settings icon (gear)

### Settings Sections

The Settings dialog includes 5 tabs for comprehensive configuration:

#### General Tab

- **Application Name:** Display name for the window title
- **Theme:** Light, Dark, or Auto (follows system)
- **Language:** Interface language selection
- **Logging Level:** DEBUG, INFO, WARNING, ERROR, or CRITICAL
- **Check Updates:** Automatic update checking (when available)

#### Plugins Tab

- **Auto-Install:** Install mandatory plugins automatically on first run
- **Download Timeout:** Network timeout in seconds (default: 300)
- **Retry Attempts:** Number of download retry attempts (default: 3)
- **Verify Checksums:** Enable SHA256 checksum verification for security
- **Plugin Directory:** Custom plugin installation location
- **Plugin Paths:** Configure paths for specific plugins

#### Storage Tab

- **Default Drive:** Preferred storage location for portable operation
- **Project Root:** Base directory where new projects are created
- **Log Location:** Application log directory (pyMM.Logs)
- **Max Log Size:** File size before log rotation (default: 10MB)
- **Log Retention:** Number of backup log files to keep

#### Git Tab

- **User Name:** Your full name for Git commits
- **User Email:** Your email address for Git commits
- **Auto-Initialize:** Create Git repositories by default for new projects
- **Default Branch:** Branch name for new repositories (main/master)
- **Git Executable Path:** Custom path to git.exe (auto-detected)

#### About Tab

- **Version:** Current application version (auto-detected from Git)
  - Automatically managed using setuptools_scm and Git tags
  - Development builds show commit hash and distance from last tag
  - Supports alpha, beta, and rc prerelease versions (e.g., v1.0.0-beta.1)
  - Stable releases from `main` branch, beta releases from `dev` branch
- **Commit Hash:** Git commit SHA (for development builds)
- **Python Version:** Embedded Python runtime version (3.13 recommended, 3.12 and 3.14 also supported)
- **Application Info:** License, author, and project details
- **Dependencies:** Installed package versions (PySide6, GitPython, Pydantic, etc.)
- **Test Coverage:** 193 tests with 73% coverage ensuring reliability

### Saving Settings

- Click **"Apply"** to save changes without closing the dialog
- Click **"OK"** to save changes and close the dialog
- Click **"Cancel"** to discard changes and close

Settings are stored in:

- System: `config/app.yaml` (default configuration, read-only)
- User: `D:\pyMM.Config\user.yaml` (your custom settings)

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms:** Double-clicking `launcher.py` does nothing

**Solutions:**

1. Verify Python 3.13 runtime: Check `pyMM\python313\` directory exists
2. Run from terminal: `python launcher.py` or `.\python313\python.exe launcher.py`
3. Check logs: `D:\pyMM.Logs\pymediamanager.log`
4. Verify drive permissions (not read-only)
5. Ensure all dependencies in `lib-py313\` are present

#### Plugin Installation Fails

**Symptoms:** Download stuck or error message

**Solutions:**

1. Check internet connection
2. Verify firewall allows Python
3. Try manual download from plugin homepage
4. Check disk space (500MB+ free)
5. Review plugin status for error details

#### Project Creation Fails

**Symptoms:** Error when creating new project

**Solutions:**

1. Verify project path is writable
2. Check disk space
3. Avoid special characters in project name
4. Ensure parent directory exists

#### Git Operations Don't Work

**Symptoms:** Git commands fail or Git not detected

**Solutions:**

1. Install Git plugin: `Plugin View > Git > Install`
2. Verify Git is in path: `Settings > Plugins > Git Path`
3. Configure Git user: `Settings > Git > User Name/Email`
4. Check project has `.git` folder

### Getting Logs

Application logs are stored at: `D:\pyMM.Logs\pymediamanager.log`

**Log Levels:**

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages (non-critical)
- `ERROR`: Error messages (operation failed)
- `CRITICAL`: Critical errors (application failure)

**Change Log Level:**

```python
# In config/user.yaml
logging:
  level: DEBUG  # or INFO, WARNING, ERROR
```

### Performance Issues

**Slow Application Start:**

- Check antivirus (may scan Python files)
- Move to faster drive (USB 3.0+, SSD)
- Reduce plugin count

**Plugin Download Slow:**

- Check internet speed
- Try different network
- Download manually and extract

**Project Operations Slow:**

- Move project to faster drive
- Check disk space
- Reduce project size (archive old files)

### Reporting Bugs

If you encounter a bug:

1. **Check logs** for error messages
2. **Reproduce** the issue if possible
3. **Document** steps to reproduce
4. **Collect**:
   - Log file (`pyMM.Logs\pymediamanager.log`)
   - Settings file (if relevant)
   - Screenshot of error
5. **Report** on GitHub Issues

---

## Keyboard Shortcuts

|Action|Shortcut|
|---|---|
|New Project|`Ctrl+N`|
|Open Settings|`Ctrl+,`|
|Plugin View|`Ctrl+P`|
|Project View|`Ctrl+1`|
|Storage View|`Ctrl+2`|
|Refresh View|`F5`|
|Quit Application|`Ctrl+Q`|

---

## Support & Resources

- **Documentation:** [GitHub Docs](https://github.com/mosh666/pyMM/tree/main/docs)
- **Issues:** [Report Bugs](https://github.com/mosh666/pyMM/issues/new?template=bug_report.yml)
- **Feature Requests:** [Request Features](https://github.com/mosh666/pyMM/issues/new?template=feature_request.yml)
- **Discussions:** [Community Forum](https://github.com/mosh666/pyMM/discussions)
- **Test Suite:** 193 tests with 73% coverage ensuring reliability and stability
- **Changelog:** [Version History](../CHANGELOG.md)
- **Security:** [Security Policy](../.github/SECURITY.md)

---

## Tips & Tricks

**Power User Tips:**

1. **Batch Plugin Install:** Select multiple plugins, click "Install All"
2. **Custom Templates:** Create project templates in `config/templates/`
3. **Portable Backups:** Copy entire `pyMM` folder for instant backup
4. **Git Remotes:** Add remote repos for cloud backup (GitHub, GitLab)
5. **Keyboard Navigation:** Most actions have keyboard shortcuts

**Workflow Optimization:**

- Use Git for all projects (easy rollback)
- Organize projects by date or client
- Keep plugins updated
- Regular log cleanup (auto-rotates at 10MB)
- Export settings for team sharing

---

Happy media managing! 🎬📸🎵
