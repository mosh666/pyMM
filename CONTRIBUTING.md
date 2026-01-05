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

2. **Create Virtual Environment:**

   ```bash
   # Create environment
   python -m venv venv

   # Activate (Windows)
   venv\Scripts\activate

   # Activate (Linux/macOS)
   source venv/bin/activate
   ```

3. **Install Dependencies:**

   ```bash
   # Install in editable mode with dev dependencies
   pip install -e ".[dev]"

   # Verify installation
   python -c "import app; print(app.__version__)"
   ```

4. **Install Pre-commit Hooks:**

   ```bash
   # Automatic setup (recommended)
   # Windows PowerShell:
   .\scripts\setup-git-hooks.ps1

   # Linux/macOS/Git Bash:
   bash scripts/setup-git-hooks.sh

   # Manual setup:
   pip install pre-commit
   pre-commit install --install-hooks
   pre-commit install --hook-type pre-push

   # Test hooks
   pre-commit run --all-files
   ```

   **What pre-commit hooks do:**

   - 🔍 **Ruff linting** - Auto-fix code style issues
   - 🎨 **Code formatting** - Ensure consistent formatting
   - ✅ **File checks** - Trailing whitespace, YAML/TOML syntax
   - 🔐 **Security** - Detect private keys
   - 📝 **Markdown linting** - Documentation quality
   - 🧪 **Unit tests** - Run fast tests on commit
   - 🚀 **Full test suite** - Run all tests before push
   - 🔎 **Type checking** - MyPy validation

5. **Run Tests:**

   ```bash
   # Run full test suite (193 tests)
   pytest

   # Run with coverage (73% overall)
   pytest --cov=app --cov-report=html

   # View coverage report
   # Open htmlcov/index.html in browser
   ```

6. **Configure Git:**

   ```bash
   # Set your identity
   git config user.name "Your Name"
   git config user.email "your.email@example.com"

   # Set default branch
   git config init.defaultBranch main
   ```

---

## Code Style

### Python Style Guide

We follow PEP 8 with these tools:

- **Ruff**: Fast linting with auto-fix and formatting (replaces Black, flake8, isort)
- **MyPy**: Static type checking
- **Modern Type Hints**: Use Python 3.12+ native types (`list`, `dict`, `tuple`) instead of
  `typing.List`, `typing.Dict`, etc.

### Running Code Quality Tools

```bash
# Format and fix code
ruff check --fix app/ tests/
ruff format app/ tests/

# Type check
mypy app/
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

We follow a branch-based release flow:

1. **Development (`dev` branch)**
   - All new features and fixes are merged here.
   - Pushes to `dev` automatically trigger a **Beta Release** (tagged `latest-beta`).
   - These releases are marked as "Pre-release" on GitHub.

2. **Stable (`main` branch)**
   - Stable releases are created by pushing a semantic version tag (e.g., `v1.0.0`) to `main`.
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

### Unit Tests

- Located in `tests/unit/`
- Test individual functions/methods in isolation
- Use mocks for external dependencies
- Aim for 70%+ coverage

Example:

```python
def test_file_system_service_resolve_path(service, app_root):
    """Test resolving relative paths."""
    rel_path = Path("test/file.txt")
    resolved = service.resolve_path(rel_path)
    assert resolved == app_root / "test" / "file.txt"
```

### GUI Tests

- Located in `tests/gui/`
- Use pytest-qt for widget testing
- Test user interactions and signals

Example:

```python
def test_button_click(qtbot):
    """Test button click handling."""
    widget = MyWidget()
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

    assert widget.clicked is True
```

### Running Specific Tests

```bash
# Run unit tests only
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_config_service.py

# Run specific test
pytest tests/unit/test_config_service.py::TestConfigService::test_load_default_config

# Run with coverage
pytest --cov=app --cov-report=html
```

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

1. Create service file in `app/core/services/`:

   ```python
   # app/core/services/my_service.py
   class MyService:
       def __init__(self):
           pass

       def do_something(self):
           pass
   ```

2. Create tests in `tests/unit/`:

   ```python
   # tests/unit/test_my_service.py
   def test_my_service():
       service = MyService()
       assert service.do_something() == expected
   ```

3. Register in main application
4. Update documentation

### Adding a New Plugin

1. Create plugin manifest:

   ```yaml
   # plugins/myplugin/plugin.yaml
   name: MyPlugin
   version: "1.0.0"
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
