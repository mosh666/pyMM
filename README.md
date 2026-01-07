<!-- markdownlint-disable MD013 MD031 MD040 MD051 MD060 -->

<div align="center">

# pyMediaManager

## 🎬 Portable Media Management Application with Modern Fluent Design

[![Python](https://img.shields.io/badge/Python-3.12%20|%203.13%20|%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/mosh666/pyMM?style=flat&color=blue)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D6?style=flat&logo=windows)](https://www.microsoft.com/windows)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python)

[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mosh666/pyMM/branch/main/graph/badge.svg)](https://codecov.io/gh/mosh666/pyMM)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

---

<p align="left">
<b>pyMediaManager (pyMM)</b> is a fully portable, Python-based media management application
that runs entirely from USB drives without requiring system installation. Built with PySide6
and featuring a modern Fluent Design interface, it provides professional-grade tools for
organizing media projects and managing external applications through an extensible plugin system.
</p>

</div>

---

## ✨ Features

### Core Capabilities

- **🎨 Modern Fluent UI** - Beautiful, responsive interface built with PySide6 and QFluentWidgets
  following Microsoft's Fluent Design System
- **💾 100% Portable** - Complete application runs from USB/external drives with zero system footprint
- **🔌 Plugin System** - Extensible YAML-based plugin architecture for managing external tools
- **📁 Project Management** - Organize media projects with metadata, templates, and optional
  Git integration
- **⚡ Smart Drive Detection** - Advanced external drive recognition using WMI and Windows APIs

### Developer Experience

- **🔍 Type-Safe** - Full type hints using Python 3.12+ native generics (`list[T]`, `dict[K, V]`)
- **🧪 Well-Tested** - 193 tests with 73% code coverage, automatic test isolation
- **📊 Rich Logging** - Structured logging with rich console output and rotating file logs
- **🔒 Security First** - Daily OpenSSF Scorecard, CodeQL analysis, Bandit security
  scanning
- **🎯 Quality Gates** - 15+ pre-commit hooks: Ruff, MyPy, pytest, YAML validation

### Technical Highlights

- **Embedded Python Runtime** - Ships with Python 3.13 for true portability
- **Automatic Versioning** - Git-based semantic versioning with `setuptools-scm`
- **Secure Configuration** - Layered YAML config with Pydantic validation and sensitive data
  redaction
- **Plugin Downloads** - Automatic downloads with SHA-256 verification, retry logic, progress
  tracking
- **Git Integration** - Optional version control using GitPython library

### Template & Migration System

Projects can be created from templates with automatic folder structure setup:

- **Template Discovery** - Automatic scanning of `templates/` directory with hot-reload support
- **Template Inheritance** - Multi-level inheritance (up to 5 levels) for composable project structures
- **Variable Substitution** - Dynamic placeholders in template files:
  - `{PROJECT_NAME}` - Project display name
  - `{PROJECT_PATH}` - Absolute project path
  - `{DATE}` / `{DATETIME}` - Creation timestamps
  - `{AUTHOR}` - Git user or system username
  - `{DESCRIPTION}` - Project description
  - `{GIT_ENABLED}` - Whether Git is initialized

**Migration Workflow:**

1. **Check** - Detect projects using outdated template versions
2. **Preview** - View changes before applying (folders to add/remove, conflicts)
3. **Apply** - Migrate projects with automatic backups and Git commits
4. **Rollback** - Restore from backup if migration fails

**Conflict Detection:**

- Identifies folders containing user files that would be removed
- Allows skipping conflicts or manual resolution
- Tracks migration history with timestamps and version changes

**Deferred Scheduling:**

- Schedule migrations for later execution
- Batch apply pending migrations across multiple projects
- Cancel or modify scheduled migrations before execution

**Built-in Templates:**

- `base` - Minimal structure (media/, exports/, cache/)
- `default` - Extends base with standard README and Git setup
- `video-editing` - Adds source/, proxies/, renders/, project-files/ with FFmpeg/MKVToolNix
- `photo-management` - Adds raw/, processed/, selections/, metadata/ with ExifTool/ImageMagick/digiKam

---

## 🚀 Quick Start

### End Users

**Download and run - no installation required!**

1. **Download** the latest release:
   ```bash
   # Stable release
   https://github.com/mosh666/pyMM/releases/latest

   # Beta release (latest features)
   https://github.com/mosh666/pyMM/releases/tag/latest-beta
   ```

2. **Extract** to your USB drive or preferred location:
   ```
   E:\pyMM\          # USB drive
   D:\Apps\pyMM\     # Local drive
   ```

3. **Run** the application:
   ```powershell
   .\pyMediaManager.exe
   # or
   python launcher.py
   ```

4. **First-time setup** - Follow the wizard to:
   - Select your portable drive
   - Install core plugins (Git, FFmpeg, ExifTool)
   - Create your first project

### Developers

**Prerequisites:** Python 3.13 (recommended), 3.12, or 3.14 • Git 2.30+ • [just](https://github.com/casey/just) (optional)

```bash
# Clone repository
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# Quick setup with just
just install          # Create venv, install deps, setup hooks
just test             # Run test suite (193 tests)
just lint             # Ruff + MyPy checks
python launcher.py    # Launch application

# Manual setup
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install --install-hooks
pytest
```

#### Docker Development

For isolated testing environments and CI validation:

```bash
# Build Docker image
docker build -t pymm:test .

# Run tests in container
docker run --rm pymm:test

# Interactive shell for debugging
docker run -it --rm --entrypoint bash pymm:test

# Disable filesystem watching (for CI environments)
docker run --rm -e PYMM_DISABLE_TEMPLATE_WATCH=1 pymm:test
```

**Notes:**

- Uses `xvfb-run` for headless GUI testing (virtual X11 display)
- Set `PYMM_DISABLE_TEMPLATE_WATCH=1` to disable template file monitoring (reduces resource usage in containers)
- Qt applications require X11 server in container; xvfb provides this automatically
- For troubleshooting Qt errors, check display configuration: `echo $DISPLAY` inside container

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [User Guide](docs/user-guide.md) | Installation, features, configuration, troubleshooting |
| [Architecture](docs/architecture.md) | Technical design, service architecture, data flows |
| [Plugin Development](docs/plugin-development.md) | Creating plugins, YAML schema, best practices |
| [Contributing](CONTRIBUTING.md) | Development setup, coding standards, PR process |
| [Changelog](CHANGELOG.md) | Version history, release notes |

### Additional Resources

- 🔒 [Security Policy](.github/SECURITY.md) - Vulnerability reporting
- 🤝 [Code of Conduct](.github/CODE_OF_CONDUCT.md) - Community guidelines
- 📝 [Citation](CITATION.cff) - Academic citation format

---

## 🏗️ Architecture

### Directory Structure

```
pyMM/
├── app/                      # Application code
│   ├── core/                 # Core services (config, filesystem, storage)
│   ├── ui/                   # PySide6 GUI components
│   ├── plugins/              # Plugin system
│   ├── services/             # Business logic (projects, Git)
│   └── main.py               # Entry point
├── plugins/                  # Plugin manifests (YAML)
├── config/                   # Configuration files
├── tests/                    # Test suite (193 tests)
│   ├── unit/                 # Unit tests (95)
│   ├── integration/          # Integration tests (10)
│   └── gui/                  # GUI tests (50)
├── docs/                     # Documentation
└── scripts/                  # Build and utility scripts
```

### Key Technologies

- **GUI Framework:** PySide6 6.6+ (Qt for Python)
- **UI Library:** QFluentWidgets 1.5+ (Fluent Design)
- **Configuration:** Pydantic 2.5+ (validation), PyYAML 6.0+
- **Testing:** pytest 7.4+, pytest-qt, pytest-cov
- **Code Quality:** Ruff (linting + formatting), MyPy (type checking)
- **Version Control:** GitPython 3.1+
- **Async I/O:** aiohttp 3.9+

---

## 🧪 Testing & Quality

<div align="center">

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tests** | 193 | ✅ All passing |
| **Code Coverage** | 73% | ✅ Above 70% threshold |
| **Python Versions** | 3.12, 3.13, 3.14 | ✅ Matrix testing |
| **Pre-commit Hooks** | 15+ checks | ✅ Enforced |
| **OpenSSF Score** | Daily scan | ✅ Monitored |
| **Security Scans** | CodeQL + Bandit | ✅ Clean |

</div>

### Test Categories

- **Unit Tests (95)** - Services, plugins, models in isolation
- **Integration Tests (10)** - End-to-end workflows (plugin install, project creation)
- **GUI Tests (50)** - UI components with pytest-qt
- **Manual Tests (4)** - Full application smoke tests

### Quality Tools

```bash
# Run all checks (same as CI)
just lint                    # Ruff + MyPy
just test                    # pytest with coverage
pre-commit run --all-files   # All hooks

# Individual tools
ruff check app/ tests/       # Linting
ruff format app/ tests/      # Formatting
mypy app/                    # Type checking
bandit -r app/               # Security scanning
pytest --cov=app             # Tests + coverage
```

---

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork** the repository on GitHub
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Code** following our style guide (Ruff enforced)
4. **Test** your changes (`pytest`)
5. **Commit** using Conventional Commits (`feat:`, `fix:`, `docs:`)
6. **Push** to your fork (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request with detailed description

### Code Standards

- ✅ **Type Hints** - All functions have complete type annotations
- ✅ **Modern Types** - Use `list[T]`, `dict[K, V]` (Python 3.12+)
- ✅ **Docstrings** - Google style for all public APIs
- ✅ **Logging** - Use `logging` module, never `print()`
- ✅ **Testing** - Write tests for new features
- ✅ **Coverage** - Maintain 70%+ code coverage

### Getting Help

- 💬 [Discussions](https://github.com/mosh666/pyMM/discussions) - Questions, ideas, feedback
- 🐛 [Issue Tracker](https://github.com/mosh666/pyMM/issues) - Bug reports, feature requests
- 📧 [Email](mailto:24556349+mosh666@users.noreply.github.com) - Security issues only

---

## 📦 Installation Details

### System Requirements

- **OS:** Windows 10 (version 1809+) or Windows 11 (64-bit)
- **Python:** 3.12, 3.13, or 3.14 (for development)
- **Storage:** 500MB+ for application and plugins
- **Recommended:** USB 3.0+ drive or SSD for best performance

### Portable Installation

The application is completely self-contained:

```
D:\pyMM\                     # Application root
├── python313\               # Embedded Python runtime
├── lib-py313\               # Dependencies
├── app\                     # Application code
├── plugins\                 # Plugin manifests
└── launcher.py              # Entry point

D:\pyMM.Projects\            # User projects (drive root)
D:\pyMM.Plugins\             # Installed plugins (drive root)
D:\pyMM.Logs\                # Application logs (drive root)
```

### Available Plugins

| Plugin | Description | Mandatory |
|--------|-------------|-----------|
| **Git** | Version control system | ✅ Yes |
| **FFmpeg** | Video/audio processing | ❌ Optional |
| **ExifTool** | Metadata extraction | ❌ Optional |
| **ImageMagick** | Image processing | ❌ Optional |
| **digiKam** | Photo management | ❌ Optional |
| **MKVToolNix** | Matroska tools | ❌ Optional |

---

## 🔒 Security

Security is a top priority for pyMediaManager.

### Security Features

- ✅ Daily OpenSSF Scorecard monitoring
- ✅ CodeQL static analysis on every PR
- ✅ Dependabot automatic security updates
- ✅ Bandit security linting (pre-commit hook)
- ✅ SHA-256 checksum verification for downloads
- ✅ Sensitive data redaction in logs and exports

### Reporting Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

- 📧 Email: <24556349+mosh666@users.noreply.github.com>
- ⏱️ Response time: 48 hours
- 📋 See [Security Policy](.github/SECURITY.md) for details

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses

pyMediaManager uses the following open-source libraries:

- PySide6 (LGPL v3)
- QFluentWidgets (GPL v3 / Commercial)
- Pydantic (MIT)
- See full list in [pyproject.toml](pyproject.toml)

---

## 📊 Project Stats

<div align="center">

![GitHub stars](https://img.shields.io/github/stars/mosh666/pyMM?style=social)
![GitHub forks](https://img.shields.io/github/forks/mosh666/pyMM?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/mosh666/pyMM?style=social)

![GitHub issues](https://img.shields.io/github/issues/mosh666/pyMM)
![GitHub pull requests](https://img.shields.io/github/issues-pr/mosh666/pyMM)
![GitHub last commit](https://img.shields.io/github/last-commit/mosh666/pyMM)
![GitHub repo size](https://img.shields.io/github/repo-size/mosh666/pyMM)

</div>

---

## 🙏 Acknowledgments

- **Qt/PySide6** - Cross-platform GUI framework
- **QFluentWidgets** - Beautiful Fluent Design components
- **Ruff** - Lightning-fast Python linting and formatting
- **pytest** - Comprehensive testing framework
- **OpenSSF** - Security best practices and tooling

---

## 📖 Citation

If you use pyMediaManager in your research or project:

```bibtex
@software{pyMediaManager,
  author = {mosh666},
  title = {pyMediaManager: Portable Media Management Application},
  year = {2026},
  url = {https://github.com/mosh666/pyMM}
}
```

Or use the citation metadata in [CITATION.cff](CITATION.cff).

---

<div align="center">

**Made with ❤️ by [mosh666](https://github.com/mosh666)**

[⬆ Back to Top](#pymediamanager)

</div>
