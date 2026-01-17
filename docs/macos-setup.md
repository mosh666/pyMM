# macOS Setup Guide

**Complete macOS installation and configuration guide** for pyMediaManager,
covering installation methods, permissions, Gatekeeper, disk access, and
macOS-specific features.

---

## 📦 Installation Methods

### Method 1: DMG Installer (Recommended)

The DMG disk image provides a native macOS installation experience with drag-and-drop simplicity.

#### System Requirements

- **OS**: macOS 11 Big Sur or later (macOS 13 Ventura recommended)
- **Python**: 3.12, 3.13, or 3.14 (3.13 recommended via Homebrew)
- **Architecture**: Apple Silicon (arm64) or Intel (x86_64)
- **Disk Space**: 500 MB (application) + 2 GB (plugins)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Display**: 1280x720 minimum resolution

#### Download

Download the latest DMG installer from:

- **GitHub Releases**: [github.com/mosh666/pyMM/releases](https://github.com/mosh666/pyMM/releases)
- **Apple Silicon**: `pyMediaManager-v2.x.x-macOS-arm64.dmg`
- **Intel**: `pyMediaManager-v2.x.x-macOS-x86_64.dmg`

#### Installation Steps

1. **Double-click** the DMG file to mount
2. **DMG window opens** showing:

   ```text
   ┌─────────────────────────────────────┐
   │                                     │
   │   pyMediaManager.app                │
   │            ▼                        │
   │      Applications                   │
   │                                     │
   └─────────────────────────────────────┘
   ```

3. **Drag** `pyMediaManager.app` to `Applications` folder
4. **Wait** for copy to complete (1-2 minutes)
5. **Eject** the DMG:

   ```bash
   # From command line
   hdiutil detach /Volumes/pyMediaManager
   ```

#### First Launch

1. **Open Finder** → **Applications**
2. **Locate** pyMediaManager.app
3. **Right-click** → **Open** (or **Control+Click** → **Open**)
4. **Gatekeeper prompt** appears:

   ```text
   "pyMediaManager" cannot be opened because it is from an unidentified developer.

   macOS cannot verify that this app is free from malware.

   [Move to Trash]  [Cancel]
   ```

5. **Click "Open"** on the secondary prompt:

   ```text
   "pyMediaManager" is from an unidentified developer. Are you sure you want to open it?

   [Cancel]  [Open]
   ```

6. **Application launches** - Subsequent launches work normally

> **Why right-click → Open?** This bypass only works for the first launch.
> Double-clicking will show the Gatekeeper block without an "Open" option.

### Method 2: Homebrew Cask (Command Line)

Install via Homebrew package manager:

```bash
# Add pyMM tap (repository)
brew tap mosh666/pymm

# Install pyMediaManager
brew install --cask pymediamanager

# Launch
open /Applications/pyMediaManager.app
```

**Benefits**:

- Automatic updates via `brew upgrade`
- No Gatekeeper warnings
- Simple uninstallation

### Method 3: Python Package (Developer)

Install from PyPI or source for development:

```bash
# Install UV (required)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install from PyPI
uv pip install --system pymediamanager

# Or install from source
git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --all-extras

# Launch
uv run python -m app
```

> **Note**: pyMediaManager uses **UV** (not pip) for package management as of v0.2.0.
> UV is 10-100x faster and provides lockfile support.
> See {ref}`migrating-from-pip` for details.

---

## 🔐 Gatekeeper & Code Signing

macOS Gatekeeper blocks unsigned applications to protect against malware.

### Why Gatekeeper Blocks pyMM

pyMediaManager is **not notarized** with an Apple Developer ID in Beta phase:

- **Notarization Cost**: $99/year Apple Developer Program membership
- **Beta Status**: Code signing planned for stable 1.0 release
- **Workaround**: Manual approval required (one-time only)

### Bypassing Gatekeeper Safely

#### Method 1: Right-Click → Open (Recommended)

1. **Right-click** pyMediaManager.app
2. Select **"Open"**
3. Click **"Open"** in confirmation dialog

This allows macOS to remember your choice.

#### Method 2: Security & Privacy Settings

If you accidentally clicked "Move to Trash":

1. Open **System Settings** (or **System Preferences** on older macOS)
2. Navigate to **Privacy & Security** → **Security**
3. Find message: *"pyMediaManager was blocked from use because it is not from an identified developer"*
4. Click **"Open Anyway"**
5. Enter administrator password
6. Confirm by clicking **"Open"**

#### Method 3: Remove Quarantine Attribute (Advanced)

For developers or advanced users:

```bash
# Remove quarantine attribute from app bundle
xattr -d com.apple.quarantine /Applications/pyMediaManager.app

# Verify removal
xattr -l /Applications/pyMediaManager.app
# Should not show com.apple.quarantine
```

> **Warning**: Only use this method for applications from trusted sources. Download pyMM only from official GitHub releases.

### Future Code Signing

Planned for stable release (v1.0+):

- **Apple Developer ID** certificate
- **Notarization** via Apple's notary service
- **Automatic Gatekeeper approval**
- **No manual bypass required**

---

## 💾 Disk Access Permissions

pyMediaManager requires disk access permissions to manage media files and detect storage drives.

### Required Permissions

| Permission | Purpose | Prompt Timing |
| ------------ | ------- | --------------- |
| **Full Disk Access** | Read/write media files across system | First file access |
| **Removable Volumes** | Detect USB/external drives | First storage scan |
| **Downloads Folder** | Import media from Downloads | First download access |

### Granting Full Disk Access

1. Open **System Settings** → **Privacy & Security** → **Privacy**
2. Select **Full Disk Access** from left sidebar
3. Click **🔒** (lock icon) to unlock (enter password)
4. Click **"+"** button
5. Navigate to **Applications** → **pyMediaManager.app**
6. Click **"Open"**
7. **Toggle switch** to enable Full Disk Access
8. **Restart** pyMediaManager for changes to take effect

### Granting Removable Volumes Access

macOS Ventura (13.0+) requires explicit permission for removable media:

1. **System Settings** → **Privacy & Security** → **Files and Folders**
2. Find **pyMediaManager**
3. Enable: ☑ **Removable Volumes**
4. Restart pyMediaManager

### Testing Permissions

```bash
# Check if pyMM has Full Disk Access
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT service, client, allowed FROM access WHERE client LIKE '%pyMediaManager%'"

# Output should show:
# kTCCServiceSystemPolicyAllFiles|/Applications/pyMediaManager.app|1
```

### Troubleshooting Permission Issues

#### Issue: Cannot access external drives

**Cause**: Removable Volumes permission not granted

**Solution**:

1. Grant "Removable Volumes" access (see above)
2. Reconnect USB drive
3. Restart pyMediaManager

#### Issue: Cannot read/write project files

**Cause**: Full Disk Access not granted

**Solution**:

1. Grant "Full Disk Access" (see above)
2. Restart pyMediaManager
3. Try operation again

---

## 🔍 Storage Drive Detection (IOKit & DiskArbitration)

pyMediaManager uses macOS native APIs for drive detection.

### IOKit Framework

IOKit provides low-level hardware information:

```bash
# List all storage devices
ioreg -r -c IOMedia

# Get device properties
ioreg -r -c IOMedia -l | grep -E "BSD Name|IOMediaEjectable|Size|Removable"
```

### DiskArbitration Framework

DiskArbitration monitors mount/unmount events:

```bash
# View mounted volumes
diskutil list

# Get volume information
diskutil info /Volumes/PhotoMaster

# Output example:
#    Device Identifier:        disk2s1
#    Device Node:              /dev/disk2s1
#    Whole:                    No
#    Part of Whole:            disk2
#    Volume Name:              PhotoMaster
#    Mounted:                  Yes
#    Mount Point:              /Volumes/PhotoMaster
#    File System:              APFS
#    Ejectable:                Yes
#    Removable Media:          Yes
#    Read-Only:                No
```

### Supported Drive Types

| Type | Protocol | Detected | Use Case |
| ------ | ---------- | -------- | ---------- |
| **USB External** | USB 3.0/3.1/3.2 | ✅ Yes | Storage Groups |
| **Thunderbolt** | Thunderbolt 3/4 | ✅ Yes | High-speed storage |
| **Internal SSD** | NVMe/SATA | ✅ Yes | Projects directory |
| **Network (SMB/AFP)** | Network | ✅ Yes | Network storage |
| **SD Card** | Card Reader | ✅ Yes | Camera imports |
| **CD/DVD** | Optical | ❌ No | Not supported |

### Drive Information Collected

```python
# Example drive detection result
{
    "device_id": "/dev/disk2s1",
    "label": "PhotoMaster",
    "mount_point": "/Volumes/PhotoMaster",
    "drive_type": "Removable",
    "total_size": 2000398934016,  # 2 TB
    "free_space": 1500299200512,
    "serial_number": "ABC123XYZ789",
    "file_system": "APFS",
    "protocol": "USB",
    "is_removable": True,
    "is_ejectable": True
}
```

---

## 🛠️ Uninstallation

### Uninstall App Bundle

#### Method 1: Finder

1. Open **Finder** → **Applications**
2. Locate **pyMediaManager.app**
3. **Drag to Trash** (or right-click → **Move to Trash**)
4. **Empty Trash**

#### Method 2: Command Line

```bash
# Remove application bundle
rm -rf /Applications/pyMediaManager.app

# Confirm removal
ls /Applications | grep pyMediaManager
# (should return nothing)
```

### Remove User Data

Application removal **does not delete** user data. To completely remove:

```bash
# Remove application support (config, logs, cache)
rm -rf ~/Library/Application\ Support/pyMM
rm -rf ~/Library/Caches/pyMM
rm -rf ~/Library/Logs/pyMM

# Remove preferences
rm ~/Library/Preferences/com.pyMM.pyMediaManager.plist

# Remove projects (⚠️ WARNING: This deletes your media projects!)
# rm -rf ~/Documents/pyMM.Projects
```

### Uninstall Homebrew Installation

```bash
# Uninstall via Homebrew
brew uninstall --cask pymediamanager

# Remove configuration (optional)
rm -rf ~/Library/Application\ Support/pyMM
```

---

## 🍺 Homebrew Installation Details

### Installing Python via Homebrew

pyMediaManager requires Python 3.12+. Install via Homebrew:

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.13 (recommended)
brew install python@3.13

# Verify installation
python3.13 --version
# Should output: Python 3.13.x

# Set as default (optional)
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Managing Dependencies

```bash
# Update Homebrew
brew update

# Upgrade pyMediaManager
brew upgrade pymediamanager

# List installed casks
brew list --cask | grep pymediamanager
```

---

## 🔧 Troubleshooting

### Issue: "Damaged and can't be opened" error

**Cause**: Gatekeeper blocking unsigned app

**Solution**:

```bash
# Remove quarantine attribute
xattr -d com.apple.quarantine /Applications/pyMediaManager.app

# Try launching again
open /Applications/pyMediaManager.app
```

### Issue: Python not found

**Cause**: Python not installed or not in PATH

**Solution**:

```bash
# Check Python installation
python3 --version

# If not found, install via Homebrew
brew install python@3.13

# Or download from python.org
open https://www.python.org/downloads/macos/
```

### Issue: Cannot detect external drives

**Cause**: Removable Volumes permission not granted

**Solution**:

1. Grant "Removable Volumes" access (see Disk Access Permissions section)
2. Reconnect USB drive
3. Verify mount:

   ```bash
   diskutil list | grep external
   ```

### Issue: App crashes on launch

**Cause**: Incompatible Python version or missing dependencies

**Solution**:

```bash
# Check Python version
python3 --version
# Must be 3.12 or 3.13

# Reinstall dependencies
pip3 install --upgrade pymediamanager

# Check crash logs
open ~/Library/Logs/DiagnosticReports/
# Look for pyMediaManager crash reports
```

### Issue: Cannot write to external drive

**Cause**: Drive formatted as NTFS (read-only on macOS)

**Solution**:

Option 1: Reformat as exFAT (cross-platform):

```bash
# ⚠️ WARNING: This erases all data on the drive!
diskutil eraseDisk ExFAT PhotoMaster /dev/disk2
```

Option 2: Install NTFS driver:

```bash
# Install Tuxera NTFS or Paragon NTFS
# Or use free ntfs-3g via Homebrew
brew install ntfs-3g
```

---

## 🔗 Command-Line Interface

pyMediaManager supports command-line usage:

```bash
# Add to PATH (if installed via DMG)
export PATH="/Applications/pyMediaManager.app/Contents/MacOS:$PATH"

# Launch application
pymm

# Create project
pymm create-project "MyProject" --type photo --location "~/Documents/pyMM.Projects"

# List projects
pymm list-projects

# Open project
pymm open-project "~/Documents/pyMM.Projects/MyProject"

# Check version
pymm --version

# Get help
pymm --help
```

---

## 🔍 Platform-Specific Features

### Native macOS Integration

- **Retina Display Support**: Optimized UI for high-DPI displays
- **Dark Mode**: Automatic adaptation to system appearance
- **Notification Center**: Progress notifications and alerts
- **Spotlight Integration**: Search pyMM projects from Spotlight
- **Quick Look**: Preview media files with spacebar
- **Touch Bar**: Common actions on MacBook Pro Touch Bar

### File System Differences

| Feature | Windows | macOS | Notes |
| --------- | ------- | ----- | ------- |
| **File System** | NTFS | APFS/HFS+ | Case-sensitive on macOS optional |
| **Path Separator** | `\` | `/` | Handled automatically |
| **Drive Letters** | C:, D:, E: | /Volumes/Name | Different mount structure |
| **Hidden Files** | Attribute | Dot prefix | `.pymm` vs `pymm.hidden` |

---

## 📋 System Compatibility

### macOS Version Support

| macOS Version | Status | Notes |
| --------------- | -------- | ------- |
| **14 Sonoma** | ✅ Fully Supported | Latest features |
| **13 Ventura** | ✅ Fully Supported | Recommended |
| **12 Monterey** | ✅ Supported | All features work |
| **11 Big Sur** | ✅ Supported | Minimum version |
| **10.15 Catalina** | ⚠️ Untested | May work |
| **10.14 Mojave** | ❌ Not Supported | Too old |

### Architecture Support

| Architecture | Status | Performance |
| -------------- | -------- | ------------- |
| **Apple Silicon (M1/M2/M3)** | ✅ Native | Excellent |
| **Intel (x86_64)** | ✅ Native | Good |
| **Rosetta 2 (Intel app on Apple Silicon)** | ✅ Compatible | Moderate |

---

## 🔗 Related Documentation

- [Installation Guide](installation.md) - General installation overview
- [Getting Started](getting-started.md) - First-time setup and configuration
- [Configuration](configuration.md) - Configuration file reference
- [Storage Groups](storage-groups.md) - Drive pairing and redundancy
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

---

**Platform**: macOS 11+ (Intel & Apple Silicon)
**Last Updated**: 2026-01-14
