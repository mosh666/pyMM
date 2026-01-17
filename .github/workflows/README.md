# GitHub Actions Workflows

> **Last Updated:** 2026-01-17 21:41 UTC
\nThis directory contains all GitHub Actions workflows for the pyMM project,
following 2026 best practices with **100% uv migration** for reproducible builds.

## 🎯 2026 Modernization Status

**✅ Complete Migration:** All workflows migrated to modern Python tooling:

- **Package Manager:** `uv` (10-100x faster than pip, with lockfile support)
- **Build System:** Hatchling + hatch-vcs (PEP 517 compliant)
- **Reproducible Builds:** `uv.lock` with `--frozen` flag in all CI workflows
- **Dependency Tracking:** Dependabot configured for both pip and uv ecosystems
- **Action Versions:** All actions pinned to latest stable versions (2026)
- **Timeout Protection:** Added to prevent infinite polling in deployments

## 📋 Workflows Overview

**Total Workflows:** 15 comprehensive workflows for CI/CD, security, and automation.

### CI/CD Workflows

#### **ci.yml** - Continuous Integration

- **Triggers:** Push to main/dev, PRs, manual
- **Purpose:** Comprehensive testing, linting, type checking
- **Features:**
  - Matrix testing across Python 3.12, 3.13, 3.14
  - Multi-OS testing (Windows, Ubuntu, macOS)
  - Docker container testing
  - Code coverage with Codecov
  - Documentation and config validation
  - **Smart Skip Patterns:** Supports `[skip ci]`, `[skip tests]`, `[skip lint]`, `[skip build]`
  - **Path-based Auto-Skip:** Automatically skips when only docs changed (non-PR commits)
  - **Security Protection:** Security scans always run, even with skip directives
  - **Skip Reporting:** Detailed summary of which jobs were skipped and why

#### **build.yml** - Build Portable Distributions

- **Triggers:** Workflow call, manual dispatch, tags
- **Purpose:** Build platform-specific portable distributions
- **Outputs:**
  - Windows: Portable ZIP archives (amd64)
  - Linux: AppImage (x86_64)
  - macOS: DMG installers (x86_64, arm64)
- **Matrix:** Python 3.12, 3.13, 3.14 across all platforms

#### **semantic-release.yml** - Automated Releases

- **Triggers:** Push to main/dev, daily schedule (1 AM UTC), manual
- **Purpose:** Automated semantic versioning and releases
- **Version:** python-semantic-release >=9.15.0,<10.0.0
- **Features:**
  - Beta releases from dev branch (with `-beta.X` suffix)
  - Stable releases from main branch
  - Automatic changelog generation
  - Change detection (skips if no commits since last release)
  - Triggers build workflow and uploads all assets
  - Auto-triggers beta cleanup after beta releases
  - **Daily Schedule:** Only runs on dev branch at 1 AM UTC if changes exist
  - **uv integration:** Uses `uv pip install --system` for fast, reproducible installs

### Maintenance Workflows

#### **cleanup-beta-releases.yml** - Beta Release Cleanup

- **Triggers:** Daily at 2 AM UTC (after releases), manual
- **Purpose:** Keep only the 3 most recent beta releases
- **Configuration:**
  - `keep_count`: Number of beta releases to retain (default: 3)
  - `dry_run`: Preview mode without actual deletion
- **Logic:** Sorts betas by creation date, keeps N newest, deletes rest

#### **update-docs.yml** - Documentation Updates

- **Triggers:** After semantic release, weekly, manual
- **Purpose:** Auto-update README statistics and sync changelog
- **Features:**
  - Updates plugin count, test count
  - Commits with `[skip ci]` to avoid loops
  - Verifies changelog from semantic-release

### Security Workflows

#### **security.yml** - Security Scanning

- **Triggers:** Push to main/dev, PRs, daily schedule, manual
- **Features:**
  - CodeQL analysis for Python
  - Dependency review on PRs (blocks GPL licenses)
  - Safety check for vulnerable dependencies
  - **Always Runs:** Security scans cannot be skipped with `[skip ci]` for safety

#### **codeql.yml** - CodeQL Advanced

- **Triggers:** Push to main, PRs to main, weekly schedule
- **Purpose:** Advanced code analysis for security vulnerabilities
- **Languages:** Python, GitHub Actions

