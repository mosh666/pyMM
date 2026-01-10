# pyMediaManager Documentation

```{note}
**Version Selector**: Use the sidebar menu to switch between documentation versions (Main/Dev).
You can also visit the [documentation home](https://mosh666.github.io/pyMM/) to select your version.
```

```{toctree}
---
maxdepth: 2
caption: User Documentation
---
user-guide
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
plugin-development
api-reference
```

```{toctree}
---
maxdepth: 1
caption: Platform-Specific
---
platform-directories
linux-udev-installer
docker-ci-testing
```

```{toctree}
---
maxdepth: 1
caption: Examples & Resources
---
examples/README
```

```{toctree}
---
maxdepth: 1
caption: Additional Resources
hidden: true
---
plugin-preferences
examples/config/README
examples/platform/README
examples/plugins/README
examples/projects/README
examples/storage/README
examples/ui/README
```

## Welcome to pyMediaManager

pyMediaManager (pyMM) is a Python-based media management application designed to organize and manage large media
collections with integrated version control and plugin support.

## Features

- **100% Portable**: Run from USB/external drives with no installation
- **Project Management**: Organize media files into structured projects with templates
- **Plugin System**: YAML manifest-based extensible architecture for integrating external tools
- **Git Integration**: Built-in version control with Git LFS support
- **Cross-Platform**: Windows 10+, Linux, macOS with native USB drive detection
- **Modern UI**: Fluent Design with QFluentWidgets and PySide6
- **Type-Safe**: Python 3.12+ with strict type hints and Pydantic validation
- **Well-Tested**: 193 tests with 73% code coverage

## Quick Start

### Installation

**Requirements:**

- Python 3.12, 3.13, or 3.14
- Windows 10/11, Linux (Ubuntu 20.04+), or macOS 11+

**Install from source:**

```bash
git clone https://github.com/mosh666/pyMM.git
cd pyMM
python -m venv .venv
# Activate: .venv\Scripts\activate (Windows) or source .venv/bin/activate (Linux/macOS)
pip install -e ".[dev]"
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

- **[User Guide](user-guide.md)** - Installation, features, and usage instructions
- **[Troubleshooting Guide](troubleshooting.md)** - Common issues, error messages, and solutions
- **[Migration Guide](migration-guide.md)** - Version upgrades and template migrations
- **[Plugin Catalog](plugin-catalog.md)** - Complete catalog of official plugins

### Developer Documentation

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
