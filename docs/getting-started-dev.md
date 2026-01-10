# 🚀 Getting Started - Developer Guide

<!-- markdownlint-disable MD013 MD033 MD036 MD040 MD051 -->

> **Target Audience:** Developers contributing to pyMediaManager
> **Estimated Time:** 30-45 minutes for complete setup
> **Last Updated:** January 10, 2026

---

## 📚 Table of Contents

- [Introduction](#introduction)
- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Development Workflow](#development-workflow)
- [First Contribution](#first-contribution)
- [Debugging Guide](#debugging-guide)
- [Testing Guide](#testing-guide)
- [Code Style Guide](#code-style-guide)
- [Documentation](#documentation)
- [Common Tasks](#common-tasks)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Introduction

Welcome to the pyMediaManager development team! This guide will help you set up your development environment and make your first contribution.

### What You'll Learn

- ✅ Setting up Python 3.13 development environment
- ✅ Installing dependencies with uv (fast) or pip (traditional)
- ✅ Configuring pre-commit hooks for code quality
- ✅ Running tests and type checking
- ✅ Creating your first pull request
- ✅ Debugging with VS Code
- ✅ Working with the plugin system

### Development Philosophy

- 🎯 **Quality First**: 100% docstring coverage, strict type checking
- 🔒 **Security Conscious**: No arbitrary code execution, SHA-256 verification
- 📝 **Documentation-Driven**: Code without docs doesn't exist
- 🧪 **Test-Driven**: All features must have tests
- 🌍 **Cross-Platform**: Windows, Linux, macOS support required

---

## 📋 Prerequisites

### Required Software

```{eval-rst}
.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Software
     - Version
     - Purpose
   * - **Python**
     - 3.13.x recommended
     - Primary runtime (3.12, 3.14 also supported)
   * - **Git**
     - 2.40+
     - Version control and collaboration
   * - **VS Code**
     - Latest
     - Recommended IDE (or PyCharm)
   * - **Node.js**
     - 18+ (optional)
     - For pre-commit hooks (markdownlint)
```

### Recommended Tools

- **uv**: Ultra-fast Python package installer (alternative to pip)
- **just**: Command runner for common tasks (alternative to make)
- **GitHub CLI**: For creating PRs from command line
- **Windows Terminal**: Better terminal experience on Windows

### Knowledge Requirements

- ✅ Python 3.10+ syntax (type hints, dataclasses, async/await)
- ✅ Git basics (clone, branch, commit, push, PR)
- ✅ PySide6 fundamentals (signals/slots, QWidget hierarchy)
- ⚠️ Qt/QML knowledge helpful but not required

---

## 🛠️ Environment Setup

### Step 1: Fork and Clone Repository

```{tabs}
.. tab:: GitHub CLI (Recommended)

   .. code-block:: bash

      # Fork and clone in one command
      gh repo fork mosh666/pyMM --clone

      # Navigate to repository
      cd pyMM

      # Add upstream remote
      git remote add upstream https://github.com/mosh666/pyMM.git

.. tab:: Git Manual

   .. code-block:: bash

      # Fork repository on GitHub web interface first
      # Then clone your fork
      git clone https://github.com/YOUR_USERNAME/pyMM.git
      cd pyMM

      # Add upstream remote
      git remote add upstream https://github.com/mosh666/pyMM.git
      git fetch upstream

.. tab:: SSH (Advanced)

   .. code-block:: bash

      # Requires SSH key configured on GitHub
      git clone git@github.com:YOUR_USERNAME/pyMM.git
      cd pyMM

      git remote add upstream git@github.com:mosh666/pyMM.git
      git fetch upstream
```

### Step 2: Install Python 3.13

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Using winget (Windows Package Manager)
      winget install Python.Python.3.13

      # Or download from python.org
      # https://www.python.org/downloads/windows/

      # Verify installation
      python --version
      # Expected: Python 3.13.x

      # Verify pip
      python -m pip --version

.. tab:: Linux (Ubuntu/Debian)

   .. code-block:: bash

      # Add deadsnakes PPA for Python 3.13
      sudo add-apt-repository ppa:deadsnakes/ppa
      sudo apt update
      sudo apt install python3.13 python3.13-venv python3.13-dev

      # Verify installation
      python3.13 --version

      # Install pip if not included
      curl -sS https://bootstrap.pypa.io/get-pip.py | python3.13

.. tab:: macOS

   .. code-block:: bash

      # Using Homebrew
      brew install python@3.13

      # Verify installation
      python3.13 --version

      # Create symlink (optional)
      ln -sf /opt/homebrew/bin/python3.13 /usr/local/bin/python
```

### Step 3: Install uv (Fast Package Manager)

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Install uv
      powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

      # Add to PATH (automatically done by installer)
      # Verify installation
      uv --version

.. tab:: Linux/macOS

   .. code-block:: bash

      # Install uv
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Add to PATH (add to ~/.bashrc or ~/.zshrc)
      export PATH="$HOME/.cargo/bin:$PATH"

      # Verify installation
      uv --version
```

### Step 4: Install Dependencies

```{tabs}
.. tab:: uv (Fast - Recommended)

   .. code-block:: bash

      # Install in editable mode with dev dependencies
      uv pip install -e ".[dev]"

      # This installs:
      # - Core dependencies (PySide6, qfluentwidgets, pydantic, etc.)
      # - Dev tools (pytest, mypy, ruff, sphinx, etc.)
      # - All optional dependencies

.. tab:: pip (Traditional)

   .. code-block:: bash

      # Create virtual environment (recommended)
      python -m venv .venv

      # Activate virtual environment
      # Windows:
      .venv\Scripts\activate
      # Linux/macOS:
      source .venv/bin/activate

      # Install dependencies
      pip install -e ".[dev]"

.. tab:: just (Automated)

   .. code-block:: bash

      # Install just command runner first
      # Windows: scoop install just
      # Linux: cargo install just
      # macOS: brew install just

      # Run setup task
      just setup
```

### Step 5: Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# Test hooks on all files (first run is slow)
pre-commit run --all-files

# Expected output:
# ✅ Ruff Linter (auto-fix)..................Passed
# ✅ Ruff Formatter..........................Passed
# ✅ Trim Trailing Whitespace................Passed
# ✅ Check YAML Syntax.......................Passed
# ... (all hooks should pass)
```

**What pre-commit hooks do:**

- 🔍 **Ruff**: Lint and format Python code
- 📝 **doc8**: Validate markdown/RST documentation
- 🎯 **interrogate**: Enforce 100% docstring coverage
- 🔬 **mypy**: Static type checking
- 🧪 **pytest**: Run unit tests (pre-push only)

### Step 6: Verify Installation

```bash
# Run verification script
python -c "
from app.core.platform import get_platform_info
from app._version import __version__

info = get_platform_info()
print(f'✅ pyMediaManager v{__version__}')
print(f'✅ Platform: {info.system} {info.release}')
print(f'✅ Python: {info.python_version}')
print(f'✅ Installation successful!')
"

# Run quick tests
just test-unit

# Check type hints
just type-check
```

---

## 🔄 Development Workflow

### Daily Development Cycle

```{mermaid}
graph LR
    A[Pull Latest] --> B[Create Branch]
    B --> C[Make Changes]
    C --> D[Run Tests]
    D --> E{Tests Pass?}
    E -->|No| C
    E -->|Yes| F[Commit]
    F --> G[Push]
    G --> H[Create PR]
```

### 1. Sync with Upstream

```bash
# Fetch latest changes from upstream
git fetch upstream

# Update your main branch
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

### 2. Create Feature Branch

```bash
# Create descriptive branch name
git checkout -b feature/add-plugin-validation
# Or for fixes:
# git checkout -b fix/storage-detection-bug

# Verify branch
git branch
```

**Branch Naming Convention:**

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions
- `chore/` - Maintenance tasks

### 3. Make Changes

```bash
# Edit files in your favorite editor
code .  # VS Code

# Check what changed
git status
git diff
```

### 4. Test Your Changes

```bash
# Run unit tests
just test-unit

# Run integration tests
just test-integration

# Run all tests with coverage
just test

# Type check
just type-check

# Lint code
just lint

# Format code
just format
```

### 5. Commit Changes

```bash
# Stage changes
git add app/services/new_service.py tests/test_new_service.py

# Commit with conventional commit message
git commit -m "feat(services): add new service for feature X

- Implement ServiceX with async support
- Add comprehensive unit tests
- Update documentation

Closes #123"
```

**Conventional Commit Format:**

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, missing semicolons, etc.)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Performance improvement
- `test`: Adding missing tests
- `chore`: Maintenance tasks

### 6. Push and Create PR

```{tabs}
.. tab:: GitHub CLI

   .. code-block:: bash

      # Push branch
      git push -u origin feature/add-plugin-validation

      # Create PR
      gh pr create --title "feat(plugins): add plugin validation" \
                   --body "Implements plugin validation with schema checks" \
                   --base dev

.. tab:: Manual

   .. code-block:: bash

      # Push branch
      git push -u origin feature/add-plugin-validation

      # Go to GitHub web interface
      # https://github.com/YOUR_USERNAME/pyMM
      # Click "Compare & pull request"
```

---

## 🎯 First Contribution

### Choose a Good First Issue

1. Visit [GitHub Issues](https://github.com/mosh666/pyMM/issues)
2. Filter by label: `good-first-issue`
3. Read issue description and requirements
4. Comment: "I'd like to work on this issue"
5. Wait for assignment (usually < 24 hours)

### Example: Add Plugin Validation

Let's walk through a complete contribution:

#### 1. Create Branch

```bash
git checkout dev
git pull upstream dev
git checkout -b feat/validate-plugin-manifest
```

#### 2. Write Code

```python
# app/plugins/validator.py
"""Plugin manifest validation utilities."""

from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.plugins.models import PluginManifest


def validate_manifest(manifest_path: Path) -> tuple[bool, str]:
    """
    Validate plugin manifest file.

    Args:
        manifest_path: Path to plugin.yaml file

    Returns:
        Tuple of (is_valid, error_message)

    Examples:
        >>> validate_manifest(Path("plugins/git/plugin.yaml"))
        (True, "")
        >>> validate_manifest(Path("plugins/invalid/plugin.yaml"))
        (False, "Invalid checksum format")
    """
    try:
        # Implementation here
        manifest = PluginManifest.from_yaml(manifest_path)
        return True, ""
    except ValidationError as e:
        return False, str(e)
```

#### 3. Write Tests

```python
# tests/test_plugin_validator.py
"""Tests for plugin manifest validation."""

import pytest
from pathlib import Path

from app.plugins.validator import validate_manifest


def test_validate_valid_manifest(tmp_path: Path) -> None:
    """Test validation of valid manifest."""
    manifest = tmp_path / "plugin.yaml"
    manifest.write_text("""
name: TestPlugin
version: 1.0.0
# ... rest of valid manifest
""")

    is_valid, error = validate_manifest(manifest)
    assert is_valid
    assert error == ""


def test_validate_invalid_checksum(tmp_path: Path) -> None:
    """Test validation fails for invalid checksum."""
    manifest = tmp_path / "plugin.yaml"
    manifest.write_text("""
name: TestPlugin
version: 1.0.0
source:
  checksum_sha256: "invalid"
""")

    is_valid, error = validate_manifest(manifest)
    assert not is_valid
    assert "checksum" in error.lower()
```

#### 4. Update Documentation

```markdown
<!-- docs/plugin-development.md -->

## Validation

All plugin manifests are validated using Pydantic schemas:

\```python
from app.plugins.validator import validate_manifest

is_valid, error = validate_manifest(Path("plugins/mytool/plugin.yaml"))
if not is_valid:
    print(f"Validation failed: {error}")
\```
```

#### 5. Run Quality Checks

```bash
# Format code
just format

# Run linter
just lint

# Type check
just type-check

# Run tests
just test

# Update docs
just docs
```

#### 6. Commit and Push

```bash
git add app/plugins/validator.py tests/test_plugin_validator.py docs/plugin-development.md
git commit -m "feat(plugins): add manifest validation

- Implement validate_manifest() function
- Add comprehensive unit tests
- Update plugin development docs

Closes #45"

git push -u origin feat/validate-plugin-manifest
```

#### 7. Create Pull Request

```bash
gh pr create --title "feat(plugins): add manifest validation" \
             --body "Implements plugin manifest validation with Pydantic schemas.

## Changes
- Added `validator.py` module
- Added comprehensive tests
- Updated documentation

## Testing
- ✅ All unit tests pass
- ✅ Type checking passes
- ✅ Documentation builds

Closes #45" \
             --base dev
```

---

## 🐛 Debugging Guide

### VS Code Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "pyMM: Launch Application",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/launcher.py",
      "console": "integratedTerminal",
      "justMyCode": false,
      "env": {
        "PYTHONPATH": "${workspaceFolder}",
        "PYMM_DEBUG": "1"
      }
    },
    {
      "name": "pyMM: Run Unit Tests",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "tests/",
        "-v",
        "--tb=short"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "pyMM: Debug Current Test",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": [
        "${file}",
        "-v",
        "--tb=short"
      ],
      "console": "integratedTerminal",
      "justMyCode": false
    },
    {
      "name": "pyMM: Type Check",
      "type": "python",
      "request": "launch",
      "module": "mypy",
      "args": [
        "app/"
      ],
      "console": "integratedTerminal"
    }
  ]
}
```

### Logging Levels

Configure logging in your development environment:

```python
# Set in config/app.yaml for development
logging:
  level: DEBUG  # CRITICAL, ERROR, WARNING, INFO, DEBUG
  console_enabled: true
  file_enabled: true
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

**Log Levels Usage:**

- `DEBUG`: Detailed diagnostic information
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical error messages for program-stopping issues

### Breakpoint Best Practices

```python
# Method 1: Python debugger (works everywhere)
import pdb; pdb.set_trace()

# Method 2: VS Code breakpoint (F9 in editor)
# Click in the gutter next to line number

# Method 3: Conditional breakpoint
# Right-click breakpoint → Edit Breakpoint → Add condition
# Example condition: len(items) > 10

# Method 4: Logpoint (doesn't pause execution)
# Right-click in gutter → Add Logpoint
# Example: "Processing {item_count} items"
```

### Common Debugging Scenarios

#### Debugging Async Code

```python
import asyncio

async def debug_async_function():
    """Debug async functions step-by-step."""
    print("Starting async operation")
    await asyncio.sleep(1)  # Set breakpoint here
    result = await fetch_data()  # Step into with F11
    print(f"Result: {result}")

# Run with debugger attached
asyncio.run(debug_async_function())
```

#### Debugging Qt Signals

```python
from PySide6.QtCore import QObject, Signal

class DebugSignals(QObject):
    my_signal = Signal(str)

    def __init__(self):
        super().__init__()
        # Connect to debug slot
        self.my_signal.connect(self.on_signal_debug)

    def on_signal_debug(self, data: str) -> None:
        """Debug callback for signal emissions."""
        print(f"Signal emitted with data: {data}")
        # Set breakpoint here to inspect signal data
        pass
```

#### Debugging Plugin Installation

```python
# Enable verbose logging
import logging
logging.getLogger("app.plugins").setLevel(logging.DEBUG)

# Set breakpoint in PluginManager
from app.plugins.plugin_manager import PluginManager

pm = PluginManager(plugins_dir, manifests_dir)
# Breakpoint on next line to step through installation
await pm.install_plugin("Git")
```

---

## 🧪 Testing Guide

### Running Tests

```bash
# Run all tests
just test

# Run unit tests only (fast)
just test-unit

# Run integration tests only
just test-integration

# Run specific test file
pytest tests/test_plugin_manager.py -v

# Run specific test function
pytest tests/test_plugin_manager.py::test_discover_plugins -v

# Run tests matching pattern
pytest tests/ -k "plugin" -v

# Run with coverage report
pytest --cov=app --cov-report=html tests/

# View coverage report
# Open htmlcov/index.html in browser
```

### Writing Tests

```python
"""Example test module structure."""

import pytest
from pathlib import Path
from app.services.example_service import ExampleService


@pytest.fixture
def example_service(tmp_path: Path) -> ExampleService:
    """Fixture providing ExampleService instance."""
    return ExampleService(data_dir=tmp_path)


def test_service_initialization(example_service: ExampleService) -> None:
    """Test service initializes correctly."""
    assert example_service is not None
    assert example_service.data_dir.exists()


def test_service_method(example_service: ExampleService) -> None:
    """Test specific service method."""
    result = example_service.do_something("test")
    assert result == "expected"


@pytest.mark.asyncio
async def test_async_method(example_service: ExampleService) -> None:
    """Test async service method."""
    result = await example_service.async_method()
    assert result is not None
```

### Test Coverage Goals

- ✅ **Minimum Coverage**: 70% (enforced in CI)
- 🎯 **Target Coverage**: 80%+ for new code
- 📊 **Current Coverage**: 73% (193 tests)

---

## 📝 Code Style Guide

### Python Style

We follow **PEP 8** with some modifications enforced by Ruff:

```python
# ✅ Good
def calculate_total(items: list[Item], tax_rate: float = 0.1) -> float:
    """
    Calculate total price including tax.

    Args:
        items: List of items to calculate
        tax_rate: Tax rate as decimal (default: 0.1 = 10%)

    Returns:
        Total price with tax applied

    Examples:
        >>> calculate_total([Item(price=100)], tax_rate=0.1)
        110.0
    """
    subtotal = sum(item.price for item in items)
    return subtotal * (1 + tax_rate)


# ❌ Bad - missing docstring, no type hints
def calc(items, rate=0.1):
    t = sum(i.price for i in items)
    return t * (1 + rate)
```

### Type Hints

```python
# Always use modern type hints (Python 3.10+)
from typing import Any

# ✅ Good - Python 3.10+ syntax
def process_data(
    data: list[dict[str, Any]],
    options: dict[str, int] | None = None
) -> tuple[bool, str]:
    """Process data with options."""
    ...

# ❌ Bad - old syntax
from typing import List, Dict, Optional, Tuple

def process_data(
    data: List[Dict[str, Any]],
    options: Optional[Dict[str, int]] = None
) -> Tuple[bool, str]:
    """Process data with options."""
    ...
```

### Docstrings

We use **Google-style** docstrings with 100% coverage requirement:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Short one-line summary of function (imperative mood).

    Longer description providing more context about what the function does,
    when to use it, and any important details.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter (default: 0)

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        IOError: When file cannot be read

    Examples:
        >>> example_function("test", 42)
        True
        >>> example_function("")
        ValueError: param1 cannot be empty

    Note:
        Important notes or warnings about function behavior

    See Also:
        - :func:`related_function`: Related functionality
        - :class:`RelatedClass`: Related class
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    # Implementation
    return True
```

---

## 📚 Documentation

### Building Documentation Locally

```bash
# Build HTML documentation
just docs

# Build with specific branch
sphinx-build -b html docs docs/_build/html

# View locally
# Open docs/_build/html/index.html in browser

# Check for broken links
sphinx-build -b linkcheck docs docs/_build/linkcheck

# Run spell checker
sphinx-build -b spelling docs docs/_build/spelling
```

### Writing Documentation

- Use **Markdown** for most documentation
- Use **RST** only when Sphinx directives are needed
- Add **Mermaid diagrams** for complex flows
- Include **code examples** with copy buttons
- Use **sphinx-tabs** for platform-specific content

---

## 🛠️ Common Tasks

### Update Dependencies

```bash
# Update all dependencies
uv pip install -U -e ".[dev]"

# Update specific package
uv pip install -U PySide6

# Update pre-commit hooks
pre-commit autoupdate
```

### Run Code Formatters

```bash
# Format with ruff
ruff format .

# Or use just
just format
```

### Generate Plugin Checksum

```{tabs}
.. tab:: Windows (PowerShell)

   .. code-block:: powershell

      # SHA-256 checksum
      Get-FileHash -Algorithm SHA256 plugin-download.zip | Select-Object -ExpandProperty Hash

.. tab:: Linux/macOS

   .. code-block:: bash

      # SHA-256 checksum
      sha256sum plugin-download.zip

      # Or on macOS
      shasum -a 256 plugin-download.zip
```

---

## 🔧 Troubleshooting

### Common Issues

#### Import Errors

```bash
# Ensure package is installed in editable mode
pip install -e .

# Verify PYTHONPATH
python -c "import sys; print('\n'.join(sys.path))"
```

#### Pre-commit Failures

```bash
# Skip hooks temporarily (not recommended)
git commit --no-verify

# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean
```

#### Qt/PySide6 Issues

```bash
# Reinstall PySide6
pip uninstall PySide6 qfluentwidgets
pip install PySide6>=6.6.0 qfluentwidgets>=1.5.0

# Set Qt environment variables
export QT_DEBUG_PLUGINS=1
```

### Getting Help

- 💬 **GitHub Discussions**: Ask questions, share ideas
- 🐛 **GitHub Issues**: Report bugs, request features
- 📧 **Email**: <mosh666@github.com>
- 📖 **Documentation**: <https://mosh666.github.io/pyMM>

---

## 🎉 Next Steps

Congratulations! You're now ready to contribute to pyMediaManager.

**Recommended Learning Path:**

1. ✅ Complete environment setup (you are here!)
2. 📖 Read [Architecture Documentation](architecture.md)
3. 🔌 Explore [Plugin Development Guide](plugin-development.md)
4. 🧪 Review [Testing Strategy](architecture.md#testing-strategy)
5. 🎯 Pick your first issue and start coding!

**Resources:**

- [API Reference](api-reference.md)
- [User Guide](user-guide.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Code of Conduct](../CODE_OF_CONDUCT.md)

Happy coding! 🚀
