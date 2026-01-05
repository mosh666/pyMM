# pyMediaManager Architecture Documentation

> **Version:** Auto-detected from Git using setuptools_scm (semantic versioning with prerelease support)
> **Last Updated:** January 5, 2026
> **Python Support:** 3.12 | 3.13 | 3.14 (embedded Python 3.13 runtime included for portability)
> **Test Suite:** 193 tests with 73% code coverage (all passing, automatic test isolation)
> **Quality Gates:** 15+ pre-commit hooks (Ruff linting/formatting, MyPy type checking, Bandit security)
> **CI/CD:** GitHub Actions with matrix testing (Python 3.12, 3.13, 3.14), CodeQL, OpenSSF Scorecard (daily)
> **Build Pipeline:** Branch-based releases (dev → beta, main → stable) with automated asset management
> **Security:** Daily OpenSSF Scorecard, CodeQL analysis, Dependabot updates, Bandit scanning
> **See also:** [CHANGELOG.md](../CHANGELOG.md) for detailed version history

## Overview

pyMediaManager is a portable, Python-based media management application designed to run
entirely from removable drives without system installation. The application follows a
modular architecture with clear separation of concerns.

## Design Principles

### 1. Portability First

- **No System Installation**: All files contained within application directory
- **No PATH Pollution**: Environment variables modified only for current process
- **No Registry Modifications**: All settings stored in portable config files
- **Drive-Agnostic**: Automatically detects current drive location
- **Relative Paths**: All internal references use paths relative to app root

### 2. Service-Oriented Architecture

- **Dependency Injection**: Services injected where needed
- **Single Responsibility**: Each service handles one aspect
- **Testability**: All services have comprehensive unit tests
- **Loose Coupling**: Services communicate through interfaces

### 3. Plugin-Based Extensibility

- **Manifest-Driven**: Plugins described in YAML manifests
- **Lazy Loading**: Plugins loaded on demand
- **Isolated Installation**: Each plugin in separate directory
- **Version Management**: Plugins track their own versions

### 4. Code Quality Standards

- **Structured Logging**: All modules use proper logger instances instead of print statements
- **Type Safety**: Comprehensive return type hints on all functions and methods
- **Modern Type Hints**: Use Python 3.12+ native generic types (`list`, `dict`, `tuple`) instead
  of importing from `typing` module
- **Documentation**: Docstrings for all public APIs following Google style
- **Testing**: 70%+ code coverage requirement with unit and integration tests
- **Code Formatting**: Consistent style enforced by Ruff formatter
- **Static Analysis**: MyPy type checking for catching errors early
- **Linting**: Ruff linter with auto-fix for code quality

### 5. Version Management

- **Automatic Detection**: Version derived from Git tags using `setuptools_scm`
- **Semantic Versioning**: Supports alpha, beta, rc prerelease tags (e.g., v1.0.0-beta.1)
- **Runtime Access**: Version and commit hash available at runtime via `app.__version__` and `app.__commit_id__`
- **Fallback**: Graceful fallback to `importlib.metadata` or dev version if Git is missing
- **UI Integration**: Version details displayed in Settings → About tab
- **Branch Strategy**: `dev` branch for beta releases, `main` branch for stable releases
- **Rolling Tags**: `latest-beta` tag automatically updated on `dev` branch pushes with asset cleanup

### 6. UI Framework Stability

- **QFluentWidgets Integration**: All navigation interfaces and views properly initialized
- **Object Names**: All views set `setObjectName()` to prevent "object name can't be empty string" errors
- **Fixed Interfaces**: Home, Settings, Storage, Plugin, and Project views properly configured

## Directory Structure

