# pyMediaManager User Guide

**Version:** Auto-detected from Git  
**Last Updated:** January 4, 2026

> **See also:** [CHANGELOG.md](../CHANGELOG.md) for detailed version history and new features

## Table of Contents

1. [Getting Started](#getting-started)
2. [First-Time Setup](#first-time-setup)
3. [Project Management](#project-management)
4. [Plugin Management](#plugin-management)
5. [Storage & Portability](#storage--portability)
6. [Git Integration](#git-integration)
7. [Settings & Configuration](#settings--configuration)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### System Requirements

- **Operating System:** Windows 10/11 (64-bit)
- **Storage:** Minimum 500MB free space (more for plugins and projects)
- **Recommended:** USB 3.0+ or SSD for portable installation

### Installation

pyMediaManager is designed to be fully portable with no system installation required:

1. **Download** the latest release (ZIP archive)
2. **Extract** to your desired location:
   - USB drive: `E:\pyMM\`
   - External SSD: `D:\pyMM\`
   - Local drive: `C:\Apps\pyMM\`
3. **Run** `launcher.py` to start the application

The application will automatically detect the drive root and configure portable folders.

---

## First-Time Setup

### Initial Launch

When you first launch pyMediaManager, the First Run Wizard will guide you through setup:

1. **Welcome Screen** - Introduction to pyMediaManager
2. **Drive Detection** - Confirms your installation location
3. **Plugin Discovery** - Scans for available plugins
4. **Configuration** - Creates default settings

### Recommended First Steps

1. **Install Core Plugins** (Essential tools):
   - Git - Version control for projects
   - ExifTool - Media metadata extraction
   - FFmpeg - Video processing

2. **Create Your First Project**:
   - Click "New Project" in the toolbar
   - Choose a name and location
   - Optionally initialize Git repository

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
   - **Git:** Check to initialize version control
3. Click **"Create"**

**Project Structure:**
```
D:\pyMM.Projects\vacation-2026\
├── .git\              # Git repository (if enabled)
├── .gitignore         # Ignore rules
├── photos\            # Organized media
├── videos\
└── exports\
```

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
```
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
|Git|Mandatory|Version control system|~40MB|
|7-Zip|Mandatory|Archive extraction|~2MB|
|ExifTool|Optional|Metadata extraction|~8MB|
|FFmpeg|Optional|Video/audio processing|~100MB|
|digiKam|Optional|Photo management|~500MB|
|ImageMagick|Optional|Image manipulation|~30MB|
|HandBrake|Optional|Video transcoding|~20MB|
|MKVToolNix|Optional|MKV tools|~35MB|
|MediaInfo|Optional|Media file analysis|~5MB|

---

## Storage & Portability

### Portable Folders

pyMediaManager uses drive-root folders for maximum portability:

```
D:\                              # Your drive root
├── pyMM\                        # Application (movable)
├── pyMM.Projects\               # Your projects
├── pyMM.Plugins\                # Installed tools
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
- Use Git for project version control

### Moving Between Drives

pyMediaManager is fully portable:

1. **Copy** entire `pyMM` folder to new drive
2. **Update** shortcuts/launchers if needed
3. **Run** - automatic drive detection on launch
4. Projects and plugins remain accessible

**Note:** If moving projects separately, update project paths in settings.

---

## Git Integration

### Git Repository Basics

Projects can optionally use Git for version control:

- Track all changes to project files
- Commit snapshots with descriptive messages
- View complete history of modifications
- Collaborate with team members

### Using Git

**Initialize Repository:**
- Enable "Initialize Git" when creating project
- Or: `Project > Initialize Git` on existing project

**Check Status:**
```
View > Git Status
```
Shows:
- Modified files (yellow)
- New files (green)
- Deleted files (red)
- Untracked files

**Commit Changes:**

1. Make changes to project files
2. Open Git Status view
3. Review changed files
4. Click **"Commit"**
5. Enter commit message
6. Confirm commit

**View History:**
```
View > Git Log
```
Shows:
- Commit messages
- Author and date
- Files changed per commit

### Git Best Practices

**Good Commit Messages:**
```
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
Default `.gitignore` excludes:
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

#### General Settings

- **Application Name:** Display name
- **Theme:** Light, Dark, or Auto
- **Language:** Interface language
- **Check Updates:** Auto-update checking

#### Plugin Settings

- **Auto-Install:** Install mandatory plugins on first run
- **Download Timeout:** Network timeout (seconds)
- **Verify Checksums:** Enable security verification
- **Plugin Directory:** Custom plugin location

#### Storage Settings

- **Default Drive:** Preferred storage location
- **Project Root:** Where to create new projects
- **Log Location:** Application log directory
- **Max Log Size:** Size before rotation

#### Git Settings

- **User Name:** Your name for commits
- **User Email:** Your email for commits
- **Auto-Initialize:** Create Git repos by default
- **Default Branch:** Branch name (main/master)

#### About

- **Version:** Current application version
- **Commit:** Git commit hash (if available)
- **Application Info:** General application details

### Saving Settings

- Click **"Save"** to apply changes
- Click **"Reset to Defaults"** to undo all changes
- Click **"Cancel"** to discard changes

Settings are stored in:
- System: `config/default.yaml` (read-only)
- User: `D:\pyMM.Config\user.yaml` (your changes)

---

## Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms:** Double-clicking `launcher.py` does nothing

**Solutions:**
1. Check Python is installed: Right-click → "Edit with IDLE"
2. Run from terminal: `python launcher.py`
3. Check logs: `D:\pyMM.Logs\pymediamanager.log`
4. Verify drive permissions (not read-only)

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

- **Documentation:** [https://github.com/mosh666/pyMM/docs](https://github.com/mosh666/pyMM/tree/main/docs)
- **Issues:** [https://github.com/mosh666/pyMM/issues](https://github.com/mosh666/pyMM/issues)
- **Discussions:** [https://github.com/mosh666/pyMM/discussions](https://github.com/mosh666/pyMM/discussions)

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

**Happy media managing! 🎬📸🎵**
