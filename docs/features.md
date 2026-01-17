.. _features:

# Features & Usage

> **Last Updated:** 2026-01-17 21:41 UTC


<!-- markdownlint-disable MD013 MD033 MD036 MD051 -->

This guide covers project management, storage groups (Phase 2 complete with sync engine), plugins, and advanced features.

.. seealso::
   Learn the basics first? See :ref:`getting-started` for UI overview.
   For sync engine details, see :doc:`sync-engine` documentation.
   For code examples, see `docs/examples/ <https://github.com/mosh666/pyMM/tree/main/docs/examples>`_

---

(features-project-management)=

## 📁 Project Management

### Creating Projects

#### Method 1: Project Wizard (Recommended)

1. Click **"+ New Project"** or press `Ctrl+N`
2. **Project Wizard** opens:

   ```text
   Step 1: Project Type
   ┌─────────────────────────────────────┐
   │ ○ Photography Project              │
   │   Optimized for photos, RAW files   │
   │                                     │
   │ ● Video Project                    │
   │   Optimized for video editing       │
   │                                     │
   │ ○ Mixed Media Project              │
   │   Photos, videos, and documents     │
   │                                     │
   │ ○ Backup Archive                   │
   │   Long-term storage and archival    │
   └─────────────────────────────────────┘
   ```

3. **Step 2: Project Details**

   - **Name**: `Client_Wedding_2026`
   - **Location**: `D:\pyMM.Projects\Client_Wedding_2026`
   - **Description**: "Wedding photography for Smith family"
   - **Tags**: `wedding`, `2026`, `client`, `photography`

4. **Step 3: Plugin Selection**

   - Select plugins for this project (DigiKam, ExifTool, etc.)
   - Configure plugin-specific settings

5. **Step 4: Git Integration** (Optional)

   - Initialize Git repository
   - Configure remote repository
   - Set up `.gitignore` for media files

6. **Step 5: Review & Create**

   - Summary of configuration
   - Click **"Create Project"**

#### Method 2: Quick Create

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Command line project creation
      pymm create-project "NewProject" --type photo --location "D:\pyMM.Projects"

      # Or with Python module
      python -m app create-project "NewProject" --type photo

.. tab:: Linux

   .. code-block:: bash

      # Command line project creation
      pymm create-project "NewProject" --type photo --location "~/pyMM.Projects"

      # Or with Python module
      python3 -m app create-project "NewProject" --type photo

.. tab:: macOS

   .. code-block:: bash

      # Command line project creation
      pymm create-project "NewProject" --type photo --location "~/Documents/pyMM.Projects"

      # Or with Python module
      python3 -m app create-project "NewProject" --type photo
```

### Project Structure

Each project maintains this structure:

```text
Client_Wedding_2026/
├── .pymm/                      # Project metadata (hidden)
│   ├── config.yaml            # Project configuration
│   ├── plugins.yaml           # Active plugins
│   └── history.json           # Project history
│
├── Media/                     # Media files
│   ├── RAW/                  # Original RAW files
│   ├── Edited/               # Processed images
│   └── Exports/              # Final exports
│
├── Plugins/                   # Plugin-specific data
│   ├── DigiKam/              # DigiKam database
│   └── ExifTool/             # Metadata logs
│
├── Backups/                  # Automatic backups
├── Logs/                     # Project-specific logs
└── README.md                 # Project documentation
```

### Opening Projects

#### Method 1: Recent Projects

- Dashboard shows 10 most recent projects
- Click project name to open

#### Method 2: Project Browser

1. Click **"📁 Projects"** in sidebar
2. Browse project list:

   ```text
   Projects (12)                          Sort by: Last Modified ▾
   ┌────────────────────────────────────────────────────────────┐
   │ Client_Wedding_2026               Modified: 2 hours ago    │
   │ D:\pyMM.Projects\Client_Wedding_2026                       │
   │ Type: Photography  |  Size: 45 GB  |  Files: 1,234         │
   │ Tags: wedding, 2026, client                                │
   │ [Open] [Properties] [Export] [Archive]                     │
   ├────────────────────────────────────────────────────────────┤
   │ Video_Project_Jan2026             Modified: Yesterday      │
   │ E:\pyMM.Projects\Video_Project_Jan2026                     │
   │ Type: Video  |  Size: 120 GB  |  Files: 345                │
   │ Tags: video, 2026, editing                                 │
   │ [Open] [Properties] [Export] [Archive]                     │
   └────────────────────────────────────────────────────────────┘
   ```

#### Method 3: Command Line

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Open specific project
      pymm open-project "D:\pyMM.Projects\Client_Wedding_2026"

      # Open last used project
      pymm open-project --last

      # List all projects
      pymm list-projects

.. tab:: Linux

   .. code-block:: bash

      # Open specific project
      pymm open-project "~/pyMM.Projects/Client_Wedding_2026"

      # Open last used project
      pymm open-project --last

      # List all projects
      pymm list-projects

.. tab:: macOS

   .. code-block:: bash

      # Open specific project
      pymm open-project "~/Documents/pyMM.Projects/Client_Wedding_2026"

      # Open last used project
      pymm open-project --last

      # List all projects
      pymm list-projects
```