```text
D:\pyMM\                          # Application root
│
├── python313\                    # Embedded Python runtime (3.13 default)
│   ├── python.exe
│   ├── python313.dll
│   └── ...
│
├── lib-py313\                    # Python dependencies (version-specific)
│   ├── PySide6\
│   ├── pydantic\
│   └── ...
│
├── app\                          # Application code
│   ├── __init__.py
│   ├── main.py                   # Entry point
│   │
│   ├── core\                     # Core services
│   │   ├── services\
│   │   │   ├── file_system_service.py
│   │   │   ├── storage_service.py
│   │   │   ├── config_service.py
│   │   │   └── plugin_service.py
│   │   └── logging_service.py
│   │
│   ├── ui\                       # User interface
│   │   ├── main_window.py
│   │   ├── views\
│   │   │   ├── storage_view.py
│   │   │   ├── plugin_view.py
│   │   │   └── project_view.py
│   │   └── components\
│   │       └── first_run_wizard.py
│   │
│   ├── plugins\                  # Plugin system
│   │   ├── plugin_base.py
│   │   └── plugin_manager.py
│   │
│   └── projects\                 # Project management
│       └── project_manager.py
│
├── plugins\                      # Plugin manifests
│   ├── digikam\
│   │   └── plugin.yaml
│   ├── ffmpeg\
│   │   └── plugin.yaml
│   └── ...
│
├── config\                       # Configuration
│   ├── app.yaml                  # Default config
│   └── user.yaml                 # User overrides (gitignored)
│
├── tests\                        # Test suite
│   ├── unit\
│   └── gui\
│
├── launcher.py                   # Application launcher
├── pyproject.toml                # Project metadata
└── README.md

D:\pyMM.Plugins\                  # Installed plugin binaries
├── digikam\
├── ffmpeg\
├── git\
└── ...

D:\pyMM.Projects\                 # User projects (drive root)
└── my-media-project\

D:\pyMM.Logs\                     # Application logs (drive root)
└── pymediamanager.log
```

## Core Components

### Service Architecture

pyMediaManager uses a service-oriented architecture with dependency injection:

- **ConfigService**: YAML-based configuration with Pydantic validation and sensitive data redaction
- **FileSystemService**: Portable path resolution and file operations
- **StorageService**: Drive detection, management, and removable drive identification
- **LoggingService**: Rich console and rotating file logs with structured logging
- **ProjectService**: Project lifecycle management and metadata
- **GitService**: Git repository operations using GitPython library
- **PluginManager**: Plugin discovery, installation, and lifecycle management

### 1. FileSystemService

**Purpose**: Abstraction layer for file operations with portable path handling

**Key Features**:

- Resolves relative paths to application root
- Ensures directories exist before operations
- Provides cross-platform path operations
- Tracks free disk space

**Usage**:

```python
from pathlib import Path
from app.core.services.file_system_service import FileSystemService

fs = FileSystemService()
project_dir: Path = fs.ensure_directory("../pyMM.Projects/new-project")
files: list[Path] = fs.list_directory(project_dir, pattern="*.jpg", recursive=True)
```

### 2. StorageService

**Purpose**: Detect and manage portable drives with enhanced external drive detection

**Key Features**:

- Enumerate all drives (fixed and removable)
- **Advanced external drive detection** using multiple methods:
  - Windows `GetDriveTypeW` API for true removable drives (USB flash drives, SD cards)
  - WMI (Windows Management Instrumentation) for detecting external USB/Thunderbolt drives
  - Identifies drives marked as "External hard disk media" by Windows
  - Detects drives even when Windows classifies them as "fixed" type
- Track drive serial numbers for identification
- Get drive capacity and free space
- Detect if path is on removable drive
- Graceful fallback when WMI is unavailable

**Detection Heuristics**:

1. Check Windows drive type (DRIVE_REMOVABLE)
2. Query WMI for USB interface or external media type indicators
3. Check partition options for "removable" flag
4. Identify common removable filesystems (FAT32, exFAT) on non-system drives
5. Exclude network drives, CD-ROMs, and RAM disks

**Usage**:

```python
from pathlib import Path
from app.core.services.storage_service import StorageService, DriveInfo

storage = StorageService()

# Get all removable/external drives (USB flash drives, external HDDs/SSDs)
removable_drives: list[DriveInfo] = storage.get_removable_drives()

# Get specific drive info
drive_info: DriveInfo | None = storage.get_drive_info(Path("D:\\"))

# Check if path is on removable/external drive
is_portable: bool = storage.is_path_on_removable_drive("D:\\pyMM")
```

