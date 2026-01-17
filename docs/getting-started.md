.. _getting-started:

# Getting Started

> **Last Updated:** January 14, 2026

<!-- markdownlint-disable MD013 MD033 MD036 MD051 -->

This guide covers the core features, user interface, and first-time configuration of pyMediaManager.

.. seealso::
   New to pyMediaManager? Start with :ref:`installation` to set up the application.

---

(quick-configuration-setup)=

## 🚀 Quick Configuration Setup

### First-Time Configuration Workflow

pyMediaManager uses YAML configuration files that can be customized for your environment. Follow these steps for initial setup:

#### Step 1: Copy Configuration Templates

Configuration templates are provided in the `config/` directory with `.example` extensions. Copy them to create your working configuration files:

**Windows (PowerShell)**:

```powershell
# Navigate to pyMM installation directory
cd D:\pyMM  # Or your installation path

# Copy user configuration template
Copy-Item config\user.yaml.example config\user.yaml

# Copy storage groups template (optional, for Storage Groups feature)
Copy-Item config\storage_groups.yaml.example config\storage_groups.yaml
```

**Linux / macOS (Bash)**:

```bash
# Navigate to pyMM installation directory
cd ~/pyMM  # Or your installation path

# Copy user configuration template
cp config/user.yaml.example config/user.yaml

# Copy storage groups template (optional, for Storage Groups feature)
cp config/storage_groups.yaml.example config/storage_groups.yaml
```

> **Note**: The `app.yaml` file contains default application settings and should **not** be edited directly. Use `user.yaml` to override default values.

#### Step 2: Edit User Configuration

Open `config/user.yaml` in your preferred text editor and customize:

**Essential Settings**:

```yaml
# Projects directory - where media projects are stored
paths:
  projects_dir: D:\MyMediaProjects  # Windows
  # projects_dir: /mnt/external/MyMediaProjects  # Linux
  # projects_dir: ~/Documents/MyMediaProjects  # macOS

# User interface preferences
ui:
  theme: auto  # Options: light, dark, auto (system default)
  window:
    width: 1280
    height: 720
    maximized: false

# Logging level for troubleshooting
logging:
  level: INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

**Advanced Settings**:

```yaml
# Plugin configuration
plugins:
  auto_detect: true  # Auto-detect installed system tools
  update_check_interval: 7  # Check for updates every 7 days

# Portable USB drive configuration (for portable installations)
paths:
  projects_dir: pyMM.Projects  # Relative path (portable)
  logs_dir: pyMM.Logs
  plugins_dir: pyMM.Plugins
```

For complete configuration options, see [Configuration Guide](configuration.md).

#### Step 3: Configure Storage Groups (Optional)

If you plan to use the **Storage Groups** feature for Master/Backup drive redundancy:

Open `config/storage_groups.yaml` and add your drive configurations:

```yaml
version: 1
groups:
  - id: "550e8400-e29b-41d4-a716-446655440000"  # Auto-generated UUID
    name: "My Photo Archive"
    created: "2026-01-14T10:00:00"
    modified: "2026-01-14T10:00:00"
    description: "Primary photo storage with backup"

    master_drive:
      serial_number: "ABC123XYZ"  # Find via: wmic diskdrive get SerialNumber (Windows)
      label: "PhotoMaster"         # Volume label
      total_size: 2000000000000    # 2 TB in bytes

    backup_drive:
      serial_number: "XYZ789ABC"
      label: "PhotoBackup"
      total_size: 2000000000000
```

**Finding Drive Information**:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Get drive serial numbers
      wmic diskdrive get SerialNumber, MediaType

      # Get volume labels and sizes
      Get-Volume | Format-Table DriveLetter, FileSystemLabel, Size

.. tab:: Linux

   .. code-block:: bash

      # Get drive serial numbers
      lsblk -o NAME,SERIAL,SIZE

      # Get volume labels
      lsblk -o NAME,LABEL,SIZE

.. tab:: macOS

   .. code-block:: bash

      # Get drive information
      diskutil list
      system_profiler SPUSBDataType | grep -A 10 "Mass Storage"
```

For detailed Storage Groups configuration, see [Storage Groups Guide](storage-groups.md).

#### Step 4: Validate Configuration

Launch pyMediaManager to validate your configuration:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Launch from command line (shows config validation messages)
      python launcher.py

      # Or double-click pyMediaManager.exe (installed version)

.. tab:: Linux

   .. code-block:: bash

      # Launch from command line
      python3 launcher.py

.. tab:: macOS

   .. code-block:: bash

      # Launch from command line
      python3 launcher.py
```

**Configuration Validation Messages**:

- ✅ **"Configuration loaded successfully"** - All settings are valid
- ⚠️ **"Using default configuration"** - No `user.yaml` found, using defaults
- ❌ **"Configuration error: [details]"** - Check YAML syntax or file paths

#### Step 5: First-Run Wizard (Optional)

On first launch, the **First-Run Wizard** guides you through:

1. **Welcome Page** - Introduction and features overview
2. **Storage Configuration** - Choose projects directory location
3. **Storage Groups Setup** - Optionally configure Master/Backup drives
4. **Plugin Selection** - Select plugins to install (DigiKam, ExifTool, etc.)
5. **Completion Summary** - Review configuration and start using pyMM

You can skip the wizard and configure settings manually anytime via the Settings dialog (`Ctrl+,`).

---

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

**Next**: See :ref:`features` for detailed usage guides.
