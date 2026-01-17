# Build System Documentation

## Overview

pyMediaManager uses a comprehensive, cross-platform build system to create portable distributions for Windows, Linux,
and macOS. This document provides detailed information about the build process, architecture, requirements, and
troubleshooting.

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Build Process](#build-process)
  - [Windows Portable Builds](#windows-portable-builds)
  - [Linux AppImage Builds](#linux-appimage-builds)
  - [macOS App Bundle Builds](#macos-app-bundle-builds)
- [Platform-Specific Requirements](#platform-specific-requirements)
- [Build Automation](#build-automation)
- [Testing and Validation](#testing-and-validation)
- [Troubleshooting](troubleshooting.md)

---

## Architecture Overview

### Build System Components

```text
pyMediaManager Build System
│
├── scripts/
│   ├── build_manager.py          # Entry point - routes to platform builders
│   ├── build_windows.py          # Windows embeddable Python + MSI
│   ├── build_linux_appimage.py   # Linux AppImage with PyInstaller
│   ├── build_macos.py            # macOS .app bundle with PyInstaller
│   └── wix_generator.py          # WiX v4 MSI installer generator
│
├── justfile                      # Task automation recipes
│   ├── build                     # Build portable for current platform
│   ├── ci-docker-build           # Docker-based CI builds
│   └── test-portable             # Validate portable distributions
│
└── .github/workflows/
    └── build.yml                 # Multi-platform CI/CD pipeline
```

### Build Targets

| Platform | Formats | Python Versions | Architectures |
| -------- | ------- | --------------- | ------------- |
| **Windows** | ZIP (portable), MSI (installer) | 3.12, 3.13, 3.14 | amd64, arm64\* |
| **Linux** | AppImage | 3.12, 3.13, 3.14 | x86_64, aarch64\* |
| **macOS** | DMG (.app bundle) | 3.12, 3.13, 3.14 | x86_64 (Intel), arm64 (M-series) |

*arm64/aarch64 builds require native runners (not available in GitHub Actions standard runners)

### Key Features

- **Zero-dependency portable distributions** - Bundles Python runtime + UV package manager
- **Dynamic versioning** - Git tags → hatch-vcs → `_version.py` (PEP 517 compliant)
- **UV-first dependency management** - 10-100x faster than pip, lockfile-based reproducibility
- **Cross-platform automation** - Single `build_manager.py` entry point
- **CI/CD integration** - Automated builds, smoke tests, SLSA attestation

---

(build-process)=

## Build Process

(windows-portable-builds)=

### Windows Portable Builds

#### Overview

Windows builds use **embeddable Python** distributions from python.org, creating fully portable ZIP archives and
optional MSI installers. The build process downloads, configures, and bundles all dependencies with UV executable.

#### Workflow Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Download Embeddable Python                                      │
│    ├── python-3.13.1-embed-amd64.zip (python.org)                  │
│    └── Extract to python313/ directory                             │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Configure Python Environment                                    │
│    ├── Edit python313._pth (add lib-py313 to sys.path)             │
│    ├── Uncomment 'import site' to enable site-packages             │
│    └── Add win32/ and win32com/ paths for pywin32                  │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Install Dependencies with UV                                    │
│    ├── uv pip install hatchling hatch-vcs wheel                    │
│    │   --target lib-py313 --python python313/python.exe            │
│    ├── uv pip install . --no-build-isolation                       │
│    │   --target lib-py313 --python python313/python.exe            │
│    └── Result: All packages in lib-py313/                          │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Setup Platform-Specific Dependencies (Windows only)             │
│    ├── pywin32: Copy DLLs to python313/                            │
│    │   ├── pythoncom313.dll, pywintypes313.dll                     │
│    │   └── pythoncomloader313.dll, pywinloader313.dll              │
│    ├── Copy .py files (win32con.py, pythoncom.py, etc.)            │
│    └── Copy win32/ and win32com/ modules                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Bundle UV Executable                                            │
│    ├── Download uv-x86_64-pc-windows-msvc.zip                      │
│    └── Extract to bin/uv.exe                                       │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Cleanup Dependencies                                            │
│    ├── Remove tests/, docs/, examples/, __pycache__/               │
│    ├── Preserve qfluentwidgets/components/widgets/docs/ (needed)   │
│    └── Savings: ~100-150MB reduction                               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Verify Critical Imports                                         │
│    ├── Test: PySide6.QtWidgets, qfluentwidgets, pydantic           │
│    ├── Test: yaml, git (GitPython), wmi (Windows only)             │
│    └── Exit if any critical import fails                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 8. Create Distribution Archive                                     │
│    ├── ZIP: python313/, lib-py313/, app/, plugins/, config/        │
│    ├── Include: launcher.py, README.md, LICENSE, bin/uv.exe        │
│    ├── Output: pyMM-v0.2.0-py3.13-win-amd64.zip (~150-200MB)       │
│    └── Generate SHA256 checksum                                    │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 9. Optional: Generate MSI Installer (Python 3.13 only)             │
│    ├── Use WiX Toolset v4 + Jinja2 templates                       │
│    ├── Script: wix_generator.py (requires jinja2)                  │
│    ├── Template: wix_template.wxs.j2                               │
│    ├── Output: pyMM-v0.2.0-py3.13-win-amd64.msi                    │
│    └── Features: Desktop shortcut, Start Menu, Add/Remove Programs │
└─────────────────────────────────────────────────────────────────────┘
```

#### Build Commands

```bash
# Build with default settings (Python 3.13, amd64, ZIP only)
just build

# Build with custom parameters
python scripts/build_manager.py --version 3.13 --arch amd64 --format zip
python scripts/build_manager.py --version 3.13 --arch amd64 --format msi
python scripts/build_manager.py --version 3.13 --arch amd64 --format both

# Dry-run (validate without creating files)
python scripts/build_manager.py --version 3.13 --dry-run
```

#### File Structure (Portable Distribution)

```text
pyMediaManager-portable/
├── python313/                    # Embeddable Python runtime
│   ├── python.exe                # Python interpreter
│   ├── python313.dll             # Core runtime DLL
│   ├── python313._pth            # Module search path config
│   ├── pythoncom313.dll          # pywin32 COM support
│   ├── pywintypes313.dll         # pywin32 Windows types
│   └── ... (standard library ZIPs)
│
├── lib-py313/                    # All dependencies (--target install)
│   ├── PySide6/                  # Qt6 bindings
│   ├── qfluentwidgets/           # Fluent Design UI
│   ├── pydantic/                 # Data validation
│   ├── yaml/                     # YAML parsing
│   ├── git/                      # GitPython
│   ├── wmi/                      # Windows Management Instrumentation
│   └── ... (all dependencies)
│
├── bin/
│   └── uv.exe                    # Bundled UV package manager
│
├── app/                          # Application source code
│   ├── __init__.py
│   ├── _version.py               # Generated by hatch-vcs
│   ├── main.py
│   ├── core/, models/, platform/, plugins/, services/, ui/
│   └── ...
│
├── plugins/                      # Plugin manifests
│   ├── git-versioning/
│   ├── avid-mcp-transcoding/
│   └── ... (plugin directories)
│
├── config/                       # Default configuration
│   ├── app.yaml                  # Application settings
│   ├── storage_groups.yaml.example
│   └── user.yaml.example
│
├── launcher.py                   # Entry point (detects portable mode)
├── README.md                     # Usage instructions
├── LICENSE                       # MIT License
└── requirements-frozen-py313-amd64.txt  # Exact dependency versions
```

#### Critical Files

##### python313._pth (Module Search Path Configuration)

```text
python313.zip
.
../lib-py313
../lib-py313/win32
../lib-py313/win32/lib
../lib-py313/Pythonwin

# Uncomment to run site.py automatically
import site
```

##### Key Points

- `../lib-py313` added to sys.path for dependency resolution
- `import site` enabled for site-packages support
- win32 paths required for pywin32 COM modules

---

(linux-appimage-builds)=

### Linux AppImage Builds

#### Overview

Linux builds use **PyInstaller** to create standalone executables, packaged as **AppImages** for universal
compatibility across distributions. The process bundles Python runtime, all dependencies, and application code into a
single executable file.

#### Workflow Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Install System Dependencies                                     │
│    ├── Qt6 libraries: libgl1, libegl1, libglib2.0-0, libfontconfig1│
│    ├── XCB libraries: libxcb-icccm4, libxcb-image0, libxkbcommon-x11│
│    ├── AppImage runtime: fuse, libfuse2                            │
│    └── Linux-specific: pyudev (udev hardware detection)            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Install Build Tools with UV                                     │
│    ├── uv pip install --system pyinstaller>=6.0                    │
│    ├── uv pip install --system hatchling hatch-vcs                 │
│    └── uv pip install --system -e . (application dependencies)     │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Generate PyInstaller Spec File (pyMM.spec)                      │
│    ├── Entry point: launcher.py                                    │
│    ├── Data files: app/, plugins/, config/, README.md, LICENSE     │
│    ├── Hidden imports: PySide6, qfluentwidgets, pyudev             │
│    ├── Excludes: tkinter, matplotlib, numpy (reduce size)          │
│    └── Options: --onefile, --windowed, --name pyMM                 │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Run PyInstaller                                                 │
│    ├── pyinstaller --clean --noconfirm pyMM.spec                   │
│    ├── Collects all dependencies and runtime files                 │
│    ├── Output: dist/pyMM/ directory with standalone binary         │
│    └── Size: ~200-300MB (includes Qt6 + Python runtime)            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Create AppImage Directory Structure                             │
│    ├── pyMM.AppDir-x86_64/                                          │
│    │   ├── usr/bin/pyMM/ (PyInstaller output)                      │
│    │   ├── AppRun (bash launcher script)                           │
│    │   ├── pyMM.desktop (Desktop Entry spec v1.0)                  │
│    │   └── pyMM.png (256x256 application icon)                     │
│    └── Permissions: chmod +x AppRun                                │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Package as AppImage                                             │
│    ├── Download appimagetool-x86_64.AppImage                       │
│    ├── ./appimagetool pyMM.AppDir-x86_64 pyMM-x86_64.AppImage      │
│    ├── Compress: gzip -9 (optional, reduces size ~30%)             │
│    └── Output: pyMM-v0.2.0-py3.13-linux-x86_64.AppImage            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Generate SHA256 Checksum                                        │
│    └── sha256sum pyMM-*.AppImage > pyMM-*.sha256                   │
└─────────────────────────────────────────────────────────────────────┘
```

#### Build Commands

```bash
# Build AppImage (default: Python 3.13, x86_64)
just build

# Build with custom parameters
python scripts/build_manager.py --version 3.13 --arch x86_64

# Manual PyInstaller build
pyinstaller --clean --noconfirm pyMM.spec
```

#### AppImage Structure

```text
pyMM.AppDir-x86_64/
├── usr/
│   └── bin/
│       └── pyMM/                 # PyInstaller bundle
│           ├── pyMM              # Main executable
│           ├── _internal/        # Dependencies and runtime
│           │   ├── PySide6/
│           │   ├── qfluentwidgets/
│           │   ├── libpython3.13.so.1.0
│           │   └── ... (all dependencies)
│           └── app/              # Application code
│
├── AppRun                        # Launcher script
├── pyMM.desktop                  # Desktop integration
└── pyMM.png                      # Application icon (256x256)
```

##### AppRun Script Example

```bash
#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
export LD_LIBRARY_PATH="$APPDIR/usr/lib:$LD_LIBRARY_PATH"
exec "$APPDIR/usr/bin/pyMM/pyMM" "$@"
```

##### pyMM.desktop Example

```ini
[Desktop Entry]
Name=pyMediaManager
Comment=Cross-platform media management application
Exec=pyMM
Icon=pyMM
Type=Application
Categories=Utility;AudioVideo;
Terminal=false
```

---

(macos-app-bundle-builds)=

### macOS App Bundle Builds

#### Overview

macOS builds use **PyInstaller** to create `.app` bundles, distributed as DMG disk images. The process includes
macOS-specific frameworks (pyobjc) for native disk management and system integration.

#### Workflow Diagram

```text
┌─────────────────────────────────────────────────────────────────────┐
│ 1. Install Build Tools with UV                                     │
│    ├── uv pip install --system pyinstaller>=6.0                    │
│    ├── uv pip install --system hatchling hatch-vcs                 │
│    └── uv pip install --system -e . (with macOS dependencies)      │
│         └── pyobjc-framework-DiskArbitration>=10.1                 │
│         └── pyobjc-framework-Cocoa>=10.1                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 2. Generate PyInstaller Spec File (pyMM.spec)                      │
│    ├── Entry point: launcher.py                                    │
│    ├── Data files: app/, plugins/, config/, README.md, LICENSE     │
│    ├── Hidden imports: PySide6, qfluentwidgets, pyobjc frameworks  │
│    ├── Options: --windowed, --name pyMediaManager                  │
│    └── Icon: resources/pyMM.icns (macOS icon format)               │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 3. Run PyInstaller                                                 │
│    ├── pyinstaller --clean --noconfirm pyMM.spec                   │
│    ├── Output: dist/pyMediaManager.app/                            │
│    └── Size: ~200-300MB (includes Qt6 + Python runtime)            │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 4. Code Signing (Optional - Requires Developer Certificate)        │
│    ├── codesign --deep --force --verify --verbose                  │
│    │   --sign "Developer ID Application: Your Name"                │
│    │   pyMediaManager.app                                          │
│    └── Note: Required for distribution outside App Store           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 5. Create DMG Disk Image                                           │
│    ├── hdiutil create -volname "pyMediaManager"                    │
│    │   -srcfolder dist/pyMediaManager.app                          │
│    │   -ov -format UDZO pyMM-v0.2.0-py3.13-macos-arm64.dmg         │
│    ├── Optional: Add background image, custom icon layout          │
│    └── Output: ~150-200MB compressed DMG                           │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 6. Notarization (Optional - Requires Apple Developer Account)      │
│    ├── xcrun notarytool submit pyMM.dmg --wait                     │
│    ├── xcrun stapler staple pyMM.dmg                               │
│    └── Note: Required for Gatekeeper approval on macOS 10.15+      │
└─────────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│ 7. Generate SHA256 Checksum                                        │
│    └── shasum -a 256 pyMM-*.dmg > pyMM-*.sha256                    │
└─────────────────────────────────────────────────────────────────────┘
```

#### Build Commands

```bash
# Build DMG (default: Python 3.13, architecture auto-detected)
just build

# Build with custom parameters
python scripts/build_manager.py --version 3.13 --arch arm64 --format dmg
python scripts/build_manager.py --version 3.13 --arch x86_64 --format dmg

# Manual PyInstaller build
pyinstaller --clean --noconfirm pyMM.spec
hdiutil create -volname "pyMediaManager" -srcfolder dist/pyMediaManager.app \
  -ov -format UDZO pyMM.dmg
```

#### App Bundle Structure

```text
pyMediaManager.app/
├── Contents/
│   ├── Info.plist                # Bundle metadata (version, identifier)
│   ├── MacOS/
│   │   └── pyMediaManager        # Main executable
│   ├── Resources/
│   │   ├── pyMM.icns             # Application icon
│   │   ├── app/                  # Application code
│   │   ├── plugins/              # Plugin manifests
│   │   └── config/               # Default configuration
│   └── Frameworks/               # Dependencies
│       ├── libpython3.13.dylib
│       ├── QtCore.framework/
│       ├── QtWidgets.framework/
│       └── ... (all dependencies)
```

---

(platform-specific-requirements)=

## Platform-Specific Requirements

### Windows Build Requirements

#### Software

| Tool              | Version              | Purpose                              | Installation                                               |
|-------------------|----------------------|--------------------------------------|------------------------------------------------------------|
| **Python**        | 3.12, 3.13, or 3.14  | Build script runtime                 | [python.org](https://www.python.org/)                      |
| **UV**            | Latest               | Dependency management                | `curl -LsSf https://astral.sh/uv/install.sh \| sh`         |
| **Git**           | Any recent           | Version detection (hatch-vcs)        | [git-scm.com](https://git-scm.com/)                        |
| **WiX Toolset**   | v4.x                 | MSI installer generation             | `dotnet tool install --global wix`                         |

#### Build Environment

- **OS:** Windows 10/11 (x64 or ARM64)
- **PowerShell:** 5.1+ or PowerShell Core 7+
- **Disk Space:** ~2GB per Python version (embeddable + dependencies)
- **Internet:** Required for downloading embeddable Python and UV

#### Python Dependencies

```bash
# Install build dependencies
uv pip install hatchling hatch-vcs jinja2 wheel packaging

# For MSI generation
dotnet tool install --global wix
```

#### Embeddable Python URLs

##### Python 3.12.8

- amd64: `https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip`
- arm64: `https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-arm64.zip`

##### Python 3.13.1

- amd64: `https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip`
- arm64: `https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-arm64.zip`

##### Python 3.14.0

- amd64: `https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-amd64.zip`
- arm64: `https://www.python.org/ftp/python/3.14.0/python-3.14.0-embed-arm64.zip`

---

### Linux Build Requirements

#### Software

| Tool | Version | Purpose | Installation |
| ---- | ------- | ------- | ------------ |
| **Python** | 3.12, 3.13, or 3.14 | Build script runtime | System package manager or [python.org](https://www.python.org/) |
| **UV** | Latest | Dependency management | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **PyInstaller** | ≥6.0 | Standalone executable creation | `uv pip install pyinstaller` |
| **appimagetool** | Latest | AppImage packaging | [AppImage releases](https://github.com/AppImage/AppImageKit/releases) |
| **Git** | Any recent | Version detection (hatch-vcs) | `sudo apt install git` |

#### System Dependencies (Debian/Ubuntu)

```bash
# Qt6 and X11 libraries
sudo apt-get update
sudo apt-get install -y \
    libgl1 libegl1 libglib2.0-0 libfontconfig1 \
    libxkbcommon-x11-0 libdbus-1-3 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-xinput0 libxcb-xfixes0 libx11-xcb1 \
    fuse libfuse2

# Python build tools
sudo apt-get install -y \
    python3-dev build-essential
```

#### Build Environment

- **OS:** Ubuntu 20.04+ or equivalent (glibc 2.31+)
- **Disk Space:** ~3GB (PyInstaller build artifacts + dependencies)
- **Internet:** Required for downloading appimagetool

#### AppImage Tool Setup

```bash
# Download appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Optional: Extract to avoid FUSE requirement
./appimagetool-x86_64.AppImage --appimage-extract
mv squashfs-root appimagetool
```

---

### macOS Build Requirements

#### Software

| Tool | Version | Purpose | Installation |
| ---- | ------- | ------- | ------------ |
| **Python** | 3.12, 3.13, or 3.14 | Build script runtime | [python.org](https://www.python.org/) or Homebrew |
| **UV** | Latest | Dependency management | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **PyInstaller** | ≥6.0 | .app bundle creation | `uv pip install pyinstaller` |
| **Xcode Command Line Tools** | Latest | Native compilation (pyobjc) | `xcode-select --install` |
| **Git** | Any recent | Version detection (hatch-vcs) | Included with Xcode CLT |

#### Build Environment

- **OS:** macOS 11+ (Big Sur or later)
- **Architecture:** x86_64 (Intel) or arm64 (M-series)
- **Disk Space:** ~3GB (PyInstaller build artifacts + dependencies)
- **Developer Account:** Optional (required for code signing/notarization)

#### Code Signing (Optional)

```bash
# List available certificates
security find-identity -v -p codesigning

# Sign .app bundle
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name (TEAM_ID)" \
  --options runtime \
  --entitlements entitlements.plist \
  dist/pyMediaManager.app

# Verify signature
codesign --verify --deep --strict --verbose=2 dist/pyMediaManager.app
spctl -a -vvv -t install dist/pyMediaManager.app
```

#### Notarization (Optional)

```bash
# Create app-specific password: appleid.apple.com

# Store credentials
xcrun notarytool store-credentials "notarytool-profile" \
  --apple-id "your@email.com" \
  --team-id "TEAM_ID" \
  --password "app-specific-password"

# Submit for notarization
xcrun notarytool submit pyMM.dmg --keychain-profile "notarytool-profile" --wait

# Staple ticket (after approval)
xcrun stapler staple pyMM.dmg
```

---

(build-automation)=

## Build Automation

### Just Recipes

#### Development Builds

```bash
# Build for current platform (default Python 3.13)
just build

# Build with specific Python version
just build 3.14

# Build with custom parameters
python scripts/build_manager.py --version 3.13 --arch amd64 --format both
```

#### CI/CD Pipeline

```bash
# Build Docker CI image
just ci-docker-build 3.13

# Run full CI pipeline in Docker
just ci-docker-test

# Build all Python versions (3.12, 3.13, 3.14)
just ci-docker-build-all
```

### GitHub Actions Workflow

**.github/workflows/build.yml** automates multi-platform builds with smoke tests:

#### Triggers

- **Git tags:** `v*` (e.g., `v0.2.0`, `v1.0.0-beta.5`)
- **Manual dispatch:** `workflow_dispatch` with optional version override
- **Workflow call:** Invoked by release workflows

#### Build Matrix

```yaml
strategy:
  matrix:
    # Windows
    python-version: ["3.12", "3.13", "3.14"]
    arch: ["amd64"]  # arm64 excluded (no GitHub ARM runners)

    # Linux
    python-version: ["3.12", "3.13", "3.14"]
    arch: ["x86_64"]  # aarch64 excluded

    # macOS
    python-version: ["3.12", "3.13", "3.14"]
    arch: ["x86_64", "arm64"]
    runner:
      - macos-15-intel  # x86_64 builds
      - macos-latest    # arm64 builds (M-series)
```

#### Smoke Tests

##### Windows

```powershell
# Extract portable ZIP
Expand-Archive pyMM-*.zip -DestinationPath test_portable

# Test launcher
cd test_portable
python313\python.exe launcher.py --version

# Verify UV bundled
if (-not (Test-Path "bin\uv.exe")) {
    Write-Error "UV executable not found"
    exit 1
}

# Test critical imports
python313\python.exe -c "import PySide6.QtWidgets; import qfluentwidgets"
```

##### Linux

```bash
# Make AppImage executable
chmod +x pyMM-*.AppImage

# Test --version flag
./pyMM-*.AppImage --version

# Verify file size (should be >10MB)
size=$(stat -c%s pyMM-*.AppImage)
if [ "$size" -lt 10000000 ]; then
    echo "Error: AppImage too small"
    exit 1
fi
```

##### macOS

```bash
# Mount DMG
hdiutil attach pyMM-*.dmg -nobrowse -mountpoint /Volumes/pyMediaManager

# Verify .app bundle
if [ -d "/Volumes/pyMediaManager/pyMediaManager.app" ]; then
    # Test --version
    /Volumes/pyMediaManager/pyMediaManager.app/Contents/MacOS/pyMediaManager --version

    # Unmount
    hdiutil detach /Volumes/pyMediaManager -force
else
    echo "Error: .app bundle not found"
    exit 1
fi
```

---

(testing-and-validation)=

## Testing and Validation

### Portable Build Testing

#### Just Recipes (Local Testing)

```bash
# Test portable build (after building)
just test-portable 3.13

# Test all Python versions
just test-portable-all
```

#### Test Script (scripts/test_portable_build.py)

The test script validates portable distributions:

1. **Extract Distribution**
   - Unzip/extract to temporary directory
   - Verify directory structure

2. **Verify UV Bundled**
   - Check `bin/uv.exe` (Windows) or `bin/uv` (Linux/macOS) exists
   - Test `uv --version` command

3. **Test Launcher**
   - Run `launcher.py --version`
   - Verify version output matches expected format
   - Confirm portable mode detection (sys.path includes `lib-py313/`)

4. **Validate Critical Imports**
   - PySide6.QtWidgets (GUI framework)
   - qfluentwidgets (Fluent Design components)
   - pydantic (data validation)
   - yaml (configuration parsing)
   - git (GitPython - version control)
   - Platform-specific:
     - Windows: `wmi` (storage detection)
     - Linux: `pyudev` (udev hardware management)
     - macOS: `DiskArbitration` (disk management)

5. **Check Dependency Sizes**
   - Verify dependencies cleaned (no tests/, docs/ directories)
   - Validate total size within expected range (150-300MB)

#### Manual Testing Checklist

##### Windows Portable

- [ ] Extract ZIP to USB drive (e.g., E:\pyMM\)
- [ ] Run `launcher.py` (double-click or `python313\python.exe launcher.py`)
- [ ] Check UV available: `bin\uv.exe --version`
- [ ] Test first-run wizard appears
- [ ] Configure storage group (test drive detection)
- [ ] Create test project
- [ ] Verify all UI elements render correctly
- [ ] Test plugin loading (check plugin manager)
- [ ] Exit and verify settings saved to `config/user.yaml`

##### Linux AppImage

- [ ] Copy AppImage to USB drive or local directory
- [ ] Make executable: `chmod +x pyMM-*.AppImage`
- [ ] Run: `./pyMM-*.AppImage`
- [ ] Test first-run wizard
- [ ] Verify drive detection (udisks2 required)
- [ ] Create test project
- [ ] Check plugin system
- [ ] Test without FUSE (extract with `--appimage-extract`)

##### macOS DMG

- [ ] Open DMG (double-click)
- [ ] Drag pyMediaManager.app to Applications
- [ ] Run from Launchpad or Applications folder
- [ ] Allow first-run security prompt (right-click > Open)
- [ ] Test first-run wizard
- [ ] Verify disk detection (diskutil integration)
- [ ] Create test project
- [ ] Check plugin system

---

## Troubleshooting

### Common Issues

#### Windows

##### Issue: "Python was not found"

- **Cause:** Embeddable Python not extracted correctly
- **Solution:** Verify `python313/python.exe` exists, re-extract ZIP

##### Issue: "ImportError: DLL load failed"

- **Cause:** Missing pywin32 DLLs or incorrect `._pth` configuration
- **Solution:**
  - Check `python313._pth` includes `../lib-py313` and `import site` is uncommented
  - Verify `pythoncom313.dll` and `pywintypes313.dll` in `python313/`
  - Run: `python313\python.exe -c "import win32com.client"` to test

##### Issue: MSI build fails with "WiX not found"

- **Cause:** WiX Toolset v4 not installed or not in PATH
- **Solution:**

  ```powershell
  dotnet tool install --global wix
  wix --version  # Verify installation
  ```

##### Issue: UV executable not bundled

- **Cause:** Network error during download or extraction failure
- **Solution:** Manually download from [UV releases][uv-rel] and place in `bin/uv.exe`

[uv-rel]: https://github.com/astral-sh/uv/releases

#### Linux

##### Issue: "AppImage cannot be mounted"

- **Cause:** FUSE not available or not configured
- **Solution:**

  ```bash
  # Install FUSE
  sudo apt install fuse libfuse2

  # OR extract without FUSE
  ./pyMM-*.AppImage --appimage-extract
  ./squashfs-root/AppRun
  ```

##### Issue: "Qt platform plugin could not be initialized"

- **Cause:** Missing Qt6 system libraries or X11 dependencies
- **Solution:**

  ```bash
  # Install Qt6 dependencies
  sudo apt install libgl1 libegl1 libxcb-xinerama0 libxkbcommon-x11-0

  # Set Qt platform (if no display server)
  export QT_QPA_PLATFORM=offscreen
  ```

##### Issue: "libpython3.13.so.1.0: cannot open shared object file"

- **Cause:** PyInstaller didn't bundle Python shared library correctly
- **Solution:** Rebuild with `--hidden-import` flags for missing modules

##### Issue: PyInstaller build fails with "No module named 'pyudev'"

- **Cause:** Linux-specific dependencies not installed
- **Solution:**

  ```bash
  uv pip install --system pyudev>=0.24.1
  # Rebuild
  ```

#### macOS

##### Issue: "pyMediaManager.app is damaged and can't be opened"

- **Cause:** Gatekeeper blocking unsigned app
- **Solution:**

  ```bash
  # Remove quarantine attribute
  xattr -cr /Applications/pyMediaManager.app

  # OR right-click > Open (first launch only)
  ```

##### Issue: "ImportError: No module named 'DiskArbitration'"

- **Cause:** pyobjc frameworks not bundled by PyInstaller
- **Solution:** Add to hidden imports in `pyMM.spec`:

  ```python
  hiddenimports=[
      'objc',
      'DiskArbitration',
      'Cocoa',
  ]
  ```

##### Issue: DMG creation fails with "Resource busy"

- **Cause:** Previous DMG mount not detached
- **Solution:**

  ```bash
  # Force unmount all pyMediaManager volumes
  hdiutil detach /Volumes/pyMediaManager -force

  # Retry DMG creation
  ```

##### Issue: Code signing fails with "errSecInternalComponent"

- **Cause:** Keychain locked or certificate expired
- **Solution:**

  ```bash
  # Unlock keychain
  security unlock-keychain ~/Library/Keychains/login.keychain-db

  # Verify certificate validity
  security find-identity -v -p codesigning
  ```

### Build Script Debugging

#### Enable Verbose Logging

##### Windows

```powershell
# Set environment variable
$env:PYMM_BUILD_DEBUG = "1"
python scripts/build_manager.py --version 3.13 --arch amd64
```

##### Linux/macOS

```bash
export PYMM_BUILD_DEBUG=1
python scripts/build_manager.py --version 3.13 --arch x86_64
```

#### Dry-Run Mode

Test build parameters without creating files:

```bash
python scripts/build_manager.py --version 3.13 --dry-run
```

#### Manual Build Steps

##### Windows (Step-by-Step)

```powershell
# 1. Download embeddable Python
Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.13.1/python-3.13.1-embed-amd64.zip" -OutFile "python.zip"
Expand-Archive -Path "python.zip" -DestinationPath "python313"

# 2. Configure _pth file
$pthFile = "python313\python313._pth"
$content = Get-Content $pthFile
$content = $content -replace "#import site", "import site"
$content += "`n../lib-py313"
Set-Content -Path $pthFile -Value $content

# 3. Install dependencies
uv pip install hatchling hatch-vcs wheel --target lib-py313 --python python313\python.exe
uv pip install . --no-build-isolation --target lib-py313 --python python313\python.exe

# 4. Test imports
python313\python.exe -c "import sys; print('\n'.join(sys.path))"
python313\python.exe -c "import PySide6.QtWidgets; import qfluentwidgets; print('OK')"
```

### Dependency Conflicts

#### Issue: Version conflicts during `uv pip install`

- **Solution:** Check `uv.lock` for pinned versions, regenerate if needed:

  ```bash
  uv lock --upgrade
  uv sync --all-extras
  ```

#### Issue: "No matching distribution found for PySide6"

- **Cause:** Unsupported Python version or architecture
- **Solution:** Verify Python version compatibility:

  ```bash
  python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
  # PySide6 requires Python 3.8-3.13 (check pyproject.toml for exact requirements)
  ```

### CI/CD Issues

#### Issue: GitHub Actions build fails with "Out of disk space"

- **Solution:** Add cleanup steps before build:

  ```yaml
  - name: Free disk space
    run: |
      sudo rm -rf /usr/local/lib/android
      sudo rm -rf /opt/hostedtoolcache/CodeQL
      df -h
  ```

#### Issue: Smoke test fails in CI but passes locally

- **Cause:** Different environment (headless CI, missing display server)
- **Solution:** Set `QT_QPA_PLATFORM=offscreen` for Linux, use `xvfb` for GUI tests:

  ```yaml
  - name: Run smoke test
    run: |
      export QT_QPA_PLATFORM=offscreen
      xvfb-run --auto-servernum python scripts/test_portable_build.py
  ```

---

## Advanced Topics

### Cross-Compilation

#### Windows → Linux (via Docker)

```bash
# Build Linux AppImage from Windows using Docker
docker run --rm -v ${PWD}:/workspace -w /workspace \
  python:3.13-slim bash -c "
    apt-get update && apt-get install -y fuse libfuse2
    pip install uv
    uv pip install --system pyinstaller hatchling hatch-vcs
    python scripts/build_manager.py --version 3.13 --arch x86_64
  "
```

### Custom Build Configurations

#### Exclude Specific Plugins

```python
# In build_windows.py or build_linux_appimage.py
EXCLUDE_PLUGINS = ["avid-mcp-transcoding"]

def copy_plugins(dest):
    for plugin in Path("plugins").iterdir():
        if plugin.name not in EXCLUDE_PLUGINS:
            shutil.copytree(plugin, dest / plugin.name)
```

#### Bundle Custom Python Packages

```bash
# Add extra packages to lib-py313/
uv pip install --target lib-py313 --python python313/python.exe pillow requests
```

### Reducing Build Size

#### Aggressive Cleanup

```python
# In cleanup_dependencies() function
REMOVE_PATTERNS = [
    "**/__pycache__",
    "**/tests",
    "**/test",
    "**/docs",
    "**/examples",
    "**/*.dist-info/RECORD",
    "**/*.pyx",  # Cython source files
    "**/*.pxd",
    "**/*.c",    # C source files (if already compiled)
]
```

#### Strip Debug Symbols (Linux/macOS)

```bash
# After PyInstaller build
find dist/pyMM/_internal -name "*.so" -exec strip {} \;  # Linux
find dist/pyMediaManager.app/Contents/Frameworks -name "*.dylib" -exec strip -x {} \;  # macOS
```

---

## References

### Official Documentation

- **UV Package Manager:** [docs.astral.sh/uv](https://docs.astral.sh/uv/)
- **Hatchling Build Backend:** [hatch.pypa.io](https://hatch.pypa.io/)
- **PyInstaller:** [pyinstaller.org](https://pyinstaller.org/)
- **WiX Toolset v4:** [wixtoolset.org/docs/intro](https://wixtoolset.org/docs/intro/)
- **AppImage:** [docs.appimage.org](https://docs.appimage.org/)

### Project Resources

- **Build Scripts:** `scripts/build_*.py`
- **CI/CD Workflow:** `.github/workflows/build.yml`
- **Justfile Recipes:** `justfile` (build, test-portable, ci-docker-*)
- **Developer Guide:** `docs/getting-started-dev.md`

### Related Documentation

- [Installation Guide](installation.md) - End-user installation instructions
- [Windows Setup](windows-setup.md) - Windows-specific configuration
- [Linux Setup](linux-udev-installer.md) - Linux udev rules and permissions
- [macOS Setup](macos-setup.md) - macOS disk permissions and security

---

## Version History

- **v1.0.0** (January 2026) - Initial build system documentation
  - Windows embeddable Python workflow
  - Linux AppImage process
  - macOS DMG creation
  - CI/CD integration guide
  - Troubleshooting section