**DriveInfo Fields**:

- `drive_letter`: Drive path (e.g., "K:\\")
- `label`: Volume label
- `file_system`: Filesystem type (NTFS, FAT32, exFAT)
- `total_size`: Total capacity in bytes
- `free_space`: Available space in bytes
- `is_removable`: True if external/removable drive
- `serial_number`: Volume serial number (hex string)

```text

### 3. ConfigService

**Purpose**: Layered configuration management with Pydantic validation and security

**Configuration Layers** (in order of precedence):

1. **Defaults**: Built-in defaults in Pydantic models
2. **Default File**: `config/app.yaml` (version controlled, read-only)
3. **User File**: `config/user.yaml` (gitignored, user customizations)
4. **Environment**: Environment variable overrides (future enhancement)

**Security Features**:

- **Automatic Redaction**: Sensitive fields (password, token, api_key, secret) automatically redacted in logs and exports
- **Type Validation**: Pydantic ensures all config values match expected types
- **Schema Evolution**: Forward-compatible configuration loading
- **Export Control**: `redact_sensitive=True` option for safe config sharing

**Configuration Structure**:

```yaml
app:
  name: pyMediaManager
  version: auto  # Managed by setuptools_scm

ui:
  theme: auto  # light, dark, or auto
  show_first_run: true
  language: en

logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  console: true
  file: true
  max_bytes: 10485760  # 10MB
  backup_count: 5

plugins:
  auto_install_mandatory: true
  download_timeout: 300
  retry_attempts: 3
  verify_checksums: true

storage:
  default_drive: null
  project_root: pyMM.Projects
  plugin_dir: pyMM.Plugins
  log_dir: pyMM.Logs

git:
  user_name: ""
  user_email: ""
  auto_initialize: false
  default_branch: main
```

**Usage**:

```python
from pathlib import Path
from app.core.services.config_service import ConfigService, AppConfig

config_service = ConfigService(app_root)
config: AppConfig = config_service.load()

# Update specific setting
config_service.update_config(ui={"theme": "dark"})

# Export without secrets
config_service.export_config(Path("config_export.yaml"), redact_sensitive=True)
```

### 4. LoggingService

**Purpose**: Rich console and rotating file logs

**Features**:

- Rich-formatted console output with colors
- Rotating file logs (10MB, 5 backups)
- Configurable log levels
- Separate loggers for modules

**Usage**:

```python
from pathlib import Path
from logging import Logger
from app.core.logging_service import LoggingService

logging_service = LoggingService(
    app_name="pyMediaManager",
    log_dir=Path("D:\\pyMM.Logs"),
    level="INFO"
)
logger: Logger = logging_service.setup()
logger.info("Application started")
```

**Code Quality Improvements**:

- **Migration from print()**: All print statements replaced with structured logging calls
  - Debug information: `logger.debug()`
  - General progress: `logger.info()`
  - User warnings: `logger.warning()`
  - Error conditions: `logger.error()`
- **Benefits**: Better debugging, production monitoring, log filtering by level, centralized output control
- **Consistency**: All 15+ modules now use logger instances from `logging.getLogger(__name__)`

### 5. ProjectService

**Purpose**: Manage project lifecycle and metadata

**Features**:

- Project creation with templates
- Metadata tracking (created date, last modified, Git status)
- Project validation and integrity checks
- Recent projects list management
- Project browser integration

**Usage**:

```python
from pathlib import Path
from app.services.project_service import ProjectService, Project

project_service = ProjectService(file_system_service, config_service)

# Create new project
project: Project = await project_service.create_project(
    name="vacation-2026",
    location=Path("D:\\pyMM.Projects"),
    initialize_git=False  # Git is now optional
)

# List all projects
projects: list[Project] = project_service.list_projects()

# Get project metadata
project_info: dict[str, Any] = project_service.get_project_info(project_path)
```

### 6. GitService

**Purpose**: Git repository operations using GitPython

**Features**:

- Initialize repositories with custom branch names
- Commit changes with author information
- Check repository status (modified, staged, untracked files)
- View commit history with pagination
- Branch management
- Remote repository operations (future)

**Usage**:

```python
from pathlib import Path
from app.services.git_service import GitService, CommitInfo

