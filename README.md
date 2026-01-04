# pyMediaManager

**Portable Python-based media management application with modern Fluent Design UI**

Version: 0.0.1 (Initial Development)

## Overview

pyMediaManager is a complete rewrite of [PSmediaManager](https://github.com/mosh666/PSmediaManager) in Python, featuring:

- 🎨 **Modern Fluent Design UI** using PySide6 and Fluent Widgets
- 💾 **Fully Portable** - runs from removable drives with no system installation
- 🔌 **Plugin System** - manages external tools (digiKam, FFmpeg, ImageMagick, etc.)
- 📁 **Project-Based Workflow** - organize media projects with version control integration
- 🔒 **Secure Configuration** - isolated settings with sensitive data redaction
- 📊 **Comprehensive Logging** - rich console output and rotating file logs

> **📖 For detailed technical documentation, see [Architecture Guide](docs/architecture.md)**

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

**Note:** The `pyMM.Projects` and `pyMM.Logs` folders are automatically created at the root of your portable drive (e.g., `D:\`) to ensure they remain accessible even if you move the `pyMM\` application folder.

## Quick Start

### Download Pre-Built Release

1. Download the latest release for your Python version:
   - **Recommended:** `pyMM-v0.0.1-py313-win64.zip` (Python 3.13)
   - `pyMM-v0.0.1-py312-win64.zip` (Python 3.12)

2. Extract to your portable drive (e.g., `D:\pyMM\`)

3. Run `launcher.py`:
   ```cmd
   D:\pyMM\python313\python.exe D:\pyMM\launcher.py
   ```

4. Complete the first-run wizard:
   - Confirm portable drive location
   - Select optional plugins to install
   - Configure default settings

### Build From Source

**Prerequisites:**
- Python 3.12+ installed on development machine
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
- **digiKam** - Media asset management
- **ExifTool** - Metadata manipulation
- **MariaDB** - Database backend for digiKam
- **Git** - Version control
- **GitVersion** - Semantic versioning
- **Git LFS** - Large file storage

### Optional Plugins
- **FFmpeg** - Video/audio processing
- **ImageMagick** - Image manipulation
- **MKVToolNix** - Matroska container tools

Plugins are managed via the GUI with one-click installation from official sources.

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

```bash
# Run all tests with coverage
pytest

# Run only unit tests
pytest tests/unit/

# Run only GUI tests
pytest tests/gui/

# Generate HTML coverage report
pytest --cov-report=html
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

## Configuration

Configuration follows a layered approach (defaults → environment → user):

1. **defaults** - `config/app.yaml` (committed to repo)
2. **environment** - Environment variables
3. **user** - `config/user.yaml` (gitignored, user-specific)

Sensitive data (passwords, API keys) is automatically redacted in logs and exports.

## Logging

pyMediaManager provides rich logging with multiple outputs:

- **Console** - Rich formatted output with colors and structure
- **File** - Rotating logs at `D:\pyMM.Logs\` (on portable drive root)
- **Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL

Logs are automatically rotated (10MB limit) with compression.

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

- Original [PSmediaManager](https://github.com/mosh666/PSmediaManager) PowerShell implementation
- [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) for modern UI components
- All plugin authors for their excellent tools

## Support

- **Issues:** https://github.com/mosh666/pyMM/issues
- **Discussions:** https://github.com/mosh666/pyMM/discussions
- **Documentation:** https://github.com/mosh666/pyMM/wiki

---

**Status:** 🚧 Active Development - v0.0.1 Initial Release
