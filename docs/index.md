# pyMediaManager Documentation

```{note}
**Version Selector**: Use the sidebar menu to switch between documentation versions (Main/Dev).
You can also visit the [documentation home](https://mosh666.github.io/pyMM/) to select your version.
```

```{toctree}
---
maxdepth: 2
caption: Contents
---
user-guide
architecture
plugin-development
```

## Welcome to pyMediaManager

pyMediaManager (pyMM) is a Python-based media management application designed to organize and manage large media
collections with integrated version control and plugin support.

## Features

- **Project Management**: Organize media files into structured projects
- **Storage Management**: Configure and manage multiple storage locations
- **Plugin System**: Extensible architecture for integrating external tools
- **Git Integration**: Built-in version control support
- **Cross-platform**: Windows support with portable external tools

## Quick Start

### Installation

```bash
git clone https://github.com/mosh666/pyMM.git
cd pyMM
pip install -e .
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

- [User Guide](user-guide.md) - End-user guide for using pyMediaManager
- [Architecture](architecture.md) - Technical architecture and design decisions
- [Plugin Development](plugin-development.md) - Guide for developing plugins

## Indices and tables

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