git_service = GitService()

# Initialize repository
repo_path = Path("D:\\pyMM.Projects\\my-project")
git_service.init_repository(
    repo_path,
    initial_branch="main",
    user_name="John Doe",
    user_email="john@example.com"
)

# Check status
status: dict[str, list[str]] = git_service.get_status(repo_path)
print(f"Modified: {status['modified']}")
print(f"Untracked: {status['untracked']}")

# Commit changes
git_service.commit(
    repo_path,
    message="Add new photos from beach shoot",
    author_name="John Doe",
    author_email="john@example.com"
)

# View history
commits: list[CommitInfo] = git_service.get_log(repo_path, max_count=10)
```

### 7. PluginManager

**Purpose**: Discover, install, and manage plugins

**Plugin Lifecycle**:

1. **Discovery**: Scan `plugins/` for `plugin.yaml` manifests
2. **Installation**: Download → Extract → Validate
3. **Registration**: Add to process PATH if configured
4. **Usage**: Execute plugin commands
5. **Uninstallation**: Remove plugin directory

**Plugin Security**:

- **Download Verification**: SHA256 checksum validation (when enabled in config)
- **Retry Logic**: Automatic retry on network failures (up to 3 attempts with exponential backoff)
- **Timeout Protection**: Configurable download timeout (default 300 seconds)
- **Progress Tracking**: Real-time download progress callbacks for UI integration
- **Source Validation**: Downloads only from URLs specified in manifests
- **Integrity Checks**: Validates plugin structure after extraction

```yaml
name: FFmpeg
version: "7.1.0"
mandatory: false  # Required for core functionality
enabled: true     # Auto-enable after installation

source:
  type: url
  base_uri: https://example.com/ffmpeg.zip
  checksum: sha256:abc123...  # Optional SHA256 for verification

command:
  path: bin       # Relative path to executable directory
  executable: ffmpeg.exe

register_to_path: true  # Add to process PATH
dependencies: []        # Other plugins required

metadata:
  description: "Video and audio processing"
  homepage: "https://ffmpeg.org"
  license: "GPL-3.0"
  platform: windows
  architecture: x64
```

**Usage**:

```python
import os
from pathlib import Path
from app.plugins.plugin_manager import PluginManager

plugin_manager = PluginManager(
    plugins_dir=Path("D:\\pyMM.Plugins"),
    manifests_dir=Path("D:\\pyMM\\plugins")
)

# Discover available plugins
count: int = plugin_manager.discover_plugins()

# Install plugin
await plugin_manager.install_plugin("FFmpeg")