### Project Operations

#### Rename Project

1. Right-click project → **"Rename"**
2. Enter new name
3. pyMM updates all references automatically

#### Move Project

1. Right-click project → **"Move"**
2. Select new location
3. pyMM moves files and updates configuration

**Warning**: Moving large projects may take time. Ensure sufficient space at destination.

#### Archive Project

1. Right-click project → **"Archive"**
2. Choose compression level:
   - **Fast** (ZIP, faster)
   - **Best** (7z, smaller)
3. Select archive location
4. pyMM creates archive and optionally removes original

#### Delete Project

1. Right-click project → **"Delete"**
2. Confirm deletion (irreversible)
3. Options:
   - Delete project folder only (keeps media)
   - Delete everything (complete removal)
   - Move to recycle bin (recoverable)

### Project Properties

View and edit project details:

```text
Project Properties: Client_Wedding_2026
┌─────────────────────────────────────────────┐
│ General                                     │
│ Name: Client_Wedding_2026                  │
│ Type: Photography Project                  │
│ Location: D:\pyMM.Projects\Client_Wedding   │
│ Created: 2026-01-01 10:30 AM               │
│ Modified: 2026-01-07 03:15 PM              │
│                                             │
│ Storage                                     │
│ Total Size: 45.2 GB                        │
│ File Count: 1,234 files                    │
│ Media Files: 1,180 (42.8 GB)              │
│ Other Files: 54 (2.4 GB)                   │
│                                             │
│ Plugins                                     │
│ Active: DigiKam 8.2.0, ExifTool 12.70      │
│ Available: 6 more plugins                  │
│                                             │
│ Git Status                                  │
│ Repository: Initialized                    │
│ Branch: main                               │
│ Commits: 45                                │
│ Uncommitted: 12 files                      │
│                                             │
│ Tags                                        │
│ wedding, 2026, client, photography         │
│                                             │
│ [Save] [Cancel] [Advanced]                │
└─────────────────────────────────────────────┘
```

---

(storage-groups-sync)=

## 🗄️ Storage Groups & Sync

Storage groups enable master/backup drive pairing with **fully implemented** automatic synchronization, providing redundancy and automated backup workflows. All Phase 2 sync features are production-ready. For comprehensive documentation, see the dedicated [Storage Groups Guide](storage-groups.md) and [Sync Engine](sync-engine.md).

### Quick Overview

**Storage Groups** pair a master drive with one or more backup drives, creating a synchronized set for project redundancy:

- **Master Drive**: Primary storage where projects actively reside
- **Backup Drives**: Secondary storage for automatic backups
- **Automatic Sync**: ✅ Real-time or scheduled synchronization (Implemented)
- **Conflict Resolution**: ✅ Handles file changes on both drives (Implemented)
- **Encryption**: ✅ Optional AES-256-GCM encryption for sensitive data (Implemented)
- **Compression**: ✅ GZIP/LZ4 compression support (Implemented)
- **Incremental Backup**: ✅ SQLite-based tracking (Implemented)

### Common Scenarios

1. **Photographer Workflow**: Master on fast SSD, backup on external HDD
2. **Video Editor**: Master on local NVMe, backup on NAS
3. **Multi-Site**: Office master syncs to home backup automatically
4. **Redundancy**: Critical projects automatically backed up in real-time

### Quick Start

1. **Create Storage Group**: `Tools > Storage Groups > New Group`
2. **Select Drives**: Choose master and backup drive(s)
3. **Assign Project**: In project properties, select storage group
4. **Configure Sync**: Choose real-time, scheduled, or manual sync
5. **Monitor**: View sync history and status in project properties

