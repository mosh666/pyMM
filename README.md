<!-- markdownlint-disable MD013 MD033 -->
<div align="center">

# pyMediaManager

### Portable Python-based media management application with modern Fluent Design UI

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

pyMediaManager is a fully portable, Python-based media management application designed to run
entirely from removable drives without system installation. It provides a modern Fluent Design
interface for managing media projects and orchestrating external tools through plugins.

### Key Features

- 🎨 **Modern Fluent UI** - Clean, responsive interface using PySide6 and QFluentWidgets
- 💾 **100% Portable** - Zero system installation, runs from USB/external drives
- 🔍 **Smart Drive Detection** - Enhanced external drive detection using WMI and Windows APIs
- 🔌 **Flexible Plugin System** - Manage external tools (Git, FFmpeg, ExifTool, digiKam, etc.)
- 📁 **Project Management** - Organize media projects with metadata and templates
- 🔒 **Secure Configuration** - Layered settings with sensitive data redaction
- 📊 **Rich Logging** - Structured logging with console and rotating file output
- ✅ **Reliable Downloads** - Plugin downloads with retry logic, checksums, and progress tracking
- ⚡ **Automatic Versioning** - Git-based semantic versioning with setuptools_scm
- 🧪 **Comprehensive Testing** - High test coverage with isolated test environment
- 🎯 **Quality Gates** - Extensive pre-commit checks with Ruff, MyPy, and security validation

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
# Install pre-commit hooks
pip install pre-commit
pre-commit install --install-hooks
pre-commit install --hook-type pre-push

# Run tests
pytest

# Run linting
ruff check app/ tests/
ruff format app/ tests/

# Run type checking
mypy app/
```

### Project Structure

```text
pyMM/
├── .github/              # GitHub workflows, templates, and configurations
├── app/                  # Application source code
│   ├── core/            # Core services (config, logging, file system)
│   ├── ui/              # User interface components
│   ├── plugins/         # Plugin system
│   ├── services/        # Business logic services
│   └── models/          # Data models
├── config/              # Configuration files
├── docs/                # Documentation
├── plugins/             # Plugin manifests
├── scripts/             # Utility scripts
├── tests/               # Test suite
├── pyproject.toml       # Project metadata and dependencies
└── launcher.py          # Application entry point
```

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
  url = {https://github.com/mosh666/pyMM},
  version = {1.0.0}
}
```

See [CITATION.cff](CITATION.cff) for more citation formats.

---

## Acknowledgments

Built with:

- [PySide6](https://doc.qt.io/qtforpython/) - Qt for Python framework
- [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) - Modern Fluent Design UI components
- [Pydantic](https://docs.pydantic.dev/) - Data validation and settings management
- [GitPython](https://gitpython.readthedocs.io/) - Git integration
- [pytest](https://pytest.org/) - Testing framework

Special thanks to all [contributors](https://github.com/mosh666/pyMM/graphs/contributors).

---

## Support

- 🐛 [Report a Bug](https://github.com/mosh666/pyMM/issues/new?template=bug_report.yml)
- 💡 [Request a Feature](https://github.com/mosh666/pyMM/issues/new?template=feature_request.yml)
- 💬 [Join Discussions](https://github.com/mosh666/pyMM/discussions)
- 📧 [Contact Maintainers](mailto:24556349+mosh666@users.noreply.github.com)

---

<div align="center">

**[⬆ Back to Top](#pymediamanager)**

Made with ❤️ by [mosh666](https://github.com/mosh666)

</div>
