# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- GitHub community standards files (CODE_OF_CONDUCT.md, SECURITY.md)
- Issue templates (bug report, feature request)
- Pull request template with comprehensive checklist
- Dependabot configuration for automated dependency updates
- Enhanced GitHub Actions workflows (security scanning, CodeQL, Scorecard)
- EditorConfig for consistent coding styles across editors
- CITATION.cff for academic/research citations
- py.typed marker file for PEP 561 compliance
- .gitattributes for Git LFS and line ending management
- Bandit configuration for security scanning
- VSCode workspace settings and extension recommendations
- Enhanced pre-commit hooks (Bandit, Safety, additional checks)
- Comprehensive .gitignore with all Python ecosystem patterns
- OpenSSF Scorecard badge
- Codecov integration badge
- Enhanced README with modern layout and badges

### Changed

- Updated pyproject.toml with latest packaging standards
  - Added project.scripts entry point
  - Enhanced metadata with more classifiers
  - Added maintainers field
  - Improved project URLs with more links
  - Enhanced Ruff configuration with 40+ rule categories
  - Added tool.setuptools.package-data configuration
- Improved pre-commit configuration with security checks
- Enhanced .gitignore with comprehensive patterns
- Updated README with modern formatting and badges

### Fixed

- Ruff configuration now includes all modern linting rules
- Pre-commit hooks now include security validation

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
