# Linux Setup Guide

> **Last Updated:** 2026-01-17 21:41 UTC

**Complete Linux installation and configuration guide** for pyMediaManager,
covering AppImage portable installation, package managers for various
distributions, permissions setup, and Linux-specific features.

---

## 📦 Installation Methods

### Method 1: AppImage (Recommended)

The AppImage format provides a **universal, portable installation** that works
across all Linux distributions without requiring system installation or package
managers. This is the recommended method for most users.

#### Why AppImage?

- ✅ **Universal** - Works on Ubuntu, Fedora, Arch, Debian, openSUSE, and all major
  distros
- ✅ **Portable** - Run from USB drives or any location
- ✅ **No Dependencies** - All libraries bundled
- ✅ **No Root Required** - Install and run as regular user
- ✅ **Easy Updates** - Download new AppImage, replace old one
- ✅ **Sandboxed** - Isolated from system libraries
- ✅ **Desktop Integration** - Automatic menu entries with AppImageLauncher

#### System Requirements

- **OS**: Any Linux distribution with glibc 2.31+ (2020 or newer)
- **Kernel**: 4.15+ (Ubuntu 18.04+, Fedora 28+, Debian 10+)
- **Architecture**: x86_64 (64-bit) or aarch64 (ARM64)
- **Disk Space**: 150 MB (AppImage) + 2 GB (plugins)
- **RAM**: 4 GB minimum, 8 GB recommended
- **Display**: 1280x720 minimum resolution, X11 or Wayland

#### Download

Download the latest AppImage from:

- **GitHub Releases**: [github.com/mosh666/pyMM/releases](https://github.com/mosh666/pyMM/releases)
- **x86_64**: `pyMediaManager-v0.x.x-x86_64.AppImage`
- **ARM64**: `pyMediaManager-v0.x.x-aarch64.AppImage`

#### Installation Steps

1. **Download AppImage**

   ```bash
   # Download latest release (x86_64)
   wget https://github.com/mosh666/pyMM/releases/latest/download/pyMediaManager-x86_64.AppImage

   # Or use curl
   curl -LO https://github.com/mosh666/pyMM/releases/latest/download/pyMediaManager-x86_64.AppImage
   ```

2. **Make Executable**

   ```bash
   chmod +x pyMediaManager-x86_64.AppImage
   ```

3. **Run Application**

   ```bash
   ./pyMediaManager-x86_64.AppImage
   ```

4. **Optional: Move to Applications Directory**

   ```bash
   # Move to ~/Applications (user-specific)
   mkdir -p ~/Applications
   mv pyMediaManager-x86_64.AppImage ~/Applications/

   # Or move to /opt (system-wide, requires sudo)
   sudo mv pyMediaManager-x86_64.AppImage /opt/
   ```

#### Desktop Integration

##### Option 1: AppImageLauncher (Recommended)

AppImageLauncher provides automatic desktop integration for AppImages:

```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:appimagelauncher-team/stable
sudo apt update
sudo apt install appimagelauncher

# Fedora
sudo dnf install appimagelauncher

# Arch Linux
yay -S appimagelauncher
```

**After installing AppImageLauncher:**

- Double-click the AppImage
- Choose "Integrate and run"
- Application appears in application menu automatically
- Updates can be checked within the app

##### Option 2: Manual Desktop Entry

Create desktop entry manually:

```bash
# Create desktop entry
cat > ~/.local/share/applications/pymediamanager.desktop << 'EOF'
[Desktop Entry]
Name=pyMediaManager
Comment=Portable Media Management Application
Exec=/home/USERNAME/Applications/pyMediaManager-x86_64.AppImage
Icon=pymediamanager
Terminal=false
Type=Application
Categories=Utility;FileTools;
EOF

# Replace USERNAME with your actual username
sed -i "s/USERNAME/$(whoami)/" ~/.local/share/applications/pymediamanager.desktop

# Update desktop database
update-desktop-database ~/.local/share/applications/
```

**Download Icon** (optional):

```bash
# Download official icon
mkdir -p ~/.local/share/icons/hicolor/256x256/apps
wget https://raw.githubusercontent.com/mosh666/pyMM/main/app/ui/resources/icon.png \
     -O ~/.local/share/icons/hicolor/256x256/apps/pymediamanager.png

# Update icon cache
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

#### First Launch

On first launch, pyMediaManager will:

1. **Check for Python 3.13** - Bundled Python included in AppImage
2. **Initialize configuration** - Create `~/.config/pyMediaManager/`
3. **Show First Run Wizard** - Guide you through initial setup
4. **Detect portable mode** - If run from USB/external drive

**No additional setup required!** The AppImage is self-contained.

#### Updating AppImage

```bash
# Download new version
wget https://github.com/mosh666/pyMM/releases/latest/download/pyMediaManager-x86_64.AppImage

# Make executable
chmod +x pyMediaManager-x86_64.AppImage

# Replace old version
mv pyMediaManager-x86_64.AppImage ~/Applications/pyMediaManager-x86_64.AppImage

# Run new version
~/Applications/pyMediaManager-x86_64.AppImage
```

**Tip**: Keep old AppImage as backup until you verify new version works.

---

### Method 2: Package Managers

For users who prefer traditional package management, pyMediaManager can be installed via distribution-specific package managers.

#### Ubuntu / Debian / Linux Mint

**Python 3.13 Installation** (required):

```bash
# Add deadsnakes PPA for Python 3.13
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.13 and pip
sudo apt install python3.13 python3.13-venv python3.13-dev
```

**pyMediaManager Installation**:

```bash
# Method A: Install from DEB package (when available)
wget https://github.com/mosh666/pyMM/releases/latest/download/pymediamanager_0.x.x_amd64.deb
sudo dpkg -i pymediamanager_0.x.x_amd64.deb
sudo apt install -f  # Fix dependencies if needed

# Method B: Install with UV (package manager)
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install pyMediaManager
git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --python 3.13

# Run application
uv run python -m app.main
```

**Add to PATH** (for Method B):

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Fedora / RHEL / CentOS Stream

**Python 3.13 Installation**:

```bash
# Fedora 38+ includes Python 3.13
sudo dnf install python3.13 python3.13-devel

# For older Fedora or RHEL, use pyenv (see Python Environment section)
```

**pyMediaManager Installation**:

```bash
# Method A: Install from RPM package (when available)
wget https://github.com/mosh666/pyMM/releases/latest/download/pymediamanager-0.x.x.x86_64.rpm
sudo dnf install pymediamanager-0.x.x.x86_64.rpm

# Method B: Install with UV
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --python 3.13

# Run application
uv run python -m app.main
```

#### Arch Linux / Manjaro

**Python 3.13 Installation**:

```bash
# Arch usually has latest Python in official repos
sudo pacman -S python python-pip

# Check version
python --version  # Should be 3.13+
```

**pyMediaManager Installation**:

```bash
# Method A: Install from AUR (when available)
yay -S pymediamanager-bin
# or
paru -S pymediamanager-bin

# Method B: Install with UV
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --python 3.13

# Run application
uv run python -m app.main
```

#### OpenSUSE

**Python 3.13 Installation**:

```bash
# OpenSUSE Tumbleweed (rolling release)
sudo zypper install python313 python313-devel

# OpenSUSE Leap (stable), use pyenv
```

**pyMediaManager Installation**:

```bash
# Install with UV
curl -LsSf https://astral.sh/uv/install.sh | sh

git clone https://github.com/mosh666/pyMM.git
cd pyMM
uv sync --python 3.13

uv run python -m app.main
```

---

### Method 3: Portable ZIP

Portable ZIP installation for manual deployments or air-gapped systems.

#### Download and Extract

```bash
# Download portable ZIP
wget https://github.com/mosh666/pyMM/releases/latest/download/pyMediaManager-v0.x.x-linux-portable.zip

# Extract to desired location
unzip pyMediaManager-v0.x.x-linux-portable.zip -d ~/pyMediaManager

# Or extract to USB drive for portable use
unzip pyMediaManager-v0.x.x-linux-portable.zip -d /media/usb/pyMediaManager
```

#### Directory Structure

```text
pyMediaManager/
├── pymm                    # Launch script
├── app/                    # Application code
├── config/                 # Configuration files
├── plugins/                # Plugin directory
├── python/                 # Bundled Python 3.13
└── README.md
```

#### Running Portable Version

```bash
# Navigate to directory
cd ~/pyMediaManager

# Run application
./pymm

# Or run directly
~/pyMediaManager/pymm
```

**Portable Mode**: When run from USB or external drive, pyMediaManager automatically:

- Stores config on the portable drive
- Detects drive reconnection
- Maintains portable project paths

---

## 🔐 Permissions & udev Rules

### USB Device Detection

For automatic USB device detection, pyMediaManager requires udev rules installation.

#### What are udev Rules?

udev rules allow pyMediaManager to:

- **Detect USB storage devices** automatically
- **Notify when drives connect/disconnect**
- **Identify master/backup drives** for Storage Groups
- **Trigger sync operations** on drive connection

#### Installation via GUI

1. **Open pyMediaManager**
2. **Settings** → **Advanced** → **USB Device Detection**
3. **Click "Install udev Rules"**
4. **Enter password** when prompted (pkexec elevation)
5. **Verify installation** - Status should show "✅ Installed"

#### Installation via CLI

```bash
# Run with pkexec GUI elevation
pkexec sh -c 'cat > /etc/udev/rules.d/99-pymm-usb.rules << EOF
# pyMediaManager USB Storage Detection Rules
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="disk", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="partition", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", \
    GROUP="plugdev", MODE="0660"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger'
```

#### Verify Installation

```bash
# Check if rules file exists
ls -l /etc/udev/rules.d/99-pymm-usb.rules

# Should output:
# -rw-r--r-- 1 root root 542 Jan 17 10:30 /etc/udev/rules.d/99-pymm-usb.rules

# Test USB detection
# Plug in USB drive, then check:
dmesg | tail -20  # Should show USB device detection
```

#### Add User to plugdev Group

For proper USB device access:

```bash
# Add current user to plugdev group
sudo usermod -aG plugdev $USER

# Log out and log back in for changes to take effect
# Or use:
newgrp plugdev

# Verify group membership
groups | grep plugdev
```

#### Uninstall udev Rules

```bash
# Via GUI: Settings → Advanced → "Uninstall udev Rules"

# Via CLI:
sudo rm /etc/udev/rules.d/99-pymm-usb.rules
sudo udevadm control --reload-rules
```

---

## 🐍 Python Environment Management

### Using pyenv (Recommended for Multiple Python Versions)

```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to ~/.bashrc or ~/.zshrc
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
source ~/.bashrc

# Install Python 3.13
pyenv install 3.13.0

# Set as global default
pyenv global 3.13.0

# Verify
python --version  # Should show Python 3.13.0
```

### Using UV Package Manager

UV is pyMediaManager's recommended package manager (10-100x faster than pip):

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv --python 3.13

# Activate environment
source .venv/bin/activate

# Install dependencies
uv sync

# Run pyMediaManager
uv run python -m app.main
```

---

## 🖥️ Display & Desktop Environment

### X11 vs Wayland

pyMediaManager supports both X11 and Wayland display servers:

| Feature | X11 | Wayland |
| --- | --- | --- |
| **Stability** | ✅ Excellent | ⚠️ Good (some bugs) |
| **Performance** | ✅ Good | ✅ Better |
| **Compatibility** | ✅ Universal | ⚠️ Newer |
| **Screen Capture** | ✅ Works | ⚠️ Limited |

**Force X11** (if Wayland has issues):

```bash
# Edit ~/.xinitrc or display manager config
export QT_QPA_PLATFORM=xcb

# Or run with X11:
QT_QPA_PLATFORM=xcb ./pyMediaManager-x86_64.AppImage
```

### Qt Platform Plugins

If you see `Could not load the Qt platform plugin` error:

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0

# Fedora
sudo dnf install xcb-util-cursor

# Arch
sudo pacman -S xcb-util-cursor
```

---

## 🔧 Troubleshooting

### Application Won't Start

#### Error: `python3.13: command not found`

**Solution**: Install Python 3.13 (see Python Environment Management section below)

```bash
# Check installed Python versions
ls /usr/bin/python*

# If Python 3.13 not installed, use AppImage instead
```

#### Error: `ImportError: No module named 'PySide6'`

**Solution**: Install dependencies

```bash
# If using UV
uv sync

# If using pip
pip install -r requirements.txt
```

#### Error: `qt.qpa.plugin: Could not load the Qt platform plugin`

**Solution**: Install Qt dependencies

```bash
# Ubuntu/Debian
sudo apt install libxcb-xinerama0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
                 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0

# Fedora
sudo dnf install xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil

# Arch
sudo pacman -S xcb-util-cursor xcb-util-image xcb-util-keysyms xcb-util-renderutil
```

---

### USB Device Detection Not Working

#### Error: Drives not detected automatically

**Solution 1**: Install udev rules (see Permissions & udev Rules section above)

**Solution 2**: Check plugdev group membership

```bash
# Verify you're in plugdev group
groups | grep plugdev

# If not, add yourself
sudo usermod -aG plugdev $USER

# Log out and back in
```

**Solution 3**: Check udev service

```bash
# Verify udev is running
systemctl status systemd-udevd

# If not running, start it
sudo systemctl start systemd-udevd
```

---

### Permission Denied Errors

#### Error: `PermissionError: [Errno 13] Permission denied`

**Solution**: Check file permissions

```bash
# For AppImage
chmod +x pyMediaManager-x86_64.AppImage

# For portable installation
chmod +x ~/pyMediaManager/pymm

# For config directory
chmod -R u+rw ~/.config/pyMediaManager/
```

---

### Display Issues

#### Error: Window appears blank or black

**Solution 1**: Update graphics drivers

```bash
# Intel
sudo apt install intel-media-va-driver  # Ubuntu/Debian
sudo dnf install intel-media-driver     # Fedora

# AMD
sudo apt install mesa-vulkan-drivers    # Ubuntu/Debian
sudo dnf install mesa-vulkan-drivers    # Fedora

# NVIDIA
# Install proprietary drivers via distribution's driver manager
```

**Solution 2**: Try software rendering

```bash
# Force software rendering
QT_QUICK_BACKEND=software ./pyMediaManager-x86_64.AppImage
```

#### Error: High DPI scaling issues

**Solution**: Set Qt scaling

```bash
# Enable automatic scaling
export QT_AUTO_SCREEN_SCALE_FACTOR=1

# Or set manual scale factor
export QT_SCALE_FACTOR=1.5

# Run application
./pyMediaManager-x86_64.AppImage
```

---

### AppImage-Specific Issues

#### Error: `AppImages require FUSE to run`

**Solution**: Install FUSE

```bash
# Ubuntu/Debian
sudo apt install fuse libfuse2

# Fedora
sudo dnf install fuse fuse-libs

# Arch
sudo pacman -S fuse2
```

**Alternative**: Extract AppImage

```bash
# Extract AppImage contents
./pyMediaManager-x86_64.AppImage --appimage-extract

# Run directly
./squashfs-root/AppRun
```

#### Error: AppImage won't execute

**Solution**: Check file system mount options

```bash
# Check if mounted with noexec
mount | grep $(df . | tail -1 | awk '{print $1}')

# If noexec, remount with exec
sudo mount -o remount,exec /path/to/partition
```

---

### Network & Plugin Download Issues

#### Error: Plugin downloads fail

**Solution**: Check firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw status
sudo ufw allow out to any port 443  # HTTPS

# Fedora (firewalld)
sudo firewall-cmd --list-all
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

**Solution 2**: Configure proxy (if behind corporate firewall)

```bash
# Set environment variables
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"

# Or configure in pyMediaManager settings
Settings → Network → Proxy Configuration
```

---

### Performance Issues

#### Application feels slow

**Solution 1**: Disable real-time sync (if enabled)

```bash
# Settings → Storage Groups → Disable real-time sync
# Use scheduled or manual sync instead
```

**Solution 2**: Increase file descriptor limits

```bash
# Check current limits
ulimit -n

# Increase temporarily
ulimit -n 4096

# Increase permanently (add to /etc/security/limits.conf)
echo "$USER soft nofile 4096" | sudo tee -a /etc/security/limits.conf
echo "$USER hard nofile 4096" | sudo tee -a /etc/security/limits.conf
```

**Solution 3**: Use SSD for config directory

```bash
# Move config to SSD
mv ~/.config/pyMediaManager ~/.config/pyMediaManager.backup
mkdir -p /path/to/ssd/pyMediaManager
ln -s /path/to/ssd/pyMediaManager ~/.config/pyMediaManager
```

---

## 📚 Additional Resources

- **Installation Guide**: [docs/installation.md](installation.md)
- **Getting Started**: [docs/getting-started.md](getting-started.md)
- **Configuration**: [docs/configuration.md](configuration.md)
- **Platform Directories**: [docs/platform-directories.md](platform-directories.md)
- **Troubleshooting (General)**: [docs/troubleshooting.md](troubleshooting.md)
- **udev Technical Details**: [docs/linux-udev-installer.md](linux-udev-installer.md)

---

## 🆘 Getting Help

- **GitHub Issues**: [github.com/mosh666/pyMM/issues](https://github.com/mosh666/pyMM/issues)
- **Documentation**: [mosh666.github.io/pyMM](https://mosh666.github.io/pyMM/)

---

**Platform Comparison**: See [Windows Setup](windows-setup.md) and
[macOS Setup](macos-setup.md) for platform-specific features and installation
methods.