#### **scorecard.yml** - OpenSSF Scorecard

- **Triggers:** Weekly (Saturdays), branch protection changes, push to main
- **Purpose:** Assess supply chain security posture
- **Results:** Uploaded as SARIF to Security tab

### Automation Workflows

#### **dependabot-automerge.yml** - Dependabot Auto-merge

- **Triggers:** Dependabot PRs on dev branch
- **Purpose:** Auto-approve and merge Dependabot updates after CI passes
- **Features:**
  - Detailed update information in comments
  - Auto-enables merge after approval
  - Monitors CI status with retries

#### **labeler.yml** - Auto-Labeling

- **Triggers:** PRs opened/updated
- **Purpose:** Automatically label PRs based on file changes
- **Config:** `.github/labeler.yml`

#### **docs.yml** - Documentation Building

- **Triggers:** Push/PR with doc changes, manual, after releases
- **Features:**
  - Sphinx multi-version documentation
  - Quality checks (docstring coverage, link validation, spell check)
  - Builds for all branches (main, dev, version tags)
  - Deploys to GitHub Pages

## 🔒 Security Best Practices (2026)

### Action Versions

All actions updated to latest stable versions:

- `actions/checkout@v6` - Secure checkout with improved caching
- `actions/setup-python@v6` - Python environment setup
- `actions/upload-artifact@v6` - Artifact uploads with retention
- `actions/download-artifact@v7` - Artifact downloads
- `github/codeql-action@v4` - Latest CodeQL security analysis
- `softprops/action-gh-release@v2` - Release management
- `ossf/scorecard-action@v2.5.0` - Supply chain security
- `python-semantic-release@v10.5.3` - Automated semantic versioning

### Permissions

All workflows use **minimal permissions** principle:

```yaml
permissions:
  contents: read  # Default - only escalate when needed
```

Elevated only when required:

- `contents: write` - For releases, commits
- `pull-requests: write` - For PR automation
- `security-events: write` - For security scans

### Concurrency Controls

Prevents race conditions and resource waste:

```yaml
concurrency:
  group: workflow-${{ github.ref }}
  cancel-in-progress: true  # or false for critical workflows
```

Applied to:

- `semantic-release.yml` - Prevents concurrent releases
- `dependabot-automerge.yml` - Per-PR concurrency
- `update-docs.yml` - Prevents conflicting doc updates

### Artifact Management

- **Retention:** 30 days for build artifacts
- **Attestation:** Ready for supply chain verification
- **Checksums:** SHA256 for all releases
- **Organized:** Structured artifact naming: `pyMM-py{version}-{os}-{arch}`

## 🚀 Release Process

### Beta Releases (Dev Branch)

1. **Automated Daily:**
   - Runs at 1 AM UTC if changes exist since last release
   - Creates beta release with `-beta.X` suffix
   - Builds all platform artifacts
   - Uploads to GitHub Releases
2. **Cleanup:**
   - Runs at 2 AM UTC daily
   - Keeps only 3 most recent beta releases
   - Deletes older betas automatically

### Stable Releases (Main Branch)

1. Merge from dev → main
2. Semantic release analyzes commits
3. Creates stable release (e.g., `v1.2.3`)
4. Builds and uploads all artifacts
5. Updates changelog

### Manual Releases

```bash
# Trigger release manually
gh workflow run semantic-release.yml \
  --ref dev \
  -f branch=dev \
  -f force=false

# Force release without changes
gh workflow run semantic-release.yml \
  --ref dev \
  -f branch=dev \
  -f force=true
```

## 📊 Monitoring

### Workflow Summaries

All workflows generate GitHub Actions summaries with:

- Build statistics
- Test results
- Release information
- Asset lists
- Error diagnostics

### Status Badges

Add to README:

```markdown
[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![Security](https://github.com/mosh666/pyMM/actions/workflows/security.yml/badge.svg)](https://github.com/mosh666/pyMM/actions/workflows/security.yml)
[![Scorecard](https://github.com/mosh666/pyMM/actions/workflows/scorecard.yml/badge.svg)](https://github.com/mosh666/pyMM/actions/workflows/scorecard.yml)
```

## 🛠️ Development

### Testing Workflows Locally

