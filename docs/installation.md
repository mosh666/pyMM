.. _installation:

# Installation & Setup

> **Last Updated:** January 14, 2026

<!-- markdownlint-disable MD013 MD033 MD036 MD051 -->

## 🎯 Introduction

**pyMediaManager (pyMM)** is a portable, Python-based media management application designed for photographers, videographers, and digital content creators who need a flexible, portable solution for managing media projects across multiple storage devices.

### Key Benefits

- **✨ Truly Portable**: Run from any drive (USB, external HDD, network) without installation
- **🎨 Modern UI**: Beautiful Fluent Design interface powered by PySide6 and QFluentWidgets
- **🔌 Plugin System**: Extensible architecture supporting DigiKam, ExifTool, FFmpeg, and more
- **📦 Project-Based**: Organize media into self-contained portable projects
- **�️ Storage Groups**: Master/backup drive pairing with automatic synchronization
- **🔄 Advanced Sync**: Real-time and scheduled sync with encryption and conflict resolution
- **�🔒 Secure**: No system modifications, registry changes, or administrative privileges required
- **🚀 Fast**: Native Python 3.13 performance with async operations

### Use Cases

- **Photographers**: Manage photo collections with DigiKam integration
- **Videographers**: Organize video projects with FFmpeg processing
- **Backup Solutions**: Maintain portable media archives with automated sync across devices
- **Multi-Site Workflows**: Sync projects between office, home, and field locations with storage groups
- **Dual-Drive Redundancy**: Automatic master/backup synchronization with conflict resolution
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
✅ Python 3.13 - Recommended (best performance, latest features, MSI installer)
✅ Python 3.12 - Fully supported (stable, production-ready)
✅ Python 3.14 - Fully supported (stable since October 2024, all platforms)
❌ Python 3.11 or earlier - Not supported
```

**Why Python 3.13?**

- Windows MSI installer available for seamless desktop integration
- 15-20% performance improvements over 3.12
- Native support for modern type hints (`list[T]`, `dict[K, V]`)
- Better async/await performance for plugin operations
- Improved Windows-specific optimizations
- All 193 tests passing with 73% coverage

---

(migrating-from-pip)=

## 🔄 Migrating from pip to UV

If you're upgrading from an older version of pyMediaManager (pre-v0.2.0), the project has **completely migrated from pip to UV** as of January 2026.

### What Changed?

- **Package Manager:** pip → **UV** (10-100x faster)
- **Build Backend:** setuptools → **Hatchling** (PEP 517 compliant)
- **Versioning:** manual → **hatch-vcs** (dynamic from git tags)
- **Lockfile:** requirements.txt → **uv.lock** (reproducible builds)

### Installing UV

**UV** is required for development and from-source installations. Portable distributions include a bundled UV executable.

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Install UV
      powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

      # Verify installation
      uv --version

.. tab:: Linux/macOS

   .. code-block:: bash

      # Install UV
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Verify installation
      uv --version
```

### Migration Steps

**For Development Environments:**

1. **Remove old virtual environment:**

   ```bash
   # Delete existing venv
   rm -rf .venv
   ```

2. **Install UV** (see above)

3. **Reinstall dependencies with UV:**

   ```bash
   # Create new environment and install dependencies
   uv sync --all-extras

   # Verify installation
   uv run pytest
   ```

**For Portable Installations:**

Portable ZIP distributions **already include UV** bundled in `bin/uv.exe` (Windows) or `bin/uv` (Linux/macOS). No additional installation needed.

### Key Differences

| Operation | pip (old) | UV (new) |
| --------- | --------- | -------- |
| Install dependencies | `pip install -e .[dev]` | `uv sync --all-extras` |
| Add package | `pip install <pkg>` | `uv add <pkg>` |
| Update deps | `pip install --upgrade -r requirements.txt` | `uv lock --upgrade` |
| Install from lock | `pip install -r requirements.txt` | `uv sync --frozen` |
| Run command | `python script.py` | `uv run python script.py` |
| Speed | Baseline | **10-100x faster** |

### UV Benefits

- **⚡ Speed:** Installs dependencies 10-100x faster than pip
- **🔒 Reproducible:** `uv.lock` ensures consistent builds across machines
- **📦 Caching:** Aggressive caching reduces re-download times
- **🔍 Resolution:** Better dependency conflict resolution
- **🌐 Compatibility:** Works with existing `pyproject.toml`

### Troubleshooting

**UV not found after installation:**

Restart your terminal or reload PATH:

```bash
# Windows PowerShell
$env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")

# Linux/macOS
source ~/.bashrc  # or ~/.zshrc
```

**Dependency conflicts:**

```bash
# Clear UV cache and retry
uv cache clean
uv sync --all-extras
```

**Need pip compatibility?**

