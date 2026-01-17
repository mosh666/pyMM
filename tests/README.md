# pyMediaManager Test Suite

> **Last Updated:** 2026-01-17 21:41 UTC


<!-- markdownlint-disable MD013 MD033 MD060 -->

> **Comprehensive testing infrastructure with 193 tests, 73% code coverage, and automatic system drive protection**
>
> **📋 Testing Roadmap:** See [docs/testing-roadmap.md](../docs/testing-roadmap.md) for test coverage plan, priority tiers (sync engine 0% → 60%, GUI 26% → 40%), and contribution guidelines. **Sync engine testing is the highest-priority gap.**

---

## 📊 Overview

pyMediaManager maintains a robust test suite ensuring code quality, reliability, and maintainability across all components.

### Quick Stats

| Metric | Value |
| ------ | ----- |
| **Total Tests** | 193 (all passing ✅) |
| **Code Coverage** | 73% (70% minimum enforced) |
| **Framework** | pytest 7.4+ with pytest-qt, pytest-asyncio |
| **CI/CD** | Matrix testing on Python 3.12, 3.13, 3.14 on all platforms |
| **Test Isolation** | Automatic system drive protection |
| **Performance** | < 60 seconds full suite execution |

### Test Distribution

```text
Unit Tests ............. 95 tests (49%)
Integration Tests ...... 10 tests (5%)
GUI Tests .............. 50 tests (26%)
Manual Tests ........... 4 scripts (2%)
Fixtures & Config ...... 34 tests (18%)
```

---

## 🗂️ Directory Structure

```text
tests/
├── unit/                           # Unit tests for individual modules (95 tests)
│   ├── test_config_service.py      # Configuration management (15 tests)
│   ├── test_file_system_service.py # File system operations (20 tests)
│   ├── test_git_service.py         # Git integration (12 tests)
│   ├── test_logging_service.py     # Logging functionality (8 tests)
│   ├── test_plugin_base.py         # Plugin base classes (10 tests)
│   ├── test_plugin_manager.py      # Plugin lifecycle (18 tests)
│   ├── test_project.py             # Project models (8 tests)
│   └── test_storage_service.py     # Storage operations (4 tests)
│
├── integration/                    # Integration tests for workflows (10 tests)
│   ├── test_plugin_workflow.py     # Plugin download, install, update (6 tests)
│   └── test_project_workflow.py    # Project creation, loading, config (4 tests)
│
├── gui/                            # GUI component tests (50 tests)
│   ├── test_first_run_wizard.py    # Initial setup wizard (12 tests)
│   ├── test_project_dialogs.py     # Project browser, wizard (25 tests)
│   └── test_views.py               # Plugin, project, storage views (13 tests)
│
├── conftest.py                     # Shared pytest fixtures and configuration
├── test_git_integration.py         # Manual Git operations test script
├── test_plugin_download.py         # Manual plugin download test script
├── test_project_management.py      # Manual project management test script
├── test_settings_dialog.py         # Manual settings dialog test script
└── README.md                       # This file
```

---

## 🚀 Running Tests

### Quick Start

```bash
# Run all tests with coverage
pytest

# Run without coverage (faster)
pytest --no-cov

# Run in parallel (requires pytest-xdist)
pytest -n auto
```

### By Category

```bash
# Unit tests only (fast, isolated)
pytest tests/unit/

# Integration tests (may access filesystem/network)
pytest tests/integration/

# GUI tests (requires display, slower)
pytest tests/gui/

# Specific test file
pytest tests/unit/test_plugin_manager.py

# Specific test function
pytest tests/unit/test_plugin_manager.py::TestPluginManager::test_load_plugins
```

### By Markers

```bash
# Skip slow tests (CI optimization)
pytest -m "not slow"

# Integration tests only
pytest -m integration

# UI tests only
pytest -m ui

# Combine markers
pytest -m "integration and not slow"

# Skip UI tests (headless environments)
pytest -m "not ui"
```

### With Coverage Reports

```bash
# HTML coverage report (interactive)
pytest --cov=app --cov-report=html
# Open: htmlcov/index.html

# Terminal report with missing lines
pytest --cov=app --cov-report=term-missing

# XML report (for CI/CD integrations)
pytest --cov=app --cov-report=xml

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=70
```

### Advanced Options

```bash
# Verbose output with full test names
pytest -v

# Very verbose with test details
pytest -vv

# Show local variables on failure
pytest -l

# Stop on first failure
pytest -x

# Show N slowest tests
pytest --durations=10

# Capture output (show print statements)
pytest -s

# Disable warnings
pytest --disable-warnings
```

