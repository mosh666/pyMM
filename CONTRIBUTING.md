# Contributing to pyMediaManager

Thank you for your interest in contributing to pyMediaManager! This document provides guidelines and instructions for contributing.

> **See also:** [CHANGELOG.md](CHANGELOG.md) for recent changes and version history

## Development Setup

### Prerequisites
- Python 3.12 or 3.13
- Git
- Windows OS (for now - Linux/macOS support planned)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mosh666/pyMM.git
   cd pyMM
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Run tests**:
   ```bash
   pytest
   ```

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

- **ruff** - Linter with auto-fix (replaces flake8, isort, and more)
- **ruff-format** - Code formatter (replaces Black)
- **trailing-whitespace** - Remove trailing whitespace
- **end-of-file-fixer** - Ensure files end with newline
- **check-yaml** - Validate YAML files
- **check-toml** - Validate TOML files
- **check-merge-conflict** - Check for merge conflict markers
- **mixed-line-ending** - Ensure consistent line endings

**Install hooks** (one-time setup):
```bash
pre-commit install
```

**Run manually** (optional):
```bash
pre-commit run --all-files
```

The hooks run automatically on `git commit`. If any hook fails, the commit will be blocked until you fix the issues.

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

1.  **Development (`dev` branch)**:
    *   All new features and fixes are merged here.
    *   Pushes to `dev` automatically trigger a **Beta Release** (tagged `latest-beta`).
    *   These releases are marked as "Pre-release" on GitHub.

2.  **Stable (`main` branch)**:
    *   Stable releases are created by pushing a semantic version tag (e.g., `v1.0.0`) to `main`.
    *   **Do not** push directly to `main`. Use Pull Requests from `dev` to `main`.
    *   The workflow will automatically build and publish the release.

3.  **Versioning**:
    *   We use [Semantic Versioning](https://semver.org/).
    *   Format: `vX.Y.Z` (Stable) or `vX.Y.Z-alpha.N` / `vX.Y.Z-beta.N` (Prerelease).
    *   `setuptools_scm` automatically handles versioning based on git tags.

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
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
```
feat(plugins): add support for custom plugin loaders

Implement plugin loader interface to allow custom plugin types
beyond the standard SimplePluginImplementation.

Closes #123
```

```
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

### PR Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (Black)
- [ ] Linting passes (Ruff)
- [ ] All tests pass
- [ ] Commit messages follow conventions

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

- **Discussions**: https://github.com/mosh666/pyMM/discussions
- **Issues**: https://github.com/mosh666/pyMM/issues

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