### Sync Features (✅ All Implemented)

- **Real-time Sync**: ✅ Automatic sync when files change (using watchdog)
- **Scheduled Sync**: ✅ Cron-like schedules with APScheduler (daily, hourly, custom intervals)
- **Manual Sync**: ✅ On-demand sync with progress tracking
- **Conflict Resolution**: ✅ Choose newest, manual merge, or skip with visual diff
- **Bandwidth Throttling**: ✅ Token bucket algorithm to limit sync speed (0.1-1000 MB/s)
- **Encryption**: ✅ AES-256-GCM encryption for backup files with password protection
- **Compression**: ✅ GZIP/LZ4 compression to reduce backup size
- **Incremental Backup**: ✅ SQLite-based change tracking (only sync changed files)
- **History Tracking**: ✅ Complete sync operation logs with export to CSV/JSON
- **Parallel Copying**: ✅ Multi-threaded file transfers (2-16 threads)

For detailed configuration, API reference, and troubleshooting, see the [Storage Groups Guide](storage-groups.md) and [Sync Engine Documentation](sync-engine.md).

---

(user-plugin-system)=

## 🔌 Plugin System

### Available Plugins

pyMM supports various media management tools through its plugin system:

| Plugin | Description | Size | Latest Version |
| ------ | ----------- | ---- | -------------- |
| **DigiKam** | Professional photo management | 450 MB | 8.2.0 |
| **ExifTool** | Read/write metadata | 12 MB | 12.70 |
| **FFmpeg** | Video/audio processing | 120 MB | 6.1 |
| **Git** | Version control system | 85 MB | 2.43.0 |
| **Git LFS** | Large file storage for Git | 15 MB | 3.4.1 |
| **GitVersion** | Semantic versioning | 8 MB | 5.12.0 |
| **ImageMagick** | Image manipulation | 65 MB | 7.1.1 |
| **MariaDB** | Database server | 180 MB | 11.2.2 |
| **MKVToolNix** | MKV file tools | 45 MB | 81.0 |

### Installing Plugins

#### Method 1: Plugin Manager UI

1. Click **"🔌 Plugins"** in sidebar
2. Click **"+ Install Plugin"**
3. Select plugin from list
4. Click **"Download & Install"**
5. Monitor progress:

   ```text
   Installing DigiKam 8.2.0
   ┌─────────────────────────────────────────┐
   │ Downloading... █████████░░░ 75%         │
   │ 337 MB / 450 MB                         │
   │ Speed: 8.5 MB/s  |  ETA: 15 seconds     │
   │                                         │
   │ [Cancel Download]                       │
   └─────────────────────────────────────────┘
   ```

#### Method 2: Command Line

```powershell
# Install single plugin
pymm install-plugin digikam

# Install multiple plugins
pymm install-plugin digikam exiftool ffmpeg

# Install specific version
pymm install-plugin digikam --version 8.2.0
```

### Managing Plugins

#### Update Plugins

1. Click **"🔌 Plugins"** → **"Check for Updates"**
2. Select plugins to update
3. Click **"Update Selected"**

#### Configure Plugins

1. Right-click plugin → **"Configure"**
2. Modify settings:

   ```text
   DigiKam Configuration
   ┌─────────────────────────────────────────┐
   │ Paths                                   │
   │ Executable: D:\pyMM.Plugins\DigiKam\... │
   │ Database: [Current Project]/Plugins/... │
   │                                         │
   │ Performance                             │
   │ ☑ Use hardware acceleration             │
   │ ☑ Enable multi-threading                │
   │ Memory Limit: 4096 MB                   │
   │                                         │
   │ Integration                             │
   │ ☑ Auto-launch with project              │
   │ ☐ Sync metadata on save                 │
   │                                         │
   │ [Save] [Restore Defaults] [Cancel]     │
   └─────────────────────────────────────────┘
   ```

#### Plugin Execution Preferences

**New in v2:** Choose between system-installed tools and portable versions.

