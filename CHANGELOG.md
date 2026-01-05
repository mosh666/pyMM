# Changelog

All notable changes to pyMediaManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Test Environment Isolation**
  - Implemented automatic test isolation to prevent system drive pollution
  - Added global `mock_drive_root` fixture to redirect all file operations to temporary directories
  - Tests no longer create `pyMM.Logs` or `pyMM.Projects` folders on C:\ or other system drives
  - All 199 tests now run in completely isolated temporary environments
  - Automatic cleanup of test artifacts after test completion

- **Automatic Version Management**
  - Implemented `setuptools_scm` for Git-based semantic versioning
  - Runtime version detection with fallback to `importlib.metadata`
  - Version and commit hash displayed in Settings → About tab
  - Support for alpha, beta, and rc prerelease tags

- **Modernized CI/CD Pipeline**
  - Branch-based release flow: `dev` → Beta releases, `main` → Stable releases
  - Automated `latest-beta` rolling tag on `dev` branch pushes
  - Python embeddable runtime caching to speed up builds
  - Added `contents: read` permissions for better security
  - Support for Python 3.14 in CI workflows (forward compatibility)

### Changed

- Expanded test suite from 137 to 199 tests with improved coverage
- Updated `pyproject.toml` to support semantic versioning with prerelease suffixes
- Improved documentation structure and clarity with accurate test counts
- Enhanced test coverage for settings dialog (5 tabs expected)
- Modernized all documentation to reflect current architecture and features

### Fixed

- **QFluentWidgets Navigation Error**: Fixed "object name can't be empty string" error by adding
  `setObjectName()` calls to all navigation interfaces and views
  - Home interface
  - Settings interface
  - Storage view
  - Plugin view
  - Project view
- Import sorting issues in `app/__init__.py` (resolved via Ruff)
- Markdown linting issues across documentation files
- Version inconsistencies between README and codebase
- Text formatting in first-run wizard welcome message
- Async mock warnings in plugin download tests
- Path comparison issues in file system service tests
- Ruff ignore rules for auto-generated `_version.py` file

### Removed

- Obsolete research and planning documentation
- Deprecated release and testing documentation files
- Unused deployment and setup files
- Test plugin and project folders from repository
- Legacy requirements.txt files (now using pyproject.toml)

## [0.0.1] - 2026-01-03

### Added

- **Core Architecture**
  - Service-oriented architecture with dependency injection
  - Modular design with clear separation of concerns
  - Pydantic-based configuration management
  - Comprehensive logging service with Rich formatting

- **Portable Design**
  - Fully portable operation from removable drives
  - No system installation or registry modifications required
  - Embedded Python runtime support (3.12, 3.13)
  - Automatic drive detection and path handling
  - Drive-root storage for projects (`pyMM.Projects`) and logs (`pyMM.Logs`)

- **Plugin System**
  - YAML-based plugin manifests
  - Plugin discovery and validation
  - Download and extraction support for ZIP and 7z archives
  - Retry logic with exponential backoff (3 attempts)
  - SHA256 checksum verification for security
  - Nested folder handling for complex archives
  - Support for mandatory plugins (Git, 7-Zip) and optional plugins
  - Plugin manifests for: digiKam, ExifTool, FFmpeg, Git, Git LFS, GitVersion, ImageMagick,
    MariaDB, MKVToolNix

- **Project Management**
  - Create and manage media projects with metadata
  - Project browser with search and filtering
  - Project templates for common workflows
  - Git repository initialization for projects
  - Project metadata storage in `.metadata` directory
  - Recent projects tracking

- **Git Integration**
  - GitPython-based version control integration
  - Initialize Git repositories for new projects
  - Commit tracking and history viewing
  - Built-in .gitignore templates for media projects
  - Git user configuration (name, email, default branch)
  - Repository status checking

- **Modern Fluent UI**
  - PySide6-based interface with QFluentWidgets
  - Side navigation with Home, Storage, Plugins, Projects, Settings
  - Light, Dark, and Auto (system-based) theme support
  - High DPI scaling support
  - Responsive layout design

