# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Documentation Overhaul (2026-01-07)

- Complete README.md rewrite from scratch following 2026 best practices
  - Modern badge layout with flat styling and proper categorization
  - Three-tiered feature presentation (Core, Developer Experience, Technical Highlights)
  - Comprehensive sections: Quick Start, Architecture, Testing & Quality, Contributing
  - Professional tables for documentation links, testing metrics, and plugins
  - Security section with reporting procedures
  - Project stats with GitHub badges (stars, forks, issues, PRs)
  - BibTeX citation format for academic use
  - Markdown lint compliant with modern README standards
- Comprehensive CHANGELOG.md following Keep a Changelog 1.1.0 format
  - Proper semantic versioning categories (Added, Changed, Deprecated, Removed, Fixed, Security)
  - Chronological organization with date stamps
  - Detailed descriptions with context and rationale
  - Breaking changes clearly marked
  - Migration guides for major changes
- Enhanced documentation across all .md files
  - CONTRIBUTING.md: Modern tools (uv, just), Python 3.13 emphasis, correct test counts
  - docs/architecture.md: Updated technical details, 193 tests, 73% coverage
  - docs/plugin-development.md: Clarified manifest-driven approach
  - docs/user-guide.md: Windows 10 version 1809+ requirements, enhanced workflows
  - tests/README.md: Comprehensive test suite documentation

#### GitHub Community Standards (2026-01-05)

- Professional issue templates using GitHub Forms (YAML format)
  - `bug_report.yml` - Structured bug reporting with validation
  - `feature_request.yml` - Feature proposals with use case templates
  - `config.yml` - Directs questions to GitHub Discussions
- Pull request template (`.github/PULL_REQUEST_TEMPLATE.md`)
  - Comprehensive review checklist
  - Testing verification steps
  - Documentation update requirements
  - Breaking changes section
- Community health files
  - `CODE_OF_CONDUCT.md` - Contributor Covenant 2.1
  - `SECURITY.md` - Vulnerability reporting and safe harbor policy
  - `FUNDING.yml` - Sponsor links and support options
  - `CODEOWNERS` - Automatic code review assignments

#### CI/CD and Automation (2026-01-05)

- GitHub Actions workflows following 2026 best practices
  - `ci.yml` - Matrix testing on Python 3.12, 3.13, 3.14 with proper token permissions
  - `security.yml` - CodeQL analysis for vulnerability detection
  - `scorecard.yml` - Daily OpenSSF Scorecard at 07:15 UTC
  - `build.yml` - Portable distribution building with embedded Python runtime
  - `release.yml` - Automated releases with changelog generation
  - `docs.yml` - Documentation building and deployment
- Dependabot configuration (`.github/dependabot.yml`)
  - Daily pip dependency updates
  - Daily GitHub Actions updates
  - Grouped updates for efficiency
  - Automatic security vulnerability alerts
- Pre-commit hooks (`.pre-commit-config.yaml`) with 15+ checks
  - **Code Quality:** Ruff linting and formatting, MyPy type checking
  - **Security:** Bandit vulnerability scanning, secret detection
  - **File Validation:** YAML, JSON, TOML syntax checking
  - **Git Hygiene:** Trailing whitespace, EOF fixes, merge conflict detection
  - **Testing:** Unit tests on commit, full suite on push

#### Development Tools (2026-01-05)

- EditorConfig (`.editorconfig`) for consistent coding styles
  - 4-space indentation for Python
  - UTF-8 encoding
  - LF line endings
  - Trim trailing whitespace
  - Final newline insertion
- Git attributes (`.gitattributes`) for comprehensive repository configuration
  - Line ending normalization (LF for text, CRLF for Windows scripts)
  - Git LFS patterns for binary files (images, videos, archives)
  - Merge strategies for lock files and generated code
  - Diff drivers for better change visualization
  - linguist overrides for language detection
- VS Code workspace configuration
  - `settings.json` - Python, Ruff, MyPy, editor settings
  - `extensions.json` - Recommended extensions for development
  - `launch.json` - Debug configurations
- Bandit configuration (`.bandit`) for security baseline
- CITATION.cff for academic citations (CFF 1.2.0 format)
  - Structured metadata for research citation
  - BibTeX export support
  - Author and maintainer information

#### Python Packaging (2026-01-05)

- `py.typed` marker file for PEP 561 type checking compliance
- Enhanced `pyproject.toml` with modern PEP 621 standards
  - Dynamic versioning with setuptools-scm
  - 50+ project classifiers for PyPI discoverability
  - `project.scripts` entry point for CLI execution (`pymm` command)
  - 6+ project URLs (Homepage, Repository, Issues, Discussions, Changelog, Docs)
  - Maintainers field separate from authors
  - Optional dependencies grouping (`dev`, future: `docs`, `test`)
  - Comprehensive Ruff configuration with 40+ rule categories
  - MyPy strict type checking configuration
  - pytest configuration with coverage thresholds

