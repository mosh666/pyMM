<!-- markdownlint-disable MD013 MD031 MD040 MD051 MD060 -->

<div align="center">

# pyMediaManager

## 🎬 Cross-Platform Portable Media Management Application

[![License](https://img.shields.io/github/license/mosh666/pyMM?style=flat&color=blue)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-0078D6?style=flat&logo=windows)](https://github.com/mosh666/pyMM)
[![Python](https://img.shields.io/badge/Python-3.12%20%7C%203.13%20%7C%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python)

[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![Documentation](https://github.com/mosh666/pyMM/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/mosh666/pyMM/actions/workflows/docs.yml)
[![Beta Release](https://img.shields.io/github/v/release/mosh666/pyMM?include_prereleases&label=beta&color=orange)](https://github.com/mosh666/pyMM/releases)

[Dev Branch](#-development) • [Quick Start](#-installation) • [Documentation](https://mosh666.github.io/pyMM) • [Contributing](https://github.com/mosh666/pyMM/blob/dev/CONTRIBUTING.md)

</div>

---

## ⚡ Repository Fresh Start

> **Welcome to pyMediaManager v0.0.1!**
>
> A stable **v1.0.0** release is coming soon!

**Current Status:**
- **Active Development:** Happening on the [`dev` branch](https://github.com/mosh666/pyMM/tree/dev)
- **Daily Beta Releases:** Available starting from [v0.0.1-beta.1](https://github.com/mosh666/pyMM/releases)
- **Main Branch:** Will host the first stable v1.0.0 release (no code yet)

---

## 📖 About pyMediaManager

**pyMediaManager (pyMM)** is a cross-platform media management application offering both portable (USB drive, zero installation) and permanent installation modes. Built with PySide6 and a modern Fluent Design interface, it provides professional-grade tools for organizing media projects across **Windows, Linux, and macOS**.

### Key Features

- **🎨 Modern Fluent UI** - Responsive interface built with PySide6 and QFluentWidgets
- **💾 100% Portable** - Runs from external drives with zero system footprint
- **🔌 Extensible Plugin System** - Manage external tools (Git, FFmpeg, ExifTool, etc.)
- **⚡ Smart Drive Detection** - Unified storage API for Windows, Linux, and macOS
- **📁 Project Management** - Metadata-rich organization with Git integration
- **🗄️ Storage Groups** - Master/backup drive pairing with automatic synchronization
- **🤖 Automated CI/CD** - 15 comprehensive workflows with daily beta releases
- **🔐 Supply Chain Security** - SLSA attestation, CodeQL scanning, OpenSSF Scorecard

### Technology Stack

- **Python:** 3.12, 3.13, 3.14 (3.13 recommended)
- **GUI Framework:** PySide6 with QFluentWidgets
- **Package Manager:** uv (10-100x faster than pip)
- **Build Backend:** Hatchling (PEP 517 compliant)
- **Versioning:** hatch-vcs (dynamic from git tags)
- **Plugins:** 9 official plugins (digiKam, ExifTool, FFmpeg, Git, Git LFS, GitVersion, ImageMagick, MariaDB, MKVToolNix)

---

## 📦 Installation

Stable releases will be available soon. For now, check the **development branch** and **beta releases**:

### Option 1: Try Beta Releases

Download the latest beta build from the [Releases page](https://github.com/mosh666/pyMM/releases):

- **Windows:** MSI installer or portable ZIP
- **Linux:** AppImage (x86_64, aarch64)
- **macOS:** DMG (Intel, ARM64)

All portable distributions include a bundled UV executable for zero-dependency package management.

### Option 2: Build from Dev Branch

```bash
# Clone the repository (dev branch)
git clone -b dev https://github.com/mosh666/pyMM.git
cd pyMM

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Linux/macOS
# or
irm https://astral.sh/uv/install.ps1 | iex       # Windows PowerShell

# Sync dependencies and run
uv sync
uv run python launcher.py
```

See the [dev branch README](https://github.com/mosh666/pyMM/blob/dev/README.md) for complete installation instructions.

---

## 🚀 Development

All active development happens on the [`dev` branch](https://github.com/mosh666/pyMM/tree/dev).

### Quick Links

- **[Development Documentation](https://github.com/mosh666/pyMM/blob/dev/DEVELOPER.md)** - Complete developer guide
- **[Contributing Guide](https://github.com/mosh666/pyMM/blob/dev/CONTRIBUTING.md)** - How to contribute
- **[Architecture](https://github.com/mosh666/pyMM/blob/dev/docs/architecture.md)** - System design overview
- **[Plugin Development](https://github.com/mosh666/pyMM/blob/dev/docs/plugin-development.md)** - Create custom plugins
- **[API Reference](https://github.com/mosh666/pyMM/blob/dev/docs/api-reference.md)** - Full API documentation

### Branch Strategy

- **`main` branch:** Stable releases only (v1.0.0+)
- **`dev` branch:** Active development with daily beta releases (v0.0.1-beta.N)

### Release Schedule

- **Beta Releases:** Daily at 1:00 AM UTC (automated)
- **Stable Release:** v1.0.0 coming soon (manual trigger after thorough testing)

---

## 📊 Project Status

| Metric | Value |
|--------|-------|
| **Version** | v0.0.1 (Beta - Daily Releases) |
| **Python Versions** | 3.12, 3.13, 3.14 |
| **Plugins Available** | 9 |
| **Test Cases** | 669 |
| **Test Coverage** | 75% |
| **Lines of Code** | ~38,280 Python |
| **Documentation Files** | 29 |
| **Docstring Coverage** | 100% (724/724) |
| **Type Safety** | 100% (0 MyPy errors) |

---

## 🤝 Contributing

We welcome contributions! Please see the [Contributing Guide](https://github.com/mosh666/pyMM/blob/dev/CONTRIBUTING.md) on the dev branch for:

- Development setup instructions
- Code quality standards
- Testing requirements
- Pull request process

### Development Workflow

1. Fork the repository
2. Create a feature branch from `dev`
3. Make your changes with tests
4. Submit a pull request to `dev` branch
5. Wait for CI validation and review

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Repository:** <https://github.com/mosh666/pyMM>
- **Documentation:** <https://mosh666.github.io/pyMM>
- **Bug Reports:** <https://github.com/mosh666/pyMM/issues>
- **Pull Requests:** <https://github.com/mosh666/pyMM/pulls>
- **Changelog:** <https://github.com/mosh666/pyMM/blob/dev/CHANGELOG.md>

---

<div align="center">

**Built with ❤️ using Python and PySide6**

*Cross-platform • Portable • Open Source*

</div>
