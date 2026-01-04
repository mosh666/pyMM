# pyMediaManager

**Portable Python-based media management application with modern Fluent Design UI**

Version: 0.1.0-beta (In Development)

## Overview

pyMediaManager is a portable Python-based media management application featuring:

- 🎨 **Modern Fluent Design UI** using PySide6 and Fluent Widgets
- 💾 **Fully Portable** - runs from removable drives with no system installation
- 🔌 **Plugin System** - manages external tools (digiKam, FFmpeg, ImageMagick, etc.)
- 📁 **Project-Based Workflow** - organize media projects with version control integration
- 🔒 **Secure Configuration** - isolated settings with sensitive data redaction
- 📊 **Comprehensive Logging** - rich console output and rotating file logs
- ✅ **Reliable Downloads** - plugin downloads with retry logic and checksum verification
- 🔄 **Git Integration** - built-in version control for projects

> **📖 Documentation:**  
> [User Guide](docs/user-guide.md) | [Architecture Guide](docs/architecture.md) | [CHANGELOG](CHANGELOG.md)

## Portable Architecture

pyMediaManager is designed to run entirely from a removable drive (USB, external SSD) with zero system modifications:

- **No Installation Required** - unzip and run
- **Embedded Python** - ships with Python 3.12+ runtime
- **Bundled Dependencies** - all Python packages included
- **Isolated Configuration** - settings stored within app directory
- **Drive-Root Storage** - projects and logs stored at portable drive root (`D:\pyMM.Projects`, `D:\pyMM.Logs`)

### Directory Structure

```
D:\pyMM\                          # Application directory
├── python312\                    # Embedded Python runtime (win64)
├── lib-py312\                    # Python dependencies
├── app\                          # Application code
├── plugins\                      # Plugin manifests (YAML)
├── config\                       # Default configurations
├── launcher.py                   # Entry point
└── README.md

D:\pyMM.Plugins\                  # Installed plugin binaries
├── digikam\
├── ffmpeg\
├── git\
└── ...

D:\pyMM.Projects\                 # Media projects (drive root)
└── my-project\

D:\pyMM.Logs\                     # Application logs (drive root)
└── pymediamanager.log
```

