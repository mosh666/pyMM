# 🚀 Getting Started - Developer Guide

<!-- markdownlint-disable MD013 MD033 MD036 MD040 MD051 -->

> **Target Audience:** Developers contributing to pyMediaManager
> **Estimated Time:** 30-45 minutes for complete setup
> **Last Updated:** January 14, 2026
> **Comprehensive Guide:** See [DEVELOPER.md](https://github.com/mosh666/pyMM/blob/main/DEVELOPER.md) for complete developer documentation

---

## 📚 Quick Links

For comprehensive developer documentation including architecture diagrams, testing strategies, and CI/CD workflows, see [DEVELOPER.md](https://github.com/mosh666/pyMM/blob/main/DEVELOPER.md).

This guide focuses on initial setup. For advanced topics, refer to:

- [DEVELOPER.md](https://github.com/mosh666/pyMM/blob/main/DEVELOPER.md) - Complete developer guide with Mermaid diagrams
- **[Architecture](architecture.md)** - Technical design and patterns
- **[Plugin Development](plugin-development.md)** - Creating custom plugins
- **[API Reference](api-reference.md)** - API documentation

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
- [Troubleshooting](#dev-troubleshooting)

---

## 🎯 Introduction

Welcome to the pyMediaManager development team! This guide will help you set up your development environment and make your first contribution.

**For comprehensive developer documentation with architecture diagrams, testing strategies, and CI/CD workflows, see [DEVELOPER.md](https://github.com/mosh666/pyMM/blob/main/DEVELOPER.md).**

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

(prerequisites)=

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
     - Primary runtime (3.12, 3.14 also fully supported)
   * - **uv**
     - Latest
     - Required package manager (10-100x faster than pip, with lockfile support)
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

- **uv** (REQUIRED): Ultra-fast Python package installer (10-100x faster than pip) and project manager with lockfile support. Replaces pip/venv/virtualenv entirely.
- **just**: Command runner for common tasks (alternative to make, highly recommended)
- **GitHub CLI**: For creating PRs from command line
- **Windows Terminal**: Better terminal experience on Windows

> **Important:** pyMediaManager completed a full migration from pip to UV in January 2026. All development workflows now use UV exclusively. See {ref}`migrating-from-pip` for details.

### Knowledge Requirements

- ✅ Python 3.10+ syntax (type hints, dataclasses, async/await)
- ✅ Git basics (clone, branch, commit, push, PR)
- ✅ PySide6 fundamentals (signals/slots, QWidget hierarchy)
- ⚠️ Qt/QML knowledge helpful but not required
- ⚠️ Understanding of uv workflow (replaces pip/virtualenv)

---

(environment-setup)=

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

      # Verify uv is installed
      uv --version

.. tab:: Linux (Ubuntu/Debian)

   .. code-block:: bash

      # Add deadsnakes PPA for Python 3.13
      sudo add-apt-repository ppa:deadsnakes/ppa
      sudo apt update
      sudo apt install python3.13 python3.13-venv python3.13-dev

      # Verify installation
      python3.13 --version

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

**Why uv?**

- 🚀 10-100x faster than pip for dependency resolution
- 🔒 Lockfile support for reproducible builds (`uv.lock`)
- 📦 Built in Rust for speed and reliability
- 🎯 Drop-in replacement for pip with better UX

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Install uv
      powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

      # Add to PATH (automatically done by installer)
      # Verify installation
      uv --version
      # Expected: uv 0.5.x or later

.. tab:: Linux/macOS

   .. code-block:: bash

      # Install uv
      curl -LsSf https://astral.sh/uv/install.sh | sh

      # Add to PATH (installer provides instructions)
      # Usually: export PATH="$HOME/.local/bin:$PATH"

      # Verify installation
      uv --version
      # Expected: uv 0.5.x or later
```

### Step 4: Install Dependencies

**Modern Workflow (uv + just - Recommended):**

```bash
# Install just task runner (one-time setup)
# Windows: cargo install just  OR  scoop install just
# Linux: cargo install just  OR  apt install just
# macOS: brew install just

# Run automated setup (creates .venv, installs deps, sets up hooks)
just install

# Verify installation
just check  # Runs lint, type-check, and tests
```

**Manual uv Workflow:**

```{tabs}
.. tab:: uv sync (Recommended)

   .. code-block:: bash

      # Create virtual environment and install all dependencies
      # (including dev tools) from uv.lock
      uv sync --all-extras

      # This automatically:
      # - Creates .venv/ directory
      # - Installs all dependencies with exact versions from uv.lock
      # - Includes dev, docs, and test extras

      # Activate virtual environment
      # Windows:
      .venv\Scripts\activate
      # Linux/macOS:
      source .venv/bin/activate

      # Install pre-commit hooks
      uv run pre-commit install

.. tab:: uv pip (Alternative)

   .. code-block:: bash

      # Create virtual environment
      uv venv

      # Activate virtual environment
      # Windows:
      .venv\Scripts\activate
      # Linux/macOS:
      source .venv/bin/activate

      # Install in editable mode with dev dependencies
      uv pip install -e ".[dev]"

      # This installs:
      # - Core dependencies (PySide6, qfluentwidgets, pydantic, etc.)
      # - Dev tools (pytest, mypy, ruff, sphinx, etc.)
      # - All optional dependencies

      # Install pre-commit hooks
      uv run pre-commit install
```

### Understanding UV: `uv sync` vs `uv pip`

**UV provides two interfaces for package management:**

#### `uv sync` - Lockfile-Based (Recommended)

- **What it does**: Installs exact package versions from `uv.lock`
- **Use case**: Development setup, reproducible builds, CI/CD
- **Advantage**: Guarantees identical dependencies across all environments
- **Speed**: Very fast (cached, pre-resolved)

```bash
uv sync --all-extras     # Install all dependencies from lockfile
uv sync                  # Install only core dependencies
```

#### `uv pip` - Pip-Compatible Interface

- **What it is**: UV's pip-compatible command interface (NOT traditional pip)
- **Use case**: Ad-hoc package installation, upgrades, pip-like workflows
- **Advantage**: Familiar pip commands with UV speed (10-100x faster)
- **Important**: This is UV internally, not pip - you get UV's performance and features

```bash
uv pip install <package>        # Install package (UV's pip interface)
uv pip install --upgrade <pkg>  # Upgrade package
uv pip list                      # List installed packages
uv pip uninstall <package>      # Uninstall package
```

**Key Difference**:

- `uv sync`: Uses lockfile → reproducible, fast, recommended for projects
- `uv pip`: Resolves dependencies on-the-fly → flexible, familiar interface

**Both use UV's engine** - no traditional pip is involved. Commands like `uv pip install` provide pip familiarity while leveraging UV's Rust-based performance.

### Understanding uv Tool Management

pyMediaManager uses two uv commands for tool installation:

**`uv tool install <package>`** - Global, persistent installation

- Installs tools globally, available across all projects
- Tools persist across terminal sessions
- Used for: pre-commit (needs to be available system-wide)
- Example: `uv tool install pre-commit`

**`uv tool run <package>==<version>`** - Ephemeral, version-locked execution

- Runs tool without permanent installation
- Ensures specific version is used (critical for semantic-release)
- Example: `uv tool run python-semantic-release==9.8.8 version --print`

**Justfile Implementation:**

- `just pre-commit-install` → Uses `uv tool install pre-commit` (persistent)
- `just release-dry-run` → Uses `uv tool run python-semantic-release==9.8.8` (version-locked)

For more details, see: <https://docs.astral.sh/uv/guides/tools/>

**Verify Installation:**

```bash
# Check Python version
python --version

# Check uv version
uv --version

# Check installed packages
uv pip list
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

# Alternative: Use just for comprehensive check
just check
```

### Step 7: Explore Just Commands (Recommended)

pyMediaManager uses **Just** (v1.27+) as a modern task runner with 2026 best practices:

```bash
# View all available recipes organized by category
just --list

# View recipe categories
just --groups
```

**Recipe Groups:**

- `setup` - Environment setup and installation
- `testing` - Test execution (unit, integration, GUI, coverage)
- `quality` - Code quality (lint, format, type-check, docstrings)
- `git` - Git workflows (pre-commit, releases, config validation)
- `documentation` - Docs building, spelling, link checking
- `build` - Building portable distributions
- `plugins` - Plugin management (migration, rollback)
- `docker` - Docker CI/CD operations
- `maintenance` - Cleanup operations

**Key Features (2026):**

- 🎨 **Colored output** for better visual feedback
- 🛡️ **Safety confirmations** for destructive operations (`clean-all`, `ci-docker-clean`)
- 📝 **Enhanced help** with `[doc()]` attributes
- 🌍 **Cross-platform** with OS-specific variants (`open-docs`)
- 🔍 **Dependency validation** with clear error messages

**Most Common Commands:**

```bash
# Quality checks
just check          # Run comprehensive checks (format, lint, type-check, test)
just lint           # Run Ruff linter
just format         # Format code with Ruff
just type-check     # Run MyPy type checker

# Testing
just test           # Run all tests with coverage
just test-unit      # Run unit tests only
just test-cov       # Generate HTML coverage report

# Documentation
just docs           # Build multi-version Sphinx documentation
just open-docs      # Open docs in browser (OS-specific)
just docs-serve     # Serve docs locally on http://localhost:8000

# Setup
just install        # Install dependencies in dev mode
just pre-commit-install  # Install pre-commit hooks

# Cleanup (with safety confirmations)
just clean          # Clean build artifacts and cache
just clean-all      # Clean everything (requires confirmation)
```

**Example Workflow:**

```bash
# Make changes to code
vim app/services/my_service.py

# Format and check
just format
just lint
just type-check

# Run tests
just test-unit

# Comprehensive check before commit
just check

# If all passes, commit!
git commit -m "feat: add new service"

# Run quick tests
just test-unit

# Check type hints
just type-check
```

---

(development-workflow)=

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

(first-contribution)=

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

(debugging-guide)=

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

(testing-guide)=

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

(code-style-guide)=

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

(documentation)=

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

#### GitHub Token for Release Tag Filtering

The documentation build process filters tags to only create documentation for tags that have an associated GitHub release. This requires a `GITHUB_TOKEN` environment variable for both CI/CD and local builds.

**For Local Development:**

1. **Create a GitHub Personal Access Token:**
   - Visit: [https://github.com/settings/tokens/new?scopes=repo&description=pyMM-docs](https://github.com/settings/tokens/new?scopes=repo&description=pyMM-docs)
   - Select scope: `repo` (Full control of private repositories)
   - Click "Generate token" and copy it immediately

2. **Set the environment variable:**

   **PowerShell:**

   ```powershell
   # Temporary (current session only)
   $env:GITHUB_TOKEN = "your_token_here"

   # Persistent (current user)
   [System.Environment]::SetEnvironmentVariable('GITHUB_TOKEN', 'your_token_here', 'User')
   ```

   **Bash/Zsh (Linux/macOS):**

   ```bash
   # Temporary (current session only)
   export GITHUB_TOKEN="your_token_here"

   # Persistent (add to ~/.bashrc or ~/.zshrc)
   echo 'export GITHUB_TOKEN="your_token_here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Build documentation:**

   ```bash
   just docs
   ```

**What happens during the build:**

- The build script queries GitHub API for all releases (including pre-releases)
- Only tags with GitHub releases are included in the documentation build
- Branches (`main` and `dev`) are always built regardless of releases
- Without `GITHUB_TOKEN`, the build will fail with a clear error message

**For CI/CD:**

GitHub Actions automatically provides `GITHUB_TOKEN` via `secrets.GITHUB_TOKEN`, so no manual configuration is needed in the workflow.

### Writing Documentation

- Use **Markdown** for most documentation
- Use **RST** only when Sphinx directives are needed
- Add **Mermaid diagrams** for complex flows
- Include **code examples** with copy buttons
- Use **sphinx-tabs** for platform-specific content

---

(common-tasks)=

## 🛠️ Common Tasks

### Using Just Task Runner (Recommended)

pyMediaManager provides a comprehensive `justfile` with modern 2026 features:

```bash
# View all commands organized by category
just --list

# View recipe groups
just --groups

# Get help on specific recipe
just --show <recipe-name>
```

**Quick Reference:**

| Task | Command | Description |
| ---- | ------- | ----------- |
| **Full Check** | `just check` | Format, lint, type-check, test (with success box!) |
| **Format Code** | `just format` | Ruff code formatter |
| **Lint Code** | `just lint` | Ruff linter |
| **Type Check** | `just type-check` | MyPy strict mode |
| **Run Tests** | `just test` | All tests with coverage |
| **Build Docs** | `just docs` | Multi-version Sphinx docs |
| **Open Docs** | `just open-docs` | OS-specific browser opening |
| **Install Deps** | `just install` | Dev dependencies with progress |
| **Clean Build** | `just clean` | Remove artifacts |
| **Clean All** | `just clean-all` | Remove everything (requires confirmation ⚠️) |

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

## 📦 Building Distributions

### Windows Builds

#### Prerequisites

```powershell
# Install build dependencies
uv pip install --system jinja2 hatchling hatch-vcs

# For MSI generation (optional)
dotnet tool install --global wix
wix --version  # Should show 4.x
```

#### Building Portable ZIP

```powershell
# Build portable ZIP for Python 3.13 (recommended)
python scripts/build_windows.py --version 3.13 --format zip

# Build for specific architecture
python scripts/build_windows.py --version 3.13 --arch amd64
python scripts/build_windows.py --version 3.13 --arch arm64

# Build for other Python versions
python scripts/build_windows.py --version 3.12 --format zip
python scripts/build_windows.py --version 3.14 --format zip
```

**Output:** `pyMM-v{VERSION}-py3.13-win-amd64.zip`

#### Building MSI Installer

```powershell
# Build MSI installer (Python 3.13 only, recommended)
python scripts/build_windows.py --version 3.13 --format msi

# Build both ZIP and MSI
python scripts/build_windows.py --version 3.13 --format both
```

**Output:**

- `pyMM-v{VERSION}-py3.13-win-amd64.msi` (~130 MB)
- `pyMM-v{VERSION}-py3.13-win-amd64.msi.sha256` (checksum)

#### Testing MSI Locally

```powershell
# Install MSI
.\pyMM-v*.msi

# Install with logging (for debugging)
msiexec /i pyMM-v*.msi /l*v install.log

# Silent install (no UI)
msiexec /i pyMM-v*.msi /quiet

# Uninstall
msiexec /x pyMM-v*.msi
```

#### Build Process Details

The build script performs these steps:

1. **Downloads Python Embeddable Package** from python.org
2. **Configures Python environment** by modifying `._pth` file
3. **Installs dependencies** to `lib-py313/` directory using uv pip install
4. **Cleans up dependencies** to reduce size (~15 MB savings):
   - Removes `**/tests`, `**/__pycache__`, `**/docs` directories
   - Removes unnecessary metadata files
5. **Verifies critical imports** after cleanup:
   - Tests: `PySide6.QtWidgets`, `PySide6.QtCore`, `qfluentwidgets`, `pydantic`, `yaml`, `GitPython`
   - Ensures correct sys.path order (lib_dir → win32 → win32com) for pywin32 modules
   - Prevents accidental removal of required modules
6. **Generates version file** using hatch-vcs
7. **Creates ZIP archive** (for `--format zip` or `both`)
8. **Generates MSI installer** (for `--format msi` or `both`):
   - Renders WiX manifest from Jinja2 template
   - Compiles MSI with WiX Toolset v4
   - Calculates SHA256 checksum

### Linux Builds

```bash
# Build AppImage for x86_64
python scripts/build_linux_appimage.py --version 3.13

# Build for aarch64 (requires native ARM64 system)
python scripts/build_linux_appimage.py --version 3.13 --arch aarch64
```

**Output:** `pyMM-v{VERSION}-py3.13-x86_64.AppImage`

### macOS Builds

```bash
# Build .app bundle for x86_64 (Intel)
python scripts/build_macos.py --version 3.13 --arch x86_64

# Build for arm64 (Apple Silicon)
python scripts/build_macos.py --version 3.13 --arch arm64
```

**Output:** `pyMM-v{VERSION}-py3.13-macos-x86_64.dmg` (future)

### Platform-Agnostic Build Manager

```bash
# Automatically detects platform and routes to correct builder
python scripts/build_manager.py --version 3.13 --format both
```

### CI/CD Build Matrix

GitHub Actions automatically builds (following 2026 best practices):

**Release Builds (Pinned Runners):**

- **Windows** (`windows-2022`): Python 3.12, 3.13, 3.14 × amd64
  - ZIP for all versions
  - MSI for Python 3.13 only (recommended)
- **Linux** (`ubuntu-22.04`): Python 3.12, 3.13, 3.14 × x86_64
  - AppImage for all versions
- **macOS** (`macos-13`/`macos-14`): Python 3.12, 3.13, 3.14 × (x86_64 + arm64)
  - DMG for all versions

**Total:** 15+ build configurations per release (3 Python versions × 5 platform variants)

**Optimizations:**

- Pinned runner versions ensure reproducible builds
- Artifact cleanup: 7-day retention (automated)
- Concurrency control: Cancels redundant builds on rapid pushes
- Supply chain security: Artifact attestation for all builds

---

(dev-troubleshooting)=

## 🔧 Troubleshooting

### Common Issues

#### Import Errors

```bash
# Ensure package is installed in editable mode
uv pip install -e . --no-deps

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
uv pip uninstall PySide6 qfluentwidgets
uv pip install PySide6>=6.6.0 qfluentwidgets>=1.5.0

# Set Qt environment variables
export QT_DEBUG_PLUGINS=1
```

### Getting Help

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
4. 🧪 Review {ref}`testing-strategy`
5. 🎯 Pick your first issue and start coding!

**Resources:**

- [API Reference](api-reference.md)
- [Installation](installation.md)
- [Getting Started](getting-started.md)
- [Features](features.md)
- [Configuration](configuration.md)
- [Contributing Guidelines](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md)
- [Code of Conduct](https://github.com/mosh666/pyMM/blob/main/.github/CODE_OF_CONDUCT.md)

Happy coding! 🚀
