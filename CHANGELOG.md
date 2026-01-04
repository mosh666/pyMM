# Changelog

All notable changes to pyMediaManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Automatic Version Management**
  - Implemented `setuptools_scm` for Git-based versioning
  - Added runtime version detection with fallback
  - Added "About" tab in Settings dialog to display version and commit hash
- **Modernized GitHub Workflows**
  - Implemented branch-based release flow: `dev` → Beta, `main` → Stable
  - Added support for alpha/beta/rc tags in versioning and releases
  - Added caching for embeddable Python to speed up builds
  - Added `contents: read` permissions to workflows for better security
  - Automated `latest-beta` rolling releases on `dev` branch pushes

### Changed
- Updated `pyproject.toml` to allow semantic versioning with prerelease suffixes (e.g., `v1.0.0-alpha.1`)
- Updated documentation to reflect new release process

### Fixed
- Markdown linting issues in documentation files
- Version inconsistencies between README (0.1.0) and code (0.0.1)
- Python 3.14 references updated to reflect actual availability (3.13 is current stable)

## [0.1.0] - 2026-01-04

### Added
- **Project Management System**
  - Create and manage media projects with metadata
  - Project browser with search and filtering capabilities
  - Recent projects quick access list
  - Project templates for common workflows
  
- **Git Integration**
  - Initialize Git repositories for new projects
  - Commit changes with descriptive messages
  - View project history and status
  - Built-in .gitignore templates for media projects
  - Git user configuration in settings
  
- **Enhanced Plugin System**
  - Reliable plugin downloads with automatic retry logic (3 attempts with exponential backoff)
  - SHA256 checksum verification for security
  - Progress tracking with detailed status indicators
  - One-click installation from GUI
  - Automatic version detection and validation
  - Support for mandatory plugins (Git, 7-Zip) and optional plugins (ExifTool, FFmpeg, digiKam, etc.)
  - Plugin PATH registration for system integration
  
- **Modern Fluent UI**
  - PySide6-based interface with Fluent Design components
  - Side navigation with collapsible menu
  - Light, Dark, and Auto (system) theme support
  - High DPI scaling support
  - Acrylic effects and transparency
  
- **First-Run Wizard**
  - Welcome screen with feature introduction
  - Portable drive detection and configuration
  - Plugin discovery and optional installation
  - Settings configuration wizard
  
- **Comprehensive Settings Dialog**
  - General settings (theme, language, updates)
  - Plugin configuration (auto-install, timeouts, verification)
  - Storage preferences (default drive, project root, log location)
  - Git configuration (user name, email, default branch)
  - Tabbed interface for organized settings
  
- **Portable Architecture**
  - Fully portable operation from removable drives
  - No system installation required
  - Embedded Python runtime (3.12, 3.13 support)
  - Bundled dependencies
  - Drive-root storage for projects and logs
  - Automatic drive detection
  
- **Configuration Management**
  - Layered configuration system (defaults → app → user)
  - Pydantic-based validation
  - Sensitive data redaction
  - YAML-based configuration files
  - Export functionality with optional secret redaction
  
- **Logging System**
  - Rich-formatted console output with colors
  - Rotating file logs (10MB limit, 5 backups)
  - Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - Structured logging throughout codebase
  - Logs stored at portable drive root
  
- **File System Services**
  - Abstraction layer for portable path handling
  - Automatic directory creation
  - Cross-platform path operations
  - Disk space monitoring
  
- **Storage Services**
  - Drive detection (fixed and removable)
  - Drive serial number tracking
  - Capacity and free space monitoring
  - Removable drive identification
  
- **Testing Infrastructure**
  - Comprehensive test suite with 137+ tests
  - Unit tests for core services
  - Integration tests for workflows
  - GUI tests using pytest-qt
  - 70%+ code coverage on core modules
  - pytest configuration with coverage reporting
  
- **Documentation**
  - Comprehensive README with quick start guide
  - Architecture documentation with design principles
  - User guide with tutorials and troubleshooting
  - Contributing guidelines with code style standards
  - Plugin manifests for all supported tools

### Changed
- Migrated from print statements to structured logging across all modules
- Updated to modern Python 3.12+ type hints (native generics)
- Implemented proper dependency injection for services
- Organized code into clear service layers

### Fixed
- Drive serial number detection on various USB drives
- Plugin download retry logic with proper error handling
- Configuration validation and error messages
- File encoding issues (UTF-8 throughout)

## [0.0.1] - 2025-12-15

### Added
- Initial project structure
- Basic application launcher
- Core service architecture
- Plugin manager foundation
- Project management models
- Configuration service with Pydantic
- Logging service setup
- Basic GUI framework with PySide6

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- N/A (initial release)

---

## Version History Summary

- **v0.1.0** (2026-01-04) - First Beta Release
  - Full project management system
  - Git integration
  - Enhanced plugin system with reliability features
  - Comprehensive UI with settings
  - First-run wizard
  - Extensive testing coverage

- **v0.0.1** (2025-12-15) - Initial Alpha
  - Core architecture and services
  - Basic plugin system
  - Foundation for future features

## Upcoming Features

See [docs/roadmap.md](docs/roadmap.md) for planned features in future releases.

### v0.2.0 (Planned)
- Media import and organization tools
- Batch metadata editing
- Export presets and profiles
- Advanced plugin workflow integration
- Improved plugin marketplace

### v0.3.0 (Planned)
- Cloud storage integration (OneDrive, Google Drive, Dropbox)
- Team collaboration features
- Advanced search and filtering
- Automated backup system
- Cross-platform support (Linux, macOS)

---

[Unreleased]: https://github.com/mosh666/pyMM/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/mosh666/pyMM/compare/v0.0.1...v0.1.0
[0.0.1]: https://github.com/mosh666/pyMM/releases/tag/v0.0.1
