# Test Suite Documentation

This directory contains the comprehensive test suite for pyMediaManager with 199 tests covering
unit, integration, and GUI components.

## Overview

**Test Statistics:**

- **Total Tests:** 199
- **Code Coverage:** 73% on core modules
- **Test Types:** Unit, Integration, GUI
- **Framework:** pytest with pytest-qt for GUI tests

## Directory Structure

```
tests/
├── unit/                       # Unit tests for individual modules
│   ├── test_config_service.py
│   ├── test_file_system_service.py
│   ├── test_git_service.py
│   ├── test_logging_service.py
│   ├── test_plugin_base.py
│   ├── test_plugin_manager.py
│   ├── test_project.py
│   └── test_storage_service.py
├── integration/                # Integration tests for workflows
│   ├── test_plugin_workflow.py
│   └── test_project_workflow.py
├── gui/                        # GUI component tests
│   ├── test_first_run_wizard.py
│   ├── test_project_dialogs.py
│   └── test_views.py
├── conftest.py                 # Shared pytest fixtures
├── test_git_integration.py     # Manual Git integration test
├── test_plugin_download.py     # Manual plugin download test
├── test_project_management.py  # Manual project management test
├── test_settings_dialog.py     # Manual settings dialog test
└── README.md                   # This file
```

---

## Test Isolation

### Automatic System Drive Protection

The test suite includes automatic isolation to prevent tests from creating files and folders on
system drives (C:\, D:\, etc.). This is achieved through a global `autouse` fixture in
[conftest.py](conftest.py) that intercepts all file system operations.

**Key Features:**

- **Automatic Mocking:** All `FileSystemService.get_drive_root()` calls are automatically redirected
  to temporary directories
- **No System Pollution:** Tests never create `pyMM.Logs`, `pyMM.Projects`, or any other folders
  on actual system drives
- **Transparent Operation:** Tests work identically but in isolated environments
- **Automatic Cleanup:** All test artifacts are cleaned up after test completion
- **Zero Configuration:** Works automatically for all tests without changes to test code

**How It Works:**

```python
# In conftest.py
@pytest.fixture(autouse=True)
def mock_drive_root(monkeypatch, tmp_path):
    """Automatically mock FileSystemService.get_drive_root() to prevent
    tests from creating folders on the system drive."""
    from app.core.services.file_system_service import FileSystemService

    mock_drive = tmp_path / "mock_drive_root"
    mock_drive.mkdir(exist_ok=True)

    def mock_get_drive_root_method(self):
        self._drive_root = mock_drive
        return mock_drive

    monkeypatch.setattr(FileSystemService, "get_drive_root", mock_get_drive_root_method)
    yield mock_drive
```

This ensures that even if tests create portable folders like `pyMM.Logs` or `pyMM.Projects`, they
are created in isolated temporary directories that are automatically cleaned up.

---

## Running Tests

### Run All Tests

```bash
# Run complete test suite with coverage
pytest

# Run tests without coverage reporting
pytest --no-cov
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration

# GUI tests only (requires display)
pytest tests/gui
```

### Run with Coverage Reports

```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View report
# Open htmlcov/index.html in browser

# Generate terminal coverage report
pytest --cov=app --cov-report=term-missing
```

### Run Tests by Markers

```bash
# Exclude slow tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run only UI tests
pytest -m ui

# Combine markers
pytest -m "integration and not slow"
```

---

## Test Markers

Tests are marked with pytest markers for filtering:

- **`@pytest.mark.integration`** - Integration tests (may access filesystem/network)
- **`@pytest.mark.slow`** - Tests that may take significant time
- **`@pytest.mark.ui`** - Tests requiring GUI components (pytest-qt)

**Example:**

```python
@pytest.mark.integration
@pytest.mark.slow
def test_plugin_download(plugin_manager):
    """Test complete plugin download workflow."""
    # Test implementation
    pass
```

---

## Manual Test Scripts

The root-level `test_*.py` files are standalone manual test scripts for development and debugging:

### Available Scripts

- **`test_git_integration.py`** - Test Git service functionality
- **`test_plugin_download.py`** - Test plugin download and extraction
- **`test_project_management.py`** - Test project creation and management
- **`test_settings_dialog.py`** - Test settings dialog UI

### Running Manual Tests

```bash
# Run directly with Python
python tests/test_git_integration.py

# Run with verbose output
python tests/test_plugin_download.py --verbose
```

**Use Cases:**

- Quick manual validation during development
- Debugging specific functionality
- Testing UI components interactively
- Verifying external integrations (Git, network)

---

## Writing Tests

### Test Structure Guidelines

**Unit Tests:**

- Focus on individual functions/methods in isolation
- Use fixtures from `conftest.py` for common setup
- Mock external dependencies (filesystem, network, etc.)
- Test edge cases and error conditions

**Example:**

```python
def test_resolve_path(file_system_service, app_root):
    """Test resolving relative paths to absolute paths."""
    rel_path = Path("test/file.txt")
    resolved = file_system_service.resolve_path(rel_path)

    assert resolved == app_root / "test" / "file.txt"
    assert resolved.is_absolute()
```

**Integration Tests:**

- Test multiple components working together
- May access real filesystem/network (with cleanup)
- Mark with `@pytest.mark.integration`
- Verify end-to-end workflows

**Example:**

