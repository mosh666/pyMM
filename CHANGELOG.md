# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed - CI/CD Improvements (2026-01-05)

- Updated Codecov action from v4 to v5 with explicit token authentication for better reliability
- Modified OpenSSF Scorecard schedule to run daily at 08:15 UTC (from weekly on Saturdays)
  - Provides more frequent security metrics and faster vulnerability detection
  - Enables daily monitoring of security best practices compliance
  - Optimized schedule timing for better resource utilization

### Added - GitHub Community Standards

- GitHub community standards files compliant with best practices
  - CODE_OF_CONDUCT.md based on Contributor Covenant 2.1
  - SECURITY.md with vulnerability reporting and safe harbor policy
  - FUNDING.yml for sponsor links
- Professional issue templates using GitHub Forms (YAML format)
  - bug_report.yml with structured fields and validation
  - feature_request.yml with comprehensive context gathering
  - config.yml to guide users to discussions for questions
- Pull request template with comprehensive review checklist
  - Code quality verification
  - Testing requirements
  - Documentation updates
  - Breaking changes notification

### Added - CI/CD and Automation

- Enhanced GitHub Actions workflows following 2026 best practices
  - security.yml: CodeQL analysis with comprehensive scanning
  - scorecard.yml: OpenSSF Scorecard security metrics
  - ci.yml: Enhanced with proper GITHUB_TOKEN permissions
- Dependabot configuration for automated security updates
  - pip dependencies (daily schedule)
  - GitHub Actions (daily schedule)
  - Grouped dependency updates for efficiency
- Pre-commit hooks with comprehensive quality gates
  - Bandit for security vulnerability scanning
  - Ruff for linting and formatting
  - MyPy for static type checking
  - YAML, JSON, TOML validation
  - Trailing whitespace and EOF fixes
  - Merge conflict detection
  - Large file prevention

### Added - Development Tools

- EditorConfig (.editorconfig) for consistent coding styles across all editors
- .gitattributes for comprehensive Git configuration
  - Line ending normalization (LF for text, CRLF for Windows scripts)
  - Git LFS patterns for binary files
  - Merge strategies for specific file types
  - Diff drivers for better change visualization
- VSCode workspace configuration
  - settings.json with Python, Ruff, MyPy, and editor settings
  - extensions.json recommending essential development extensions
- Bandit configuration (.bandit) for security baseline
- CITATION.cff for academic/research citations (CFF 1.2.0 format)

### Added - Python Packaging

- py.typed marker file for PEP 561 type checking compliance
- Enhanced pyproject.toml with modern PEP 621 standards
  - 50+ project classifiers for better PyPI discoverability
  - project.scripts entry point for CLI execution
  - Comprehensive project URLs (6 different resource links)
  - Maintainers field separate from authors
  - Enhanced optional dependencies grouping

### Changed - Code Quality

- Updated pyproject.toml build system configuration
  - Modern setuptools configuration with explicit backend
  - Enhanced Ruff configuration with 40+ rule categories
  - Comprehensive linting rules (import sorting, code complexity, security)
  - Type checking configuration for strict validation
  - Tool.setuptools.package-data for proper distribution
- Improved code formatting and linting standards
  - Sorted imports across all Python files
  - Fixed f-string formatting (explicit type conversions)
  - Removed unnecessary code (pass statements, else after return)
  - Fixed pytest fixtures (removed unnecessary yield)
  - Consistent quote style (double quotes preferred)
- Enhanced test reliability
  - Clearer test output formatting
  - Better error messages
  - Improved fixture management

### Changed - Documentation

- Updated README.md with comprehensive modern layout
  - Added CI, Security, Codecov, OpenSSF Scorecard badges
  - Enhanced feature highlights with emoji icons
  - Improved navigation with quick links
  - Added citation instructions
  - Better support section with issue templates
- Enhanced .gitignore with all Python ecosystem patterns
  - Virtual environment patterns (venv, .venv, env)
  - IDE configurations (VSCode, PyCharm, Visual Studio)
  - Python build artifacts (eggs, wheels, distributions)
  - Testing and coverage outputs
  - OS-specific files (Windows, macOS, Linux)
  - Database and cache files

### Changed - Security

- Security scanning integrated into CI/CD
  - CodeQL analysis on pull requests and schedule
  - OpenSSF Scorecard weekly assessments
  - Dependabot for automated dependency updates
- Pre-commit security validation
  - Bandit security linting
  - Secret scanning prevention
  - License compliance checking

### Fixed

- Ruff linting issues resolved
  - Sorted __all__ declarations
  - Fixed import ordering
  - Removed unnecessary else statements
  - Added explicit subprocess check arguments
  - Fixed f-string type conversion calls
- Code formatting standardized across entire codebase
- Type checking passes with zero errors (MyPy strict mode)
- All 193 tests passing with 72.77% code coverage maintained

## [1.0.0] - 2026-01-05

### Added

- Initial release
- Portable Python-based media management application
- Modern Fluent Design UI with PySide6
- Plugin system for external tools
- Project management functionality
- Comprehensive test suite (193 tests, 72.77% coverage)
- CI/CD pipelines with GitHub Actions
- Pre-commit hooks for code quality
- Documentation (User Guide, Architecture Guide, Contributing Guide)

[Unreleased]: https://github.com/mosh666/pyMM/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/mosh666/pyMM/releases/tag/v1.0.0