UV provides pip-compatible commands:

```bash
# Use UV's pip interface (still 10x faster than pip)
uv pip install <package>
uv pip list
uv pip uninstall <package>
```

### Further Reading

- [UV Documentation](https://github.com/astral-sh/uv)
- [Hatchling Build System](https://hatch.pypa.io/latest/)
- [Getting Started for Developers](getting-started-dev.md)

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

      # Install with uv
      uv sync --all-extras

.. tab:: Linux

   .. code-block:: bash

      # Navigate to pyMM directory
      cd ~/pyMM

      # Install with uv
      uv sync --all-extras

.. tab:: macOS

   .. code-block:: bash

      # Navigate to pyMM directory
      cd ~/Documents/pyMM

      # Install with uv
      uv sync --all-extras
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

### Method 2: MSI Installer (Windows Only)

For permanent desktop installation with Start Menu integration:

.. note::
   MSI installer is available for Python 3.13 on Windows x64 only. For ARM64 or other Python versions, use the portable ZIP method below.

#### Step 1: Download MSI Installer

1. Visit `GitHub Releases <https://github.com/mosh666/pyMM/releases/latest>`_
2. Download: ``pyMM-v{VERSION}-py3.13-win-amd64.msi``
   - **Python 3.13 recommended** for best compatibility
   - **File size**: ~130 MB

#### Step 2: Run Installer

1. **Double-click** the MSI file
2. **UAC Prompt**: Click "Yes" to allow installation (requires administrator privileges)
3. **Setup Wizard**:

   .. image:: _static/screenshots/msi-installer-wizard.png
      :alt: MSI Installer Wizard
      :align: center
      :width: 600px

   - **Welcome Screen**: Click "Next"
   - **Installation Location**: Choose directory (default: ``C:\Program Files\pyMediaManager\``)
     - Can be customized to any location
     - Requires write permissions
   - **Components**: Select installation components
     - ✅ Application Files (required)
     - ✅ Start Menu Shortcuts (recommended)
     - ✅ Desktop Shortcut (optional)
   - **Ready to Install**: Review settings and click "Install"
   - **Progress**: Wait for installation to complete (1-2 minutes)
   - **Completion**: Click "Finish"

#### Step 3: First Launch

1. **Launch Application**:
   - **Start Menu**: Search for "pyMediaManager" and click
   - **Desktop**: Double-click the pyMediaManager shortcut (if created)
   - **Direct**: Navigate to ``C:\Program Files\pyMediaManager\`` and run ``python313\python.exe launcher.py``

2. **First-Run Setup Wizard**:
   - Configure workspace location
   - Set up storage groups (optional)
   - Complete initial configuration

   .. image:: _static/screenshots/first-run-wizard.png
      :alt: First Run Setup Wizard
      :align: center
      :width: 600px

#### Step 4: Uninstall (if needed)

**Option 1: Windows Settings (Recommended)**

1. **Settings** → **Apps** → **Apps & features**
2. Search for "pyMediaManager"
3. Click "Uninstall"
4. Confirm removal

**Option 2: Start Menu**

1. **Start Menu** → **pyMediaManager** folder
2. Click "Uninstall pyMediaManager"
3. Confirm removal

**Option 3: Command Line**

Silent uninstall:

.. code-block:: powershell

   msiexec /x "C:\Path\To\pyMM-v{VERSION}-py3.13-win-amd64.msi" /quiet

.. note::
   **Clean Uninstall**: The MSI installer removes all application files and registry entries. User data (projects, logs) in separate directories like ``pyMM.Projects\`` and ``pyMM.Logs\`` is preserved.

#### Features

- ✅ **Start Menu Integration**: Launch from Windows Start Menu
- ✅ **Desktop Shortcut**: Quick access from desktop (optional)
- ✅ **Automatic PATH Configuration**: Python and application added to system PATH
- ✅ **Clean Uninstall**: Proper Windows uninstaller integration
- ✅ **Automatic Upgrades**: Installing a new version automatically removes the old one
- ✅ **Enterprise Deployment**: Compatible with Group Policy and SCCM
- ✅ **Silent Installation**: Supports ``/quiet`` flag for automated deployment

---

### Method 3: Portable Installation

For use on USB drives or external storage:

.. note::
   Portable installation is primarily designed for Windows with Python Embeddable Package. Linux/macOS users should use Method 1 or 3 for full functionality.

```{tabs}
.. tab:: Windows

   **Portable Windows Setup with Bundled UV**

   pyMediaManager portable ZIP distributions include a **bundled UV executable** for seamless dependency management. No separate UV or pip installation required.

   **Step 1: Download Portable ZIP**

   1. Visit `GitHub Releases <https://github.com/mosh666/pyMM/releases/latest>`_
   2. Download: ``pyMM-portable-py3.13-win-amd64.zip`` (or ARM64 version)
   3. Extract to your portable drive (e.g., ``E:\pyMM``)

   **Step 2: Run Application**

   The portable distribution includes:
   - Python embeddable package (no installation required)
   - All dependencies pre-installed in ``lib-py313/`` directory
   - **UV executable** bundled in ``bin/uv.exe``
   - Launch scripts for easy startup
   - **Automatic PATH configuration** via launcher.py

   .. code-block:: powershell

      # Navigate to portable directory
      cd E:\pyMM

      # Launch with Python
      .\python313\python.exe launcher.py

      # Or use the batch script
      .\LaunchPyMM.bat

   **Step 3: Update Dependencies (Optional)**

   The bundled UV executable is **automatically added to PATH** by ``launcher.py``:

   .. code-block:: powershell

      # UV is available after launching pyMM
      uv --version

      # Update application dependencies
      uv sync --all-extras

      # Install additional packages
      uv pip install <package-name>

   .. note::
      **About UV Commands**: Commands like ``uv pip install`` use UV's pip-compatible interface, not traditional pip. This provides pip familiarity with UV's speed (10-100x faster) and lockfile support. For lockfile-based installs, use ``uv sync`` instead.

   **Step 4: Create Launch Script** (Optional)

   Create ``E:\LaunchPyMM.bat``:

   .. code-block:: batch

      @echo off
      set PYTHONPATH=E:\pyMM
      E:\pyMM\python313\python.exe E:\pyMM\launcher.py
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

      # Install dependencies
      uv sync --all-extras

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

      # Create portable virtual environment with uv
      uv venv

      # Install dependencies
      uv sync --all-extras

   **Step 5: Create Launch Script**

   .. code-block:: bash

      cat > ../launch-pymm.command << 'EOF'
#!/bin/bash
DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/pyMM/.venv/bin/activate"
python -m app
EOF
      chmod +x ../launch-pymm.command

   Double-click ``launch-pymm.command`` to run.
```

### Method 4: Development Installation

For contributors and developers:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Install in development mode with all tools
      # Install in development mode with all tools
      uv sync --all-extras

      # Install pre-commit hooks
      uv run pre-commit install

      # Run tests to verify setup
      uv run pytest

      # Start application
      uv run python3 launcher.py

.. tab:: macOS

   .. code-block:: bash

      # Clone repository
      git clone https://github.com/mosh666/pyMM.git
      cd pyMM

      # Install in development mode with all tools
      uv sync --all-extras

      # Install pre-commit hooks
      uv run pre-commit install

      # Run tests to verify setup
      uv run pytest

      # Start application
      uv run python3 launcher.py
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

#### Step 3: Storage Groups Configuration (Optional)

**New in v2.0**: Configure Master/Backup drive pairs for data redundancy.

```text
Storage Groups Setup (Optional):
┌─────────────────────────────────────────────────┐
│ 💡 Tip: Skip this step and configure later     │
│     from Storage Management view                │
│                                                 │
│ Master Drive:                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ -- Skip (configure later) --                │ │
│ │ E:\ (PhotoMaster) - 2000.0 GB              │ │
│ │ F:\ (VideoMaster) - 4000.0 GB              │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Backup Drive:                                   │
│ ┌─────────────────────────────────────────────┐ │
│ │ -- Select backup drive --                   │ │
│ │ G:\ (PhotoBackup) - 2000.0 GB              │ │
│ │ H:\ (VideoBackup) - 4000.0 GB              │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Group Name:                                     │
│ ┌─────────────────────────────────────────────┐ │
│ │ Photo Archive 2026                          │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ ✓ Found 4 removable drive(s)                   │
└─────────────────────────────────────────────────┘
```

**Storage Groups Benefits:**

- ✅ Automatic backup to secondary drive
- ✅ Failover support if primary drive fails
- ✅ Real-time and scheduled synchronization
- ✅ Configure now or skip and set up later

#### Step 4: Folder Structure Creation

pyMM creates portable folder structure:

```text
D:\pyMM.Projects\       # Project storage
D:\pyMM.Logs\           # Application logs
D:\pyMM.Plugins\        # Downloaded plugins
```

**Portability Note**: If you move pyMM to another drive, these folders automatically relocate.

#### Step 5: Plugin Configuration

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

#### Step 6: Initial Configuration

Configure basic settings:

- **Language**: English (more languages planned)
- **Theme**: Light, Dark, Auto (follows system)
- **Default Project Location**: `D:\pyMM.Projects`
- **Auto-Update Plugins**: Enabled (recommended)
- **Telemetry**: Disabled by default (respects privacy)

#### Step 7: Complete Setup

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

```ini
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

---

**Next**: See :ref:`getting-started` to learn about core features and the user interface.
