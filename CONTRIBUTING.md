# Contributing to pyMediaManager

> **Last Updated:** 2026-01-17 21:41 UTC

Thank you for your interest in contributing to pyMediaManager! This guide provides comprehensive
instructions for setting up your development environment, writing code, testing, and submitting
contributions.

> **Quick Start:** See [DEVELOPER.md](DEVELOPER.md) for comprehensive developer documentation with architecture
> diagrams, testing strategies, and CI/CD workflows.
> **See also:** [CHANGELOG.md](CHANGELOG.md) | [Architecture Guide](docs/architecture.md) |
> [Installation](docs/installation.md) | [Getting Started](docs/getting-started.md) |
> [Developer Getting Started](docs/getting-started-dev.md) |
> [Plugin Development Guide](docs/plugin-development.md) | [Semantic Release](docs/semantic-release.md)

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

> **New Contributors:** For a comprehensive developer onboarding guide with architecture diagrams,
> Mermaid flowcharts, testing strategies, and CI/CD workflows, see [DEVELOPER.md](DEVELOPER.md).
>
> **Platform-Specific Instructions:** For detailed platform-specific instructions, VS Code debugging
> configurations, and your first contribution walkthrough, see [Getting Started for Developers](docs/getting-started-dev.md).
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

- **Python:** 3.12, 3.13, or 3.14 (Python 3.13 recommended; 3.14 fully supported since October 2024)
- **Git:** 2.30+ (latest version recommended)
- **OS:** Windows 10/11, Linux, or macOS
- **IDE:** VS Code recommended with Python, Ruff, and MyPy extensions
- **Required Tools:**
  - [uv](https://github.com/astral-sh/uv) - Modern Python package manager (10-100x faster than pip, with lockfile support)
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

2. **Install uv (Required):**

   **uv** is the **only** package manager used by this project. The project completed a full migration from pip/setuptools
   to a UV-only ecosystem in January 2026. It's 10-100x faster than pip and provides lockfile support (`uv.lock`) for
   reproducible builds. All portable distributions bundle a UV executable that's automatically added to PATH by launcher.py.

   ```bash
   # Windows (PowerShell)
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

   # Linux/macOS
   curl -lsSf https://astral.sh/uv/install.sh | sh
   ```

   After installation, verify uv is available:

   ```bash
   uv --version
   ```

   **Note:** Portable distributions include a bundled UV executable that's automatically added to PATH by launcher.py,
   eliminating the need for manual UV installation in portable mode.

3. **Initialize Environment (Using just):**

   The project uses `just` to automate setup. This command creates the virtual environment,
   installs dependencies (including dev tools) using uv, and sets up the development environment.

   ```bash
   just install
   ```

4. **Install Git Hooks:**

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

5. **Verify Setup:**

   ```bash
   just test
   ```

### Manual Setup (Without just)

If you cannot use `just`, follow these manual steps:

1. **Install uv (if not already installed):**

    ```bash
    # Windows (PowerShell)
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    # Linux/macOS
    curl -lsSf https://astral.sh/uv/install.sh | sh
    ```

2. **Install Dependencies:**

   ```bash
   # Sync all dependencies from lockfile (reproducible)
   uv sync --frozen --all-extras
   ```

   > **Note:** The `--frozen` flag uses the committed `uv.lock` file for reproducible builds.
   > If you need to update dependencies, use `just upgrade-deps` or `uv lock --upgrade`.

3. **Install Pre-commit:**

   ```bash
   uv run pre-commit install --install-hooks
   uv run pre-commit install --hook-type pre-push
   ```

4. **Run Tests:**

   ```bash
   # Run full test suite with coverage
   uv run pytest

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

### Troubleshooting uv

**Common uv issues and solutions:**

1. **uv not found after installation:**

   ```bash
   # Restart your terminal or reload PATH
   # Windows PowerShell:
   $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "User")

   # Linux/macOS:
   source ~/.bashrc  # or ~/.zshrc
   ```

2. **Dependency resolution conflicts:**

   ```bash
   # Clear uv cache and retry
   uv cache clean
   uv sync --all-extras
   ```

3. **Lockfile out of sync:**

   ```bash
   # Update lockfile to match pyproject.toml
   uv lock
   uv sync --frozen --all-extras
   ```

4. **Using wrong Python version:**

   The project uses a `.python-version` file (3.13) for automatic version selection.
   Ensure uv detects it:

   ```bash
   # Check detected Python version
   uv python pin

   # Force specific version
   uv python pin 3.13
   ```

5. **Missing platform-specific dependencies:**

   ```bash
   # Windows - install pywin32 and wmi
   uv pip install --system pywin32 wmi

   # Linux - install pyudev
   uv pip install --system pyudev
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
- **full-tests** - Run complete test suite before push (671 tests with 49.96% coverage)

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

