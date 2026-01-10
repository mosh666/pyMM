# Contributing to pyMediaManager

Thank you for your interest in contributing to pyMediaManager! This guide provides comprehensive
instructions for setting up your development environment, writing code, testing, and submitting
contributions.

> **See also:** [CHANGELOG.md](CHANGELOG.md) | [Architecture Guide](docs/architecture.md) |
> [User Guide](docs/user-guide.md) | [Developer Getting Started](docs/getting-started-dev.md) |
> [Plugin Development Guide](docs/plugin-development.md)

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Code Style](#code-style)
3. [Testing Guidelines](#testing-guidelines)
4. [Pull Request Process](#pull-request-process)
5. [Release Process](#release-process)
6. [Adding New Features](#adding-new-features)
7. [Documentation](#documentation)
8. [Internationalization (i18n)](#internationalization-i18n)
9. [Issue Reporting](#issue-reporting)

---

## Development Setup

> **New Contributors:** For a comprehensive developer onboarding guide with platform-specific
> instructions, VS Code debugging configurations, and your first contribution walkthrough,
> see [Getting Started for Developers](docs/getting-started-dev.md).
>
> **Plugin Developers:** For detailed plugin development workflow including "Your First Plugin"
> tutorial with step-by-step instructions, see [Plugin Development Guide](docs/plugin-development.md).

### Fast Track with just (Recommended)

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

- **Python:** 3.12, 3.13, or 3.14 (Python 3.13 recommended for latest features and performance)
- **Git:** 2.30+ (latest version recommended)
- **OS:** Windows 10/11, Linux, or macOS
- **IDE:** VS Code recommended with Python, Ruff, and MyPy extensions
- **Optional Tools:**
  - [uv](https://github.com/astral-sh/uv) - Fast Python package installer (alternative to pip)
  - [just](https://github.com/casey/just) - Command runner for simplified workflows

### Setup Steps

1. **Fork and Clone:**

   ```bash
   # Fork the repository on GitHub first
   git clone https://github.com/YOUR_USERNAME/pyMM.git
   cd pyMM

   # Add upstream remote
   git remote add upstream https://github.com/mosh666/pyMM.git
   ```

2. **Initialize Environment (Using just):**

   The project uses `just` to automate setup. This command creates the virtual environment,
   installs dependencies (including dev tools), and compiles requirements.

   ```bash
   just install
   ```

3. **Install Git Hooks:**

   Set up pre-commit hooks to ensure code quality (linting, formatting, type checking) before commits.

   ```bash
   just setup-hooks
   ```

   **What pre-commit hooks do:**

   - 🔍 **Ruff linting** - Auto-fix code style issues
   - 🎨 **Ruff formatting** - Ensure consistent code formatting
   - 🔎 **MyPy** - Static type checking
   - 🔐 **Ruff Security** - Security vulnerability scanning (S-prefix rules)
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
   .venv\Scripts\activate  # Windows PowerShell
   # source .venv/bin/activate  # Linux/macOS
   ```

2. **Install Dependencies:**

   Option 1: Using pip (traditional):

   ```bash
   pip install -e ".[dev]"
   ```

   Option 2: Using uv (faster, modern alternative):

   ```bash
   pip install uv
   uv pip install -e ".[dev]"
   ```

3. **Install Pre-commit:**

   ```bash
   pip install pre-commit
   pre-commit install --install-hooks
   pre-commit install --hook-type pre-push
   ```

4. **Run Tests:**

   ```bash
   # Run full test suite with coverage
   pytest

   # Run specific test categories
   pytest tests/unit/          # Unit tests only
   pytest tests/integration/   # Integration tests only
   pytest tests/gui/           # GUI tests only
   ```

5. **Configure Git:**

   ```bash
   # Set your identity
   git config user.name "Your Name"
   git config user.email "your.email@example.com"

   # Set default branch
   git config init.defaultBranch main
   ```

6. **Environment Configuration (Optional):**

   By default, the application runs in "Portable Mode" locally (saving data to the app directory).
   To prevent cluttering your drive root or source folder during development, you can use:

   - **Windows (PowerShell):** `$env:PYMM_PORTABLE="false"`
   - **Action:** Keeps Logs and Projects in your local Drive Root (e.g., `D:/Projects`, `D:/Logs`)
     instead of the application folder, simulating a deployed environment or keeping source clean.

   ```powershell
   # Enable Dev Mode paths
   $env:PYMM_PORTABLE="false"
   python launcher.py
   ```

---

## Code Style

### Python Style Guide

We follow PEP 8 with these tools and standards:

- **Ruff**: Fast linting with auto-fix, formatting, and security checks (S-prefix rules)
- **MyPy**: Static type checking for type safety
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

### Automated Release System

pyMediaManager uses a fully automated release system powered by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) and GitHub Actions.
Releases are triggered automatically based on commit history and conventional commits.

#### Daily Beta Releases (Dev Branch)

- **Automatic:** Every day at midnight UTC, the system checks for new commits on the `dev` branch
- **Conditional:** A beta release is only created if there are commits since the last tag
- **Versioning:** Beta releases follow the format `v0.y.z-beta.N` (e.g., `v0.3.0-beta.1`)
- **Pre-v1.0.0:** All versions remain at `0.y.z` until the first stable `v1.0.0` release
- **GitHub Releases:** Each beta is published with a "Latest Beta" badge in the description

#### Manual Release Trigger

You can manually trigger a release via GitHub Actions:

1. Go to the [Actions tab](../../actions/workflows/semantic-release.yml)
2. Click "Run workflow"
3. Select the branch (`dev` or `main`)
4. Optionally enable "force" to release even without new commits
5. Click "Run workflow"

This is useful for immediate releases or testing the release pipeline.

#### Stable Releases (Main Branch)

- **Trigger:** Merging `dev` into `main` automatically creates a stable release
- **Versioning:** Stable releases follow `v0.y.z` format (or `v1.y.z` after first major release)
- **Changelog:** Automatically updated from conventional commits
- **Documentation:** Rebuilt and deployed with each release

### Building the Portable Distribution

You can build the portable Windows distribution locally without relying on CI:

```bash
# Using just (recommended)
just build

# Or using the python script directly
python scripts/build_manager.py --version 3.13
```

This will:

1. Download the embedded Python distribution.
2. Install all dependencies from `pyproject.toml`.
3. Configure the runtime environment.
4. Create a zip archive in the build directory.

### Branch Strategy

We follow a [Semantic Release](https://github.com/python-semantic-release/python-semantic-release) flow with automated versioning:

1. **Development (`dev` branch)**
   - All new features and fixes are merged here
   - Daily automated beta releases at midnight UTC (when changes exist)
   - Beta versions: `v0.y.z-beta.N` (e.g., `v0.3.0-beta.1`)
   - Tags created automatically based on conventional commits

2. **Stable (`main` branch)**
   - Stable releases created by merging `dev` into `main`
   - Triggers semantic version tag (e.g., `v0.3.0`)
   - Publishes official release with complete changelog
   - **Do not** manually tag releases

3. **Versioning Rules**
    - **Pre-v1.0.0:** All versions stay at `0.y.z` format
    - **`feat` commits:** Bump minor version (0.1.0 → 0.2.0)
    - **`fix` commits:** Bump patch version (0.1.0 → 0.1.1)
    - **Breaking changes:** Will bump minor version until v1.0.0 is released
    - **First major release (v1.0.0):** Manual decision by maintainers
    - Managed automatically via [python-semantic-release](https://python-semantic-release.readthedocs.io/)
    - Version calculated from [Conventional Commits](https://www.conventionalcommits.org/)
    - Uses [setuptools-scm](https://setuptools-scm.readthedocs.io/) for version from git tags

### Release Artifacts

Each release automatically includes:

- **Windows Portable ZIP** (Python 3.12, 3.13, 3.14)
- **Linux AppImage** (Python 3.12, 3.13, 3.14)
- **macOS DMG** (Python 3.12, 3.13, 3.14, Intel only - ARM64 via manual builds)
- **SHA256 Checksums** for all artifacts
- **Automated Changelog** from conventional commits
- **Updated Documentation** with version selector

### Release Notes

Release notes are automatically generated from conventional commits. Commits of type `chore`, `ci`,
`refactor`, `style`, `test`, and `docs` are excluded from the changelog to keep it focused on
user-facing changes.

## Commit Messages

We strictly enforce [Conventional Commits](https://www.conventionalcommits.org/) to automate
versioning and changelogs. Pre-commit hooks validate commit message format before allowing commits.

**Format:**

```text
<type>(<scope>): <subject>

<body>

<footer>
```

**Important:** The `<type>` determines the version bump!

### Types

- `feat`: New feature (**Minor** version bump in v0.x, e.g., 0.1.0 → 0.2.0)
- `fix`: Bug fix (**Patch** version bump, e.g., 0.1.0 → 0.1.1)
- `perf`: Performance improvements (**Patch**)
- `docs`: Documentation changes (No version bump, excluded from changelog)
- `style`: Code style changes (No version bump, excluded from changelog)
- `refactor`: Code refactoring (No version bump, excluded from changelog)
- `test`: Adding or updating tests (No version bump, excluded from changelog)
- `chore`: Maintenance tasks (No version bump, excluded from changelog)
- `ci`: CI/CD changes (No version bump, excluded from changelog)

### Breaking Changes

To indicate a breaking change (which will bump minor version in v0.x):

```text
feat(api)!: redesign plugin configuration API

BREAKING CHANGE: Plugin configuration now uses YAML instead of TOML.
Migration guide available in docs/migration-guide.md
```

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

**Total Tests:** 193 (all passing with 73% code coverage)

#### Unit Tests (~95 tests)

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

### Platform-Specific Test Markers

pyMM provides composable pytest markers for platform-specific tests. These markers use **OR logic**:
a test marked with multiple platform markers will run if the current platform matches **any** of them.

**Available Markers:**

| Marker | Platforms | Description |
| ------ | --------- | ----------- |
| `@pytest.mark.windows` | Windows | Windows-only tests |
| `@pytest.mark.linux` | Linux | Linux-only tests |
| `@pytest.mark.macos` | macOS | macOS-only tests |
| `@pytest.mark.unix` | Linux, macOS | Unix-like systems (Linux + macOS) |

**Example Usage:**

```python
import pytest

@pytest.mark.linux
def test_udev_installation():
    """This test only runs on Linux."""
    ...

@pytest.mark.windows
def test_registry_access():
    """This test only runs on Windows."""
    ...

@pytest.mark.unix
def test_posix_permissions():
    """This test runs on Linux and macOS."""
    ...

# Composable markers (OR logic) - runs on Linux OR macOS
@pytest.mark.linux
@pytest.mark.macos
def test_unix_like_behavior():
    """This test runs on both Linux and macOS."""
    ...
```

**How It Works:**

The markers are registered in `pyproject.toml` and auto-skip logic is implemented in
`tests/conftest.py` via the `pytest_collection_modifyitems` hook. Tests without any platform
markers run on all platforms.

**Migration from skipif:**

Replace the old pattern:

```python
# Old (deprecated)
@pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test")
def test_linux_feature():
    ...
```

With the new marker:

```python
# New
@pytest.mark.linux
def test_linux_feature():
    ...
```

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

- Scheduled daily scan (07:15 UTC) for frequent security metrics
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

# Run linting (includes security checks)
python -m ruff check .
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
- Follow 100% docstring coverage requirement for all public APIs
- Include detailed code examples in docstring Examples sections
- Use `.. versionadded:: dev` or `.. versionchanged:: dev` directives for unreleased features

## Internationalization (i18n)

### Overview

pyMediaManager documentation supports internationalization with German as the primary
translation target. We welcome community-driven translations.

For detailed information, see [docs/i18n-strategy.md](docs/i18n-strategy.md).

### Translation Workflow

#### 1. Extract Translatable Strings

After updating English documentation:

```bash
just docs-gettext
```

This generates `.pot` (Portable Object Template) files in `docs/_build/gettext/`.

#### 2. Update Translation Files

To update German translation files:

```bash
just docs-translate
```

This updates `.po` files in `docs/locales/de/LC_MESSAGES/` with new translatable strings.

#### 3. Translate Content

Edit `.po` files with your favorite editor:

- **Command line**: Any text editor (nano, vim, emacs)
- **GUI**: [Poedit](https://poedit.net/) - Free cross-platform translation editor
- **VS Code**: [Gettext extension](https://marketplace.visualstudio.com/items?itemName=mrorz.language-gettext)

Example translation entry:

```po
#: ../../user-guide.md:25
msgid "Installation"
msgstr "Installation"

#: ../../user-guide.md:27
msgid "To install pyMediaManager, follow these steps:"
msgstr "Um pyMediaManager zu installieren, folgen Sie diesen Schritten:"
```

#### 4. Build and Test Translations

Build German documentation locally:

```bash
just docs-build-de
```

Preview at `docs/_build/html-de/index.html`.

### Translation Guidelines

**DO:**

✅ Keep technical terms consistent (use glossary in [docs/i18n-strategy.md](docs/i18n-strategy.md))
✅ Preserve markup and formatting (e.g., `**bold**`, `[links](url)`)
✅ Maintain code examples exactly as-is (don't translate code)
✅ Translate user-facing strings, keep product names (PySide6, QFluentWidgets)
✅ Ask for clarification if meaning is unclear

**DON'T:**

❌ Translate URLs or file paths
❌ Modify Markdown/reStructuredText syntax
❌ Translate code snippets or variable names
❌ Change formatting or indentation
❌ Skip fuzzy entries (review and update them)

### Translation Priority

Focus on high-impact user-facing documentation first:

1. **High Priority**: README.md, docs/index.md, docs/user-guide.md, docs/troubleshooting.md
2. **Medium Priority**: docs/plugin-catalog.md, docs/migration-guide.md
3. **Low Priority**: docs/architecture.md, docs/api-reference.md (developer docs)

### Submitting Translations

1. **Create feature branch**:

   ```bash
   git checkout -b i18n/german-update
   ```

2. **Commit translations**:

   ```bash
   git add docs/locales/de/
   git commit -m "docs(i18n): update German translations for user guide"
   ```

3. **Push and create PR**:

   ```bash
   git push origin i18n/german-update
   ```

4. **PR description should include**:
   - Which files were translated
   - Translation completion percentage (if partial)
   - Any questions or unclear terms
   - Native speaker verification (if available)

### Translation Review

- PRs reviewed by native speakers when possible
- Automated checks verify `.po` file syntax
- CI builds translated documentation to verify rendering
- Community feedback welcome via comments

### Getting Help

- **Questions**: [GitHub Discussions - i18n](https://github.com/mosh666/pyMM/discussions)
- **Issues**: Report translation bugs or suggest improvements
- **Strategy**: Read [docs/i18n-strategy.md](docs/i18n-strategy.md) for complete details

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
