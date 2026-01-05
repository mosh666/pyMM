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

Built with Python 3.12-3.14 support, the application includes an embedded Python runtime for true portability across Windows systems. Version management is automated using Git tags and setuptools_scm, supporting semantic versioning with prerelease tags (alpha, beta, rc).

### Key Features

- 🎨 **Modern Fluent UI** - Clean, responsive interface using PySide6 and QFluentWidgets
- 💾 **100% Portable** - Zero system installation, runs from USB/external drives with embedded Python 3.13
- 🔍 **Smart Drive Detection** - Enhanced external drive detection using WMI and Windows APIs
- 🔌 **Flexible Plugin System** - Manage external tools (Git, FFmpeg, ExifTool, digiKam, etc.)
- 📁 **Project Management** - Organize media projects with metadata and optional Git integration
- 🔒 **Secure Configuration** - Layered YAML-based settings with sensitive data redaction
- 📊 **Rich Logging** - Structured logging with console and rotating file output
- ✅ **Reliable Downloads** - Plugin downloads with retry logic, SHA256 checksums, and progress tracking
- ⚡ **Automatic Versioning** - Git-based semantic versioning with setuptools_scm
- 🧪 **Comprehensive Testing** - 193 tests with 73% code coverage and automatic test isolation
- 🎯 **Quality Gates** - 15+ pre-commit hooks including Ruff, MyPy, and Bandit security scanning
- 🔐 **Security Focused** - CodeQL analysis, OpenSSF Scorecard (daily), Dependabot, and comprehensive security scanning

---

## Documentation

📖 Comprehensive documentation available:

- [User Guide](docs/user-guide.md) - Installation, usage, and configuration
- [Architecture Guide](docs/architecture.md) - Technical architecture and design decisions
- [Contributing Guide](CONTRIBUTING.md) - Development setup and contribution guidelines
- [Changelog](CHANGELOG.md) - Version history and release notes
- [Security Policy](.github/SECURITY.md) - Security reporting and practices
- [Code of Conduct](.github/CODE_OF_CONDUCT.md) - Community guidelines

---

## Installation

### Requirements

- **Python**: 3.12, 3.13, or 3.14
- **OS**: Windows 10/11 64-bit (Linux/macOS support planned)
- **Drive**: USB 3.0+ or external SSD recommended

### Quick Start

```bash
# Clone the repository
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Run the application
python launcher.py
```

For portable deployment instructions, see the [User Guide](docs/user-guide.md).

---

## Development

### Setup Development Environment

```bash
# Install pre-commit hooks for automated quality checks
pip install pre-commit
pre-commit install --install-hooks
pre-commit install --hook-type pre-push

# Run full test suite with coverage
pytest

# Run linting and formatting
ruff check app/ tests/ launcher.py
ruff format app/ tests/ launcher.py

# Run type checking
mypy app/
```

### Project Structure

```text
pyMM/
├── .github/              # GitHub workflows, templates, and configurations
├── app/                  # Application source code
│   ├── core/            # Core services (config, logging, file system, storage)
│   ├── ui/              # User interface components and views
│   ├── plugins/         # Plugin system base and manager
│   ├── services/        # Business logic services (git, project)
│   └── models/          # Data models (project, etc.)
├── config/              # Configuration files (YAML)
├── docs/                # Comprehensive documentation
├── plugins/             # Plugin manifests for external tools
├── scripts/             # Utility scripts (git hooks setup)
├── tests/               # Comprehensive test suite (unit, integration, GUI)
│   ├── unit/           # Unit tests for individual components
│   ├── integration/    # Integration tests for workflows
│   └── gui/            # GUI component tests
├── pyproject.toml       # Project metadata, dependencies, and tool configs
└── launcher.py          # Application entry point with path setup
```

### Architecture Highlights

- **Service-Oriented Design**: Dependency injection with clear separation of concerns
- **Type Safety**: Comprehensive type hints validated by MyPy
- **Modern Python**: Native generic types (list, dict, tuple) instead of typing imports
- **Structured Logging**: Logger instances throughout, no print statements in production code
- **Testing**: Unit tests, integration tests, and GUI tests with pytest-qt
- **Quality Gates**: Ruff linting/formatting, MyPy type checking, Bandit security scanning

---

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up your development environment
- Code style and quality standards
- Testing requirements
- Pull request process
- Community guidelines

Please read our [Code of Conduct](.github/CODE_OF_CONDUCT.md) before contributing.

---

## Security

Security is a top priority. Please see our [Security Policy](.github/SECURITY.md) for:

- Supported versions
- How to report vulnerabilities
- Security update process
- Safe harbor for researchers

**Do not report security vulnerabilities through public GitHub issues.**

### Security Features

- Daily OpenSSF Scorecard metrics
- CodeQL static analysis
- Bandit security scanning in pre-commit hooks
- Dependabot for automated dependency updates
- SHA256 checksum verification for plugin downloads
- Sensitive data redaction in configuration exports

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Citation

If you use pyMediaManager in academic or research work, please cite it:

```bibtex
@software{pymediamanager,
  author = {mosh666},
  title = {pyMediaManager: Portable Python Media Management Application},
  year = {2026},
  url = {https://github.com/mosh666/pyMM}
}
```

See [CITATION.cff](CITATION.cff) for more citation formats.

---

## Acknowledgments

Built with:

- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python framework
- [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Modern Fluent Design UI components
- [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management
- [pytest](https://pytest.org/) - Testing framework with extensive plugin ecosystem
- [Ruff](https://docs.astral.sh/ruff/) - Fast Python linter and formatter

---

<div align="center">

Made with ❤️ by the pyMediaManager community

[Report Bug](https://github.com/mosh666/pyMM/issues) • [Request Feature](https://github.com/mosh666/pyMM/discussions) • [Discussions](https://github.com/mosh666/pyMM/discussions)

</div>