# Get PATH entries for enabled plugins
paths: list[Path] = plugin_manager.register_plugins_to_path()
os.environ['PATH'] = os.pathsep.join([str(p) for p in paths]) + os.pathsep + os.environ['PATH']
```

## UI Architecture

### Fluent Design System

pyMediaManager uses **PyQt-Fluent-Widgets** for modern, consistent UI:

- **FluentWindow**: Main window with fluent styling and acrylic effects
- **NavigationInterface**: Side navigation with collapsible menu and smooth transitions
- **Theme Support**: Light, dark, and auto (follows system theme)
- **Acrylic Effects**: Transparency and blur effects for modern appearance
- **Responsive Layout**: Adapts to different window sizes

### UI Components

#### Main Window (MainWindow)

**Navigation Structure**:

- **Top Navigation**:
  - Home: Dashboard and quick actions
  - Storage View: Drive management and status
  - Plugin View: Plugin installation and updates
  - Project View: Project browser and management

- **Bottom Navigation**:
  - Settings: Application configuration (5 tabs)

**All views properly initialized** with:

- `setObjectName()` set to prevent Qt warnings
- Proper parent-child relationships
- Signal/slot connections for inter-component communication

#### Storage View

**Features**:

- Display all available drives (fixed, removable, external)
- Enhanced external drive detection using WMI
- Show drive capacity, free space, and file system
- Identify removable/external drives with indicators
- Select default drive for portable operation

#### Plugin View

**Features**:

- Grid layout showing all available plugins
- Status indicators (installed, available, error)
- Install/uninstall buttons with progress tracking
- Plugin details (version, size, description)
- Automatic detection of plugin availability
- Batch operations (install multiple plugins)

#### Project View

**Features**:

- Recent projects list
- Project browser with search and filtering
- Quick actions (New Project, Open, Delete)
- Project metadata display (Git status, size, dates)
- Integration with ProjectWizard for creation

### Dialog Components

#### FirstRunWizard

**Purpose**: Guide new users through initial setup

**Pages**:

1. **Welcome Page**: Introduction and feature overview
2. **Storage Page**: Select portable drive for projects/logs with enhanced drive detection
3. **Plugin Page**: Choose optional plugins to install (mandatory plugins installed automatically)
4. **Complete Page**: Summary and "don't show again" option

**Features**:

- Comprehensive validation at each step
- Progress tracking (page 1 of 4)
- Skip option after first completion
- Persistent settings in user.yaml

#### ProjectWizard

**Purpose**: Create new projects with templates

**Fields**:

- Project name (validated, no special characters)
- Location selection with browse button
- Optional Git initialization (now optional, not automatic)
- Template selection (None, Basic, Photography, Video)
- Description and metadata

#### ProjectBrowser

**Purpose**: Browse and manage all projects

**Features**:

- Search by name or location
- Filter by Git status, date range
- Sort by name, date, size
- Context menu (Open, Delete, Show in Explorer)
- Keyboard navigation and shortcuts

#### SettingsDialog

**Purpose**: Configure all application settings

**Tabs** (5 total):

1. **General**: Theme, language, logging level, application name
2. **Plugins**: Auto-install, timeout, retry, checksum verification, paths
3. **Storage**: Default drive, project root, log location, max log size
4. **Git**: User name/email, auto-initialize, default branch, executable path
5. **About**: Version info (auto-detected from Git), Python version, dependencies, test coverage

**Features**:

- Real-time validation
- Apply/OK/Cancel buttons
- Tabbed interface for organization
- Help tooltips on hover
- Version information with setuptools_scm integration

## Portable Path Management

### Path Resolution Strategy

1. **Application Root**: Detected from `launcher.py` location
2. **Drive Root**: Parent directory of application root
3. **Projects**: `drive_root / "pyMM.Projects"`
4. **Logs**: `drive_root / "pyMM.Logs"`
5. **Plugins**: `drive_root / "pyMM.Plugins"`

### Example Path Resolution

```plaintext
Scenario: App installed on D:\pyMM

Application Root:  D:\pyMM
Drive Root:        D:\
Projects:          D:\pyMM.Projects\
Logs:              D:\pyMM.Logs\
Plugins:           D:\pyMM.Plugins\
Config:            D:\pyMM\config\
```

### Why This Structure?

- **Projects at drive root**: Easier to find and access
- **Logs at drive root**: Persistent across app updates
- **Plugins at drive root**: Shared across app versions
- **Config in app dir**: Portable with application

## Dependency Management

### Embedded Python Approach

**Benefits**:

- No system Python required
- Version consistency
- Isolated dependencies
- True portability

**Trade-offs**:

- Larger download size (~200MB with deps)
- Manual updates required
- Platform-specific builds

### Build Process

1. Download embeddable Python package
2. Configure `._pth` file for custom lib directory
3. Install pip
4. Install dependencies to `lib-py{version}/`
5. Freeze dependencies for reproducibility
6. Package as ZIP archive

### Version Matrix

Python 3.12 and 3.13 explicitly supported with separate builds:

- `pyMM-v0.1.0-py313-win64.zip` (Python 3.13, **recommended**)
- `pyMM-v0.1.0-py312-win64.zip` (Python 3.12)

**Note:** Python 3.14 support tested in CI workflows for forward compatibility.

## Testing Strategy

### Comprehensive Test Suite

**Current Stats**: 193 tests with 73% code coverage
**Coverage Target**: 70% minimum (enforced in CI)

**Test Structure**:

```plaintext
tests/
├── unit/                         # Core service unit tests
│   ├── test_file_system_service.py
│   ├── test_storage_service.py
│   ├── test_config_service.py
│   ├── test_logging_service.py
│   ├── test_plugin_manager.py
│   ├── test_plugin_base.py
│   ├── test_project.py
│   ├── test_git_service.py
│   └── test_storage_service.py
├── gui/                          # UI component tests
│   ├── test_first_run_wizard.py
│   ├── test_project_dialogs.py
│   └── test_views.py
├── integration/                  # Integration tests
│   ├── test_plugin_workflow.py
│   └── test_project_workflow.py
├── test_git_integration.py       # Git integration tests
├── test_plugin_download.py       # Plugin download tests
├── test_project_management.py    # Project management tests
└── test_settings_dialog.py       # Settings dialog tests
```

### GUI Tests (pytest-qt)

**Tools**: pytest-qt, QTest

**Key Patterns**:

```python
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt

