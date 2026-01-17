# Windows Setup Guide

> **Last Updated:** 2026-01-17 21:41 UTC
\n**Complete Windows installation and configuration guide** for
pyMediaManager, covering MSI installer, portable installation, permissions,
and Windows-specific features.

---

## 📦 Installation Methods

### Method 1: MSI Installer (Recommended)

The Windows MSI installer provides a traditional installation experience with
Start Menu integration, automatic PATH configuration, and easy uninstallation.

#### System Requirements

- **OS**: Windows 10 (1809+) or Windows 11
- **Python**: 3.12, 3.13, or 3.14 (3.13 recommended)
- **Architecture**: x64 (64-bit) or ARM64
- **Disk Space**: 500 MB (application) + 2 GB (plugins)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Display**: 1280x720 minimum resolution

#### Download

Download the latest MSI installer from:

- **GitHub Releases**: [github.com/mosh666/pyMM/releases](https://github.com/mosh666/pyMM/releases)
- **File**: `pyMediaManager-v2.x.x-win64.msi`

#### Interactive Installation

1. **Double-click** the MSI installer
2. **User Account Control (UAC)** prompt appears:
   - Click **"Yes"** to allow installation
   - Administrator privileges required for system-wide installation
3. **Setup Wizard** opens:
   - **Welcome** - Click "Next"
   - **License Agreement** - Accept MIT License, click "Next"
   - **Installation Folder**:
     - Default: `C:\Program Files\pyMediaManager\`
     - Custom: Click "Change" to select different location
   - **Features Selection**:
     - ☑ Application Files (required)
     - ☑ Start Menu Shortcuts (recommended)
     - ☑ Desktop Shortcut (optional)
     - ☑ Add to PATH (recommended for CLI usage)
   - **Ready to Install** - Review settings, click "Install"
4. **Installation Progress** - Wait for completion (2-5 minutes)
5. **Completion** - Click "Finish"

#### Silent Installation

For automated deployments, corporate environments, or unattended installation:

```powershell
# Basic silent install (default settings)
msiexec /i pyMediaManager-v2.0.0-win64.msi /quiet /norestart

# Silent install with custom path
msiexec /i pyMediaManager-v2.0.0-win64.msi /quiet /norestart INSTALLDIR="D:\Apps\pyMediaManager"

# Silent install with logging
msiexec /i pyMediaManager-v2.0.0-win64.msi /quiet /norestart /l*v install.log

# Silent install with all features
msiexec /i pyMediaManager-v2.0.0-win64.msi /quiet /norestart ADDLOCAL=ALL

# Silent install without desktop shortcut
msiexec /i pyMediaManager-v2.0.0-win64.msi /quiet /norestart ADDLOCAL=ApplicationFiles,StartMenuShortcuts
```

**MSI Parameters**:

| Parameter | Description | Values |
| ----------- | ------------- | -------- |
| `/i` | Install package | Path to MSI file |
| `/quiet` | Silent mode (no UI) | - |
| `/norestart` | Prevent automatic reboot | - |
| `/l*v` | Verbose logging | Log file path |
| `INSTALLDIR` | Custom install location | Full path |
| `ADDLOCAL` | Features to install | `ALL`, `ApplicationFiles`, `StartMenuShortcuts`, `DesktopShortcut`, `PATHEntry` |

#### Post-Installation

After MSI installation, pyMediaManager is available:

- **Start Menu**: Start → pyMediaManager
- **Desktop**: Double-click "pyMediaManager" shortcut (if selected)
- **Command Line**: `pymm` (if PATH entry added)
- **Installation Path**: `C:\Program Files\pyMediaManager\` (or custom path)

### Method 2: Portable ZIP

Portable installation for USB drives, network shares, or systems without admin privileges.

#### Download

- **GitHub Releases**: [github.com/mosh666/pyMM/releases](https://github.com/mosh666/pyMM/releases)
- **File**: `pyMediaManager-v2.x.x-portable-win64.zip`

#### Installation

1. **Extract** ZIP to desired location:

   ```powershell
   # Extract to local drive
   Expand-Archive -Path pyMediaManager-v2.0.0-portable-win64.zip -DestinationPath D:\pyMM

   # Extract to USB drive
   Expand-Archive -Path pyMediaManager-v2.0.0-portable-win64.zip -DestinationPath E:\pyMM
   ```

2. **Verify** extraction:

   ```text
   D:\pyMM\
   ├── launcher.py
   ├── app\
   ├── config\
   ├── plugins\
   └── README.md
   ```

3. **Launch** application:
   - Double-click `launcher.py`
   - Or run from command line: `python launcher.py`

#### Portable Configuration

Portable mode uses relative paths to keep all data within the installation folder:

```yaml
# config/user.yaml
paths:
  projects_dir: pyMM.Projects    # Relative to installation root
  logs_dir: pyMM.Logs
  plugins_dir: pyMM.Plugins
  config_dir: config
```

This ensures the entire pyMM folder can be moved between drives or systems without breaking paths.

### Method 3: Python Package (Developer)

Install from PyPI or source for development:

```powershell
# Install UV (required)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install from PyPI
uv pip install --system pymediamanager

# Or install from source
git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --all-extras

# Launch
uv run python -m app
```

> **Note**: pyMediaManager migrated to **UV** package manager (replacing pip) in early 2026.
> UV is 10-100x faster and provides lockfile support.
> See {ref}`migrating-from-pip` for details if upgrading from older versions.

---

## 🔐 Permissions & Security

### User Account Control (UAC)

pyMediaManager requires elevated privileges for certain operations:

#### When UAC Prompts Appear

| Operation | Requires Admin | Why |
| ----------- | ---------------- | ----- |
| MSI Installation | ✅ Yes | System-wide installation |
| Plugin Installation | ❌ No | User-level directories |
| Storage Drive Detection | ❌ No | WMI read-only access |
| Portable USB Installation | ❌ No | User-writable location |
| System Service Installation | ✅ Yes | Service registration |

#### Bypassing UAC for Portable

If you want to avoid UAC prompts entirely:

1. **Use portable ZIP installation** (no admin required)
2. **Extract to user-writable location**:
   - ✅ `%USERPROFILE%\pyMM` (e.g., `C:\Users\YourName\pyMM`)
   - ✅ `D:\Apps\pyMM` (non-system drive)
   - ❌ `C:\Program Files\pyMM` (requires admin)

### Windows Defender & Antivirus

pyMediaManager is **not signed** with a code-signing certificate in Beta phase. Windows Defender may show warnings:

#### SmartScreen Warning

On first launch:

```text
Windows protected your PC
Microsoft Defender SmartScreen prevented an unrecognized app from starting.

Running this app might put your PC at risk.

[More info]  [Don't run]
```

**To proceed**:

1. Click **"More info"**
2. Click **"Run anyway"**

This warning appears only on first launch of each new version.

#### Adding Exclusion (Optional)

To prevent future warnings:

```powershell
# Add pyMM folder to Windows Defender exclusions (requires admin)
Add-MpPreference -ExclusionPath "D:\pyMM"

# Verify exclusion
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

> **Note**: Only add exclusions if you trust the source. Download pyMM only from official GitHub releases.

---

## 🔧 Windows Management Instrumentation (WMI)

pyMediaManager uses WMI for cross-platform drive detection on Windows.

### WMI Access Requirements

- **Permissions**: Standard user (read-only WMI access)
- **Service**: Windows Management Instrumentation service must be running
- **Firewall**: No special firewall rules required (local access only)

### Verify WMI Access

```powershell
# Test WMI access
Get-WmiObject -Class Win32_LogicalDisk

# Output should show all drives:
# DeviceID  : C:
# DriveType : 3
# Size      : 512110190592
# FreeSpace : 123456789012
```

### Troubleshooting WMI

#### Issue: "Invalid class" or "Access denied"

**Cause**: WMI service not running or permissions issue

**Solution**:

```powershell
# Check WMI service status
Get-Service -Name Winmgmt

# If stopped, start the service (requires admin)
Start-Service -Name Winmgmt

# Set to automatic startup
Set-Service -Name Winmgmt -StartupType Automatic
```

#### Issue: No drives detected

**Cause**: WMI cache corruption

**Solution**:

```powershell
# Rebuild WMI repository (requires admin)
# WARNING: This resets WMI configuration
Stop-Service -Name Winmgmt -Force
winmgmt /resetrepository
Start-Service -Name Winmgmt
```

---

## 💾 Storage Drive Detection

pyMediaManager uses Windows APIs to detect removable and fixed drives.

### Supported Drive Types

| Type | WMI DriveType | Detected | Use Case |
| ------ | --------------- | -------- | ---------- |
| **Removable (USB)** | 2 | ✅ Yes | Storage Groups (Master/Backup) |
| **Fixed (HDD/SSD)** | 3 | ✅ Yes | Projects directory |
| **Network** | 4 | ✅ Yes | Network project storage |
| **CD-ROM** | 5 | ❌ No | Not supported |
| **RAM Disk** | 6 | ✅ Yes | Temporary storage |

### Drive Information Collected

```python
# Example WMI query results
{
    "device_id": "E:",
    "label": "PhotoMaster",
    "drive_type": "Removable",
    "total_size": 2000398934016,  # 2 TB
    "free_space": 1500299200512,
    "serial_number": "ABC123XYZ789",
    "file_system": "NTFS",
    "is_removable": True
}
```

### Testing Drive Detection

```powershell
# Launch pyMM with debug logging
python launcher.py --log-level DEBUG

# Check logs for drive detection
Get-Content "$env:APPDATA\pyMM\logs\app.log" | Select-String "Detected drive"

# Output example:
# 2026-01-14 10:15:23 - INFO - Detected drive C: (Fixed, NTFS, 512 GB)
# 2026-01-14 10:15:23 - INFO - Detected drive E: (Removable, NTFS, 2 TB)
```

---

## 🛠️ Uninstallation

### Uninstall MSI Installation

#### Method 1: Settings App

1. Open **Settings** → **Apps** → **Installed apps**
2. Find **pyMediaManager** in the list
3. Click **⋮** (three dots) → **Uninstall**
4. Click **Uninstall** to confirm
5. MSI uninstaller runs → Click **"Yes"** on UAC prompt
6. Wait for completion

#### Method 2: Control Panel

1. Open **Control Panel** → **Programs and Features**
2. Find **pyMediaManager** in the list
3. Click **Uninstall**
4. Follow prompts

#### Method 3: Command Line

```powershell
# Silent uninstall (requires MSI product code)
msiexec /x {550E8400-E29B-41D4-A716-446655440000} /quiet /norestart

# Find product code
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*pyMediaManager*"} | Select-Object IdentifyingNumber, Name
```

### Remove User Data

MSI uninstaller **does not remove** user data. To completely remove all traces:

```powershell
# Remove application data (config, logs, cache)
Remove-Item -Recurse -Force "$env:APPDATA\pyMM"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\pyMM"

# Remove projects (⚠️ WARNING: This deletes your media projects!)
# Remove-Item -Recurse -Force "D:\pyMM.Projects"
```

### Uninstall Portable

Simply delete the folder:

```powershell
# Delete portable installation
Remove-Item -Recurse -Force "D:\pyMM"
```

---

## 🔍 Registry Keys

MSI installation creates registry keys for application registration:

### Installed Keys

```text
HKEY_LOCAL_MACHINE\SOFTWARE\pyMediaManager\
├── InstallPath        = "C:\Program Files\pyMediaManager"
├── Version            = "2.0.0"
├── InstallDate        = "2026-01-14"
└── UninstallString    = "msiexec /x {ProductCode}"

HKEY_CURRENT_USER\Software\pyMediaManager\
└── (User preferences - managed by app)
```

### Viewing Registry Keys

```powershell
# View installation keys
Get-ItemProperty -Path "HKLM:\SOFTWARE\pyMediaManager"

# View user preferences
Get-ItemProperty -Path "HKCU:\Software\pyMediaManager"
```

### Manual Cleanup

If uninstaller fails to remove registry keys:

```powershell
# Remove application registry keys (requires admin)
Remove-Item -Path "HKLM:\SOFTWARE\pyMediaManager" -Recurse -Force

# Remove user registry keys
Remove-Item -Path "HKCU:\Software\pyMediaManager" -Recurse -Force
```

---

## 🔧 Troubleshooting

### Issue: "Python not found" on launch

**Cause**: Python not in PATH or not installed

**Solution**:

```powershell
# Check Python installation
python --version

# If not found, download from python.org or Microsoft Store
# Then add to PATH or use Python Launcher
py -3.13 launcher.py
```

### Issue: MSI installer fails with error 2503/2502

**Cause**: Temporary folder permissions

**Solution**:

```powershell
# Run installer from command line with admin privileges
Start-Process msiexec.exe -ArgumentList "/i","pyMediaManager-v2.0.0-win64.msi" -Verb RunAs
```

### Issue: Drives not detected or wrong drive letters

**Cause**: Drive letter assignment conflicts or WMI cache

**Solution**:

1. Reconnect USB drives
2. Refresh pyMM Storage view (F5)
3. Restart WMI service (see WMI troubleshooting above)

### Issue: SmartScreen blocks every launch

**Cause**: Unsigned executable

**Solution**:

- Add Windows Defender exclusion (see Security section)
- Download from official GitHub releases only
- Wait for code-signing certificate in stable release

---

## 📋 Command-Line Interface

pyMediaManager supports command-line usage when installed with PATH entry:

```powershell
# Launch application
pymm

# Create project
pymm create-project "MyProject" --type photo --location "D:\pyMM.Projects"

# List projects
pymm list-projects

# Open project
pymm open-project "D:\pyMM.Projects\MyProject"

# Check version
pymm --version

# Get help
pymm --help
```

---

## 🔗 Related Documentation

- [Installation Guide](installation.md) - General installation overview
- [Getting Started](getting-started.md) - First-time setup and configuration
- [Configuration](configuration.md) - Configuration file reference
- [Storage Groups](storage-groups.md) - Drive pairing and redundancy
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

**Platform**: Windows 10/11 x64