- **First-Run Wizard**
  - Multi-step setup wizard for initial configuration
  - Welcome screen with feature overview
  - Portable drive detection and selection
  - Optional plugin installation
  - Settings configuration
  - "Don't show again" option

- **Settings Dialog**
  - Tabbed interface with 5 sections:
    - General (theme, language, auto-updates)
    - Plugins (auto-install, download timeout, checksum verification)
    - Storage (default drive, project root, log location)
    - Git (user name, email, default branch)
    - About (version info, commit hash, license)
  - Real-time validation
  - Settings persistence

- **Storage Management**
  - Drive detection (fixed and removable)
  - Drive serial number tracking
  - Capacity and free space monitoring
  - Drive type identification
  - Removable drive filtering

- **Configuration Services**
  - Layered configuration system (defaults → app → user)
  - YAML-based configuration files
  - Pydantic validation
  - Sensitive data redaction for logging
  - Configuration export functionality

- **Logging System**
  - Rich-formatted console output with colors and timestamps
  - Rotating file logs (10MB limit, 5 backups)
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Structured logging throughout entire codebase
  - Logs stored at portable drive root (`pyMM.Logs`)

- **Testing Infrastructure**
  - Comprehensive test suite with 137+ tests
  - Unit tests for all core services
  - Integration tests for plugin and project workflows
  - GUI tests using pytest-qt
  - 73% code coverage on core modules
  - pytest configuration with fixtures and markers
  - Coverage reporting and test organization

- **Code Quality Tools**
  - Pre-commit hooks for automated checks
  - Ruff for linting and formatting
  - MyPy for static type checking (all errors resolved)
  - Black code formatter integration
  - Comprehensive type hints (Python 3.12+ native generics)
  - Return type annotations on all functions

- **Documentation**
  - Comprehensive README with quick start guide
  - Architecture documentation with design principles
  - User guide with tutorials and troubleshooting
  - Contributing guidelines with code style standards
  - Deployment guide for GitHub releases
  - Project status tracking documents

### Changed

- Migrated from print statements to structured logging across all modules
- Updated to modern Python 3.12+ type hints (native generics instead of `typing` module)
- Implemented proper dependency injection for services
- Organized code into clear service layers (core, UI, plugins, projects)
- Reformatted entire codebase with Black and Ruff
- Enhanced error handling with proper exception types

### Fixed

- Critical bug fixes for logger initialization in UI modules
- Pydantic serialization issues in test mocks
- File encoding issues (standardized to UTF-8 throughout)
- Drive serial number detection on various USB drives
- Plugin download error handling
- Configuration validation edge cases
- Escape sequence warnings in docstrings
- File system path resolution issues
- Test fixture cleanup and isolation

### Security

- SHA256 checksum verification for all plugin downloads
- Sensitive data redaction in logs and configuration exports
- Secure configuration file handling
- No credentials stored in plain text

---

## Version History Summary

- **[Unreleased]** (dev branch) - Development builds with latest features
  - Automatic version management with setuptools_scm
  - Enhanced CI/CD with branch-based releases
  - QFluentWidgets navigation fixes
  - Documentation improvements

- **v0.0.1** (2026-01-03) - Initial Release
  - Complete portable architecture
  - Plugin system with download and verification
  - Project management with Git integration
  - Modern Fluent UI with themes
  - Comprehensive settings and configuration
  - First-run wizard
  - 73% test coverage

---

## Upcoming Features

### v0.2.0 (Planned)

- Media import and organization tools
- Batch metadata editing with ExifTool integration
- Export presets and profiles
- Advanced plugin workflow integration
- Plugin update notifications
- Enhanced project templates

### v0.3.0 (Planned)

- Cloud storage integration (OneDrive, Google Drive, Dropbox)
- Team collaboration features
- Advanced search and filtering
- Automated backup system
- Cross-platform support (Linux, macOS)
- Plugin marketplace

---

## Links

[Unreleased]: https://github.com/mosh666/pyMM/compare/v0.0.1...dev
[0.0.1]: https://github.com/mosh666/pyMM/releases/tag/v0.0.1