def test_button_click(qtbot: QtBot) -> None:
    widget: MyWidget = MyWidget()
    qtbot.addWidget(widget)

    # Click button
    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

    # Wait for signal
    with qtbot.waitSignal(widget.finished, timeout=1000):
        pass
```

### CI/CD Pipeline

**GitHub Actions Workflows**:

1. **ci.yml** - Continuous Integration
   - **Matrix Testing**: Python 3.12, 3.13, 3.14 for forward compatibility
   - **Code Quality**:
     - Ruff linting with auto-fix suggestions
     - Ruff formatting checks
     - MyPy static type checking
     - Bandit security scanning
   - **Test Execution**: Full test suite (193 tests) with pytest
   - **Coverage Reports**:
     - 70% minimum enforced (fails build if below)
     - HTML reports uploaded as artifacts
     - Codecov integration for tracking
   - **Triggers**: Push to all branches, all pull requests
   - **Runtime**: ~5-8 minutes per Python version

2. **build.yml** - Build Automation
   - **Python Embeddable Caching**: Speeds up builds by caching downloaded runtimes
   - **Multi-Version Builds**:
     - Separate ZIP packages for Python 3.12, 3.13, 3.14
     - Each includes embedded runtime + dependencies
   - **Pre-Build Testing**: Full test suite runs before building
   - **Artifact Upload**: ZIP packages available for download in workflow artifacts
   - **Naming Convention**: `pyMM-vX.Y.Z-py3XX-win64.zip`
   - **Triggers**: Manual workflow dispatch
   - **Runtime**: ~15-20 minutes for all versions

3. **release.yml** - Release Management
   - **Branch-Based Releases**:
     - `dev` branch → Beta releases (prerelease flag set)
     - `main` branch → Stable releases
     - Git tags (`v*.*.*` pattern) → Version-specific releases
   - **Automatic Tagging**:
     - `latest-beta` rolling tag on `dev` branch pushes
     - Automatically updated with each dev push
     - Old assets cleaned before new upload
   - **Asset Management**:
     - Builds for Python 3.12, 3.13, 3.14
     - SHA256 checksums for all artifacts
     - Automatic cleanup of old assets from rolling tags
   - **GitHub Releases**:
     - Created with changelog extraction
     - Download links for all Python versions
     - Source code archives (zip, tar.gz)
   - **Version Detection**: setuptools_scm for automatic versioning
   - **Security**:
     - Read-only permissions by default
     - Minimal scope for write operations
     - No secrets exposed in logs
   - **Triggers**:
     - Git tags matching `v*.*.*`
     - Pushes to `dev` branch (beta releases)
   - **Runtime**: ~25-30 minutes for full release

4. **security.yml** - Security Scanning (CodeQL)
   - **Scheduled**: Weekly on Mondays at 00:00 UTC
   - **On-Demand**: Pull requests affecting code
   - **Analysis**:
     - CodeQL for Python security issues
     - SQL injection detection
     - Command injection detection
     - Path traversal vulnerabilities
     - Insecure cryptography usage
   - **Integration**: Results appear in GitHub Security tab
   - **Runtime**: ~5-10 minutes

5. **scorecard.yml** - OpenSSF Scorecard
   - **Scheduled**: Daily at 08:00 UTC
   - **On-Demand**: Pushes to `main` branch
   - **Checks**:
     - Branch protection enforcement
     - Code review requirements
     - CI test coverage
     - Dependency update practices
     - Security policy presence
     - SAST tool usage
     - Signed releases
     - Token permissions
   - **Publishing**:
     - Results published to OpenSSF database
     - Badge available for README
     - Trends tracked over time
   - **Runtime**: ~3-5 minutes

**Dependabot Configuration**:

- **pip Dependencies**: Daily checks
- **GitHub Actions**: Daily checks
- **Grouped Updates**: Related updates batched together
- **Auto-Merge**: Not enabled (manual review required)
- **Security Updates**: Immediate notification

**Workflow Best Practices**:

- All workflows use minimal permissions
- Caching for Python dependencies and embeddable runtimes
- Fail-fast strategy for quick feedback
- Comprehensive logging for debugging
- Artifact retention: 90 days

## Security Considerations

### Sensitive Data Handling

**Configuration Security**:

- **Automatic Redaction**: Fields named `password`, `token`, `api_key`, `secret` automatically redacted
- **Export Control**: `redact_sensitive=True` option for safe config sharing
- **No Logging**: Sensitive values never appear in log files
- **Validation**: Pydantic ensures type safety prevents injection attacks

**Example Redaction**:

```yaml
# Original config
database:
  host: localhost
  password: super_secret_123