---

## 🔒 Test Isolation & System Protection

### Automatic System Drive Protection

The test suite **prevents system drive pollution** through automatic mocking in [conftest.py](conftest.py). All file system operations are transparently redirected to temporary directories.

#### How It Works

```python
# conftest.py - Automatic system protection fixture
@pytest.fixture(autouse=True)
def mock_drive_root(monkeypatch, tmp_path):
    """
    Automatically redirects FileSystemService.get_drive_root() to temporary
    directories, preventing tests from creating folders on system drives.

    - Runs automatically for ALL tests (autouse=True)
    - Zero configuration required
    - Transparent to test code
    - Automatic cleanup after tests
    """
    from app.core.services.file_system_service import FileSystemService

    mock_drive = tmp_path / "mock_drive_root"
    mock_drive.mkdir(exist_ok=True)

    def mock_get_drive_root_method(self):
        self._drive_root = mock_drive
        return mock_drive

    monkeypatch.setattr(
        FileSystemService,
        "get_drive_root",
        mock_get_drive_root_method
    )

    yield mock_drive
    # Automatic cleanup by pytest tmp_path
```

#### Benefits

- ✅ **No System Pollution**: Tests never create `pyMM.Logs`, `pyMM.Projects`, or any folders on C:\, D:\, etc.
- ✅ **Zero Configuration**: Works automatically without changes to test code
- ✅ **Transparent Operation**: Tests work identically in isolated environments
- ✅ **Automatic Cleanup**: All test artifacts removed after execution
- ✅ **CI/CD Ready**: Perfect for automated testing environments
- ✅ **Parallel Safe**: Each test gets unique temporary directory

#### Example

```python
# Test code (no changes needed)
def test_project_creation(project_service):
    """Test runs in isolated temp directory automatically."""
    project = project_service.create_project("TestProject")

    # This path is in tmp_path, NOT on system drive
    assert project.path.exists()
    assert "TestProject" in project.name
    # After test: automatically cleaned up
```

---

## 🏷️ Test Markers

Tests use pytest markers for categorization and filtering:

### Standard Markers

| Marker | Purpose | Example Usage |
|--------|---------|---------------|
| `@pytest.mark.integration` | Integration tests (filesystem/network) | `pytest -m integration` |
| `@pytest.mark.slow` | Tests taking > 5 seconds | `pytest -m "not slow"` |
| `@pytest.mark.ui` | GUI tests requiring display | `pytest -m "not ui"` |

### Custom Markers (Configured in pyproject.toml)

```toml
[tool.pytest.ini_options]
markers = [
    "integration: Integration tests (may be slower, access filesystem/network)",
    "slow: Tests that may take significant time to complete",
    "ui: Tests that require GUI components",
]
```

### Usage Examples

```python
# Integration test with potential filesystem access
@pytest.mark.integration
def test_plugin_download_workflow(plugin_manager):
    """Download and extract plugin from GitHub."""
    result = plugin_manager.download_plugin("digikam")
    assert result.success

# Slow test (e.g., network operations, large datasets)
@pytest.mark.slow
@pytest.mark.integration
def test_full_project_workflow(project_service):
    """Complete project lifecycle test."""
    # Long-running operations
    pass

# GUI test requiring display
@pytest.mark.ui
def test_settings_dialog_rendering(qtbot):
    """Test settings dialog UI rendering."""
    dialog = SettingsDialog()
    qtbot.addWidget(dialog)
    assert dialog.isVisible()
```

---

## 🛠️ Manual Test Scripts

Root-level `test_*.py` files are **standalone scripts** for interactive development and debugging. These are **not** run by pytest.

### Available Scripts

| Script | Purpose | Run Command |
|--------|---------|-------------|
| `test_git_integration.py` | Git service testing (clone, commit, push) | `python test_git_integration.py` |
| `test_plugin_download.py` | Plugin download from GitHub releases | `python test_plugin_download.py` |
| `test_project_management.py` | Project CRUD operations | `python test_project_management.py` |
| `test_settings_dialog.py` | Settings UI interactive testing | `python test_settings_dialog.py` |

### Use Cases

- 🔍 **Manual Validation**: Quick verification during development
- 🐛 **Debugging**: Step-through debugging with IDE
- 🎨 **UI Testing**: Interactive GUI component testing
- 🌐 **External Services**: Test Git, network, or system integrations
- 📊 **Performance Profiling**: Measure execution time and resource usage

### Example Usage

```bash
# Run with Python directly
python tests/test_git_integration.py

# With verbose output (if supported)
python tests/test_plugin_download.py --verbose

# Debug in IDE
# Set breakpoint in test_git_integration.py and run with debugger
```

