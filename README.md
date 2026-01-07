<!-- markdownlint-disable MD013 MD033 -->
<div align="center">

# pyMediaManager

## Portable Python-based media management application with modern Fluent Design UI

[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13%20%7C%203.14-blue?logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/mosh666/pyMM)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)](https://www.python.org)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![Security](https://github.com/mosh666/pyMM/actions/workflows/security.yml/badge.svg)](https://github.com/mosh666/pyMM/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/mosh666/pyMM/branch/main/graph/badge.svg)](https://codecov.io/gh/mosh666/pyMM)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](.github/CODE_OF_CONDUCT.md)

[Features](#key-features) •
[Installation](#installation) •
[Documentation](#documentation) •
[Contributing](#contributing) •
[License](#license)

</div>

---

## Overview

pyMediaManager (pyMM) is a fully portable, Python-based media management application designed to run entirely from removable drives without requiring system installation. It provides a modern Fluent Design interface for managing media projects and orchestrating external tools through an extensible plugin system.

Built with Python 3.12+ support, the application includes an embedded Python runtime for true portability across Windows systems.

### Key Features

- 🎨 **Modern Fluent UI** - Clean, responsive interface using PySide6 and QFluentWidgets
- 💾 **100% Portable** - Zero system installation, runs from USB/external drives
- 🔍 **Smart Drive Detection** - Enhanced external drive detection using WMI and Windows APIs
- 🔌 **Flexible Plugin System** - Manage external tools (Git, FFmpeg, ExifTool, digiKam, etc.)
- 📁 **Project Management** - Organize media projects with metadata and optional Git integration
- 🔒 **Secure Configuration** - Layered YAML-based settings with sensitive data redaction
- 📊 **Rich Logging** - Structured logging with console and rotating file output
- ✅ **Reliable Downloads** - Plugin downloads with retry logic, SHA256 checksums, and progress tracking
- ⚡ **Automatic Versioning** - Git-based semantic versioning
- 🧪 **Comprehensive Testing** - Extensive unit and integration tests with automatic isolation
- 🎯 **Quality Gates** - Pre-commit hooks including Ruff, MyPy, and Bandit security scanning

---

## Documentation

📖 Comprehensive documentation available:

- [User Guide](docs/user-guide.md) - Installation, usage, and configuration
- [Architecture Guide](docs/architecture.md) - Technical architecture and design decisions
- [Contributing Guide](CONTRIBUTING.md) - Development setup and contribution guidelines
- [Plugin Development](docs/plugin-development.md) - Creating and managing plugins
- [API Reference](docs/api/index.rst) - Complete API documentation
- [Changelog](CHANGELOG.md) - Version history and release notes
- [Security Policy](.github/SECURITY.md) - Security reporting and practices
- [Code of Conduct](.github/CODE_OF_CONDUCT.md) - Community guidelines

---

## Installation

### For End Users (Portable)

1. Download the latest release from the [Releases](https://github.com/mosh666/pyMM/releases) page.
2. Extract the ZIP file to your USB drive or preferred location.
3. Run pyMediaManager.exe (or launcher.py if using source build).
4. No installation is required. The app runs completely self-contained.

### For Developers

**Prerequisites:**

- Python 3.12, 3.13, or 3.14
- [just](https://github.com/casey/just) (command runner)

**Quick Start:**

`ash

# Clone the repository

git clone <https://github.com/mosh666/pyMM.git>
cd pyMM

# Initialize project (creates venv and installs dependencies)

just install

# Run the application

python launcher.py
`

**Common Development Commands:**

- just install - Set up environment and dependencies
- just test - Run test suite
- just lint - Run formatters and type checkers (ruff, mypy)
- just lock - Update dependency lockfile

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to get started, our code of conduct, and the pull request process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
