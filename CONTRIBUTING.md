# Contributing to pyMediaManager

Thank you for your interest in contributing to pyMediaManager! This guide provides comprehensive
instructions for setting up your development environment, writing code, testing, and submitting
contributions.

> **See also:** [CHANGELOG.md](CHANGELOG.md) | [Architecture Guide](docs/architecture.md) |
> [User Guide](docs/user-guide.md)

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Style](#code-style)
3. [Testing Guidelines](#testing-guidelines)
4. [Pull Request Process](#pull-request-process)
5. [Release Process](#release-process)
6. [Adding New Features](#adding-new-features)
7. [Documentation](#documentation)
8. [Issue Reporting](#issue-reporting)

---

## Development Setup

### fast track with just (Recommended)

If you have [just](https://github.com/casey/just) installed, you can use the following commands to get started quickly:

```bash
# Install dependencies
just install

# Run tests
just test

# Run linting
just lint

# Build portable distribution
just build
```

### Prerequisites

- **Python:** 3.12, 3.13, or 3.14 (3.13 recommended)
- **Git:** Latest version
- **OS:** Windows 10/11 64-bit (Linux/macOS support planned)
- **IDE:** VS Code recommended (with Python extension)

### Setup Steps

1. **Fork and Clone:**

   ```bash
   # Fork the repository on GitHub first
   git clone https://github.com/YOUR_USERNAME/pyMM.git
   cd pyMM

   # Add upstream remote
   git remote add upstream https://github.com/mosh666/pyMM.git
   ```

2. **Initialize Environment (Using Just):**

   The project uses `just` to automate setup. This command creates the virtual environment,
   installs dependencies (including dev tools), and compiles requirements.

   ```bash
   just install
   ```

3. **Install Git Hooks:**

   Set up pre-commit hooks to ensure code quality (linting, formatting, type checking) before simple commits.

   ```bash
   just setup-hooks
   ```

   **What pre-commit hooks do:**
   - 🔍 **Ruff linting** - Auto-fix code style issues
   - 🎨 **Ruff formatting** - Ensure consistent code formatting
   - 🔎 **MyPy** - Static type checking
   - 🔐 **Bandit** - Security vulnerability scanning
   - 🧪 **Unit tests** - Run fast unit tests on commit

4. **Verify Setup:**

   ```bash
   just test
   ```

### Manual Setup (Fallback)

If you cannot use `just`, follow these manual steps:

1. **Create Virtual Environment:**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/macOS
   ```

2. **Install Dependencies:**

   ```bash
   pip install pip-tools
   pip-compile -o requirements.lock pyproject.toml
   pip install -e ".[dev]"
   ```

3. **Install Pre-commit:**

   ```bash
   pip install pre-commit
   pre-commit install --install-hooks
   pre-commit install --hook-type pre-push
   ```



5. **Run Tests:**

   ```bash
   # Run full test suite
   just test
   ```

6. **Configure Git:**

   ```bash
   # Set your identity
   git config user.name "Your Name"
   git config user.email "your.email@example.com"

   # Set default branch
   git config init.defaultBranch main
   ```

7. **Environment Configuration (Optional):**

   By default, the application runs in "Portable Mode" locally (saving data to the app directory).
   To prevent cluttering your drive root or source folder during development, you can use:

   - **Windows (PowerShell):** `$env:PYMM_PORTABLE="false"`
   - **Action:** Keeps Logs and Projects in your local Drive Root (e.g., `D:/Projects`, `D:/Logs`)
     instead of the application folder, simulating a deployed environment or keeping source clean.

   ```bash
   # Enable Dev Mode paths
   $env:PYMM_PORTABLE="false"
   python launcher.py
   ```

---

## Code Style

### Python Style Guide

We follow PEP 8 with these tools and standards:

- **Ruff**: Fast linting with auto-fix and formatting (replaces Black, flake8, isort)
- **MyPy**: Static type checking for type safety
- **Bandit**: Security vulnerability scanning
- **Modern Type Hints**: Use Python 3.12+ native types (`list`, `dict`, `tuple`) instead of
  `typing.List`, `typing.Dict`, etc.

### Code Quality Standards

**All production code must follow these standards:**

1. **Structured Logging**: Use `LoggingService` and logger instances, never `print()` statements

   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.info("Processing started")
   logger.debug(f"Processing {count} items")
   ```

2. **Type Hints**: All functions must have complete type hints including return types

   ```python
   def process_items(items: list[str], count: int) -> dict[str, int]:
       """Process items and return results."""
       return {}
   ```

3. **Modern Generic Types**: Use built-in generic types (Python 3.12+)

   ```python
   # ✅ Correct (Python 3.12+)
   def get_items() -> list[str]: ...
   def get_config() -> dict[str, Any]: ...
   def get_pair() -> tuple[int, str]: ...

   # ❌ Wrong (old style)
   from typing import List, Dict, Tuple
   def get_items() -> List[str]: ...
   ```

4. **Docstrings**: All public functions, classes, and methods must have docstrings

   ```python
   def calculate_total(items: list[float]) -> float:
       """
       Calculate total from list of numbers.

       Args:
           items: List of numbers to sum

       Returns:
           Total sum of all items

       Raises:
           ValueError: If items list is empty
       """
       if not items:
           raise ValueError("Items list cannot be empty")
       return sum(items)
   ```

5. **YAML Configuration**: Use Pydantic models with validation
   - Sensitive data redaction for passwords, tokens, API keys
   - Type-safe configuration with validation
   - Layered config: defaults → app.yaml → user.yaml

### Running Code Quality Tools

```bash
# Format and fix code
just format
just lint

# Type check
just lint
```

### Pre-commit Hooks

We use [pre-commit](https://pre-commit.com/) to automatically run code quality checks before each
commit. The hooks are configured in [.pre-commit-config.yaml](.pre-commit-config.yaml) and include:

**Code Quality:**

- **ruff** - Linter with auto-fix (replaces flake8, isort, and more)
- **ruff-format** - Code formatter (replaces Black)
- **mypy** - Static type checking for type safety

**File Checks:**

- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **check-yaml** - Validate YAML files
- **check-toml** - Validate TOML files
- **check-json** - Validate JSON files
- **check-merge-conflict** - Check for merge conflict markers
- **mixed-line-ending** - Ensure consistent line endings

**Security:**

- **detect-private-key** - Prevent committing private keys

**Documentation:**

- **markdownlint** - Strict markdown linting for documentation quality

**Tests:**

- **unit-tests** - Run fast unit tests on commit (~140 tests)
- **full-tests** - Run complete test suite before push (193 tests with 73% coverage)

**Install hooks** (one-time setup):

```bash
# Automatic setup (recommended)
# Windows PowerShell:
.\scripts\setup-git-hooks.ps1

# Linux/macOS/Git Bash:
bash scripts/setup-git-hooks.sh
```

**Run manually** (optional):

```bash
pre-commit run --all-files
```

The hooks run automatically on `git commit` and `git push`. If any hook fails, the commit/push
will be blocked until you fix the issues. This ensures all code meets quality standards before
entering the repository.

### Pre-commit Checks

Before committing, ensure:

```bash
# All tests pass
pytest

# Code is formatted and linted
ruff check --fix app/ tests/
ruff format app/ tests/
```

## Release Process

### Building the Portable Distribution

You can build the portable Windows distribution locally without relying on CI:

```bash
# Using just (recommended)
just build

# Or using the python script directly
python scripts/build_distribution.py --version 3.13
```

This will:
1. Download the embedded Python distribution.
2. Install all dependencies from `pyproject.toml`.
3. Configure the runtime environment.
4. Create a zip archive in the build directory.

### Branch Strategy

We follow a branch-based release flow:

1. **Development (`dev` branch)**
   - All new features and fixes are merged here.
   - Pushes to `dev` automatically trigger a **Beta Release** (tagged `latest-beta`).
   - These releases are marked as "Pre-release" on GitHub.

2. **Stable (`main` branch)**
   - Stable releases are created by pushing a semantic version tag (e.g., `vX.Y.Z`) to `main`.
   - **Do not** push directly to `main`. Use Pull Requests from `dev` to `main`.
   - The workflow will automatically build and publish the release.

3. **Versioning**
   - We use [Semantic Versioning](https://semver.org/).
   - Format: `vX.Y.Z` (Stable) or `vX.Y.Z-alpha.N` / `vX.Y.Z-beta.N` (Prerelease).
   - `setuptools_scm` automatically handles versioning based on git tags.

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```text
feat(plugins): add support for custom plugin loaders

Implement plugin loader interface to allow custom plugin types
beyond the standard SimplePluginImplementation.

Closes #123
```

```text
fix(storage): correct drive serial number detection on USB drives

The serial number detection was failing for some USB drives due to
incorrect API calls. Fixed by using correct Windows API.

Fixes #456
```

## Testing Guidelines

### Test Philosophy

- **Test-Driven Development (TDD)**: Write tests before implementation when possible
- **Coverage Target**: Maintain 70%+ code coverage (enforced in CI)
- **Isolation**: Tests use automatic drive mocking to prevent system pollution
- **Fast Feedback**: Unit tests run in <5 seconds, full suite in <30 seconds
- **Comprehensive**: Unit, integration, and GUI tests for complete coverage

### Test Categories

#### Unit Tests (~140 tests)

Located in `tests/unit/`, these test individual components in isolation:

**Service Tests**:

- `test_config_service.py`: Configuration loading, validation, redaction
- `test_file_system_service.py`: Path resolution, file operations
- `test_storage_service.py`: Drive detection, removable drive identification
- `test_logging_service.py`: Logger setup, file rotation, formatting
- `test_project_service.py`: Project creation, metadata management
- `test_git_service.py`: Git operations, repository management

**Plugin Tests**:

- `test_plugin_manager.py`: Plugin discovery, installation, PATH registration
- `test_plugin_base.py`: Plugin base class, validation, download logic

**Example Unit Test**:

```python
import pytest
from pathlib import Path
from app.core.services.config_service import ConfigService

def test_config_service_loads_defaults(tmp_path):
    """Test that config service loads default values correctly."""
    config_service = ConfigService(tmp_path)
    config = config_service.load()

    assert config.app.name == "pyMediaManager"
    assert config.logging.level == "INFO"
    assert config.plugins.retry_attempts == 3

def test_config_service_redacts_sensitive_data(tmp_path):
    """Test that sensitive fields are redacted in exports."""
    config_service = ConfigService(tmp_path)

    # Set sensitive data
    config_service.update_config(database={"password": "secret123"})

    # Export with redaction
    exported = config_service.export_config(redact_sensitive=True)

    assert exported["database"]["password"] == "***REDACTED***"
```

#### Integration Tests (~10 tests)

Located in `tests/integration/`, these test workflows across multiple components:

- `test_plugin_workflow.py`: Complete plugin download and installation
- `test_project_workflow.py`: End-to-end project creation with Git

#### GUI Tests (~50 tests)

Located in `tests/gui/`, these test UI components using pytest-qt:

- `test_first_run_wizard.py` (17 tests): Wizard pages, navigation, validation
- `test_project_browser.py`: Project list, search, filtering
- `test_project_wizard.py`: Project creation dialog
- `test_settings_dialog.py`: Settings tabs, validation, persistence
- `test_views.py`: Storage, Plugin, and Project views

**Example GUI Test**:

```python
from pytestqt.qtbot import QtBot
from PySide6.QtCore import Qt
from app.ui.dialogs.project_wizard import ProjectWizard

def test_project_wizard_validation(qtbot: QtBot):
    """Test that project wizard validates input correctly."""
    wizard = ProjectWizard()
    qtbot.addWidget(wizard)

    # Try to proceed with empty name
    assert not wizard.validateCurrentPage()

    # Enter valid name
    wizard.name_input.setText("test-project")
    assert wizard.validateCurrentPage()

def test_project_wizard_creates_project(qtbot: QtBot, tmp_path):
    """Test that wizard creates project successfully."""
    wizard = ProjectWizard()
    qtbot.addWidget(wizard)

    # Fill in project details
    wizard.name_input.setText("vacation-2026")
    wizard.location_input.setText(str(tmp_path))

    # Create project
    with qtbot.waitSignal(wizard.finished, timeout=1000):
        wizard.accept()

    # Verify project exists
    project_path = tmp_path / "vacation-2026"
    assert project_path.exists()
    assert (project_path / ".pymm").exists()
```

### Test Fixtures

Common fixtures in `tests/conftest.py`:

- `mock_drive_root`: Automatically mocks drive root for all tests (autouse=True)
- `app_root`: Temporary application root directory
- `mock_config_service`: Pre-configured ConfigService for testing
- `mock_file_system_service`: FileSystemService with mocked paths
- `mock_storage_service`: StorageService with test drives
- `qapp`: Qt application instance for GUI tests (pytest-qt)

### Test Isolation

The test suite automatically isolates all file system operations to prevent polluting the system
drive during test execution. This is handled transparently by the `mock_drive_root` fixture in
`tests/conftest.py`.

**Key Points:**

- Tests never create folders on C:\ or other system drives
- All `pyMM.Logs` and `pyMM.Projects` folders are created in temporary directories
- Cleanup is automatic - no manual intervention needed
- Test isolation is enabled for all 193 tests automatically

**How It Works:**

The `mock_drive_root` fixture (with `autouse=True`) monkey-patches
`FileSystemService.get_drive_root()` to return temporary directories instead of actual drive roots.
This ensures complete isolation without requiring changes to test code.

If you're writing new tests that use `FileSystemService`, the isolation will work automatically.
No special configuration is needed.

---

## CI/CD and GitHub Actions

pyMediaManager uses GitHub Actions for continuous integration and security scanning. All workflows
are located in `.github/workflows/` and automatically run on pull requests and pushes.

### CI Workflow (`ci.yml`)

**Runs on:**

- Push to `main` and `dev` branches
- Pull requests to `main` and `dev`

**What it does:**

- Tests on Python 3.12, 3.13, and 3.14
- Runs full test suite with coverage reporting
- Uploads coverage to Codecov
- Validates code quality with Ruff and MyPy
- Checks for security vulnerabilities
- Ensures all pre-commit hooks pass

**Key features:**

- Matrix testing across Python versions
- Proper GITHUB_TOKEN permissions (read-only by default)
- Coverage threshold enforcement (70% minimum)
- Fast fail strategy for quick feedback

### Security Workflow (`security.yml`)

**Runs on:**

- Pull requests (paths: `app/**`, `tests/**`, `.github/workflows/security.yml`)
- Scheduled weekly scan (Mondays at 00:00 UTC)
- Manual dispatch available

**What it does:**

- CodeQL analysis for security vulnerabilities
- Detects common security issues:
  - SQL injection
  - Cross-site scripting (XSS)
  - Command injection
  - Path traversal
  - Insecure cryptography
- Uploads results to GitHub Security tab
- Integrates with GitHub Advanced Security

**Languages analyzed:**

- Python (comprehensive security scanning)

### OpenSSF Scorecard (`scorecard.yml`)

**Runs on:**

- Scheduled weekly scan (Mondays at 08:00 UTC)
- Push to `main` branch
- Manual dispatch available

**What it does:**

- Evaluates repository security practices
- Checks for:
  - Branch protection settings
  - Code review enforcement
  - Signed commits
  - Dependency update tools
  - Automated security testing
  - Proper permission settings
- Publishes results to OpenSSF Scorecard API
- Displays badge on README

**Score categories:**

- Binary artifacts
- Branch protection
- CI tests
- Code review
- Contributors
- Dangerous workflow
- Dependency update
- Fuzzing
- License
- Maintained
- Packaging
- Pinned dependencies
- SAST (Static Application Security Testing)
- Security policy
- Signed releases
- Token permissions
- Vulnerabilities
- Webhooks

### Dependabot

Dependabot automatically checks for dependency updates and creates pull requests:

- **pip dependencies**: Daily updates
- **GitHub Actions**: Daily updates
- Grouped updates for efficiency
- Automatic security vulnerability alerts

### Local CI Testing

Before pushing, you can run the same checks locally:

```bash
# Run all pre-commit hooks (same as CI)
pre-commit run --all-files

# Run full test suite with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run linting
ruff check app/ tests/

# Run formatting check
ruff format --check app/ tests/

# Run type checking
mypy app/

# Run security scanning
bandit -r app/ -c .bandit
```

---

## Pull Request Process

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**:
   - Write tests first (TDD encouraged)
   - Implement the feature
   - Update documentation
   - Ensure tests pass

3. **Commit your changes**:

   ```bash
   git add .
   git commit -m "feat: add my new feature"
   ```

4. **Push to your fork**:

   ```bash
   git push origin feature/my-new-feature
   ```

5. **Create Pull Request**:
   - Provide clear description of changes
   - Reference related issues
   - Ensure CI passes
   - Wait for code review

### PR Checklist

Use the pull request template (`.github/PULL_REQUEST_TEMPLATE.md`) which includes:

- [ ] Tests added/updated and all tests pass
- [ ] Documentation updated
- [ ] Code formatted with Ruff
- [ ] Linting passes (Ruff check)
- [ ] Type checking passes (MyPy)
- [ ] All CI checks pass
- [ ] Commit messages follow Conventional Commits
- [ ] Breaking changes documented
- [ ] Screenshots/demos for UI changes
- [ ] Security considerations addressed

## Adding New Features

### Adding a New Service

**Service Architecture:**

Services follow dependency injection patterns:

- **ConfigService**: YAML-based configuration with Pydantic validation
- **FileSystemService**: Portable path handling and file operations
- **StorageService**: Drive detection and management
- **LoggingService**: Structured logging with Rich console and rotating files
- **ProjectService**: Project lifecycle management
- **GitService**: Git repository operations using GitPython

**Creating a new service:**

1. Create service file in `app/core/services/`:

   ```python
   # app/core/services/my_service.py
   import logging
   from pathlib import Path

   logger = logging.getLogger(__name__)

   class MyService:
       """Service for managing X functionality."""

       def __init__(self, config_service: ConfigService):
           """Initialize service with dependencies."""
           self.config = config_service
           logger.info("MyService initialized")

       def do_something(self, input_path: Path) -> dict[str, Any]:
           """Perform service operation.

           Args:
               input_path: Path to process

           Returns:
               Dictionary of results
           """
           logger.debug(f"Processing {input_path}")
           return {}
   ```

2. Create comprehensive tests in `tests/unit/`:

   ```python
   # tests/unit/test_my_service.py
   import pytest
   from pathlib import Path
   from app.core.services.my_service import MyService

   @pytest.fixture
   def service(mock_config_service):
       return MyService(mock_config_service)

   def test_my_service_basic_operation(service):
       """Test basic service operation."""
       result = service.do_something(Path("test.txt"))
       assert isinstance(result, dict)
       assert "key" in result

   def test_my_service_error_handling(service):
       """Test service handles errors correctly."""
       with pytest.raises(ValueError):
           service.do_something(None)
   ```

3. Register in main application with dependency injection
4. Update architecture documentation in `docs/architecture.md`
5. Add integration tests if service interacts with other components

### Adding a New Plugin

1. Create plugin manifest:

   ```yaml
   # plugins/myplugin/plugin.yaml
   name: MyPlugin
   version: "X.Y.Z"
   mandatory: false
   enabled: false
   source:
     type: url
     base_uri: https://example.com/myplugin.zip
   command:
     path: bin
     executable: myplugin.exe
   ```

2. Test download URL
3. Submit PR with manifest

### Adding a New UI View

1. Create view class:

   ```python
   # app/ui/views/my_view.py
   from PySide6.QtWidgets import QWidget

   class MyView(QWidget):
       def __init__(self, parent=None):
           super().__init__(parent)
           self._init_ui()

       def _init_ui(self):
           # Setup UI
           pass
   ```

2. Register in MainWindow:

   ```python
   self.my_view = MyView()
   self.addSubInterface(
       self.my_view,
       FluentIcon.CUSTOM,
       "My View",
       NavigationItemPosition.TOP
   )
   ```

3. Add tests in `tests/gui/test_views.py`

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """
    Short description of function.

    Longer description with more details about what the function does,
    how it works, and any important notes.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
    """
    pass
```

### Documentation Files

- **README.md**: User-facing overview
- **docs/architecture.md**: Technical architecture
- **docs/plugin-development.md**: Plugin development guide
- **CONTRIBUTING.md**: This file

### Updating Documentation

- Update relevant docs with code changes
- Add examples for new features
- Keep docs in sync with code

## Issue Reporting

### Bug Reports

Include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:

- Use case description
- Proposed solution
- Alternative approaches considered

## Questions?

- **Discussions**: <https://github.com/mosh666/pyMM/discussions>
- **Issues**: <https://github.com/mosh666/pyMM/issues>

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