# Exported with redaction
database:
  host: localhost
  password: "***REDACTED***"
```

### Plugin Security

**Download Security**:

- **SHA256 Checksums**: Optional checksum verification in manifests (planned)
- **HTTPS Only**: Plugin downloads require HTTPS URLs
- **Retry Logic**: Automatic retry with exponential backoff (3 attempts)
- **Timeout Protection**: Configurable download timeout (default 300s)
- **Progress Tracking**: Real-time monitoring for hung downloads

**Current Security Model**:

- Plugins run in same process (trusted plugin model)
- Plugins have full file system access
- Manual review of plugin manifests before merging
- Community-maintained plugin repository

### Security Scanning

**Pre-commit Hooks**:

- **Bandit**: Python security linter scans for:
  - Hardcoded passwords and secrets
  - SQL injection vulnerabilities
  - Use of insecure functions (eval, exec)
  - Weak cryptography
  - Path traversal vulnerabilities
  - Shell injection risks

**Continuous Integration**:

- **CodeQL**: Daily automated security scanning
  - Detects complex security vulnerabilities
  - Tracks security advisories
  - Integration with GitHub Security tab

- **OpenSSF Scorecard**: Weekly security posture assessment
  - Branch protection enforcement
  - Code review requirements
  - Dependency update practices
  - SAST (Static Application Security Testing)
  - Vulnerability disclosure
  - Published to OpenSSF database

- **Dependabot**: Automated dependency updates
  - Daily checks for vulnerabilities
  - Automatic PR creation for updates
  - Grouped updates for efficiency
  - Security advisories integration

### Future Security Enhancements

**Planned Improvements**:

1. **Plugin Signatures**: Digital signatures for plugin verification
2. **Plugin Sandboxing**: Process isolation for untrusted plugins
3. **Permission System**: Granular plugin permissions (file access, network, etc.)
4. **SBOM Generation**: Software Bill of Materials for supply chain security
5. **Reproducible Builds**: Bit-for-bit reproducible releases

## Performance Considerations

### Startup Time

- **Cold Start**: ~2-3 seconds (including Qt initialization)
- **Warm Start**: ~1-2 seconds (OS cached)

### Optimization Strategies

- Lazy plugin discovery (on-demand)
- Async plugin downloads (aiohttp)
- Cached configuration (loaded once)
- Minimal imports in launcher

### Memory Usage

- **Base**: ~80MB (PySide6 + app)
- **Per Plugin**: ~10-50MB (depending on plugin)

## Extension Points

### Adding New Plugins

1. Create `plugins/{name}/plugin.yaml` manifest
2. Test download URL
3. Verify executable path
4. Commit manifest to repository

### Adding New Views

1. Create view class in `app/ui/views/`
2. Inherit from QWidget
3. Register in `MainWindow._init_navigation()`
4. Add tests in `tests/gui/test_views.py`

### Custom Plugin Implementations

```python
from collections.abc import Callable
from app.plugins.plugin_base import PluginBase

