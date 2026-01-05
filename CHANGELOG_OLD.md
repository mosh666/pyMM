# Changelog

All notable changes to pyMediaManager will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Comprehensive Pre-Commit Quality Gates**
  - Implemented 15+ automated checks that run before every commit:
    - Ruff linting with auto-fix for code quality
    - Ruff formatting for consistent code style
    - MyPy type checking for type safety
    - Markdown linting for documentation quality
    - YAML, TOML, and JSON validation
    - Security checks (private key detection)
    - Fast unit tests (140 tests) on commit
    - Full test suite (193 tests) on push
  - Created automated setup script for Windows (`scripts/setup-git-hooks.ps1`)
  - Created automated setup script for Linux/macOS (`scripts/setup-git-hooks.sh`)
  - Added `.pre-commit-config.yaml` with comprehensive hook configuration
  - PowerShell-based Git hooks for native Windows compatibility
  - All quality gates now passing: 193 tests, 72.77% coverage, zero linting errors, zero type errors

- **Enhanced CI/CD Pipeline**
  - 6 separate validation jobs with fail-fast strategy:
    - Lint job with strict Ruff checking (PASSING)
    - Type-check job with MyPy validation (PASSING)
    - Test matrix for Python 3.12, 3.13, 3.14 on Windows (PASSING)
    - Lint-docs job for documentation validation (PASSING)
    - Validate-config job for YAML/TOML files (PASSING)
    - Summary job for overall status reporting (PASSING)
  - No continue-on-error flags - all checks must pass
  - Automatic formatting of setuptools_scm generated files
  - Coverage requirement enforced at 70% minimum (currently 72.77%)

- **Enhanced External Drive Detection**
  - Added WMI (Windows Management Instrumentation) integration for accurate drive detection
  - Now detects USB flash drives, external HDDs/SSDs, and other removable media
  - Multi-layered detection approach:
    - Windows `GetDriveTypeW` API for standard removable drives
    - WMI queries to identify drives with USB interface or "external" media type
    - Detects external drives even when Windows classifies them as "fixed" (NTFS external drives)
  - Graceful fallback to legacy detection methods if WMI is unavailable
  - Supports all external drive types: USB flash drives, external SSDs, portable HDDs
  - Added `WMI>=1.5.1` as Windows-only dependency in `pyproject.toml`

- **Test Environment Isolation**
  - Implemented automatic test isolation to prevent system drive pollution
  - Added global `mock_drive_root` fixture to redirect all file operations to temporary directories
  - Tests no longer create `pyMM.Logs` or `pyMM.Projects` folders on C:\ or other system drives
  - All 193 tests now run in completely isolated temporary environments
  - Automatic cleanup of test artifacts after test completion

- **Automatic Version Management**
  - Implemented `setuptools_scm` for Git-based semantic versioning
  - Runtime version detection with fallback to `importlib.metadata`
  - Version and commit hash displayed in Settings → About tab
  - Support for alpha, beta, and rc prerelease tags

- **Modernized CI/CD Pipeline**
  - Branch-based release flow: `dev` → Beta releases, `main` → Stable releases
  - Automated `latest-beta` rolling tag on `dev` branch pushes
  - Automatic cleanup of old assets from `latest-beta` before uploading new builds
  - Python embeddable runtime caching to speed up builds
  - Added `contents: read` permissions for better security
  - Support for Python 3.14 in CI workflows (forward compatibility)
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
  - Automatic cleanup of old assets from `latest-beta` before uploading new builds
  - Python embeddable runtime caching to speed up builds
  - Added `contents: read` permissions for better security
  - Support for Python 3.14 in CI workflows (forward compatibility)

### Changed

- **Decoupled Git Integration from Project Management**
  - Git integration removed from project management system for cleaner architecture
  - GitService remains available as standalone service for plugin use
  - Projects no longer have `git_enabled` field or `is_git_repo` property
  - Removed automatic git repository initialization from project creation
  - Removed git-related methods from ProjectService (init_git_repository, get_git_status, commit_changes, get_git_log)
  - Updated project wizard to remove git checkbox
  - Simplified project browser and views by removing git-specific UI elements
  - Total: 338 lines of coupling code removed across 18 files

- **Code Quality Improvements**
  - **100% MyPy Compliance**: All type checking errors resolved with proper type hints and ignores
  - **Zero Linting Errors**: All Ruff checks passing with consistent code style
  - **Strict Markdown Linting**: All documentation now passes markdownlint with MD033 and MD041 rules enabled
  - Configured MyPy properly with appropriate ignores for PySide6 Qt attributes
  - Fixed all import statement formatting issues
  - Auto-formatted entire codebase with Ruff
  - Removed all unused `type: ignore` comments
  - Test coverage maintained at 72.77% (exceeds 70% requirement)
  - All 193 tests passing in CI/CD pipeline

- **Development Workflow Enhancement**
  - Updated CONTRIBUTING.md with comprehensive pre-commit workflow documentation
  - Updated README.md with development setup instructions and accurate statistics
  - All Git hooks now use PowerShell for Windows compatibility
  - Removed bash dependency for Git hooks (was causing issues on Windows)
  - Users can now use external git tools and workflows independently
  - Updated documentation to reflect new architecture and recommend external git clients
- Expanded test suite from 137 to 193 tests with improved coverage
- Updated `pyproject.toml` to support semantic versioning with prerelease suffixes
- Improved documentation structure and clarity with accurate test counts and statistics
- Enhanced test coverage for settings dialog (5 tabs expected)
- Modernized all documentation to reflect current architecture and features
- Refactored release workflow to clean old assets before updating `latest-beta`
- Updated all .md files with latest codebase information and accurate metrics

### Fixed

- **QFluentWidgets Navigation Error**: Fixed "object name can't be empty string" error by adding
  `setObjectName()` calls to all navigation interfaces and views
  - Home interface
  - Settings interface
  - Storage view
  - Plugin view
  - Project view
- **MyPy Type Checking**: Resolved all type checking errors across the codebase
  - Added appropriate `type: ignore[attr-defined]` for Qt dynamic attributes
  - Fixed return type hints for all methods
  - Proper typing for PySide6 enums and Qt constants
- **Strict Markdown Linting**: Fixed all MD033 (inline HTML) and MD041 (first line heading) violations
- Import sorting issues in `app/__init__.py` (resolved via Ruff)
- Version inconsistencies between README and codebase
- Text formatting in first-run wizard welcome message
- Async mock warnings in plugin download tests
- Path comparison issues in file system service tests
- Ruff ignore rules for auto-generated `_version.py` file
- All pre-commit hooks now passing without errors

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