> **📖 Detailed Documentation:** For comprehensive information about semantic-release configuration,
> version bumping rules, troubleshooting, and the v1.0.0 upgrade process, see
> [Semantic Release Documentation](docs/semantic-release.md).

### Automated Release System

pyMediaManager uses a fully automated release system powered by
[python-semantic-release](https://python-semantic-release.readthedocs.io/) (v9.8.8) and GitHub Actions.
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

You can build distributions locally without relying on CI:

#### Windows Builds

```powershell
# Build portable ZIP (recommended for all versions)
python scripts/build_windows.py --version 3.13 --format zip

# Build MSI installer (Python 3.13 only)
python scripts/build_windows.py --version 3.13 --format msi

# Build both ZIP and MSI
python scripts/build_windows.py --version 3.13 --format both

# Using just (builds ZIP only)
just build
```

**Prerequisites for MSI:**

- WiX Toolset v4: `dotnet tool install --global wix`
- jinja2: `pip install jinja2`

#### Linux Builds

```bash
# Build AppImage
python scripts/build_linux_appimage.py --version 3.13
```

#### macOS Builds

```bash
# Build .app bundle
python scripts/build_macos.py --version 3.13 --arch x86_64  # Intel
python scripts/build_macos.py --version 3.13 --arch arm64   # Apple Silicon
```

#### Platform-Agnostic

```bash
# Auto-detects platform and builds accordingly
python scripts/build_manager.py --version 3.13 --format both
```

**Build Process:**

1. Downloads embedded Python distribution (Windows) or uses PyInstaller (Linux/macOS)
2. Installs dependencies from `pyproject.toml` or `requirements.lock`
3. Cleans up test/doc files (~15 MB savings)
4. Verifies critical imports (PySide6, pydantic, yaml, GitPython)
5. Generates version file using hatch-vcs
6. Creates distribution package:
   - **Windows ZIP:** Portable archive with embedded Python
   - **Windows MSI:** Installer with Start Menu integration (Python 3.13 only)
   - **Linux AppImage:** Self-contained executable
   - **macOS DMG:** Disk image with .app bundle (future)

### Branch Strategy

We follow a [Semantic Release](https://github.com/python-semantic-release/python-semantic-release) flow with automated versioning:

1. **Development (`dev` branch)**
   - All new features and fixes are merged here
   - Daily automated beta releases at midnight UTC (when changes exist)
   - Beta versions: `v0.y.z-beta.N` (e.g., `v0.3.0-beta.1`)
   - Tags created automatically based on conventional commits
   - Dependabot PRs target this branch exclusively

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
    - Uses [hatch-vcs](https://github.com/ofek/hatch-vcs) for version from git tags

### Release Artifacts

Each release automatically includes:

- **Windows Distributions:**
  - **MSI Installer** (`pyMM-v{VERSION}-py3.13-win-amd64.msi`) - Python 3.13 only,
    recommended for permanent installation
  - **Portable ZIP** (`pyMM-v{VERSION}-py{VERSION}-win-amd64.zip`) - Python 3.12, 3.13,
    3.14 for all architectures (amd64, arm64)
- **Linux AppImage** (`pyMM-v{VERSION}-py{VERSION}-x86_64.AppImage`) - Python 3.12, 3.13, 3.14
- **macOS DMG** (`pyMM-v{VERSION}-py{VERSION}-macos-{ARCH}.dmg`) - Python 3.12, 3.13, 3.14 (Intel + Apple Silicon, future)
- **SHA256 Checksums** for all artifacts
- **Supply Chain Attestation** (SLSA) for build provenance
- **Automated Changelog** from conventional commits
- **Updated Documentation** with version selector

### Branch Protection

To support the automated workflow, the following branch protection rules are configured:

#### `dev` Branch Protection

- **Require status checks to pass**: All CI checks must pass before merging
  - Applies to both manual and automated PRs
  - Ensures code quality and test coverage
- **Require 1 approving review**: Required for manual PRs only
  - `dependabot[bot]` is allowed to bypass this requirement
  - Automated dependency updates merge without manual review after CI passes
- **Dependabot Auto-Merge**:
  - Dependency PRs are automatically approved and merged via GitHub Actions workflow
  - Full details posted as PR comments (dependency names, versions, release notes)
  - CI failures trigger retry logic (3 attempts, 5 minute intervals)
  - Failed checks prevent merge and post explanatory comments

#### `main` Branch Protection

- Different rules apply as this branch only receives merges from `dev`
- Protects stable release integrity
- Manual review process for `dev` → `main` merges

For detailed setup instructions, see the [Architecture Documentation](docs/architecture.md#branch-protection-setup).

### Release Notes

Release notes are automatically generated from conventional commits. Commits of type `chore`, `ci`,
`refactor`, `style`, `test`, and `docs` are excluded from the changelog to keep it focused on
user-facing changes.

### v1.0.0 Release Process

> ⚠️ **Important:** The v1.0.0 release marks the transition from beta to production-ready.
> This is a **manual, deliberate decision** by project maintainers and requires following
> specific steps to ensure production readiness.

#### Pre-Release Requirements

Before releasing v1.0.0, the following criteria must be met:

1. **Feature Completeness**
   - All planned core features implemented and tested
   - Plugin system fully stable with comprehensive catalog
   - Cross-platform compatibility verified (Windows, Linux, macOS)

2. **Quality Standards**
   - Test coverage ≥ 80% (currently ~73%)
   - Zero critical or high-severity bugs
   - All security vulnerabilities addressed
   - Performance benchmarks met for typical workflows

3. **Documentation Completeness**
   - User guide covers all major features
   - API documentation complete for plugin developers
   - Migration guide from beta versions prepared
   - Troubleshooting guide comprehensive

4. **Production Hardening**
   - Error handling robust across all platforms
   - Logging system production-ready
   - Backup/recovery procedures documented
   - Rollback strategy defined

#### Release Steps

1. **Preparation Phase** (1-2 weeks before release)
   - Create GitHub Discussion: "v1.0.0 Release Planning"
   - Update `pyproject.toml` `tag_regex` to allow v1.x.x
   - Update `.github/workflows/semantic-release.yml` version guards
   - Update `.pre-commit-config.yaml` to remove version validation hook
   - Complete documentation review
   - Perform comprehensive testing on all platforms

2. **Release Execution**
   - Merge final features to `dev` branch
   - Create final beta: `v0.y.z-beta.N`
   - Stabilization period: 1 week minimum
   - Fix any critical issues found
   - Merge `dev` → `main`
   - Manually create annotated tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
   - Push tag: `git push origin v1.0.0`
   - Semantic release workflow creates GitHub Release automatically

3. **Post-Release**
   - Update `major_on_zero = true` in `pyproject.toml`
   - Update documentation version references
   - Announce release on GitHub Discussions
   - Update README.md badges to "stable"

#### Version Constraints

**During beta (current):** The `tag_regex` in `pyproject.toml` restricts tags to `v0.y.z`
format only. This prevents accidental v1.0.0 releases. Additionally, a pre-commit hook
and GitHub Actions workflow validate that all tags remain in the v0.y.z range.

**Important:** Branch-specific semantic-release configurations don't inherit root-level settings.
Ensure `major_on_zero = false` is explicitly set in both `[tool.semantic_release.branches.main]`
and `[tool.semantic_release.branches.dev]` configurations to prevent BREAKING CHANGE commits
from attempting major version bumps during the v0.y.z phase.

**For v1.0.0 release:** Maintainers must manually:

1. Update `tag_regex` in `pyproject.toml` to allow v1+
2. Update `major_on_zero = true` in root and all branch-specific configurations
3. Remove version validation from `.github/workflows/semantic-release.yml`
4. Remove version validation from `.pre-commit-config.yaml`

This multi-layered approach ensures v1.0.0 is a conscious, deliberate decision.

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

**Important for v0.y.z phase:** Due to `major_on_zero = false` in our semantic-release
configuration, `BREAKING CHANGE:` commits bump the **minor** version (0.1.0 → 0.2.0), not
the major version. This is intentional during the beta phase to keep all releases at v0.y.z
until the project reaches production readiness. Once v1.0.0 is released, breaking changes
will properly bump the major version (1.0.0 → 2.0.0).

### Using [skip ci]

Add skip directives to commit messages to control which CI jobs run:

**Available Skip Directives:**

```text
docs: fix typo in README [skip ci]          # Skip ALL CI jobs
test: refactor helper function [skip tests]  # Skip tests only
style: reformat code [skip lint]            # Skip linting only
build: update dependencies [skip build]      # Skip build jobs only
```

**When to use [skip ci]:**

- Documentation-only changes (typo fixes, formatting)
- Trivial maintenance (comment updates, whitespace)
- Non-functional changes that don't require validation

**When to use [skip tests]:**

- Minor code refactoring that doesn't change behavior
- Internal code cleanup or reorganization
- ⚠️ Use with caution - tests validate correctness

**When to use [skip lint]:**

- When you know linting will be fixed in a follow-up commit
- Emergency hotfixes (fix code first, lint later)
- ⚠️ Use sparingly - linting catches issues early

**When to use [skip build]:**

- Changes that don't affect build artifacts
- Documentation or test-only changes
- Minor bug fixes that don't require new builds

**When NOT to use skip directives:**

- Any code changes in `app/` or `tests/`
- Configuration changes (pyproject.toml, workflows)
- Changes that need validation

**🔒 Security Note:** Security scans (CodeQL, dependency review, safety checks)
**always run** regardless of skip directives to ensure project safety.

**✅ Automatic Validation:** A pre-commit hook validates skip directive usage and
prevents misuse on code changes. Install with `pre-commit install`.

**🤖 Smart Auto-Skip:** CI automatically skips when only documentation files are
changed (on non-PR commits), even without `[skip ci]`.

**📊 Skip Reporting:** When a skip directive is used, the CI workflow provides a
detailed summary showing which jobs were skipped and which still ran.

- Configuration changes (`pyproject.toml`, `.github/workflows/`)
- Changes that affect functionality or require testing
- Changes to user-facing documentation (installation guides, feature docs)

**Note:** Semantic-release automatically adds `[skip ci]` to its own release commits to avoid infinite loops.

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

> **Testing Roadmap:** For comprehensive test coverage plan, priority tiers (sync engine 0% → 60%, GUI expansion),
> and contribution guidelines, see [Testing Roadmap](docs/testing-roadmap.md). **Sync engine testing is the
> highest-priority contribution area.**

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

### Working with Dependabot PRs

This project uses Dependabot to automatically update dependencies. When Dependabot creates a PR,
it's important to understand how it interacts with our UV-based dependency management.

#### UV Lockfile Limitation

**⚠️ Important:** Dependabot's `pip` ecosystem does **not** understand UV's `uv.lock` format.

**What This Means:**

- Dependabot only reads `pyproject.toml` version constraints
- It ignores the 5,000+ line `uv.lock` file with precise dependency resolution
- May propose updates that conflict with locked transitive dependencies

**Automated Solution:**

We have a GitHub Action ([`dependabot-uv-lock-update.yml`](.github/workflows/dependabot-uv-lock-update.yml))
that automatically runs after Dependabot PRs are merged to update the lockfile. For complete details, see [.github/DEPENDABOT.md](.github/DEPENDABOT.md).

The workflow:

1. ✅ Detects when a Dependabot PR is merged
2. ✅ Extracts the package name from the PR title
3. ✅ Runs `uv lock --upgrade-package <name>`
4. ✅ Commits the updated `uv.lock` back to the dev branch
5. ✅ Posts a comment on the PR with verification instructions

**Manual Process (If Automation Fails):**

If you need to manually update the lockfile after merging a Dependabot PR:

```bash
# 1. Pull the latest changes
git checkout dev
git pull origin dev

# 2. Update lockfile for the specific package
# Replace <package-name> with the actual package (e.g., "pydantic")
uv lock --upgrade-package <package-name>

# 3. Verify the lock is valid
uv sync --frozen

# 4. Run tests to ensure compatibility
uv run pytest

# 5. Commit the lockfile update
git add uv.lock
git commit -m "chore(deps): update uv.lock after <package-name> merge"
git push origin dev
```

**For Grouped Updates:**

When Dependabot merges a grouped update (multiple packages), use:

```bash
uv lock --upgrade  # Full upgrade for all packages in group
```

#### Dependabot Auto-Merge Rules

Our Dependabot configuration includes smart auto-merge rules. For complete details, workflow
configurations, and testing procedures, see [.github/DEPENDABOT.md](.github/DEPENDABOT.md).

**Summary:**

**✅ Auto-merged (no manual review needed):**

- Patch updates for all Python packages (e.g., 1.2.3 → 1.2.4)
- Minor updates for dev dependencies only (pytest, ruff, mypy, types-*)
- Patch/minor updates for GitHub Actions

**⏸️ Manual review required:**

- Minor updates for runtime dependencies (PySide6, pydantic, aiohttp, etc.)
- Major updates for any Python package (e.g., 1.x → 2.x)
- All Docker base image updates
- Major updates for GitHub Actions

**What Happens:**

1. Dependabot creates PR with dependency update
2. CI runs full test matrix (3 OS × 3 Python versions)
3. Auto-merge workflow validates update type
4. If auto-mergeable: Approves and enables auto-merge
5. If manual review needed: Adds `needs-manual-review` label
6. After merge: UV lockfile update workflow runs automatically

#### Reviewing Dependabot PRs

When reviewing a Dependabot PR that requires manual approval:

**For Major Version Updates:**

- [ ] Review CHANGELOG/release notes for breaking changes
- [ ] Check if code changes are needed for compatibility
- [ ] Verify all tests pass with updated dependencies
- [ ] Test critical user workflows if needed
- [ ] After merge: Verify `uv.lock` was updated automatically

**For Minor Updates (Runtime Dependencies):**

- [ ] Review release notes for any behavioral changes
- [ ] Ensure tests cover affected functionality
- [ ] Check for new deprecation warnings
- [ ] After merge: Verify `uv.lock` was updated automatically

**For Docker Updates:**

- [ ] Check Debian/Python base image release notes
- [ ] Verify system package compatibility
- [ ] Test Docker build locally if possible
- [ ] Check for deprecated system packages

**Verification After Any Dependency Update:**

```bash
# Ensure lockfile is in sync
uv sync --frozen

# Run full test suite
uv run pytest

# Check for new issues
just lint
```

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