### Changed

#### Documentation Improvements (2026-01-07)

- README.md completely rewritten with modern structure
  - Centered header with emoji-enhanced subtitle
  - Flat-style badges organized by category
  - Quick navigation links
  - Comprehensive feature list with three categories
  - Separate end user and developer quick start sections
  - Architecture section with directory structure
  - Testing & quality metrics table
  - Contributing workflow with code standards
  - Installation details with portable structure
  - Security section with vulnerability reporting
  - License information with third-party acknowledgments
  - Project statistics badges
  - Citation section with BibTeX format
- All documentation follows latest Python and GitHub best practices
  - Python 3.13 recommended (supports 3.12, 3.14)
  - Modern type hints: `list[T]`, `dict[K, V]`, `tuple[T, ...]` (Python 3.12+)
  - 193 tests with 73% code coverage prominently featured
  - Daily OpenSSF Scorecard metrics (changed from weekly)
  - Modern tooling: uv (fast package installation), just (command runner)
  - Proper bash code fences throughout
  - No print statements (structured logging only)

#### CI/CD Improvements (2026-01-05)

- Updated Codecov action from v4 to v5 with explicit token authentication
- Modified OpenSSF Scorecard schedule to daily runs at 07:15 UTC
  - More frequent security metrics and faster vulnerability detection
  - Daily monitoring of security best practices compliance
  - Better resource utilization and earlier daily reports
- Enhanced GitHub Actions workflows
  - Proper GITHUB_TOKEN permissions (read-only by default, write when needed)
  - Matrix testing across Python versions (3.12, 3.13, 3.14)
  - Improved caching strategies for faster CI runs
  - Concurrency groups to prevent duplicate runs
  - Better artifact handling and retention policies

#### Code Quality Standards (2026-01-05)

- Updated `pyproject.toml` build system configuration
  - Modern setuptools >=68.0 with setuptools-scm >=8.0
  - Enhanced Ruff configuration with 40+ rule categories:
    - `F` - Pyflakes errors
    - `E`, `W` - pycodestyle errors and warnings
    - `I` - isort import sorting
    - `N` - pep8-naming conventions
    - `UP` - pyupgrade for modern Python syntax
    - `B` - flake8-bugbear bug detection
    - `S` - flake8-bandit security checks
    - `A` - flake8-builtins shadowing prevention
    - `C4` - flake8-comprehensions optimization
    - `DTZ` - flake8-datetimez timezone awareness
    - `T10` - flake8-debugger detection
    - `RUF` - Ruff-specific rules
  - Comprehensive type checking with MyPy strict mode
  - pytest configuration with 70% minimum coverage threshold
- Improved code formatting and linting standards
  - Sorted imports across all Python files
  - Fixed f-string formatting (explicit type conversions)
  - Removed unnecessary code (pass statements, else after return)
  - Fixed pytest fixtures (removed unnecessary yield)
  - Consistent quote style (double quotes preferred)
  - Removed unused imports and variables
- Enhanced test reliability
  - Clearer test output formatting
  - Better error messages with context
  - Improved fixture management and isolation
  - Automatic drive mocking to prevent system pollution

#### Documentation Structure (2026-01-05)

- Updated README.md with comprehensive modern layout
  - CI, Security, Codecov, OpenSSF Scorecard badges
  - Feature highlights with emoji icons for better scannability
  - Quick navigation links
  - Citation instructions for academic use
  - Support section with multiple channels
- Enhanced .gitignore with all Python ecosystem patterns
  - Virtual environments: venv, .venv, env, ENV
  - IDE configurations: VSCode, PyCharm, Visual Studio, Sublime Text
  - Python build artifacts: eggs, wheels, distributions
  - Testing and coverage: .pytest_cache, htmlcov, .coverage
  - OS-specific: Thumbs.db, .DS_Store, desktop.ini
  - Database and cache files

#### Security Practices (2026-01-05)

- Security scanning integrated into CI/CD pipeline
  - CodeQL analysis on all pull requests and scheduled weekly
  - Daily OpenSSF Scorecard assessments (upgraded from weekly)
  - Dependabot for automated dependency updates
  - Branch protection rules enforced
- Pre-commit security validation
  - Bandit security linting for Python code
  - Secret scanning to prevent credential leaks
  - License compliance checking
  - Large file detection
- Enhanced security documentation
  - Comprehensive SECURITY.md with reporting procedures
  - Safe harbor policy for security researchers
  - Coordinated disclosure timeline (48 hours initial response)
  - Multiple reporting channels

### Fixed

#### Code Quality Refinement (2026-01-07)