---

## ✍️ Writing Tests

### Test Structure Guidelines

#### Unit Test Template

```python
"""Unit tests for ModuleName.

Tests isolated functionality with mocked dependencies.
"""

import pytest
from app.module import ClassName


class TestClassName:
    """Test suite for ClassName."""

    @pytest.fixture
    def instance(self):
        """Create ClassName instance for testing."""
        return ClassName()

    def test_method_success(self, instance):
        """Test method_name returns expected result."""
        result = instance.method_name("input")
        assert result == "expected_output"

    def test_method_validation(self, instance):
        """Test method_name validates input."""
        with pytest.raises(ValueError, match="Invalid input"):
            instance.method_name(None)

    @pytest.mark.parametrize("input_val,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
        ("test3", "result3"),
    ])
    def test_method_variants(self, instance, input_val, expected):
        """Test method_name with various inputs."""
        assert instance.method_name(input_val) == expected
```

#### Integration Test Template

```python
"""Integration tests for WorkflowName.

Tests component interactions and end-to-end scenarios.
"""

import pytest


@pytest.mark.integration
class TestWorkflowName:
    """Test suite for WorkflowName integration."""

    def test_complete_workflow(self, service_a, service_b):
        """Test complete workflow from start to finish."""
        # Arrange
        initial_data = service_a.prepare()

        # Act
        result = service_b.process(initial_data)

        # Assert
        assert result.success
        assert result.data is not None

    @pytest.mark.slow
    def test_external_service_integration(self, service):
        """Test integration with external service."""
        # May involve network calls, file I/O
        response = service.call_external_api()
        assert response.status_code == 200
```

#### GUI Test Template

```python
"""GUI tests for ComponentName.

Tests Qt widget functionality and user interactions.
"""

import pytest
from PySide6.QtCore import Qt


@pytest.mark.ui
class TestComponentName:
    """Test suite for ComponentName GUI."""

    @pytest.fixture
    def widget(self, qtbot):
        """Create widget instance for testing."""
        from app.ui.components import ComponentName

        widget = ComponentName()
        qtbot.addWidget(widget)
        return widget

    def test_widget_initialization(self, widget):
        """Test widget initializes correctly."""
        assert widget.isVisible()
        assert widget.windowTitle() == "Expected Title"

    def test_button_click(self, widget, qtbot):
        """Test button click triggers action."""
        button = widget.findChild(QPushButton, "submitButton")

        with qtbot.waitSignal(widget.actionTriggered, timeout=1000):
            qtbot.mouseClick(button, Qt.LeftButton)

    def test_text_input(self, widget, qtbot):
        """Test text input updates state."""
        line_edit = widget.findChild(QLineEdit, "nameInput")
        qtbot.keyClicks(line_edit, "Test Name")

        assert line_edit.text() == "Test Name"
        assert widget.get_name() == "Test Name"
```

### Best Practices

#### Naming Conventions

```python
# Test files
test_<module_name>.py          # matches app/<module_name>.py

# Test classes
class Test<ClassName>:         # group related tests

# Test functions
def test_<method>_<scenario>:  # descriptive, specific
```

#### AAA Pattern (Arrange-Act-Assert)

```python
def test_calculate_total():
    """Test calculate_total with multiple items."""
    # Arrange - Set up test data
    items = [
        {"price": 10.0, "quantity": 2},
        {"price": 5.0, "quantity": 3},
    ]

    # Act - Execute the code being tested
    total = calculate_total(items)

    # Assert - Verify expected results
    assert total == 35.0
    assert isinstance(total, float)
```

#### Fixture Usage

```python
# conftest.py - Shared fixtures
@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file."""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("key: value")
    return config_file

# test_config.py - Use fixtures
def test_load_config(temp_config_file):
    """Test config loading from file."""
    config = load_config(temp_config_file)
    assert config["key"] == "value"
```

#### Parametrization

```python
@pytest.mark.parametrize("input_val,expected", [
    ("valid@email.com", True),
    ("invalid-email", False),
    ("", False),
    (None, False),
])
def test_email_validation(input_val, expected):
    """Test email validation with various inputs."""
    assert validate_email(input_val) == expected
```

#### Mocking External Dependencies

```python
def test_api_call(mocker):
    """Test API call with mocked requests."""
    # Mock external dependency
    mock_response = mocker.Mock()
    mock_response.json.return_value = {"data": "test"}
    mocker.patch("requests.get", return_value=mock_response)

    # Test code that uses requests.get
    result = fetch_data()
    assert result["data"] == "test"
```