Use [act](https://github.com/nektos/act) for local testing:

```bash
# Install act
choco install act-cli  # Windows
brew install act       # macOS

# Test CI workflow
act push --job test

# Test with specific event
act workflow_dispatch --job build-windows
```

### Debugging Workflows

Enable debug logging:

```bash
# Repository secrets
ACTIONS_STEP_DEBUG=true
ACTIONS_RUNNER_DEBUG=true
```

## 📝 Configuration Files

Related configuration files:

- `.github/labeler.yml` - PR auto-labeling rules
- `.github/dependabot.yml` - Dependabot configuration
- `pyproject.toml` - Semantic release config
  - `[tool.semantic_release.branches.main]` - Stable releases
  - `[tool.semantic_release.branches.dev]` - Beta releases

## 🎯 CI Skip Directives

The CI workflow supports intelligent skip patterns to save Actions minutes while maintaining safety.

### Available Skip Directives

| Directive     | Effect                            | Use Case                           |
| ------------- | --------------------------------- | ---------------------------------- |
| `[skip ci]`   | Skip ALL CI jobs except security  | Docs-only, trivial changes         |
| `[skip tests]`| Skip test jobs only               | Minor refactoring, internal cleanup|
| `[skip lint]` | Skip linting jobs only            | Emergency hotfixes (fix code first)|
| `[skip build]`| Skip build jobs only              | Changes that don't affect artifacts|

### Usage Examples

```bash
git commit -m "docs: fix typo in README [skip ci]"
git commit -m "test: refactor helper function [skip tests]"
git commit -m "style: reformat code [skip lint]"
git commit -m "chore: update comments [skip build]"
```

### Smart Behavior

**Path-Based Auto-Skip:**

- Automatically skips CI when only documentation files changed (non-PR commits)
- No `[skip ci]` needed for pure doc updates

**Security Protection:**

- Security scans (CodeQL, dependency review, safety) **always run**
- Cannot be skipped with any directive
- Ensures project safety and compliance

**Pre-commit Validation:**

- Validates skip directive usage before commit
- Blocks invalid usage (e.g., `[skip ci]` with code changes)
- Warns on questionable usage
- Install: `pre-commit install`

**Skip Reporting:**

- Detailed job summary shows what was skipped and why
- Lists changed file categories
- Indicates which jobs still ran

**Pull Request Override:**

- Tests always run on PR code changes, even with `[skip tests]`
- Ensures PR validation before merge

### When NOT to Skip

❌ **Never skip on:**

- Code changes in `app/` or `tests/`
- Configuration changes (`pyproject.toml`, workflows)
- Dependency updates
- Breaking changes

✅ **Safe to skip on:**

- Documentation typos
- Comment updates
- Whitespace/formatting (after lint validation)
- README badge updates

## 🔄 Update Checklist

When updating workflows:

- [ ] Use latest stable action versions
- [ ] Apply minimal permissions
- [ ] Add concurrency controls where needed
- [ ] Use `uv sync --frozen --all-extras` for reproducible builds
- [ ] Use `uv pip install --system` when installing outside virtual env
- [ ] Update `uv.lock` with `just upgrade-deps` when adding dependencies
- [ ] Include workflow summaries
- [ ] Test in fork before merging
- [ ] Document changes in this README
- [ ] Update status badges if workflow names change

## 📦 Dependency Management

### Using uv in Workflows

**Installation:**

```yaml
- uses: astral-sh/setup-uv@v5
  with:
    enable-cache: true
    version: "latest"
```

**Reproducible installs (from lockfile):**

```yaml
- run: uv sync --frozen --all-extras
```

**System-wide installs (no venv):**

```yaml
- run: uv pip install --system package-name
```

**Updating dependencies:**

```bash
# Locally
just upgrade-deps  # Updates uv.lock and syncs

# Or manually
uv lock --upgrade
uv sync --all-extras
```

**Dependabot configuration:**

- **Pip ecosystem:** Monday 9 AM UTC (pyproject.toml tracking)
- **UV ecosystem:** Tuesday 9 AM UTC (uv.lock tracking)
- **GitHub Actions:** Monday 9 AM UTC (workflow updates)

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [uv - Python Package Manager](https://github.com/astral-sh/uv)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [CodeQL](https://codeql.github.com/)
- [Dependabot](https://docs.github.com/en/code-security/dependabot)

---

**Last Updated:** January 17, 2026
**Maintained by:** @mosh666
