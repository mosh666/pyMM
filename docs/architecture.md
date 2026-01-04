# pyMediaManager Architecture Documentation

## Overview

pyMediaManager is a portable, Python-based media management application designed to run entirely from removable drives without system installation. The application follows a modular architecture with clear separation of concerns.

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

## Directory Structure

```
D:\pyMM\                          # Application root
│
├── python312\                    # Embedded Python runtime
│   ├── python.exe
│   ├── python312.dll
│   └── ...
│
├── lib-py312\                    # Python dependencies (version-specific)
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

### 1. FileSystemService
**Purpose**: Abstraction layer for file operations with portable path handling

**Key Features**:
- Resolves relative paths to application root
- Ensures directories exist before operations
- Provides cross-platform path operations
- Tracks free disk space

**Usage**:
```python
from app.core.services.file_system_service import FileSystemService

fs = FileSystemService()
project_dir = fs.ensure_directory("../pyMM.Projects/new-project")
files = fs.list_directory(project_dir, pattern="*.jpg", recursive=True)
```

### 2. StorageService
**Purpose**: Detect and manage portable drives

**Key Features**:
- Enumerate all drives (fixed and removable)
- Track drive serial numbers for identification
- Get drive capacity and free space
- Detect if path is on removable drive

**Usage**:
```python
from app.core.services.storage_service import StorageService

storage = StorageService()
removable_drives = storage.get_removable_drives()
drive_info = storage.get_drive_info(Path("D:\\"))
```

### 3. ConfigService
**Purpose**: Layered configuration management with Pydantic validation

**Configuration Layers** (in order of precedence):
1. **Defaults**: Built-in defaults in Pydantic models
2. **Default File**: `config/app.yaml` (version controlled)
3. **User File**: `config/user.yaml` (gitignored)
4. **Environment**: Environment variable overrides (future)

**Features**:
- Type-safe configuration with Pydantic
- Automatic validation
- Sensitive data redaction
- Export with/without secrets

**Usage**:
```python
from app.core.services.config_service import ConfigService

config_service = ConfigService(app_root)
config = config_service.load()

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
from app.core.logging_service import LoggingService

logging_service = LoggingService(
    app_name="pyMediaManager",
    log_dir=Path("D:\\pyMM.Logs"),
    level="INFO"
)
logger = logging_service.setup()
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

### 5. PluginManager
**Purpose**: Discover, install, and manage plugins

**Plugin Lifecycle**:
1. **Discovery**: Scan `plugins/` for `plugin.yaml` manifests
2. **Installation**: Download → Extract → Validate
3. **Registration**: Add to process PATH if configured
4. **Usage**: Execute plugin commands
5. **Uninstallation**: Remove plugin directory

**Plugin Manifest Structure**:
```yaml
name: FFmpeg
version: "7.1.0"
mandatory: false
enabled: true

source:
  type: url
  base_uri: https://example.com/ffmpeg.zip

command:
  path: bin
  executable: ffmpeg.exe

register_to_path: true
dependencies: []
```

**Usage**:
```python
from app.plugins.plugin_manager import PluginManager

plugin_manager = PluginManager(
    plugins_dir=Path("D:\\pyMM.Plugins"),
    manifests_dir=Path("D:\\pyMM\\plugins")
)

# Discover available plugins
count = plugin_manager.discover_plugins()

# Install plugin
await plugin_manager.install_plugin("FFmpeg")

# Get PATH entries for enabled plugins
paths = plugin_manager.register_plugins_to_path()
os.environ['PATH'] = os.pathsep.join([str(p) for p in paths]) + os.pathsep + os.environ['PATH']
```

## UI Architecture

### Fluent Design System
pyMediaManager uses **PyQt-Fluent-Widgets** for modern, consistent UI:

- **NavigationInterface**: Side navigation with collapsible menu
- **FluentWindow**: Main window with fluent styling
- **Theme Support**: Light, dark, and auto (system) themes
- **Acrylic Effects**: Transparency and blur effects

### View Pattern
Each major feature has a dedicated view:

- **StorageView**: Manage drives
- **PluginView**: Install/update plugins
- **ProjectView**: Create/manage projects
- **Settings**: Configure application

### First-Run Wizard
**Purpose**: Guide new users through initial setup

**Pages**:
1. **Welcome**: Introduction and features
2. **Storage**: Select portable drive for projects/logs
3. **Plugins**: Choose optional plugins to install
4. **Complete**: Summary and "don't show again" option

**Integration**:
```python
# Check if first run
if config.ui.show_first_run:
    wizard = FirstRunWizard(storage_service, optional_plugins)
    wizard.finished.connect(on_setup_complete)
    wizard.show()
```

## Portable Path Management

### Path Resolution Strategy

1. **Application Root**: Detected from `launcher.py` location
2. **Drive Root**: Parent directory of application root
3. **Projects**: `drive_root / "pyMM.Projects"`
4. **Logs**: `drive_root / "pyMM.Logs"`
5. **Plugins**: `drive_root / "pyMM.Plugins"`

### Example Path Resolution

```
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

Python 3.12 and 3.13 supported with separate builds:
- `pyMM-v0.0.1-py312-win64.zip` (Python 3.12)
- `pyMM-v0.0.1-py313-win64.zip` (Python 3.13, recommended)

## Testing Strategy

### Unit Tests (pytest)
**Coverage Target**: 70%+

**Test Structure**:
```
tests/
├── unit/
│   ├── test_file_system_service.py
│   ├── test_storage_service.py
│   ├── test_config_service.py
│   └── test_plugin_manager.py
└── gui/
    ├── test_first_run_wizard.py
    └── test_views.py
```

### GUI Tests (pytest-qt)
**Tools**: pytest-qt, QTest

**Key Patterns**:
```python
def test_button_click(qtbot):
    widget = MyWidget()
    qtbot.addWidget(widget)
    
    # Click button
    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)
    
    # Wait for signal
    with qtbot.waitSignal(widget.finished, timeout=1000):
        pass
```

### CI/CD Pipeline

**GitHub Actions Workflows**:
1. **ci.yml**: Lint, test, coverage (Python 3.12 + 3.13 matrix)
2. **build.yml**: Build portable packages per Python version
3. **release.yml**: Create GitHub releases on version tag

## Security Considerations

### Sensitive Data Handling
- Config redaction: `password`, `token`, `api_key`, `secret` auto-redacted
- Logs: Sensitive values never logged
- Export: `redact_sensitive=True` option for config export

### Plugin Security
- **Source Verification**: Download URLs in manifests
- **Checksum Validation**: Future enhancement
- **Sandboxing**: Plugins run in same process (trust model)

### Future Enhancements
- Digital signatures for plugins
- SHA-256 checksums in manifests
- Plugin permission system

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
from app.plugins.plugin_base import PluginBase

class CustomPlugin(PluginBase):
    async def download(self, progress_callback=None):
        # Custom download logic
        pass
    
    def validate_installation(self):
        # Custom validation
        pass
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

### v0.1.0
- Complete project management implementation
- Git integration for version control
- digiKam integration for media management

### v0.2.0
- Cross-platform support (Linux, macOS)
- Plugin auto-updates
- Enhanced settings UI

### v0.3.0
- Plugin marketplace
- Cloud sync support
- Advanced project templates

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.
