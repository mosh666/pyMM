<!-- markdownlint-disable MD013 MD031 MD040 MD051 MD060 -->

<div align="center">

# pyMediaManager

## 🎬 Cross-Platform Portable Media Management Application

[![Python](https://img.shields.io/badge/Python-3.12%20|%203.13%20|%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/mosh666/pyMM?style=flat&color=blue)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-0078D6?style=flat&logo=windows)](https://github.com/mosh666/pyMM)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python)

[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mosh666/pyMM/branch/main/graph/badge.svg)](https://codecov.io/gh/mosh666/pyMM)
[![Stable Release](https://img.shields.io/github/v/release/mosh666/pyMM?label=stable&color=success)](https://github.com/mosh666/pyMM/releases/latest)
[![Beta Release](https://img.shields.io/github/v/release/mosh666/pyMM?include_prereleases&label=beta&color=orange)](https://github.com/mosh666/pyMM/releases)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

<p align="left">
<b>pyMediaManager (pyMM)</b> is a fully portable, cross-platform media management application designed to run entirely from USB drives without system installation. Built with PySide6 and a modern Fluent Design interface, it offers professional-grade tools for organizing media projects across <b>Windows, Linux, and macOS</b>. It features an extensible plugin system with unified, platform-aware drive detection and storage management.
</p>

---

## ✨ Features

- **🎨 Modern Fluent UI** - Responsive interface built with PySide6 and QFluentWidgets.
- **💾 100% Portable** - Runs from external drives with zero system footprint on any supported OS.
- **🔌 Extensible Plugin System** - manage external tools (Git, FFmpeg, ExifTool) via YAML manifests.
- **⚡ Smart Drive Detection** - Unified storage API supporting:
  - **Windows:** WMI / Win32 APIs
  - **Linux:** udisks2 / sysfs
  - **macOS:** diskutil / IOKit
- **📁 Project Management** - Metadata-rich project organization with templates and Git integration.

---

## 🚀 Quick Start

### 📦 Download & Installation

pyMediaManager provides portable distributions for Windows, Linux, and macOS. Download the latest release from [GitHub Releases](https://github.com/mosh666/pyMM/releases).

#### Windows (Portable ZIP)

**Recommended:** Python 3.13 for x64 systems

1. **Download:**
   - **Intel/AMD (x64):** `pyMM-v{VERSION}-py3.13-win-amd64.zip` (most Windows PCs)
   - **ARM64:** `pyMM-v{VERSION}-py3.13-win-arm64.zip` (Surface Pro X, ARM-based Windows devices)

2. **Extract** to your preferred location (e.g., `D:\pyMM\`)

3. **Run:**
   ```powershell
   # For AMD64/x64 systems:
   .\python313\python.exe launcher.py

   # For ARM64 systems:
   .\python313-arm64\python.exe launcher.py

   # Option 2: Create a shortcut with target:
   D:\pyMM\python313\python.exe D:\pyMM\launcher.py
   # (or python313-arm64\python.exe for ARM64)
   ```

4. **First Launch:** Complete the setup wizard to configure your workspace

**Verification (PowerShell):**
```powershell
(Get-FileHash -Path pyMM-*.zip -Algorithm SHA256).Hash -eq (Get-Content pyMM-*.sha256)
```

---

#### Linux (AppImage)

**Recommended:** Python 3.13 for x86_64 systems

1. **Download:**
   - **x86_64 (Intel/AMD):** `pyMM-v{VERSION}-py3.13-x86_64.AppImage`
   - **ARM64 (Raspberry Pi, ARM servers):** `pyMM-v{VERSION}-py3.13-aarch64.AppImage`

2. **Make Executable & Run:**
   ```bash
   chmod +x pyMM-*.AppImage
   ./pyMM-*.AppImage
   ```

3. **Optional - Desktop Integration:**
   ```bash
   # Create desktop menu entry
   ./pyMM-*.AppImage --appimage-install

   # Uninstall desktop entry
   ./pyMM-*.AppImage --appimage-uninstall
   ```

**Verification:**
```bash
sha256sum -c pyMM-*.sha256
```

**Portable Usage:**

- Copy AppImage to USB drive or any directory
- Run directly - no installation required
- All settings stored in `~/.config/pyMediaManager/` or `$XDG_CONFIG_HOME`

**System Requirements:**

- FUSE 2 or FUSE 3 (usually pre-installed)
- Qt dependencies (bundled, but may need system libs on minimal distros)

---

#### macOS (DMG)

**Recommended:** Python 3.13

1. **Download:**
   - **Intel Macs (x86_64):** `pyMM-v{VERSION}-py3.13-macos-x86_64.dmg`
   - **Apple Silicon (M1/M2/M3 - arm64):** `pyMM-v{VERSION}-py3.13-macos-arm64.dmg`

2. **Install:**
   - Open the DMG file
   - Drag `pyMediaManager.app` to your **Applications** folder

3. **First Launch (Gatekeeper Bypass):**
   ```bash
   # Option 1: Right-click → Open (bypasses Gatekeeper)

   # Option 2: Command line
   xattr -cr /Applications/pyMediaManager.app
   open /Applications/pyMediaManager.app
   ```

4. **Portable Usage:**
   - Copy `.app` bundle to USB drive or any folder
   - Run from Finder or terminal

**Verification:**
```bash
shasum -a 256 -c pyMM-*.sha256
```

**System Requirements:**

- macOS 11 (Big Sur) or later
- Rosetta 2 for Intel apps on Apple Silicon (auto-installs if needed)

---

### 🔧 Developer Setup

**Prerequisites:**

- Python 3.13 (recommended), 3.12, or 3.14
- Git 2.30+
- **[just](https://github.com/casey/just)** (recommended task runner)

```bash
# 1. Clone
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# 2. Setup (creates venv, installs dependencies & hooks)
just install

# 3. Verify
just check      # Runs lint, type-check, and tests
just --list     # Show all available build/test recipes

# 4. Run
python launcher.py
```

---

### 🏗️ Building from Source

Build portable distributions for all platforms:

**Windows:**
```powershell
# Requires Windows to build
# AMD64/x64 (most PCs):
python scripts/build_manager.py --version 3.13 --arch amd64

# ARM64 (Surface Pro X, ARM devices):
python scripts/build_manager.py --version 3.13 --arch arm64
```

**Linux AppImage:**
```bash
# Requires Linux to build
python scripts/build_manager.py --version 3.13 --arch x86_64
python scripts/build_manager.py --version 3.13 --arch aarch64
```

**macOS DMG:**
```bash
# Requires macOS to build
python scripts/build_manager.py --version 3.13 --arch x86_64  # Intel
python scripts/build_manager.py --version 3.13 --arch arm64   # Apple Silicon
```

**Outputs:** Built packages appear in `dist/` directory with SHA256 checksums.

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [**User Guide**](docs/user-guide.md) | Installation, features, configuration, templates |
| [**Plugin Catalog**](docs/plugin-catalog.md) | Official plugins and usage examples |
| [**Troubleshooting**](docs/troubleshooting.md) | Solutions for common issues per platform |
| [**Migration Guide**](docs/migration-guide.md) | Upgrading plugins from v0.x to v1.x |
| [**Architecture**](docs/architecture.md) | Technical design, directory structure, services |
| [**API Reference**](docs/api-reference.md) | Developer API documentation |
| [**Plugin Development**](docs/plugin-development.md) | Creating custom plugins via YAML |

---

## 🧪 Quality & Security

We adhere to strict 2026 Python best practices:

- **Type Safety:** 100% typed codebase (MyPy strict mode).
- **Testing:** 193+ tests with >73% coverage (pytest).
- **Security:**
  - Weekly OpenSSF Scorecard analysis (Saturdays 01:30 UTC).
  - CodeQL & Ruff security scanning (S-prefix rules).
  - Dependabot for daily dependency updates.
- **CI/CD:** Matrix testing on Python 3.12, 3.13, 3.14 across OSs.

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for style guides and workflows.

**Quick Workflow:**

1. Fork & Clone
2. `just install`
3. Create branch `feat/my-feature`
4. `just test` & `just lint`
5. Push & PR

---

## 📄 License

MIT License - see [LICENSE](LICENSE).

<div align="center">
  <b>Made with ❤️ by <a href="https://github.com/mosh666">mosh666</a></b>
</div>