```python
@pytest.mark.integration
def test_project_creation_workflow(project_service, tmp_path):
    """Test complete project creation workflow."""
    project = project_service.create_project(
        name="test-project",
        location=tmp_path,
        init_git=True
    )

    assert project.path.exists()
    assert (project.path / ".git").exists()
```

**GUI Tests:**

- Use `qtbot` fixture from pytest-qt
- Test user interactions (clicks, inputs)
- Verify signals and slots
- Mark with `@pytest.mark.ui`

**Example:**

```python
@pytest.mark.ui
def test_button_click(qtbot):
    """Test button click handling."""
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Simulate button click
    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

    # Wait for signal
    with qtbot.waitSignal(widget.clicked, timeout=1000):
        pass

    assert widget.state == "clicked"
```

---

## Fixtures

Common fixtures are defined in `conftest.py`:

### Available Fixtures

- **`app_root`** - Application root directory path
- **`file_system_service`** - FileSystemService instance
- **`storage_service`** - StorageService instance
- **`config_service`** - ConfigService instance
- **`plugin_manager`** - PluginManager instance
- **`project_service`** - ProjectService instance
- **`mock_config`** - Mock configuration object
- **`qtbot`** - pytest-qt fixture for GUI testing

**Example Usage:**

```python
def test_with_fixtures(config_service, file_system_service):
    """Test using multiple fixtures."""
    config = config_service.load()
    paths = file_system_service.ensure_portable_folders()

    assert config.app_name == "pyMediaManager"
    assert paths["projects"].exists()
```

---

## Coverage Requirements

**Minimum Coverage Targets:**

- **Overall:** 70%
- **Core Services:** 80%+
- **UI Components:** 60%+
- **Utilities:** 90%+

**Current Coverage:**

- `app/core/services/` - 80-95%
- `app/plugins/` - 75-85%
- `app/services/` - 70-80%
- `app/ui/` - 60-70%
- `app/models/` - 85-95%

---

## CI/CD Integration

Tests run automatically on GitHub Actions for every push and pull request.

### Workflows

1. **CI Workflow** (`ci.yml`)
   - Runs on: Push to any branch, Pull Requests
   - Python versions: 3.12, 3.13, 3.14
   - Tests: Full test suite (199 tests) with coverage reporting
   - Code quality: Ruff linting and formatting checks
   - Reports: Coverage reports uploaded to artifacts
   - Minimum coverage: 70% required

2. **Build Workflow** (`build.yml`)
   - Runs on: Push to `dev` branch, version tags (`v*`)
   - Python versions: 3.12, 3.13, 3.14 (embeddable builds)
   - Creates portable distributions with embedded Python runtimes
   - Generates SHA256 checksums for all builds
   - Artifacts: ZIP files with all dependencies included

3. **Release Workflow** (`release.yml`)
   - Runs on: Push to `dev` branch (beta), version tags (stable)
   - Calls build workflow to create distributions
   - **Beta releases**: Updates `latest-beta` tag, cleans old assets first
   - **Stable releases**: Creates new release with changelog
   - Uploads all build artifacts (3.12, 3.13, 3.14)
   - Generates release notes with download instructions

### Local CI Simulation

```bash
# Run tests as CI would
pytest --cov=app --cov-report=html --cov-fail-under=70

# Check if coverage meets minimum
pytest --cov=app --cov-fail-under=70
```

---

## Debugging Tests

### Verbose Output

```bash
# Show detailed test output
pytest -v

# Show captured output (print statements)
pytest -s

# Show both
pytest -vs
```

### Run Single Test

```bash
# By file
pytest tests/unit/test_config_service.py

# By test class
pytest tests/unit/test_config_service.py::TestConfigService

# By specific test
pytest tests/unit/test_config_service.py::TestConfigService::test_load_config
```

### Debug with PDB

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger on first failure, then exit
pytest -x --pdb
```

---

## Best Practices

### Do's

- ✅ Write tests before or alongside code (TDD)
- ✅ Keep tests focused and isolated
- ✅ Use descriptive test names
- ✅ Mock external dependencies
- ✅ Test edge cases and error conditions
- ✅ Clean up resources (files, processes)
- ✅ Use fixtures for common setup
- ✅ Document complex test scenarios

### Don'ts

- ❌ Don't test external libraries
- ❌ Don't make tests dependent on each other
- ❌ Don't leave test files/directories behind
- ❌ Don't use hard-coded absolute paths
- ❌ Don't ignore intermittent failures
- ❌ Don't commit commented-out tests

---

## Troubleshooting

### Common Issues

**Issue: Tests fail with "Module not found"**

```bash
# Solution: Install in development mode
pip install -e ".[dev]"
```

**Issue: GUI tests fail with "Could not find the Qt platform plugin"**

```bash
# Solution: Set QT_QPA_PLATFORM
export QT_QPA_PLATFORM=offscreen  # Linux/macOS
$env:QT_QPA_PLATFORM="offscreen"  # Windows PowerShell
```

**Issue: Slow test execution**

```bash
# Solution: Run in parallel
pip install pytest-xdist
pytest -n auto
```

**Issue: Coverage not generated**

```bash
# Solution: Check pytest-cov is installed
pip install pytest-cov

# Verify with
pytest --cov=app
```

---

## Resources

- **pytest Documentation:** <https://docs.pytest.org/>
- **pytest-qt Documentation:** <https://pytest-qt.readthedocs.io/>
- **Coverage.py:** <https://coverage.readthedocs.io/>
- **Contributing Guide:** [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Questions?** Open an issue or discussion on GitHub!
