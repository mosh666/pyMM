# pyMediaManager User Guide

<!-- markdownlint-disable MD013 MD033 MD036 MD051 -->

---

## 📖 Table of Contents

- [Introduction](#introduction)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [First Run Setup](#first-run-setup)
- [Core Features](#core-features)
- [Project Management](#project-management)
- [Plugin System](#plugin-system)
- [Storage Management](#storage-management)
- [Configuration](#configuration)
- [Command Line Interface](#command-line-interface)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Getting Help](#getting-help)

---

(introduction)=

## 🎯 Introduction

**pyMediaManager (pyMM)** is a portable, Python-based media management application designed for photographers, videographers, and digital content creators who need a flexible, portable solution for managing media projects across multiple storage devices.

### Key Benefits

- **✨ Truly Portable**: Run from any drive (USB, external HDD, network) without installation
- **🎨 Modern UI**: Beautiful Fluent Design interface powered by PySide6 and QFluentWidgets
- **🔌 Plugin System**: Extensible architecture supporting DigiKam, ExifTool, FFmpeg, and more
- **📦 Project-Based**: Organize media into self-contained portable projects
- **🔒 Secure**: No system modifications, registry changes, or administrative privileges required
- **🚀 Fast**: Native Python 3.13 performance with async operations

### Use Cases

- **Photographers**: Manage photo collections with DigiKam integration
- **Videographers**: Organize video projects with FFmpeg processing
- **Backup Solutions**: Maintain portable media archives across devices
- **Multi-Site Workflows**: Sync projects between office, home, and field locations
- **Education**: Portable labs for teaching media management workflows

---

(system-requirements)=

## 💻 System Requirements

### Minimum Requirements

| Component | Requirement |
| --------- | ----------- |
| **Operating System** | Windows 10 (Version 1809+), Windows 11, Ubuntu 20.04+, Debian 11+, macOS 11+ |
| **Python Version** | 3.12+ (**3.13 recommended** for best performance) |
| **RAM** | 4 GB (8 GB recommended for large projects) |
| **Storage** | 200 MB for application + space for projects/plugins |
| **Display** | 1280×720 minimum (1920×1080 recommended) |
| **Graphics** | OpenGL 2.0+ capable GPU |

### Recommended Configuration

- **OS**: Windows 11 with latest updates
- **Python**: 3.13.x (latest stable release)
- **RAM**: 16 GB or more
- **Storage**: SSD for application, HDD for media storage
- **Display**: 1920×1080 or higher resolution
- **GPU**: Dedicated GPU for video processing

### Python Version Notes

```text
✅ Python 3.13 - Recommended (best performance, latest features)
✅ Python 3.12 - Fully supported (stable, production-ready)
✅ Python 3.14 - Supported (early adopter, may have minor issues)
❌ Python 3.11 or earlier - Not supported
```

**Why Python 3.13?**

- 15-20% performance improvements over 3.12
- Native support for modern type hints (`list[T]`, `dict[K, V]`)
- Better async/await performance for plugin operations
- Improved Windows-specific optimizations

---

(installation)=

## 📦 Installation

### Method 1: Standard Installation (Recommended)

#### Step 1: Install Python

```{tabs}
.. tab:: Windows

   1. Download Python 3.13 from `python.org <https://www.python.org/downloads/>`_
   2. Run installer with these options:

      - ✅ "Add Python to PATH"
      - ✅ "Install for all users" (optional)
      - ✅ "Install py launcher"

   3. Verify installation:

      .. code-block:: powershell

         python --version
         # Output: Python 3.13.x

.. tab:: Linux (Ubuntu/Debian)

   .. code-block:: bash

      # Update package list
      sudo apt update

      # Install Python 3.13
      sudo apt install python3.13 python3.13-venv python3.13-dev

      # Verify installation
      python3.13 --version
      # Output: Python 3.13.x

      # Create symlink (optional)
      sudo ln -sf /usr/bin/python3.13 /usr/bin/python

.. tab:: macOS

   .. code-block:: bash

      # Using Homebrew (install from https://brew.sh if needed)
      brew install python@3.13

      # Verify installation
      python3.13 --version
      # Output: Python 3.13.x

      # Create symlink (optional)
      ln -sf /opt/homebrew/bin/python3.13 /usr/local/bin/python
```

#### Step 2: Clone or Download Repository

**Option A: Git Clone (Recommended)**

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Navigate to desired location
      cd D:\

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

.. tab:: Linux

   .. code-block:: bash

      # Navigate to desired location
      cd ~/

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

.. tab:: macOS

   .. code-block:: bash

      # Navigate to desired location
      cd ~/Documents

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM
```

**Option B: Download ZIP**

1. Visit `github.com/mosh666/pyMM <https://github.com/mosh666/pyMM>`_
2. Click "Code" → "Download ZIP"
3. Extract to desired location:
   - Windows: ``D:\pyMM``
   - Linux: ``~/pyMM``
   - macOS: ``~/Documents/pyMM``

#### Step 3: Install Dependencies

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Navigate to pyMM directory
      cd D:\pyMM

      # Install application
      pip install -e .

      # Or install with development tools (optional)
      pip install -e ".[dev]"

.. tab:: Linux

   .. code-block:: bash

      # Navigate to pyMM directory
      cd ~/pyMM

      # Install application
      pip3 install -e .

      # Or install with development tools (optional)
      pip3 install -e ".[dev]"

.. tab:: macOS

   .. code-block:: bash

      # Navigate to pyMM directory
      cd ~/Documents/pyMM

      # Install application
      pip3 install -e .

      # Or install with development tools (optional)
      pip3 install -e ".[dev]"
```

#### Step 4: Run Application

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Launch with Python module
      python -m app

      # Or use the launcher script
      python launcher.py

      # Or use installed command (if PATH configured)
      pymm

.. tab:: Linux

   .. code-block:: bash

      # Launch with Python module
      python3 -m app

      # Or use the launcher script
      python3 launcher.py

      # Or use installed command (if in PATH)
      pymm

.. tab:: macOS

   .. code-block:: bash

      # Launch with Python module
      python3 -m app

      # Or use the launcher script
      python3 launcher.py

      # Or use installed command (if in PATH)
      pymm
```

### Method 2: Portable Installation

For use on USB drives or external storage:

.. note::
   Portable installation is primarily designed for Windows with Python Embeddable Package. Linux/macOS users should use Method 1 or 3 for full functionality.

```{tabs}
.. tab:: Windows

   **Step 1: Portable Python**

   1. Download `Python Embeddable Package <https://www.python.org/downloads/windows/>`_
      - Choose "Windows embeddable package (64-bit)"
   2. Extract to your portable drive (e.g., ``E:\PortablePython``)

   **Step 2: Setup pip for Embeddable Python**

   .. code-block:: powershell

      # Navigate to portable Python directory
      cd E:\PortablePython

      # Download get-pip.py
      Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile get-pip.py

      # Install pip
      .\python.exe get-pip.py

   **Step 3: Install pyMM**

   .. code-block:: powershell

      # Navigate to portable drive
      cd E:\

      # Clone or copy pyMM
      git clone https://github.com/mosh666/pyMM.git

      # Install dependencies
      .\PortablePython\python.exe -m pip install -e .\pyMM

   **Step 4: Create Launch Script**

   Create ``E:\LaunchPyMM.bat``:

   .. code-block:: batch

      @echo off
      set PYTHONPATH=E:\PortablePython
      E:\PortablePython\python.exe E:\pyMM\launcher.py
      pause

   Double-click ``LaunchPyMM.bat`` to run.

.. tab:: Linux

   **Portable Mode with Virtual Environment**

   .. code-block:: bash

      # Navigate to USB drive
      cd /media/$USER/USBDrive

      # Clone pyMM
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Create portable virtual environment
      python3 -m venv --copies .venv

      # Activate and install
      source .venv/bin/activate
      pip install -e .

      # Create launch script
      cat > ../launch-pymm.sh << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/pyMM/.venv/bin/activate"
python -m app
EOF
      chmod +x ../launch-pymm.sh

   Run with: ``./launch-pymm.sh``

.. tab:: macOS

   **Portable Mode with Virtual Environment**

   .. code-block:: bash

      # Navigate to USB drive
      cd /Volumes/USBDrive

      # Clone pyMM
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Create portable virtual environment
      python3 -m venv --copies .venv

      # Activate and install
      source .venv/bin/activate
      pip install -e .

      # Create launch script
      cat > ../launch-pymm.command << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/pyMM/.venv/bin/activate"
python -m app
EOF
      chmod +x ../launch-pymm.command

   Double-click ``launch-pymm.command`` to run.
```

### Method 3: Development Installation

For contributors and developers:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Install in development mode with all tools
      pip install -e ".[dev]"

      # Install pre-commit hooks
      pre-commit install

      # Run tests to verify setup
      pytest

      # Start application
      python launcher.py

.. tab:: Linux

   .. code-block:: bash

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Install in development mode with all tools
      pip3 install -e ".[dev]"

      # Install pre-commit hooks
      pre-commit install

      # Run tests to verify setup
      pytest

      # Start application
      python3 launcher.py

.. tab:: macOS

   .. code-block:: bash

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Install in development mode with all tools
      pip3 install -e ".[dev]"

      # Install pre-commit hooks
      pre-commit install

      # Run tests to verify setup
      pytest

      # Start application
      python3 launcher.py
```

.. seealso::
   For detailed developer setup including VS Code configuration, debugging, and testing workflows, see :doc:`getting-started-dev`.

---

(first-run-setup)=

## 🚀 First Run Setup

### Initial Launch

When you first run pyMM, the **First Run Wizard** guides you through essential configuration:

#### Step 1: Welcome Screen

- Introduction to pyMM features
- Links to documentation and tutorials
- Privacy and data handling information

#### Step 2: Drive Selection

```text
Select Application Drive:
┌─────────────────────────────────────┐
│ ○ C:\ - Local Disk (NTFS)          │
│   Free: 250 GB / Total: 500 GB      │
│                                     │
│ ● D:\ - Data Drive (NTFS)          │
│   Free: 1.5 TB / Total: 2 TB        │
│   ✅ Recommended for large projects │
│                                     │
│ ○ E:\ - External USB (exFAT)       │
│   Free: 100 GB / Total: 500 GB      │
│   ⚠️  Slower performance expected    │
└─────────────────────────────────────┘
```

**Drive Selection Tips:**

- ✅ Choose drives with sufficient free space (≥10 GB recommended)
- ✅ NTFS preferred for Windows (supports large files, permissions)
- ⚠️ exFAT works but may have performance limitations
- ⚠️ Network drives supported but may be slower

#### Step 3: Folder Structure Creation

pyMM creates portable folder structure:

```text
D:\pyMM.Projects\       # Project storage
D:\pyMM.Logs\           # Application logs
D:\pyMM.Plugins\        # Downloaded plugins
D:\pyMM.Config\         # Configuration files
```

**Portability Note**: If you move pyMM to another drive, these folders automatically relocate.

#### Step 4: Plugin Configuration

Select plugins to download and configure:

```text
Available Plugins:
┌──────────────────────────────────────────┐
│ ☑ DigiKam             [Photo Management] │
│   Latest: 8.2.0       Size: 450 MB       │
│                                          │
│ ☑ ExifTool            [Metadata Tool]    │
│   Latest: 12.70       Size: 12 MB        │
│                                          │
│ ☐ FFmpeg              [Video Processing] │
│   Latest: 6.1         Size: 120 MB       │
│                                          │
│ ☐ Git                 [Version Control]  │
│   Latest: 2.43.0      Size: 85 MB        │
└──────────────────────────────────────────┘

Total Download Size: 462 MB
Estimated Time: ~5 minutes (10 Mbps)
```

#### Step 5: Initial Configuration

Configure basic settings:

- **Language**: English (more languages planned)
- **Theme**: Light, Dark, Auto (follows system)
- **Default Project Location**: `D:\pyMM.Projects`
- **Auto-Update Plugins**: Enabled (recommended)
- **Telemetry**: Disabled by default (respects privacy)

#### Step 6: Complete Setup

- Summary of configuration
- Launch application button
- Quick start tutorial link

### Linux-Specific Setup: USB Device Detection

**Linux users only:** pyMM can automatically detect USB storage devices using udev rules.

#### What are udev rules?

udev rules enable automatic detection of USB devices without requiring the application to run as root. This provides better security and integration with your Linux desktop.

#### Installing udev Rules

**Option 1: Using the GUI (Recommended)**

1. Go to **⚙️ Settings** → **Linux udev Rules**
2. Click **"Install udev Rules"**
3. Enter your password when prompted (pkexec authentication)
4. Wait for confirmation: "udev rules installed successfully"
5. Rules take effect immediately (no reboot required)

**Option 2: Using Command Line**

```bash
# Install udev rules
pymm install-udev-rules

# Check installation status
pymm check-udev-rules

# Uninstall if needed
pymm uninstall-udev-rules
```

#### What Gets Installed

The installer creates `/etc/udev/rules.d/99-pymm-usb.rules` with:

```udev
# pyMediaManager USB Storage Detection Rules
# Detects USB storage devices and notifies pyMM

# USB Mass Storage devices
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", \
  ENV{ID_TYPE}=="disk", \
  RUN+="/usr/bin/notify-send 'pyMediaManager' 'USB Storage Detected: %E{ID_MODEL}'"

# Trigger udev to reload
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", \
  RUN+="/usr/bin/udevadm control --reload-rules"
```

**Security Notes:**

- Rules run as root but only execute predefined safe commands
- pyMM itself does NOT run as root
- Uses `pkexec` for privilege escalation (same as system settings)
- Rules are read-only after installation

#### Checking Installation Status

From the GUI, go to **⚙️ Settings** → **Linux udev Rules**:

```text
┌─────────────────────────────────────────┐
│ Linux udev Rules Status                 │
├─────────────────────────────────────────┤
│ Status: ✓ Installed                     │
│ Location: /etc/udev/rules.d/            │
│          99-pymm-usb.rules              │
│                                         │
│ Rule Version: 1.0.0                     │
│ Last Modified: 2026-01-15 10:30:25      │
│                                         │
│ Capabilities:                           │
│ ✓ USB mass storage detection            │
│ ✓ Desktop notifications                 │
│ ✓ Automatic device discovery            │
│                                         │
│ [ Reinstall ] [ Uninstall ] [ Close ]  │
└─────────────────────────────────────────┘
```

#### Uninstalling

If you no longer need USB device detection:

1. Go to **⚙️ Settings** → **Linux udev Rules**
2. Click **"Uninstall"**
3. Enter your password when prompted
4. Rules are removed immediately

**Note:** pyMM continues to work without udev rules, but you'll need to manually refresh storage devices.

#### Troubleshooting

**Rules not working after installation:**

```bash
# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Check if rules file exists
ls -l /etc/udev/rules.d/99-pymm-usb.rules

# Test rule syntax
sudo udevadm test /sys/block/sda
```

**Permission denied during installation:**

- Ensure you're in the `wheel` or `sudo` group
- Check pkexec is installed: `which pkexec`
- Try manual installation:

  ```bash
  sudo cp config/99-pymm-usb.rules /etc/udev/rules.d/
  sudo chmod 644 /etc/udev/rules.d/99-pymm-usb.rules
  sudo udevadm control --reload-rules
  ```

For more details, see [Linux udev Rules Documentation](linux-udev-installer.md).

---

(core-features)=

## ✨ Core Features

### Modern Fluent UI

pyMM features a beautiful, modern interface inspired by Windows 11 Fluent Design:

- **Acrylic Effects**: Translucent backgrounds with blur
- **Smooth Animations**: Fluid transitions and interactions
- **Dark/Light Themes**: Automatic or manual theme switching
- **Responsive Design**: Adapts to different screen sizes
- **Keyboard Shortcuts**: Efficient navigation and actions

### Dashboard Overview

```text
┌────────────────────────────────────────────────────────┐
│  pyMediaManager                    🔍 Search  ⚙️ Settings │
├────────────────────────────────────────────────────────┤
│  📊 Dashboard                                          │
│                                                        │
│  Quick Stats:                                          │
│  ┌───────────┬───────────┬───────────┬───────────┐    │
│  │ Projects  │  Storage  │  Plugins  │   Health  │    │
│  │    12     │  1.2 TB   │     8     │    98%    │    │
│  └───────────┴───────────┴───────────┴───────────┘    │
│                                                        │
│  Recent Projects:                                      │
│  📁 Wedding_2026         Last accessed: 2 hours ago   │
│  📁 Client_Portfolio     Last accessed: Yesterday     │
│  📁 Backup_Archive       Last accessed: 3 days ago    │
│                                                        │
│  Quick Actions:                                        │
│  [+ New Project]  [📥 Import]  [🔌 Manage Plugins]    │
└────────────────────────────────────────────────────────┘
```

### Navigation

- **Sidebar**: Primary navigation (Projects, Plugins, Storage, Settings)
- **Top Bar**: Search, notifications, user profile, quick actions
- **Breadcrumbs**: Current location and navigation history
- **Tab System**: Multiple projects/views open simultaneously

---

(project-management)=

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

(plugin-system)=

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

## ⚙️ Configuration

### Application Settings

Access via **⚙️ Settings** button or `Ctrl+,`:

#### General Settings

```text
General
┌─────────────────────────────────────────┐
│ Language: English                       │
│ Theme: Auto (follows system)            │
│ ○ Light  ○ Dark  ● Auto                 │
│                                         │
│ Startup:                                │
│ ☑ Launch on Windows startup             │
│ ☑ Restore last session                  │
│ ☐ Check for updates on startup          │
│                                         │
│ Default Locations:                      │
│ Projects: D:\pyMM.Projects              │
│ [Browse]                                │
│                                         │
│ Plugins: D:\pyMM.Plugins                │
│ [Browse]                                │
└─────────────────────────────────────────┘
```

#### Performance Settings

```text
Performance
┌─────────────────────────────────────────┐
│ Processing:                             │
│ Thread Pool Size: Auto (8 threads)      │
│ Max Memory Usage: 4096 MB               │
│                                         │
│ Cache:                                  │
│ Thumbnail Cache: 512 MB                 │
│ ☑ Preload thumbnails                    │
│ ☑ Cache metadata                        │
│                                         │
│ Network:                                │
│ Download Threads: 4                     │
│ Connection Timeout: 30 seconds          │
└─────────────────────────────────────────┘
```

#### Privacy Settings

```text
Privacy
┌─────────────────────────────────────────┐
│ Data Collection:                        │
│ ☐ Send anonymous usage statistics       │
│ ☐ Send crash reports                    │
│                                         │
│ Logging:                                │
│ Log Level: INFO                         │
│ ☑ Log to file                           │
│ ☐ Enable debug logging                  │
│                                         │
│ Auto-Save:                              │
│ ☑ Auto-save project changes             │
│ Save interval: 5 minutes                │
└─────────────────────────────────────────┘
```

### Configuration Files

pyMM stores configuration in platform-specific standard directories:

#### Platform-Specific Locations

**Windows:**

```text
Config:  %APPDATA%\pyMM\config\
Data:    %APPDATA%\pyMM\data\
Cache:   %LOCALAPPDATA%\pyMM\cache\
Logs:    %APPDATA%\pyMM\logs\

Example: C:\Users\YourName\AppData\Roaming\pyMM\
```

**Linux (XDG Base Directory):**

```text
Config:  $XDG_CONFIG_HOME/pyMM/  (default: ~/.config/pyMM/)
Data:    $XDG_DATA_HOME/pyMM/    (default: ~/.local/share/pyMM/)
Cache:   $XDG_CACHE_HOME/pyMM/   (default: ~/.cache/pyMM/)
Logs:    $XDG_STATE_HOME/pyMM/   (default: ~/.local/state/pyMM/)

Example: /home/username/.config/pyMM/
```

**macOS:**

```text
Config:  ~/Library/Application Support/pyMM/config/
Data:    ~/Library/Application Support/pyMM/data/
Cache:   ~/Library/Caches/pyMM/
Logs:    ~/Library/Logs/pyMM/

Example: /Users/YourName/Library/Application Support/pyMM/
```

#### Application Config (`app.yaml`)

**Location:** `{config_dir}/app.yaml`

```yaml
# Application-wide configuration
version: "1.0.0"

general:
  language: "en"
  theme: "auto"
  startup:
    launch_on_boot: true
    restore_session: true
    check_updates: false

paths:
  projects: "D:\\pyMM.Projects"
  plugins: "D:\\pyMM.Plugins"
  logs: "D:\\pyMM.Logs"
  config: "D:\\pyMM.Config"

performance:
  max_threads: 8
  max_memory_mb: 4096
  cache_size_mb: 512
  preload_thumbnails: true

network:
  download_threads: 4
  timeout_seconds: 30
  retry_attempts: 3
```

#### User Config (`D:\pyMM.Config\user.yaml`)

```yaml
# User-specific preferences
user:
  name: "User"
  email: "user@example.com"

ui:
  window:
    width: 1280
    height: 720
    maximized: false
  recent_projects:
    - "D:\\pyMM.Projects\\Client_Wedding_2026"
    - "D:\\pyMM.Projects\\Video_Project_Jan2026"
  sidebar_width: 250

privacy:
  telemetry_enabled: false
  crash_reports_enabled: false
  log_level: "INFO"
```

---

(command-line-interface)=

## 💻 Command Line Interface

pyMM provides a powerful CLI for automation and scripting:

### Basic Commands

```powershell
# Show version
pymm --version

# Show help
pymm --help

# Launch GUI
pymm

# Run in console mode (no GUI)
pymm --console
```

### Project Commands

```powershell
# Create new project
pymm create-project "MyProject" --type photo --location "D:\pyMM.Projects"

# Open project
pymm open-project "D:\pyMM.Projects\MyProject"

# List all projects
pymm list-projects

# Archive project
pymm archive-project "MyProject" --output "D:\Archives" --format 7z

# Delete project
pymm delete-project "MyProject" --confirm
```

### Plugin Commands

```powershell
# List available plugins
pymm list-plugins

# Install plugin
pymm install-plugin digikam

# Update plugin
pymm update-plugin digikam

# Remove plugin
pymm remove-plugin digikam --purge

# Show plugin info
pymm plugin-info digikam
```

### Storage Commands

```powershell
# Show storage usage
pymm storage-info

# Clean up temporary files
pymm cleanup --temp --logs --cache

# Move project to different drive
pymm move-project "MyProject" --destination "E:\pyMM.Projects"
```

### Advanced Commands

```powershell
# Export project metadata
pymm export-metadata "MyProject" --output "metadata.json"

# Import project from archive
pymm import-project "archive.7z" --destination "D:\pyMM.Projects"

# Run maintenance tasks
pymm maintenance --verify-integrity --optimize-db --rebuild-cache

# Generate project report
pymm generate-report "MyProject" --format pdf --output "report.pdf"
```

---

(troubleshooting)=

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms**: Double-clicking launcher does nothing or shows error.

**Solutions**:

1. **Verify Python installation**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         python --version
         # Should show Python 3.12+ or 3.13+

   .. tab:: Linux

      .. code-block:: bash

         python3 --version
         # Should show Python 3.12+ or 3.13+

   .. tab:: macOS

      .. code-block:: bash

         python3 --version
         # Should show Python 3.12+ or 3.13+
   ```

2. **Check dependencies**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pip list | Select-String PySide6
         # Should show PySide6 6.6.0 or higher

   .. tab:: Linux

      .. code-block:: bash

         pip3 list | grep PySide6
         # Should show PySide6 6.6.0 or higher

   .. tab:: macOS

      .. code-block:: bash

         pip3 list | grep PySide6
         # Should show PySide6 6.6.0 or higher
   ```

3. **Reinstall dependencies**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pip install --force-reinstall -e .

   .. tab:: Linux

      .. code-block:: bash

         pip3 install --force-reinstall -e .

   .. tab:: macOS

      .. code-block:: bash

         pip3 install --force-reinstall -e .
   ```

4. **Check logs**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         # View latest log file
         Get-Content "D:\pyMM.Logs\pymm_*.log" -Tail 50

         # Or view in Notepad
         notepad "D:\pyMM.Logs\pymm_$(Get-Date -Format 'yyyy-MM-dd').log"

   .. tab:: Linux

      .. code-block:: bash

         # View latest log file
         tail -n 50 ~/pyMM.Logs/pymm_*.log

         # Or follow live
         tail -f ~/pyMM.Logs/pymm_$(date +%Y-%m-%d).log

   .. tab:: macOS

      .. code-block:: bash

         # View latest log file
         tail -n 50 ~/Library/Logs/pyMM/pymm_*.log

         # Or follow live
         tail -f ~/Library/Logs/pyMM/pymm_$(date +%Y-%m-%d).log
   ```

#### Projects Not Loading

**Symptoms**: Projects appear in list but won't open.

**Solutions**:

1. **Verify project integrity**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm verify-project "D:\pyMM.Projects\MyProject"

   .. tab:: Linux

      .. code-block:: bash

         pymm verify-project "~/pyMM.Projects/MyProject"

   .. tab:: macOS

      .. code-block:: bash

         pymm verify-project "~/Documents/pyMM.Projects/MyProject"
   ```

2. **Check permissions**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         # Ensure you have read/write access
         Test-Path -Path "D:\pyMM.Projects\MyProject" -PathType Container

         # Check file permissions
         icacls "D:\pyMM.Projects\MyProject"

   .. tab:: Linux

      .. code-block:: bash

         # Check if directory exists and is writable
         test -w ~/pyMM.Projects/MyProject && echo "Writable" || echo "Not writable"

         # Check permissions
         ls -ld ~/pyMM.Projects/MyProject

   .. tab:: macOS

      .. code-block:: bash

         # Check if directory exists and is writable
         test -w ~/Documents/pyMM.Projects/MyProject && echo "Writable" || echo "Not writable"

         # Check permissions
         ls -ld ~/Documents/pyMM.Projects/MyProject
   ```

3. **Repair project**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm repair-project "MyProject"

   .. tab:: Linux

      .. code-block:: bash

         pymm repair-project "MyProject"

   .. tab:: macOS

      .. code-block:: bash

         pymm repair-project "MyProject"
   ```

#### Plugin Download Fails

**Symptoms**: Plugin download stalls or shows error.

**Solutions**:

1. **Check internet connection**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         Test-Connection -ComputerName github.com -Count 4

         # Alternative with curl
         curl -I https://github.com

   .. tab:: Linux

      .. code-block:: bash

         # Ping GitHub
         ping -c 4 github.com

         # Check HTTP connectivity
         curl -I https://github.com

   .. tab:: macOS

      .. code-block:: bash

         # Ping GitHub
         ping -c 4 github.com

         # Check HTTP connectivity
         curl -I https://github.com
   ```

2. **Try manual download**:

   - Visit plugin's GitHub releases page
   - Download manually
   - Extract to platform-specific location:

     - Windows: ``D:\pyMM.Plugins\<plugin_name>``
     - Linux: ``~/pyMM.Plugins/<plugin_name>``
     - macOS: ``~/Library/Application Support/pyMM/Plugins/<plugin_name>``

3. **Clear download cache**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm cleanup --download-cache

   .. tab:: Linux

      .. code-block:: bash

         pymm cleanup --download-cache

   .. tab:: macOS

      .. code-block:: bash

         pymm cleanup --download-cache
   ```

#### Performance Issues

**Symptoms**: Application is slow or unresponsive.

**Solutions**:

1. **Increase memory limit**:
   - Settings → Performance → Max Memory: 8192 MB

2. **Disable thumbnail preloading**:
   - Settings → Performance → ☐ Preload thumbnails

3. **Reduce thread count**:
   - Settings → Performance → Thread Pool: 4 threads

4. **Move to faster storage**:
   - Use SSD instead of HDD for application and projects

#### Git Integration Issues

**Symptoms**: Git operations fail or show errors.

**Solutions**:

1. **Verify Git installation**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         where.exe git

   .. tab:: Linux

      .. code-block:: bash

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         which git

   .. tab:: macOS

      .. code-block:: bash

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         which git
   ```

2. **Initialize repository manually**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         cd "D:\pyMM.Projects\MyProject"
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"

   .. tab:: Linux

      .. code-block:: bash

         cd ~/pyMM.Projects/MyProject
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"

   .. tab:: macOS

      .. code-block:: bash

         cd ~/Documents/pyMM.Projects/MyProject
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"
   ```

3. **Check Git status**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         cd "D:\pyMM.Projects\MyProject"
         git status

   .. tab:: Linux

      .. code-block:: bash

         cd ~/pyMM.Projects/MyProject
         git status

   .. tab:: macOS

      .. code-block:: bash

         cd ~/Documents/pyMM.Projects/MyProject
         git status
   ```

### Error Messages

| Error | Cause | Solution |
| ----- | ----- | -------- |
| `PermissionError: [Errno 13]` | Insufficient permissions | Run as administrator or check folder permissions |
| `ModuleNotFoundError: 'PySide6'` | Dependencies not installed | Run `pip install -e .` |
| `FileNotFoundError: config.yaml` | Missing configuration | Run first-time setup wizard |
| `OSError: [WinError 145]` | File in use | Close all applications using the file |
| `ConnectionError: github.com` | No internet connection | Check network connection and firewall |

### Debug Mode

Enable detailed logging for troubleshooting:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Launch with debug logging
      pymm --debug

      # Or set in config (D:\pyMM.Config\app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      $env:PYMM_LOG_LEVEL="DEBUG"; pymm

.. tab:: Linux

   .. code-block:: bash

      # Launch with debug logging
      pymm --debug

      # Or set in config (~/.config/pyMM/app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      PYMM_LOG_LEVEL=DEBUG pymm

.. tab:: macOS

   .. code-block:: bash

      # Launch with debug logging
      pymm --debug

      # Or set in config (~/Library/Application Support/pyMM/app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      PYMM_LOG_LEVEL=DEBUG pymm
```

### Collecting Diagnostic Information

When reporting issues, collect this information:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # System information
      python --version
      pip list | Select-String "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      Get-Content "D:\pyMM.Logs\pymm_*.log" -Tail 100 | Out-File "diagnostic.txt"

      # System details
      systeminfo | Select-String "OS Name|OS Version|System Type"

.. tab:: Linux

   .. code-block:: bash

      # System information
      python3 --version
      pip3 list | grep -E "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      tail -n 100 ~/.local/share/pyMM/Logs/pymm_*.log > diagnostic.txt

      # System details
      uname -a
      lsb_release -a

.. tab:: macOS

   .. code-block:: bash

      # System information
      python3 --version
      pip3 list | grep -E "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      tail -n 100 ~/Library/Logs/pyMM/pymm_*.log > diagnostic.txt

      # System details
      uname -a
      sw_vers
```

---

(faq)=

## ❓ FAQ

### General

**Q: Is pyMM free?**
A: Yes! pyMM is open-source software licensed under MIT. Free to use, modify, and distribute.

**Q: Does pyMM require internet connection?**
A: Only for initial plugin downloads and updates. Once installed, pyMM works completely offline.

**Q: Can I run pyMM on macOS or Linux?**
A: Yes! pyMM runs on Windows 10+, Windows 11, Ubuntu 20.04+, Debian 11+, and macOS 11+. Configuration directories follow platform standards (XDG Base Directory on Linux, ~/Library on macOS, %APPDATA% on Windows).

**Q: How much storage does pyMM need?**
A: ~200 MB for application. Plugins vary (12 MB - 450 MB each). Projects depend on your media.

### Projects

**Q: Can I share projects with others?**
A: Yes! Archive projects and share the archive file. Recipients extract and open in their pyMM.

**Q: What happens if I move pyMM to another drive?**
A: pyMM is fully portable. Move the entire `D:\pyMM` folder to any drive and run.

**Q: Can I have projects on multiple drives?**
A: Yes! Configure project location per-project. Mix local, external, and network drives.

**Q: How do I backup projects?**
A: Use built-in archive feature or copy project folders manually. Git integration provides version history.

### Plugins

**Q: Are plugins safe?**
A: All official plugins are verified and downloaded from trusted sources (GitHub, official websites).

**Q: Can I use my existing DigiKam database?**
A: Yes! Configure DigiKam plugin to point to your existing database location.

**Q: Why are some plugins so large?**
A: Plugins include full applications (DigiKam, FFmpeg) for portability. No system installation needed.

**Q: Can I create custom plugins?**
A: Yes! See [Plugin Development Guide](plugin-development.md) for instructions.

### Performance

**Q: Why is pyMM slow on my USB drive?**
A: USB 2.0 drives are slow. Use USB 3.0+ or move application to faster storage.

**Q: Can I use SSD for application and HDD for media?**
A: Yes! Install pyMM on SSD (`C:\pyMM`), configure project location on HDD (`D:\pyMM.Projects`).

**Q: How much RAM does pyMM use?**
A: Typically 200-500 MB idle, up to 2-4 GB when processing large projects.

---

(getting-help)=

## 🆘 Getting Help

### Documentation

- **README**: [README.md](https://github.com/mosh666/pyMM/blob/main/README.md) - Quick start and overview
- **Contributing**: [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) - Development guide
- **Architecture**: [docs/architecture.md](architecture.md) - Technical details
- **Plugin Development**: [docs/plugin-development.md](plugin-development.md) - Create plugins
- **Changelog**: [CHANGELOG.md](https://github.com/mosh666/pyMM/blob/main/CHANGELOG.md) - Version history

### Community & Support

- **GitHub Issues**: <https://github.com/mosh666/pyMM/issues>
  - Report bugs
  - Request features
  - Ask technical questions

- **Email Support**: <24556349+mosh666@users.noreply.github.com>
  - Security issues (private)
  - Commercial inquiries
  - Partnership opportunities

### Contributing

Want to help improve pyMM? We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) for detailed guidelines.

### Security

Found a security vulnerability?

**Do not create a public issue.** Report privately to:
<24556349+mosh666@users.noreply.github.com>

See [SECURITY.md](https://github.com/mosh666/pyMM/blob/main/.github/SECURITY.md) for our security policy.

---

<div align="center">

**pyMediaManager** | **Version**: 0.0.0-dev | **Python**: 3.12+ (3.13 recommended) | **License**: MIT

[GitHub](https://github.com/mosh666/pyMM) · [Issues](https://github.com/mosh666/pyMM/issues)

**Made with ❤️ for media professionals**

</div>