class CustomPlugin(PluginBase):
    async def download(self, progress_callback: Callable[[int, int], None] | None = None) -> None:
        # Custom download logic
        pass

    def validate_installation(self) -> bool:
        # Custom validation
        return True
```

## Testing Architecture

### Test Isolation

The test suite implements automatic system drive protection to prevent tests from creating files
on system drives during test execution.

**Isolation Mechanism:**

- **Global Fixture**: `mock_drive_root` in `tests/conftest.py` (autouse=True)
- **Method**: Monkey-patches `FileSystemService.get_drive_root()` to return temporary directories
- **Scope**: Applies to all 193 tests automatically
- **Cleanup**: Pytest's `tmp_path` fixture handles automatic cleanup

**Benefits:**

- No `pyMM.Logs` or `pyMM.Projects` folders created on C:\ or other system drives
- Tests run in complete isolation from production environment
- Parallel test execution is safe
- No manual cleanup required

### Test Categories

1. **Unit Tests** (~95 tests): Test individual modules in isolation
   - Service layer (config, file system, storage, logging)
   - Plugin system (base, manager)
   - Git integration
   - Project models and services

2. **Integration Tests** (~10 tests): Test workflows across multiple components
   - Plugin download and installation workflows
   - Project lifecycle management
   - Git repository operations

3. **GUI Tests** (~50 tests): Test user interface components
   - First-run wizard (17 tests)
   - Project dialogs and browser (14 tests)
   - Views (storage, plugin, project views)
   - Settings dialog

4. **Manual Integration Tests** (~4 tests): Higher-level integration tests
   - Git service integration
   - Plugin download testing
   - Project management workflows
   - Settings dialog behavior

**Total Tests:** 193
**Coverage:** 73% overall with focus on critical business logic
**All tests passing** with comprehensive validation

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific category
pytest tests/unit
pytest tests/integration
pytest tests/gui
```

## Troubleshooting

### Common Issues

**Issue**: "Module not found" errors
**Solution**: Check `python*._pth` file includes lib directory

**Issue**: Plugins not appearing
**Solution**: Run `plugin_manager.discover_plugins()`

**Issue**: First-run wizard shows every time
**Solution**: Check `config/user.yaml` for `show_first_run: false`

**Issue**: Qt platform plugin error
**Solution**: Ensure `lib-py*/PySide6/plugins/` directory exists

## Future Roadmap

### v1.0.0 (Current - January 2026)

- ✅ Complete project management implementation
- ✅ Git integration for version control
- ✅ Automatic version management with setuptools_scm
- ✅ Comprehensive test suite (193 tests, 73% coverage)
- ✅ CI/CD pipeline with matrix testing (Python 3.12, 3.13, 3.14)
- ✅ Branch-based release workflow (dev → beta, main → stable)
- ✅ Rolling beta releases with latest-beta tag
- ✅ Pre-commit hooks with security scanning (Bandit, Ruff, MyPy)
- ✅ Security analysis (CodeQL, OpenSSF Scorecard, Dependabot)
- ✅ Complete documentation (User Guide, Architecture, Contributing)
- ✅ GitHub community standards (CODE_OF_CONDUCT, SECURITY, issue templates)

### v1.1.0 (Q1 2026 - Planned)

- digiKam integration for media management
- Enhanced plugin marketplace discovery
- Plugin auto-update notifications
- Plugin SHA-256 checksum verification for downloads
- Advanced project templates with custom wizards

### v1.2.0 (Q2 2026 - Planned)

- Cross-platform support (Linux, macOS)
- Enhanced settings UI with advanced configuration options
- Project export/import functionality
- Plugin dependency resolution improvements

### v2.0.0 (Future)

- Cloud sync support for projects
- Digital signatures for plugin security
- Plugin sandboxing and permissions system
- Advanced media processing workflows
- Multi-language support (i18n)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.