---

## 📈 Code Coverage

### Coverage Configuration

Configured in [pyproject.toml](../pyproject.toml):

```toml
[tool.pytest.ini_options]
addopts = [
    "--cov=app",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=70",  # Enforce 70% minimum
]

[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/app/_version.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

### Current Coverage Stats

| Module | Coverage | Status |
|--------|----------|--------|
| `app/core/` | 85% | ✅ Excellent |
| `app/models/` | 90% | ✅ Excellent |
| `app/services/` | 75% | ✅ Good |
| `app/plugins/` | 68% | ⚠️ Needs improvement |
| `app/ui/` | 60% | ⚠️ Needs improvement |
| **Overall** | **73%** | ✅ Above threshold |

### Improving Coverage

```bash
# Identify uncovered lines
pytest --cov=app --cov-report=term-missing

# Generate HTML report for detailed analysis
pytest --cov=app --cov-report=html
# Open htmlcov/index.html

# Focus on specific module
pytest tests/unit/test_plugin_manager.py --cov=app.plugins.plugin_manager

# Show coverage for new code only
pytest --cov=app --cov-report=term:skip-covered
```

---

## 🔧 Fixtures & Configuration

### Key Fixtures (conftest.py)

| Fixture | Scope | Purpose |
|---------|-------|---------|
| `mock_drive_root` | `function` | Auto-mocks file system operations |
| `app_config` | `session` | Provides test configuration |
| `qtbot` | `function` | Qt testing utilities (pytest-qt) |
| `temp_project_dir` | `function` | Temporary project directory |
| `mock_plugin_manager` | `function` | Mocked plugin manager |
| `sample_project` | `function` | Pre-configured project instance |

### Fixture Example Usage

```python
def test_with_multiple_fixtures(
    mock_drive_root,
    temp_project_dir,
    sample_project
):
    """Test using multiple fixtures."""
    # mock_drive_root: Automatic system protection
    # temp_project_dir: Isolated directory for this test
    # sample_project: Pre-configured Project object

    assert temp_project_dir.exists()
    assert sample_project.name == "SampleProject"
```

### Custom Fixtures

```python
# In conftest.py or test file
@pytest.fixture
def custom_config():
    """Provide custom configuration for tests."""
    return {
        "debug": True,
        "timeout": 30,
        "retries": 3,
    }

# Use in test
def test_with_custom_config(custom_config):
    """Test with custom configuration."""
    assert custom_config["debug"] is True
```

---

## 🐛 Debugging Tests

### Run Single Test with Debug Output

```bash
# Full verbose output
pytest tests/unit/test_plugin_manager.py::test_load_plugins -vv -s

# Show local variables on failure
pytest tests/unit/test_plugin_manager.py::test_load_plugins -l

# Enter debugger on failure
pytest tests/unit/test_plugin_manager.py::test_load_plugins --pdb
```

### IDE Debugging

#### VS Code

Add to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "pytest: Current Test",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "${file}",
                "-v",
                "-s"
            ],
            "console": "integratedTerminal",
            "justMyCode": false
        }
    ]
}
```

#### PyCharm

1. Right-click test function
2. Select "Debug 'pytest in test_...'"
3. Breakpoints work automatically

### Common Debugging Techniques

```python
# Print debugging (use -s flag)
def test_debug_output():
    result = function_under_test()
    print(f"Result: {result}")  # Visible with pytest -s
    assert result is not None

# Use pytest.set_trace() for interactive debugging
def test_interactive_debug():
    result = function_under_test()
    import pytest; pytest.set_trace()  # Breakpoint here
    assert result == expected

# Capture and inspect logs
def test_with_logs(caplog):
    function_that_logs()
    assert "Expected message" in caplog.text
```

---

## 🚀 CI/CD Integration

### GitHub Actions Workflow

