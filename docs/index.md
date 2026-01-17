# pyMediaManager Documentation

> **Last Updated:** 2026-01-17 21:41 UTC

```{note}
**Version Selector**: Use the sidebar menu to switch between documentation versions (Main/Dev).
You can also visit the [documentation home](https://mosh666.github.io/pyMM/) to select your version.
```

```{toctree}
---
maxdepth: 2
caption: User Documentation
---
installation
getting-started
features
configuration
storage-groups
sync-engine
templates
troubleshooting
migration-guide
plugin-catalog
```

```{toctree}
---
maxdepth: 2
caption: Developer Documentation
---
getting-started-dev
architecture
build-system
plugin-development
api-reference
testing-roadmap
semantic-release
```

```{toctree}
---
maxdepth: 1
caption: Platform-Specific
---
windows-setup
macos-setup
linux-setup
platform-directories
linux-udev-installer
docker-ci-testing
```

```{toctree}
---
maxdepth: 1
caption: Additional Resources
hidden: true
---
plugin-preferences
```

## Welcome to pyMediaManager

pyMediaManager (pyMM) is a Python-based media management application designed to organize and manage large media
collections with integrated version control and plugin support.

## Features

- **100% Portable**: Run from USB/external drives with no installation - includes bundled UV executable for
  zero-dependency package management
- **Project Management**: Organize media files into structured projects with 5 built-in templates
- **Plugin System**: YAML manifest-based extensible architecture for integrating external tools
- **Storage Groups**: Master/backup drive pairing with Phase 2 sync features fully implemented
- **Advanced Sync**: ✅ Real-time file watching, scheduled sync (APScheduler), manual sync with progress tracking
- **Incremental Backup**: ✅ SQLite-based change tracking, encryption (AES-256-GCM), compression (GZIP/LZ4)
- **Conflict Resolution**: ✅ Automatic detection with visual diff and manual resolution workflow
- **Git Integration**: Built-in version control with Git LFS support
- **Cross-Platform**: Windows 10+, Linux, macOS with native USB drive detection and platform-specific optimizations
- **Modern UI**: Fluent Design with QFluentWidgets and PySide6
- **Type-Safe**: Python 3.12-3.14 with strict type hints and Pydantic validation
- **Well-Tested**: 193 tests passing with 73% coverage (sync engine pending test coverage)
- **Windows MSI Installer**: Professional installer with Start Menu integration (Python 3.13)
- **UV-Only Ecosystem**: Complete migration from pip to UV (10-100x faster) with lockfile support

## Quick Start

### Installation

**Requirements:**

- Python 3.12 or 3.13
- Windows 10/11, Linux (Ubuntu 20.04+), or macOS 11+

**Install from source:**

```bash
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# Recommended: Use Just task runner (https://github.com/casey/just)
just install    # Sets up venv, installs deps, configures hooks

# Or manual setup with uv:
uv venv
uv sync --all-extras
uv tool install pre-commit
pre-commit install
```

**Verify installation:**

```bash
# Using Just (recommended - includes colored output)
just check

# Or manually:
python -m pytest tests/
```

### Running the Application

```bash
python launcher.py
```

Or use the installed entry point:

```bash
pymm
```

## Documentation Sections

### User Documentation

- **[Installation & Setup](installation.md)** - System requirements, installation methods, and first run setup
- **[Getting Started](getting-started.md)** - Core features, UI overview, quick configuration setup
- **[Features & Usage](features.md)** - Project management, storage groups, plugins, and advanced features
- **[Configuration & Troubleshooting](configuration.md)** - Configuration options, CLI usage, and troubleshooting
- **[Storage Groups](storage-groups.md)** - Master/backup drive pairing (Phase 1 & 2 complete)
- **[Sync Engine](sync-engine.md)** - ✨ **NEW** - Comprehensive synchronization documentation
- **[Project Templates](templates.md)** - ✨ **NEW** - Template system and custom template creation
- **[Windows Setup](windows-setup.md)** - ✨ **NEW** - MSI installer, UAC, WMI, and Windows-specific features
- **[macOS Setup](macos-setup.md)** - ✨ **NEW** - DMG installation, Gatekeeper, disk permissions
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues, error messages, and solutions
- **[Migration Guide](migration-guide.md)** - Version upgrades and template migrations
- **[Plugin Catalog](plugin-catalog.md)** - Complete catalog of official plugins

### Developer Documentation

- **[Getting Started (Developer)](getting-started-dev.md)** - Complete setup guide with modern Just task runner (2026 features)
- **[Architecture](architecture.md)** - Technical architecture and design decisions
- **[Plugin Development](plugin-development.md)** - Creating custom plugins
- **[API Reference](api-reference.md)** - Auto-generated API documentation

### Platform-Specific Guides

- **[Platform Directories](platform-directories.md)** - Platform-specific directory structures
- **[Linux udev Installer](linux-udev-installer.md)** - Linux USB drive detection setup
- **[Docker CI Testing](docker-ci-testing.md)** - Docker-based testing environment

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
