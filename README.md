<!-- markdownlint-disable MD013 MD031 MD040 MD051 MD060 -->

<div align="center">

# pyMediaManager

> **Last Updated:** 2026-01-17 21:41 UTC
\n## 🎬 Cross-Platform Portable Media Management Application

[![License](https://img.shields.io/github/license/mosh666/pyMM?style=flat&color=blue)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-0078D6?style=flat&logo=windows)](https://github.com/mosh666/pyMM)

<!-- Branch-specific status comparison -->
| Metric | Main Branch | Dev Branch |
|--------|-------------|------------|
| **Python** | [![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org) | [![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org) |
| **GUI Framework** | [![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python) | [![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python) |
| **CI Pipeline** | [![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml) | [![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml) |
| **Documentation** | [![Documentation](https://github.com/mosh666/pyMM/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/mosh666/pyMM/actions/workflows/docs.yml) | [![Documentation](https://github.com/mosh666/pyMM/actions/workflows/docs.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/docs.yml) |
| **CodeQL Analysis** | [![CodeQL](https://github.com/mosh666/pyMM/actions/workflows/codeql.yml/badge.svg?branch=main)](https://github.com/mosh666/pyMM/actions/workflows/codeql.yml) | [![CodeQL](https://github.com/mosh666/pyMM/actions/workflows/codeql.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/codeql.yml) |
| **Code Coverage** | [![codecov](https://codecov.io/gh/mosh666/pyMM/branch/main/graph/badge.svg?token=YDS4DEZ722)](https://codecov.io/gh/mosh666/pyMM) | [![codecov](https://codecov.io/gh/mosh666/pyMM/branch/dev/graph/badge.svg?token=YDS4DEZ722)](https://codecov.io/gh/mosh666/pyMM) |
| **Release** | [![Stable Release](https://img.shields.io/github/v/release/mosh666/pyMM?label=stable&color=success)](https://github.com/mosh666/pyMM/releases/latest) | [![Beta Release](https://img.shields.io/github/v/release/mosh666/pyMM?include_prereleases&label=beta&color=orange)](https://github.com/mosh666/pyMM/releases) |

[![Docstring Coverage](https://img.shields.io/badge/docstring--coverage-100%25-brightgreen)](https://github.com/mosh666/pyMM/actions/workflows/docs.yml)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](https://mosh666.github.io/pyMM) • [Contributing](#-contributing)

</div>

---

<p align="left">
<b>pyMediaManager (pyMM)</b> is a cross-platform media management application offering both portable (USB drive, zero installation) and permanent installation modes. Built with PySide6 and a modern Fluent Design interface, it provides professional-grade tools for organizing media projects across <b>Windows, Linux, and macOS</b>. Windows users can choose between an MSI installer for seamless desktop integration or portable ZIP for USB drives with <b>bundled UV executable</b> for zero-dependency package management. It features an extensible plugin system with unified, platform-aware drive detection and storage management. The project follows 2026 Python best practices with modern tooling: <b>uv</b> (10-100x faster package manager with lockfile), <b>Hatchling</b> (PEP 517 compliant build backend), and <b>hatch-vcs</b> (dynamic versioning from git tags). Supports Python <b>3.12, 3.13, and 3.14</b> (3.13 recommended). 100% UV-only ecosystem with automatic PATH configuration in portable mode. All portable distributions bundle UV executable for seamless dependency management. Production-ready beta with daily automated releases.
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
- **🗄️ Storage Groups** - Master/backup drive pairing with automatic synchronization:
  - **First-run wizard integration** - Optional setup during initial configuration
  - Assign projects to storage groups for automated backup
  - Real-time and scheduled sync with conflict resolution
  - Encryption and compression support for secure backups
  - Bandwidth throttling and sync history tracking
  - Manage storage groups from the Storage Management view
- **🔄 Advanced Sync Engine** - Comprehensive file synchronization:
  - Real-time file watching with watchdog integration
  - Scheduled sync with cron-like expressions (APScheduler)
  - Backup tracking with metadata and versioning
  - Configurable sync options (bidirectional, exclude patterns)
- **🤖 Automated CI/CD** - 11 comprehensive workflows following 2026 best practices:
  - **Modern build system:** Complete migration from pip/setuptools to **uv + Hatchling + hatch-vcs**
  - **uv package manager:** 10-100x faster than pip with lockfile support and caching
  - **Hatchling build backend:** PEP 517 compliant, replaces setuptools entirely
  - **hatch-vcs versioning:** Dynamic version from git tags with custom templates
  - Daily beta releases (1 AM UTC) with automatic cleanup (keeps 3 most recent)
  - Automated artifact cleanup (7-day retention) to optimize storage costs
  - Supply chain security with SLSA artifact attestation and CodeQL scanning
  - Pinned runners for reproducible release builds (Windows 2022, Ubuntu 22.04)
  - Enhanced concurrency groups to reduce Actions minutes consumption
  - Multi-platform testing (Windows, Linux, macOS ARM64/Intel)
  - Dependabot automation with auto-merge after CI passes

<!-- AUTO-GENERATED:STATS:START -->
### 📊 Project Statistics

| Metric | Value |
|--------|-------|
| **Python Versions** | 3.12, 3.13, 3.14 |
| **Plugins Available** | 9 |
| **Test Cases** | 33+ |
| **Test Coverage** | N/A |
| **Lines of Code** | ~36,330 Python |
| **Documentation Files** | 31 |
| **Documentation Completeness** | 100.0% |
<!-- AUTO-GENERATED:STATS:END -->

---

## 🚀 Quick Start

### 📦 Download & Installation

pyMediaManager provides portable distributions for Windows, Linux, and macOS. Download the latest release from [GitHub Releases](https://github.com/mosh666/pyMM/releases).

#### Windows

Choose your preferred installation method:

##### Option 1: MSI Installer (Recommended)

**Best for:** Permanent desktop installation with Start Menu integration

**Recommended:** Python 3.13 for x64 systems

1. **Download:** `pyMM-v{VERSION}-py3.13-win-amd64.msi`

2. **Install:**
   - Double-click the MSI file
   - Follow the setup wizard
   - Choose installation location (default: `C:\Program Files\pyMediaManager\`)
   - Select components (Application, Desktop Shortcut, Start Menu)

3. **Launch:**
   - From Start Menu: **pyMediaManager**
   - From Desktop shortcut (if selected)
   - Complete the first-run setup wizard

4. **Uninstall:**
   - Settings → Apps → pyMediaManager → Uninstall
   - Or use Start Menu → pyMediaManager → Uninstall pyMediaManager

**Features:**

- ✅ Start Menu integration
- ✅ Desktop shortcut
- ✅ Automatic PATH configuration
- ✅ Clean uninstall via Windows Settings
- ✅ Automatic upgrades (installs over previous version)

---

##### Option 2: Portable ZIP

**Best for:** USB drives, no-installation scenarios, or multiple Python versions

1. **Download:**
   - **Intel/AMD (x64):** `pyMM-v{VERSION}-py3.13-win-amd64.zip` (most Windows PCs)
   - **ARM64:** `pyMM-v{VERSION}-py3.13-win-arm64.zip` (Surface Pro X, ARM-based Windows devices)

2. **Extract** to your preferred location (e.g., `D:\pyMM\` or USB drive)

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
5. **To Remove:** Simply delete the folder (no registry entries)

**Features:**

- ✅ Zero installation footprint
- ✅ Run from any location (USB drive, network drive)
- ✅ No registry modifications
- ✅ Multiple Python versions available (3.12, 3.13, 3.14)
- ✅ **Bundled UV executable** for automatic package management (no pip needed)
- ✅ Auto-configures PATH for UV when running launcher.py

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

## 👨‍💻 For Developers

Interested in contributing or extending pyMediaManager? Check out our comprehensive developer guide:

**📖 [Developer Guide](DEVELOPER.md)** - Complete guide for contributors with:

- 🚀 Quick developer setup (3-step process)
- 🏗️ Architecture overview with Mermaid diagrams
- 🔌 Plugin development guide
- 🧪 Test pyramid and testing strategies
- 📦 CI/CD pipeline explanation
- 🤝 Contributing guidelines and workflow

**Quick Setup:**

```bash
# Clone repository
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# Install with uv (10-100x faster than pip)
uv sync --all-extras

# Install pre-commit hooks
uv run pre-commit install

# Run tests
uv run pytest
```

See [DEVELOPER.md](DEVELOPER.md) for complete development documentation, including:

- Building from source for all platforms
- Using Just task runner for common operations
- Debugging tips and performance profiling
- Release process and semantic versioning
- Testing strategies and CI/CD workflows

For contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/semantic-release.md](docs/semantic-release.md).

---

### 🔌 Available Plugins

<!-- AUTO-GENERATED:PLUGIN_LIST:START -->
| Plugin | Status |
|--------|--------|
| **Digikam** | ✅ Configured |
| **Exiftool** | ✅ Configured |
| **Ffmpeg** | ✅ Configured |
| **Git** | ✅ Configured |
| **Gitlfs** | ✅ Configured |
| **Gitversion** | ✅ Configured |
| **Imagemagick** | ✅ Configured |
| **Mariadb** | ✅ Configured |
| **Mkvtoolnix** | ✅ Configured |
<!-- AUTO-GENERATED:PLUGIN_LIST:END -->

See [Plugin Catalog](docs/plugin-catalog.md) for detailed usage examples.

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [**Installation**](docs/installation.md) | System requirements, installation methods, first run setup |
| [**Getting Started**](docs/getting-started.md) | Core features, UI overview, quick configuration setup |
| [**Features**](docs/features.md) | Project management, storage groups, plugins |
| [**Configuration**](docs/configuration.md) | Configuration options, CLI, troubleshooting |
| [**Storage Groups**](docs/storage-groups.md) | Master/backup drive pairing (Phase 1 & 2 complete) |
| [**✨ Sync Engine**](docs/sync-engine.md) | **NEW** - Comprehensive synchronization documentation |
| [**✨ Project Templates**](docs/templates.md) | **NEW** - Template system and custom template creation |
| [**✨ Windows Setup**](docs/windows-setup.md) | **NEW** - MSI installer, UAC, WMI, Windows-specific features |
| [**✨ macOS Setup**](docs/macos-setup.md) | **NEW** - DMG installation, Gatekeeper, disk permissions |
| [**Plugin Catalog**](docs/plugin-catalog.md) | Official plugins and usage examples |
| [**Troubleshooting**](docs/troubleshooting.md) | Solutions for common issues per platform |
| [**Migration Guide**](docs/migration-guide.md) | Upgrading plugins from v0.x to v1.x |
| [**Architecture**](docs/architecture.md) | Technical design, directory structure, services |
| [**API Reference**](docs/api-reference.md) | Developer API documentation with sync module APIs |
| [**Plugin Development**](docs/plugin-development.md) | Creating custom plugins via YAML |

---

## 🧪 Quality & Security

We adhere to strict 2026 Python best practices:

- **Modern Build System:**
  - **uv** package manager (10-100x faster than pip, with lockfile support)
  - **Hatchling** build backend (PEP 517 compliant, replaces setuptools)
  - **hatch-vcs** for dynamic versioning from git tags
  - All CI pipelines optimized with uv caching
- **Type Safety:** 100% typed codebase (MyPy strict mode, 0 errors across 61 source files).
- **Testing:** 193 tests with 73% coverage (pytest), comprehensive platform-specific test markers.
  - All 193 tests passing reliably across timezones and platforms
  - Platform-specific tests properly skipped on non-matching systems (Windows/Linux/macOS)
  - Comprehensive UI, integration, and unit test coverage with pytest-qt
  - ⚠️ **Critical Gap:** Sync engine (9 modules) has 0% test coverage - contributions highly encouraged!
  - See [docs/examples/](docs/examples/) for executable code examples demonstrating APIs
- **Documentation:** 100% docstring coverage (724/724 items with comprehensive docstrings), 29 documentation files totaling ~25,000 lines.
- **Resource Management:** Proper cleanup of database connections, file handles, and background processes with destructors and context managers.
- **Security:**
  - Weekly OpenSSF Scorecard analysis (Saturdays 01:30 UTC).
  - CodeQL & Ruff security scanning (S-prefix rules).
  - Automated Dependabot updates (weekly, auto-merged after CI passes).
  - Supply chain security with SLSA attestation for all releases.
- **CI/CD (11 Comprehensive Workflows):**
  - **Testing:** Matrix testing on Python 3.12, 3.13, 3.14 across Windows/Linux/macOS (Intel + ARM)
  - **Building:** Multi-platform portable builds (ZIP, AppImage, DMG, MSI) with pinned runners
  - **Releases:** Automated semantic versioning (python-semantic-release v9.8.8)
  - **Versioning:** v0.y.z enforced with 5 protection layers until v1.0.0 release
  - **Automation:** Daily beta releases (1 AM UTC), cleanup (2 AM UTC, keeps 3 recent)
  - **Documentation:** Sphinx docs with sphinx-multiversion for dev/main branches
  - **Security:** CodeQL scanning, OpenSSF Scorecard, dependency review
  - **Stats:** Auto-update README statistics weekly and post-release
  - **PR Management:** Auto-labeling, Dependabot auto-merge
  - **MSI Installer:** WiX Toolset v4 for Python 3.13 Windows builds
  - **Optimization:** Enhanced concurrency groups, 7-day artifact retention

---

## 🤝 Contributing

Contributions are welcome! Visit our **[Developer Guide](DEVELOPER.md)** for complete setup instructions, architecture overview, and development workflows.

**Key Resources:**

- 📖 [DEVELOPER.md](DEVELOPER.md) - Comprehensive developer documentation
- 📝 [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines and workflow
- 🛠️ [docs/build-system.md](docs/build-system.md) - Build system architecture and portable distribution guide
- 🔖 [docs/semantic-release.md](docs/semantic-release.md) - Version management guide

---

## 📄 License

MIT License - see [LICENSE](LICENSE).

<div align="center">
  <b>Made with ❤️ by <a href="https://github.com/mosh666">mosh666</a></b>
</div>