Tests run automatically on every push and pull request:

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Set up uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv sync --all-extras

      - name: Run tests with coverage
        run: |
          pytest --cov=app --cov-report=xml

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
```

### Coverage Enforcement

- ✅ Minimum 70% coverage required to pass CI
- ✅ Coverage reports automatically uploaded to Codecov
- ✅ Pull requests show coverage diff
- ✅ Failing coverage blocks merge

---

## ⚠️ Test Coverage Gaps

### Sync Engine Modules (Zero Test Coverage)

The synchronization engine in `app/core/sync/` is **fully implemented and production-ready** but currently has **zero test coverage**. This represents a significant testing gap for the following 9 modules:

| Module | Purpose | Status |
|--------|---------|--------|
| `file_synchronizer.py` | Core sync logic, conflict detection | ❌ No tests |
| `backup_tracking.py` | SQLite-based change tracking | ❌ No tests |
| `scheduled_sync.py` | APScheduler integration | ❌ No tests |
| `realtime_sync.py` | Watchdog file system monitoring | ❌ No tests |
| `notifications.py` | Sync progress callbacks | ❌ No tests |
| `crypto_compression.py` | AES-256-GCM + GZIP/LZ4 | ❌ No tests |
| `bandwidth_throttler.py` | Token bucket rate limiting | ❌ No tests |
| `advanced_sync_options.py` | Configuration dataclass | ❌ No tests |
| `__init__.py` | Public API exports | ❌ No tests |

#### Why This Matters

- **Production Code**: These modules are used in production and handle critical data synchronization
- **Complex Logic**: Includes file conflict resolution, encryption, compression, and scheduled operations
- **Data Safety**: Untested sync logic could lead to data loss or corruption
- **Coverage Target**: Adding these tests would significantly increase overall coverage (currently 73%)

#### Testing Priorities

**High Priority** (Critical for data safety):

1. `file_synchronizer.py` - Test sync operations, conflict detection, checksum verification
2. `backup_tracking.py` - Test SQLite operations, schema migrations, history tracking
3. `crypto_compression.py` - Test encryption/decryption, compression/decompression correctness

**Medium Priority** (Important for reliability):
4. `realtime_sync.py` - Test watchdog event handling, debouncing, sync loop prevention
5. `scheduled_sync.py` - Test APScheduler integration, cron triggers, interval schedules
6. `bandwidth_throttler.py` - Test token bucket algorithm, rate limiting accuracy

**Low Priority** (Nice to have):
7. `notifications.py` - Test callback execution
8. `advanced_sync_options.py` - Test serialization/deserialization
9. `__init__.py` - Test public API surface

#### Contributing Test Coverage

If you'd like to help add test coverage for the sync engine:

1. **Start Small**: Begin with `advanced_sync_options.py` (simple dataclass testing)
2. **Use Mocking**: Mock file system operations to avoid flakiness
3. **Test Edge Cases**: Focus on conflict resolution, error handling, and boundary conditions
4. **Follow Existing Patterns**: Reference `tests/unit/` for testing conventions
5. **PR Welcome**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup

Example test structure:

```python
# tests/unit/test_file_synchronizer.py
import pytest
from pathlib import Path
from app.core.sync import FileSynchronizer, SyncStatistics

class TestFileSynchronizer:
    def test_sync_directory_basic(self, tmp_path):
        """Test basic directory synchronization."""
        source = tmp_path / "source"
        dest = tmp_path / "dest"
        source.mkdir()
        (source / "file1.txt").write_text("content")

        sync = FileSynchronizer()
        stats = sync.sync_directory(source, dest)

        assert stats.files_copied == 1
        assert (dest / "file1.txt").read_text() == "content"

    def test_conflict_detection(self, tmp_path):
        """Test file conflict detection."""
        # Add test implementation
        pass
```

---

## 📚 Additional Resources

### Documentation

- [pytest Documentation](https://docs.pytest.org/) - Official pytest guide
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/) - Qt testing with pytest
- [Coverage.py Documentation](https://coverage.readthedocs.io/) - Code coverage measurement
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Project contribution guidelines
- [docs/architecture.md](../docs/architecture.md) - System architecture details

### Related Files

- [pyproject.toml](../pyproject.toml) - Test configuration and dependencies
- [conftest.py](conftest.py) - Shared fixtures and test configuration
- [.github/workflows/](../.github/workflows/) - CI/CD pipeline definitions

### Getting Help

- **Issues**: Report test failures or request features at [GitHub Issues](https://github.com/mosh666/pyMM/issues)
- **Discussions**: Ask questions at [GitHub Discussions](https://github.com/mosh666/pyMM/discussions)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup

---

## 📝 Changelog

### Recent Updates

- **2026-01-07**: Complete test suite documentation rewrite with 2026 best practices
- **2026-01-05**: Added automatic system drive protection fixture
- **2026-01-05**: Increased test count to 193 with 73% coverage
- **2026-01-03**: Added GUI test suite with pytest-qt
- **2026-01-01**: Implemented integration tests for workflows

---

<div align="center">

**Questions? Found a bug in tests?**
[Open an Issue](https://github.com/mosh666/pyMM/issues) · [Start a Discussion](https://github.com/mosh666/pyMM/discussions)

**Testing Framework:** pytest 7.4+ | **Python:** 3.12+ (3.13 recommended) | **License:** MIT

</div>