**Note:** The `pyMM.Projects` and `pyMM.Logs` folders are automatically created at the root of your
portable drive (e.g., `D:\`) to ensure they remain accessible even if you move the `pyMM\`
application folder.

## Quick Start

### Download Pre-Built Release

1. Download the latest release for your Python version:
   - **Recommended:** `pyMM-v0.1.0-py313-win64.zip` (Python 3.13)
   - Also available: `pyMM-v0.1.0-py312-win64.zip` (Python 3.12)

2. Extract to your portable drive (e.g., `D:\pyMM\`)

3. Run `launcher.py`:
   ```cmd
   D:\pyMM\python314\python.exe D:\pyMM\launcher.py
   ```

4. Complete the first-run wizard:
   - Confirm portable drive location
   - Install essential plugins (Git, ExifTool)
   - Create your first project
   - Configure preferences

> **📖 New to pyMediaManager? Check out the [User Guide](docs/user-guide.md) for detailed instructions.**

### Build From Source

**Prerequisites:**
- Python 3.12 or 3.13 installed on development machine (3.13 recommended)
- Git for version control

**Steps:**

1. Clone the repository:
   ```bash
   git clone https://github.com/mosh666/pyMM.git
   cd pyMM
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Run tests:
   ```bash
   pytest
   ```

4. Build portable distribution:
   ```bash
   # Automated via GitHub Actions, or manually:
   python tools/build_portable.py --python-version 3.12
   ```

## Plugin System

pyMediaManager orchestrates external tools through a flexible plugin system:

### Mandatory Plugins
- **Git** - Version control for projects
- **7-Zip** - Archive extraction for plugin installations

### Optional Plugins  
- **ExifTool** - Metadata extraction (8MB)
- **FFmpeg** - Video/audio processing (100MB)
- **digiKam** - Photo management suite (500MB)
- **ImageMagick** - Image manipulation (30MB)
- **MKVToolNix** - Matroska container tools (35MB)
- **HandBrake** - Video transcoding (20MB)
- **MediaInfo** - Media file analysis (5MB)

**Features:**
- ✅ One-click installation from GUI
- ✅ Automatic download with retry logic (3 attempts, exponential backoff)
- ✅ SHA256 checksum verification for security
- ✅ Progress tracking with detailed status
- ✅ Automatic PATH registration
- ✅ Version detection and validation

Plugins install to `D:\pyMM.Plugins\` and are automatically discovered by the application.

> **📖 See [User Guide - Plugin Management](docs/user-guide.md#plugin-management) for installation instructions.**

## Development

### Project Structure

```
pyMM/
├── app/
│   ├── core/
│   │   ├── services/          # Service layer (storage, config, plugins)
│   │   └── logging_service.py
│   ├── ui/
│   │   ├── views/             # Main application views
│   │   ├── components/        # Reusable UI components
│   │   └── main_window.py
│   ├── plugins/
│   │   └── plugin_manager.py
│   └── projects/
│       └── project_manager.py
├── tests/
│   ├── unit/                  # Unit tests (pytest)
│   └── gui/                   # GUI tests (pytest-qt)
├── plugins/                   # Plugin manifests (YAML)
└── config/                    # Configuration schemas
```

### Testing

We maintain comprehensive test coverage for all core functionality:

```bash
# Run all tests with coverage
pytest

# Run specific test suites
pytest tests/unit                    # Unit tests only
pytest tests/integration             # Integration tests only
pytest tests/gui                     # GUI tests (requires X server)

# Run tests with detailed coverage report
pytest --cov=app --cov-report=html

# Run tests excluding GUI (CI/headless)
pytest tests/unit tests/integration
```

**Test Coverage Status:**
- **Total Tests:** 137 passing
- **Core Coverage:** 70-100% on business logic modules
- **Test Types:** Unit, Integration, GUI (pytest-qt)

See [Testing Status](docs/testing-status.md) for detailed coverage breakdown.

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

## Features

### v0.1.0 (Current - Beta)

✅ **Project Management**
- Create and manage media projects with metadata
- Project templates for common workflows
- Project browser with search and filtering
- Recent projects quick access

✅ **Git Integration**
- Initialize Git repositories for new projects
- Commit changes with descriptive messages
- View project history and status
- Built-in .gitignore templates

✅ **Enhanced Plugin System**
- Reliable downloads with retry logic (3 attempts)
- SHA256 checksum verification
- Progress tracking and detailed status
- One-click installation from GUI
- Automatic version detection

✅ **Settings UI**
- Comprehensive settings dialog with tabs
- Theme selection (Light/Dark/Auto)
- Plugin configuration
- Storage preferences
- Git user configuration

✅ **Robust Testing**
- 137 comprehensive tests
- 70%+ coverage on core modules
- Unit, integration, and GUI test suites

### Roadmap

🔄 **v0.2.0** (Planned)
- Media import and organization
- Batch metadata editing
- Export presets and profiles
- Advanced plugin workflow integration

🔄 **v0.3.0** (Planned)  
- Cloud storage integration
- Team collaboration features
- Advanced search and filtering
- Automated backup system

## Configuration

Configuration follows a layered approach (defaults → environment → user):

1. **defaults** - `config/app.yaml` (committed to repo)
2. **environment** - Environment variables
3. **user** - `config/user.yaml` (gitignored, user-specific)

Sensitive data (passwords, API keys) is automatically redacted in logs and exports.

> **📖 See [User Guide - Settings](docs/user-guide.md#settings--configuration) for configuration options.**

## Logging

pyMediaManager provides rich logging with multiple outputs:

- **Console** - Rich formatted output with colors and structure
- **File** - Rotating logs at `D:\pyMM.Logs\` (on portable drive root)
- **Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL

Logs are automatically rotated (10MB limit, 5 backups) with proper encoding.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Guidelines

- Follow existing code style (Black formatting)
- Add tests for new features (maintain 70%+ coverage)
- Update documentation for user-facing changes
- Use conventional commits for clear history

## License

MIT License - see [LICENSE](LICENSE) for details

## Acknowledgments

- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) for modern UI components
- All plugin authors for their excellent tools

## Support

- **Issues:** https://github.com/mosh666/pyMM/issues
- **Discussions:** https://github.com/mosh666/pyMM/discussions
- **Documentation:** https://github.com/mosh666/pyMM/wiki

---

**Status:** 🚧 v0.1.0-beta In Development - January 2026

> **Note:** See [CHANGELOG.md](CHANGELOG.md) for detailed version history and release notes.
