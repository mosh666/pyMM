# pyMediaManager

**Portable Python-based media management application with modern Fluent Design UI**

[![Python](https://img.shields.io/badge/python-3.12%20%7C%203.13-blue)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://www.python.org)
[![Status](https://img.shields.io/badge/status-beta-yellow)](https://github.com/mosh666/pyMM)

## Overview

pyMediaManager is a fully portable, Python-based media management application designed to run
entirely from removable drives without system installation. It provides a modern Fluent Design
interface for managing media projects, orchestrating external tools through plugins, and
maintaining version control integration.

### Key Features

- 🎨 **Modern Fluent UI** - Clean, responsive interface using PySide6 and QFluentWidgets
- 💾 **100% Portable** - Zero system installation, runs from USB/external drives
- � **Smart Drive Detection** - Enhanced external drive detection using WMI and Windows APIs
- �🔌 **Flexible Plugin System** - Manage external tools (Git, FFmpeg, ExifTool, digiKam, etc.)
- 📁 **Project Management** - Organize media projects with metadata and templates
- 🔄 **Git Integration** - Built-in version control with GitPython
- 🔒 **Secure Configuration** - Layered settings with sensitive data redaction
- 📊 **Rich Logging** - Structured logging with console and rotating file output
- ✅ **Reliable Downloads** - Plugin downloads with retry logic, checksums, and progress tracking
- ⚡ **Automatic Versioning** - Git-based semantic versioning with setuptools_scm
- 🧪 **Comprehensive Testing** - 199 tests with 73% code coverage and isolated test environment

> **📖 Documentation:**  
> [User Guide](docs/user-guide.md) | [Architecture Guide](docs/architecture.md) | [Contributing](CONTRIBUTING.md) | [CHANGELOG](CHANGELOG.md)

---

## Portable Architecture

pyMediaManager is engineered for true portability with zero system footprint:

### Design Principles

- ✅ **No System Installation** - Extract and run, no installers required
- ✅ **No Registry Modifications** - All settings in portable config files
- ✅ **No PATH Pollution** - Environment modified only for current process
- ✅ **Drive-Agnostic** - Automatic drive detection on startup
- ✅ **Relative Paths** - All references relative to app root
- ✅ **Embedded Runtime** - Ships with Python 3.12/3.13 runtime
- ✅ **Bundled Dependencies** - All packages included (PySide6, Pydantic, GitPython, etc.)

### Directory Structure

```
D:\pyMM\                          # Application directory (portable)
├── python313\                    # Embedded Python 3.13 runtime (win64)
│   ├── python.exe
│   └── python313.dll
├── lib-py313\                    # Python dependencies (version-specific)
│   ├── PySide6\
│   ├── pydantic\
│   └── ...
├── app\                          # Application source code
│   ├── core\                     # Core services
│   │   ├── services\
│   │   │   ├── config_service.py
│   │   │   ├── file_system_service.py
│   │   │   └── storage_service.py
│   │   └── logging_service.py
│   ├── ui\                       # User interface
│   │   ├── main_window.py
│   │   ├── views\
│   │   ├── dialogs\
│   │   └── components\
│   ├── plugins\                  # Plugin system
│   │   ├── plugin_manager.py
│   │   └── plugin_base.py
│   ├── services\
│   │   ├── git_service.py
│   │   └── project_service.py
│   └── models\
│       └── project.py
├── plugins\                      # Plugin manifests (YAML)
│   ├── git\plugin.yaml
│   ├── ffmpeg\plugin.yaml
│   ├── exiftool\plugin.yaml
│   └── ...
├── config\                       # Configuration files
│   ├── app.yaml                  # Default configuration
│   └── user.yaml.example         # User template
├── tests\                        # Test suite
│   ├── unit\
│   ├── integration\
│   └── gui\
├── launcher.py                   # Application entry point
├── pyproject.toml                # Project metadata and dependencies
└── README.md

D:\pyMM.Plugins\                  # Installed plugin binaries (drive root)
├── git\
├── ffmpeg\
├── exiftool\
└── ...

D:\pyMM.Projects\                 # Media projects (drive root)
├── .metadata\                    # Project metadata
└── my-project\
    ├── .git\
    └── assets\

D:\pyMM.Logs\                     # Application logs (drive root)
└── pymediamanager.log
```

**Note:** The `pyMM.Projects`, `pyMM.Plugins`, and `pyMM.Logs` folders are automatically created
at the root of your portable drive (e.g., `D:\`) to ensure they remain accessible even if you
move the `pyMM\` application folder.

---

## Quick Start

### Option 1: Download Pre-Built Release

1. **Download the latest release:**
   - **Beta (Latest Features):** [latest-beta](https://github.com/mosh666/pyMM/releases/tag/latest-beta)
   - **Stable:** [Releases Page](https://github.com/mosh666/pyMM/releases) (when available)
   - **Recommended:** `pyMM-latest-beta-py3.13-win64.zip` (Python 3.13)

2. **Extract to your portable drive:**
   ```cmd
   # Extract to D:\pyMM\ (or any drive letter)
   ```

3. **Run the application:**
   ```cmd
   D:\pyMM\python313\python.exe D:\pyMM\launcher.py
   ```

4. **Complete first-run wizard:**
   - ✅ Confirm portable drive location
   - ✅ Install essential plugins (Git, ExifTool)
   - ✅ Create your first project
   - ✅ Configure theme and preferences

> **📖 New User?** Check out the [User Guide](docs/user-guide.md) for detailed walkthroughs and tutorials.

### Option 2: Build From Source

**Prerequisites:**
- Python 3.12 or 3.13 (3.13 recommended)
- Git

**Setup:**

```bash
# 1. Clone repository
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -e ".[dev]"

# 4. Run tests
pytest

# 5. Run application
python launcher.py
```

**Build Portable Distribution:**
```bash
# Automated via GitHub Actions CI/CD
# Manual build (if needed):
python tools/build_portable.py --python-version 3.13
```

---

## Plugin System

pyMediaManager orchestrates external media tools through a flexible, manifest-based plugin system.

### Available Plugins

#### Mandatory Plugins
- **Git** - Version control for projects (70MB)
- **7-Zip** - Archive extraction for plugin installations (5MB)

#### Optional Plugins

| Plugin | Purpose | Size |
| --- | --- | --- |
| **ExifTool** | Metadata extraction/editing | 8MB |
| **FFmpeg** | Video/audio processing | 100MB |
| **digiKam** | Photo management suite | 500MB |
| **ImageMagick** | Image manipulation | 30MB |
| **MKVToolNix** | Matroska container tools | 35MB |
| **Git LFS** | Large file storage for Git | 10MB |
| **GitVersion** | Semantic versioning from Git | 15MB |
| **MariaDB** | Database backend | 200MB |

### Plugin Features

- ✅ **One-Click Installation** - Install from GUI with progress tracking
- ✅ **Automatic Downloads** - Retry logic with exponential backoff (3 attempts)
- ✅ **SHA256 Verification** - Checksum validation for security
- ✅ **Smart Extraction** - Handles nested archives and complex structures
- ✅ **PATH Registration** - Automatic binary path discovery
- ✅ **Version Detection** - Validates installed plugin versions
- ✅ **Manifest-Driven** - YAML-based plugin definitions

**Installation Location:** All plugins install to `D:\pyMM.Plugins\` and are automatically discovered by the application.

> **📖 Learn More:** [User Guide - Plugin Management](docs/user-guide.md#plugin-management)

---

## Project Management

Organize your media projects with metadata, templates, and version control.

### Features

- ✅ **Create Projects** - Wizard-based project creation with templates
- ✅ **Project Browser** - Search, filter, and browse projects
- ✅ **Metadata Storage** - Project descriptions, tags, and custom fields
- ✅ **Git Integration** - Automatic Git initialization with .gitignore templates
- ✅ **Recent Projects** - Quick access to recently opened projects
- ✅ **Project Templates** - Pre-configured templates for common workflows

### Git Integration

Built-in Git support powered by GitPython:

- Initialize repositories for new projects
- Commit changes with descriptive messages
- View project history and status
- Configure Git user (name, email, default branch)
- Built-in .gitignore templates for media workflows

**Storage:** Project metadata stored in `D:\pyMM.Projects\.metadata\`

---

## User Interface

Modern Fluent Design interface powered by PySide6 and QFluentWidgets.

### Main Views

- **Home** - Dashboard with quick actions and recent projects
- **Storage** - Enhanced drive detection with WMI, capacity monitoring, serial number tracking
- **Plugins** - Plugin installation, updates, and management
- **Projects** - Project browser with search and filtering
- **Settings** - Comprehensive configuration with 5 tabs

### First-Run Wizard

Multi-step setup wizard for initial configuration with intelligent drive detection:

1. **Welcome** - Feature overview and introduction
2. **Drive Detection** - Enhanced portable drive selection
   - Detects USB flash drives, SD cards, and removable media
   - Identifies external HDDs and SSDs (even when classified as "fixed" by Windows)
   - Uses WMI to detect USB interface and external media type
   - Displays drive capacity, free space, and volume labels
3. **Plugin Installation** - Install essential plugins (Git, ExifTool)
4. **Settings** - Configure theme, language, and preferences
5. **Complete** - Summary and "Don't show again" option

### Settings Dialog

Tabbed interface with comprehensive configuration:

- **General** - Theme (Light/Dark/Auto), language, auto-updates
- **Plugins** - Auto-install, download timeout, checksum verification
- **Storage** - Default drive, project root, log location
- **Git** - User name, email, default branch
- **About** - Version info, commit hash, license

### Theme Support

- **Light Mode** - Clean, bright interface
- **Dark Mode** - Eye-friendly dark theme
- **Auto Mode** - Follows system theme settings
- **High DPI** - Full support for high-resolution displays

---

## Configuration

Layered configuration system with secure defaults.

### Configuration Layers

1. **Defaults** - `config/app.yaml` (committed to repository)
2. **User Settings** - `config/user.yaml` (gitignored, user-specific)
3. **Runtime Overrides** - Environment variables (if needed)

### Key Configuration Options

```yaml
# config/app.yaml
app_name: pyMediaManager

paths:
  projects_dir: pyMM.Projects  # Drive root
  logs_dir: pyMM.Logs          # Drive root
  plugins_dir: pyMM.Plugins    # Drive root
  config_dir: config           # App root

logging:
  level: INFO
  console_enabled: true
  file_enabled: true
  max_file_size: 10485760     # 10MB
  backup_count: 5

ui:
  theme: auto                  # light, dark, or auto
  show_first_run: true
  window_width: 1200
  window_height: 800

plugins:
  auto_update_check: true
  download_timeout: 300        # seconds
  parallel_downloads: 3
```

### Security Features

- ✅ **Sensitive Data Redaction** - Passwords, API keys hidden in logs
- ✅ **Isolated Configuration** - User settings in separate file
- ✅ **Pydantic Validation** - Strong typing and schema validation
- ✅ **SHA256 Checksums** - Plugin download verification
- ✅ **No Credentials in Logs** - Automatic redaction of sensitive fields

> **📖 Configuration Reference:** [User Guide - Settings](docs/user-guide.md#settings--configuration)

---

## Logging

Comprehensive logging system with Rich formatting and file rotation.

### Logging Features

- **Console Output** - Rich-formatted with colors, timestamps, and structure
- **File Logging** - Rotating logs at `D:\pyMM.Logs\pymediamanager.log`
- **Log Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Automatic Rotation** - 10MB limit, 5 backup files
- **UTF-8 Encoding** - Proper character handling
- **Structured Logging** - Consistent format across all modules

### Log Configuration

```python
# Configure via config/app.yaml or programmatically
logger = logging_service.setup()
logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### Log Location

- **Windows:** `D:\pyMM.Logs\pymediamanager.log`
- **Rotation:** `pymediamanager.log.1`, `pymediamanager.log.2`, etc.

---

## Version Management

Automatic semantic versioning powered by `setuptools_scm`.

### Versioning Features

- ✅ **Git-Based Versioning** - Version derived from Git tags
- ✅ **Semantic Versioning** - Supports `vX.Y.Z`, `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`
- ✅ **Runtime Access** - Version available via `app.__version__`
- ✅ **Commit Hash** - Full commit ID via `app.__commit_id__`
- ✅ **Fallback** - Graceful fallback to `importlib.metadata` or `0.0.0-dev`
- ✅ **UI Integration** - Displayed in Settings > About tab

### Version Examples

- `0.1.0` - Stable release
- `0.1.0-beta.1` - Beta release
- `0.1.0-alpha.2` - Alpha release
- `0.1.0-rc.1` - Release candidate
- `0.1.1.dev0+g1234567` - Development build

---

## Development

### Testing

Comprehensive test suite with multiple test types:

```bash
# Run all tests with coverage
pytest

# Run specific test suites
pytest tests/unit              # Unit tests only
pytest tests/integration       # Integration tests only
pytest tests/gui               # GUI tests (requires display)

# Run with detailed coverage report
pytest --cov=app --cov-report=html

# Run tests excluding GUI (CI/headless)
pytest tests/unit tests/integration
```

**Test Statistics:**
- **Total Tests:** 137+
- **Code Coverage:** 73% on core modules
- **Test Types:** Unit, Integration, GUI (pytest-qt)
- **Markers:** `integration`, `slow`, `ui`

### Code Quality Tools

```bash
# Lint with Ruff (replaces Black, flake8, isort)
ruff check app/ tests/
ruff format app/ tests/

# Type checking with MyPy
mypy app/

# Run pre-commit hooks
pre-commit run --all-files
```

### Code Style Standards

- **Ruff** - Fast linting and formatting
- **MyPy** - Static type checking
- **Modern Type Hints** - Python 3.12+ native generics (`list`, `dict`, `tuple`)
- **Structured Logging** - No print statements, proper logger usage
- **Return Type Annotations** - All functions have explicit return types
- **Docstrings** - Google-style docstrings for public APIs

### Project Structure

```
pyMM/
├── app/                      # Application code
│   ├── core/                 # Core services
│   │   ├── services/
│   │   │   ├── config_service.py
│   │   │   ├── file_system_service.py
│   │   │   └── storage_service.py
│   │   └── logging_service.py
│   ├── ui/                   # User interface
│   │   ├── main_window.py
│   │   ├── views/
│   │   ├── dialogs/
│   │   └── components/
│   ├── plugins/              # Plugin system
│   │   ├── plugin_manager.py
│   │   └── plugin_base.py
│   ├── services/
│   │   ├── git_service.py
│   │   └── project_service.py
│   └── models/
│       └── project.py
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   ├── integration/          # Integration tests
│   └── gui/                  # GUI tests
├── plugins/                  # Plugin manifests (YAML)
├── config/                   # Configuration files
├── docs/                     # Documentation
├── launcher.py               # Entry point
└── pyproject.toml           # Project metadata
```

---

## CI/CD Pipeline

Automated build and release workflow powered by GitHub Actions.

### Release Strategy

**Beta Releases (`dev` branch)**:
- Automatic deployment on every push to `dev`
- Tagged as `latest-beta` (rolling tag)
- Old assets automatically cleaned before new builds uploaded
- Includes Python 3.12, 3.13, and 3.14 builds
- Pre-release flag enabled
- Download: [latest-beta](https://github.com/mosh666/pyMM/releases/tag/latest-beta)

**Stable Releases (`main` branch)**:
- Manual deployment via version tags (e.g., `v1.0.0`)
- Semantic versioning: `vX.Y.Z` or `vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`
- Permanent releases with changelog
- Download: [Releases Page](https://github.com/mosh666/pyMM/releases)

### Pipeline Features

- ✅ **Branch-Based Releases**
  - `dev` branch → Beta releases (`latest-beta` tag)
  - `main` branch → Stable releases (semantic version tags)
- ✅ **Automated Testing** - Run full test suite on push/PR
- ✅ **Python Matrix** - Test on Python 3.12 and 3.13
- ✅ **Portable Builds** - Embeddable Python runtime + dependencies
- ✅ **Runtime Caching** - Cached Python embeddable archives for faster builds
- ✅ **Artifact Generation** - Release ZIP files with embedded runtime
- ✅ **Version Injection** - setuptools_scm version in artifacts

### Release Process

1. **Development** - Work on `dev` branch
2. **Testing** - Automated CI tests on push
3. **Beta Release** - Push to `dev` → `latest-beta` tag updated
4. **Merge to Main** - PR from `dev` to `main`
5. **Stable Release** - Tag `main` with `vX.Y.Z` → stable release

---

## Roadmap

### Current Version: Beta (Unreleased on `dev`)

✅ **Completed Features:**
- Automatic version management with setuptools_scm
- Modernized CI/CD with branch-based releases
- QFluentWidgets navigation error fixes
- Comprehensive test suite (137+ tests, 73% coverage)
- Modern Fluent UI with theming
- Plugin system with retry logic and checksums
- Project management with Git integration
- First-run wizard and settings dialog
- Rich logging and configuration system

### v0.2.0 (Planned - Q1 2026)

🔄 **Upcoming Features:**
- Media import and organization tools
- Batch metadata editing with ExifTool integration
- Export presets and profiles
- Advanced plugin workflow integration
- Plugin update notifications
- Enhanced project templates

### v0.3.0 (Planned - Q2 2026)

🔮 **Future Vision:**
- Cloud storage integration (OneDrive, Google Drive, Dropbox)
- Team collaboration features
- Advanced search and filtering
- Automated backup system
- Cross-platform support (Linux, macOS)
- Plugin marketplace

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/pyMM.git`
3. **Create branch:** `git checkout -b feature/amazing-feature`
4. **Make changes** and add tests
5. **Run tests:** `pytest`
6. **Commit:** `git commit -m 'Add amazing feature'`
7. **Push:** `git push origin feature/amazing-feature`
8. **Open Pull Request** to `dev` branch

### Contribution Guidelines

- ✅ Follow Ruff code style (auto-formatted)
- ✅ Add tests for new features (maintain 70%+ coverage)
- ✅ Update documentation for user-facing changes
- ✅ Use conventional commits for clear history
- ✅ Ensure all tests pass before submitting PR

---

## License

MIT License - see [LICENSE](LICENSE) for full details.

Copyright (c) 2026 mosh666

---

## Acknowledgments

- **[PySide6](https://doc.qt.io/qtforpython/)** - Qt for Python bindings
- **[QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)** - Modern Fluent Design components
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation and settings management
- **[GitPython](https://gitpython.readthedocs.io/)** - Git integration
- **[Rich](https://rich.readthedocs.io/)** - Beautiful console output
- **Plugin Authors** - All external tool developers (FFmpeg, ExifTool, Git, etc.)

---

## Support & Community

- 🐛 **Issues:** [GitHub Issues](https://github.com/mosh666/pyMM/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/mosh666/pyMM/discussions)
- 📖 **Wiki:** [GitHub Wiki](https://github.com/mosh666/pyMM/wiki) (coming soon)
- 📧 **Contact:** [24556349+mosh666@users.noreply.github.com](mailto:24556349+mosh666@users.noreply.github.com)

---

## Project Status

🚧 **Beta Development** - January 2026

- Current Branch: `dev`
- Latest Tag: `latest-beta`
- Python: 3.12, 3.13
- Platform: Windows (Linux/macOS planned)
- Status: Active Development

> **📖 Release Notes:** See [CHANGELOG.md](CHANGELOG.md) for detailed version history and all changes.