- Resolved remaining linter errors and type checking issues
  - Fixed complexity in RollbackDialog
  - Fixed circular imports in Service layer
- Fixed application startup in development environment
  - Relaxed template version requirements for dev builds
- Fixed race condition in ProjectService destructor

#### Code Quality Issues (2026-01-05)

- Ruff linting issues resolved across entire codebase
  - Sorted `__all__` declarations alphabetically
  - Fixed import ordering (stdlib → third-party → first-party)
  - Removed unnecessary else statements after return
  - Added explicit `check=` arguments to subprocess calls
  - Fixed f-string type conversion calls (use `str()` not `!s`)
  - Removed unused imports and variables
  - Fixed line length violations (120 char limit)
- Code formatting standardized
  - Consistent indentation (4 spaces)
  - Proper blank line spacing
  - Trailing whitespace removed
  - Files end with single newline
- Type checking improvements
  - All functions have complete type hints
  - Return types specified explicitly
  - MyPy passes with zero errors in strict mode
  - Modern type hints used: `list[T]` not `List[T]`

#### Testing Improvements (2026-01-05)

- All 193 tests passing with 73% code coverage
  - Unit tests: 95 tests for individual components
  - Integration tests: 10 tests for end-to-end workflows
  - GUI tests: 50 tests for UI components
  - Manual tests: 4 tests for full application
- Test isolation enhanced
  - Automatic drive mocking prevents system pollution
  - All temporary files created in isolated directories
  - Proper cleanup after test execution
  - No side effects between tests
- Test reliability improved
  - Clearer assertion messages
  - Better error context
  - Reduced flakiness in GUI tests
  - Proper fixture scoping

### Security

#### Enhanced Security Measures (2026-01-05)

- Daily OpenSSF Scorecard monitoring (upgraded from weekly)
  - Tracks 18 security best practices
  - Public scorecard badge on README
  - Automated security posture reporting
- CodeQL static analysis on every pull request
  - Detects security vulnerabilities
  - Identifies code quality issues
  - Language-specific security patterns
  - Integration with GitHub Security tab
- Dependabot automatic security updates
  - Daily scans for vulnerable dependencies
  - Automatic pull requests for security patches
  - Grouped updates to reduce PR noise
  - pip and GitHub Actions ecosystems covered
- Pre-commit security scanning
  - Bandit security linter for Python code
  - Secret detection to prevent credential leaks
  - License compliance verification
- SHA-256 checksum verification for plugin downloads
  - All external binaries verified before installation
  - Prevents supply chain attacks
  - Retry logic with integrity checking
  - Progress tracking for large downloads

## [Unreleased] - Development Branch

> **Note:** Changes in this section are in the `dev` branch and not yet released to `main`.

See above for current unreleased changes.

## Version History

> **Note:** This project is currently in beta. Version 1.0.0 will be released when the
> application reaches feature completeness and production stability.

Future releases will be documented here following semantic versioning:

- **Major versions (X.0.0)** - Breaking changes, major new features
- **Minor versions (0.X.0)** - New features, backward compatible
- **Patch versions (0.0.X)** - Bug fixes, backward compatible

---

## Upgrading

### From Beta to 1.0.0 (Future)

When 1.0.0 is released, upgrade instructions will be provided here.

### Branch Strategy

- **`main` branch** - Stable releases (tagged as `vX.Y.Z`)
- **`dev` branch** - Beta releases (tagged as `latest-beta`)

To use the latest beta version, download from the `latest-beta` tag. For production use,
download from the latest stable release tag.

---

## Release Process

### Semantic Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version (X.0.0) - Incompatible API changes
- **MINOR** version (0.X.0) - Add functionality (backward compatible)
- **PATCH** version (0.0.X) - Bug fixes (backward compatible)
- **Pre-release** - Alpha, beta, rc tags (vX.Y.Z-beta.1)

### Versioning with setuptools-scm

Versions are automatically derived from Git tags using setuptools-scm:

- Tags must follow pattern: `v{version}` (e.g., `v1.0.0`, `v0.5.0-beta.1`)
- Version accessible at runtime via `app.__version__`
- Commit hash available via `app.__commit_id__`

### Release Workflow

1. **Development** - Work in `dev` branch
2. **Beta Release** - Push to `dev` triggers `latest-beta` tag
3. **Stable Release** - Merge to `main` and tag with `vX.Y.Z`
4. **Changelog** - Update this file with release notes
5. **GitHub Release** - Automated release creation with assets

---

## Links

- **Repository:** <https://github.com/mosh666/pyMM>
- **Issues:** <https://github.com/mosh666/pyMM/issues>
- **Discussions:** <https://github.com/mosh666/pyMM/discussions>
- **Security Policy:** [SECURITY.md](.github/SECURITY.md)
- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)

[Unreleased]: https://github.com/mosh666/pyMM/compare/main...dev