1. Click **"⚙️ Settings"** → **"Plugin Preferences"**
2. Select plugin from list
3. Configure execution preference:

   ```text
   Plugin Preferences: Git
   ┌─────────────────────────────────────────┐
   │ Execution Source                        │
   │ ○ Auto (Recommended)                    │
   │   Try system first, fallback to portable│
   │                                         │
   │ ○ System Only                           │
   │   Use system-installed Git only         │
   │   System version: 2.43.1                │
   │   Required: ≥2.40.0  ✓ Compatible      │
   │                                         │
   │ ● Portable Only                         │
   │   Use pyMM's portable Git               │
   │   Portable version: 2.47.1              │
   │                                         │
   │ Notes:                                  │
   │ [Using portable for better integration] │
   │                                         │
   │ [Apply] [Reset to Default] [Cancel]    │
   └─────────────────────────────────────────┘
   ```

**Execution Modes:**

- **Auto (Default)**: Tries system-installed tool first, falls back to portable if:
  - System tool not found
  - System version doesn't meet minimum requirements
  - System tool fails to execute
- **System Only**: Only uses system-installed tool. Shows error if unavailable.
- **Portable Only**: Only uses pyMM's portable version. Always downloads if missing.

**Version Validation:**

When using **Auto** or **System Only**, pyMM validates the system tool version:

```text
┌─────────────────────────────────────────┐
│ Version Check: Git                      │
├─────────────────────────────────────────┤
│ System version: 2.35.1                  │
│ Required version: ≥2.40.0               │
│ Status: ⚠ Version too old               │
│                                         │
│ The system-installed version does not   │
│ meet the minimum requirement.           │
│                                         │
│ Choose an action:                       │
│ ○ Use system version anyway (not        │
│   recommended)                          │
│ ● Download portable version (4.2 MB)    │
│ ○ Disable this plugin                   │
│                                         │
│           [ Cancel ]    [ OK ]          │
└─────────────────────────────────────────┘
```

**Platform Support:**

Different plugins have different platform configurations:

| Plugin | Windows | Linux | macOS |
| ------ | ------- | ----- | ----- |
| **Git** | Portable + System | System only | System only |
| **ExifTool** | Portable + System | System only | System only |
| **FFmpeg** | Portable + System | System only | System only |
| **DigiKam** | Portable | System (APT/Flatpak) | System (Homebrew) |
| **MariaDB** | Portable | System (APT) | System (Homebrew) |

See [Plugin Development Guide](plugin-development.md) for technical details.

#### Remove Plugins

1. Right-click plugin → **"Uninstall"**
2. Choose removal option:
   - **Remove Plugin Only**: Keep configuration and data
   - **Complete Removal**: Delete everything
3. Confirm uninstallation

### Plugin Development

Want to create custom plugins? See [Plugin Development Guide](plugin-development.md).

---

(storage-management)=

## 💾 Storage Management

### Storage Overview

Monitor storage across all drives:

```text
Storage Management
┌────────────────────────────────────────────────────────────┐
│ D:\ - Data Drive (NTFS)                                    │
│ ████████████████░░░░░░░░░░░░ 60% Used                      │
│ Used: 1.2 TB  |  Free: 800 GB  |  Total: 2 TB              │
│                                                            │
│ pyMM Usage:                                                │
│ - Projects: 950 GB (12 projects)                           │
│ - Plugins: 1.2 GB (8 plugins)                             │
│ - Logs: 150 MB                                            │
│ - Config: 15 MB                                           │
│                                                            │
│ [Optimize Storage] [Clean Up] [Move Projects]             │
├────────────────────────────────────────────────────────────┤
│ E:\ - Backup Drive (NTFS)                                 │
│ ██████░░░░░░░░░░░░░░░░░░░░ 25% Used                        │
│ Used: 250 GB  |  Free: 750 GB  |  Total: 1 TB             │
│                                                            │
│ pyMM Usage:                                                │
│ - Archived Projects: 245 GB (8 archives)                   │
│ - Backups: 5 GB                                           │
│                                                            │
│ [View Archives] [Create Backup]                           │
└────────────────────────────────────────────────────────────┘
```

### Storage Optimization

#### Clean Up Temporary Files

1. Click **"Optimize Storage"**
2. Select cleanup targets:
   - ☑ Temporary project files
   - ☑ Old plugin versions
   - ☑ Log files older than 30 days
   - ☑ Thumbnail cache
3. Review space to recover: **~2.5 GB**
4. Click **"Clean Up"**

#### Move Projects Between Drives

1. Select project(s)
2. Click **"Move"**
3. Select destination drive
4. pyMM handles the move with progress tracking

---

(configuration)=

---

**Next**: See :ref:`configuration` for detailed configuration options.
