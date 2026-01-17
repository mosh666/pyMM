# Dependabot Documentation

> **Last Updated:** 2026-01-17 21:41 UTC
\nComplete guide for automated dependency management in the pyMM project.

---

## Table of Contents

1. [Overview](#overview)
2. [What's Automated](#whats-automated)
3. [Quick Reference](#quick-reference)
4. [Configuration Details](#configuration-details)
5. [Testing Guide](#testing-guide)
6. [Troubleshooting](#troubleshooting)

---

## Overview

This project uses Dependabot for automated dependency updates across multiple ecosystems, with smart auto-merge
rules and automatic UV lockfile updates.

### Key Features

- ✅ **Multi-ecosystem monitoring**: Python (pip), Docker, GitHub Actions
- ✅ **Smart auto-merge**: Graduated rules based on update type (patch/minor/major)
- ✅ **UV lockfile automation**: Automatic updates after Dependabot merges
- ✅ **Pre-commit automation**: Weekly hook updates
- ✅ **Comprehensive grouping**: 15+ dependency groups for related packages

### Critical Limitation

**⚠️ UV Lockfile Support**: Dependabot's `pip` ecosystem doesn't understand `uv.lock` format. It only reads
`pyproject.toml` version constraints, which can lead to version conflicts. We mitigate this with the
`dependabot-uv-lock-update.yml` workflow that automatically runs `uv lock --upgrade-package <name>` after
every Dependabot merge to main or dev branches.

**How it works:**

1. Dependabot creates PR updating `pyproject.toml`
2. Auto-merge workflow merges PR after CI passes (if eligible)
3. `dependabot-uv-lock-update.yml` triggers on merge
4. Workflow runs `uv lock --upgrade-package` for changed packages
5. Commits updated `uv.lock` with `[skip ci]` to avoid loop

---

## What's Automated

### Update Schedule

| Ecosystem        | Day       | Time (UTC) | Frequency |
| ---------------- | --------- | ---------- | --------- |
| Python packages  | Monday    | 09:00      | Weekly    |
| Docker images    | Tuesday   | 09:00      | Weekly    |
| GitHub Actions   | Wednesday | 09:00      | Weekly    |
| Pre-commit hooks | Monday    | 10:00      | Weekly    |

### Auto-Merge Rules

| Update Type                                            | Auto-Merge | Manual Review |
| ------------------------------------------------------ | :--------: | :-----------: |
| Python patch (all packages)                            |     ✅     |      ❌       |
| Python minor (dev deps: pytest, ruff, mypy, types-\*)  |     ✅     |      ❌       |
| Python minor (runtime deps)                            |     ❌     |      ✅       |
| Python major (all packages)                            |     ❌     |      ✅       |
| Docker (all updates)                                   |     ❌     |      ✅       |
| GitHub Actions (patch/minor)                           |     ✅     |      ❌       |
| GitHub Actions (major)                                 |     ❌     |      ✅       |

### Dependency Groups

Python dependencies are organized into 15+ groups:

- **pyside6**: GUI framework (PySide6\*)
- **pytest**: Testing framework (pytest\*, excluding pytest-qt)
- **pytest-gui**: GUI testing (pytest-qt)
- **type-checking**: Type tools (mypy, types-\*)
- **code-quality**: Linters (ruff, black, interrogate, doc8)
- **documentation**: Docs tools (sphinx\*, furo, myst-parser)
- **async-networking**: Async/network libs (aiohttp, APScheduler)
- **security**: Security packages (cryptography) - allows major updates
- **data-validation**: Validation tools (pydantic)
- **build-tools**: Build system (hatchling, hatch-vcs, jinja2)
- **utilities**: Core utilities (rich, pyyaml, psutil, etc.) - minor/patch only
- **platform-windows**: Windows-specific (WMI) - minor/patch only
- **platform-linux**: Linux-specific (pyudev) - minor/patch only
- **platform-macos**: macOS-specific (pyobjc-\*) - minor/patch only

GitHub Actions are grouped into:

- **github-core**: Core actions (actions/\*)
- **security-scanning**: Security tools (codeql, scorecard, dependency-review)
- **code-coverage**: Coverage reporting (codecov)
- **python-tooling**: Python setup (astral-sh/setup-uv)
- **linting**: Quality tools (markdownlint)
- **dependabot-utils**: Dependabot metadata tools
- **other-tools**: Misc tools (setup-just)

---

## Quick Reference

### Reviewing a Manual-Review PR

When a PR has the `needs-manual-review` label:

1. **Review the auto-generated comment** with checklist
2. **Check release notes** for breaking changes
3. **Verify CI passes** (all checks green)
4. **For major updates**:
   - Review CHANGELOG for breaking changes
   - Check if code changes needed
   - Test critical workflows if possible
5. **For runtime dependency minors**:
   - Review behavioral changes
   - Check for new deprecation warnings
6. **For Docker updates**:
   - Check base image release notes
   - Verify system package compatibility
7. **Approve and merge** when safe
8. **Wait for lockfile update** (automatic via workflow)

### Manual Dependabot Commands

Comment on any Dependabot PR:

```text
@dependabot rebase              # Rebase on latest target branch
@dependabot recreate            # Close and recreate the PR
@dependabot merge               # Merge after CI passes
@dependabot cancel merge        # Cancel auto-merge
@dependabot close               # Close without merging
@dependabot reopen              # Reopen a closed PR
@dependabot ignore this [dependency]    # Skip this dependency
@dependabot ignore this major version   # Skip major updates
@dependabot ignore this minor version   # Skip minor updates
```

### Checking Lockfile Status

```bash
# Verify lockfile is valid
uv sync --frozen

# See what would change
uv lock --dry-run

# Upgrade specific package
uv lock --upgrade-package <package-name>

# Full upgrade (for grouped updates)
uv lock --upgrade
```

### Manual Lockfile Update (If Automation Fails)

```bash
# 1. Pull latest changes
git checkout dev
git pull origin dev

# 2. Update lockfile
uv lock --upgrade-package <package-name>

# 3. Commit
git add uv.lock
git commit -m "chore(deps): update uv.lock after <package> merge"
git push origin dev
```

---

## Configuration Details

### Dependabot Config ([.github/dependabot.yml](.github/dependabot.yml))

**Key Settings**:

- `rebase-strategy: auto` - Automatically rebase PRs on target branch changes
- `versioning-strategy: auto` - Smart version constraint updates
- `timezone: "Etc/UTC"` - Explicit timezone for schedules
- Staggered schedules (Mon/Tue/Wed) to reduce PR flood

**Ignore Rules**:

```yaml
# Selective ignoring (not blanket blocking)
- python-semantic-release (major only)
- sphinx (versions >= 8.0.0)
```

### Workflows

#### dependabot-automerge.yml

- Validates update type and decides auto-merge eligibility
- Approves eligible PRs automatically
- Enables auto-merge after approval
- Monitors CI status (45-minute timeout)
- Labels manual-review cases

#### dependabot-uv-lock-update.yml

- Triggers after Dependabot PRs merge
- Extracts package name from PR title
- Runs `uv lock --upgrade-package <name>`
- Commits updated lockfile to dev branch
- Posts results on merged PR

#### pre-commit-autoupdate.yml

- Runs weekly (Mondays 10:00 UTC)
- Updates `.pre-commit-config.yaml`
- Tests hooks on all files
- Auto-commits or creates PR

---

## Testing Guide

### Pre-Testing Setup

1. **Verify GitHub repository settings**:
   - Actions have "Read and write permissions"
   - Auto-merge is enabled
   - Branch protection (if used) allows Dependabot

2. **Verify label exists**:

   ```bash
   gh label list | grep "needs-manual-review"
   ```

3. **Check workflows are active**:

   ```bash
   gh workflow list
   ```

### Test Scenarios

#### 1. Python Patch Update (Auto-Merge)

**Objective**: Verify patch updates auto-merge and lockfile updates.

**Steps**:

1. Wait for patch update PR (e.g., pytest 8.0.1 → 8.0.2)
2. Verify `automerge` workflow runs (not `manual-review`)
3. Wait for CI to pass
4. Verify PR merges automatically
5. Verify lockfile update workflow runs
6. Check lockfile commit appears after merge

**Verification**:

```bash
git log --oneline -5 | grep "update uv.lock"
uv sync --frozen
uv run pytest
```

#### 2. Python Minor Update - Dev Dependency (Auto-Merge)

**Objective**: Verify dev dependency minors auto-merge.

**Steps**: Same as Test 1, but with minor update to pytest, ruff, mypy, or types-\*.

#### 3. Python Minor Update - Runtime Dependency (Manual Review)

**Objective**: Verify runtime dependency minors require manual review.

**Steps**:

1. Wait for minor update to PySide6, pydantic, aiohttp, etc.
2. Verify `needs-manual-review` label is added
3. Verify manual review comment with checklist
4. Manually approve and merge
5. Verify lockfile updates automatically

#### 4. Python Major Update (Manual Review)

**Objective**: Verify all major updates require manual review.

**Expected**: Same as Test 3, with emphasis on breaking changes.

#### 5. Docker Base Image Update (Manual Review)

**Objective**: Verify Docker updates require manual review.

**Expected**: Manual review with Docker-specific checklist.

#### 6. GitHub Actions Update (Auto-Merge for Patch/Minor)

**Objective**: Verify Actions patch/minor auto-merge, majors need review.

**Expected**: Auto-merge for patch/minor, manual review for major.

#### 7. Grouped Dependencies Update

**Objective**: Verify grouped updates work correctly.

**Expected**:

- PR title mentions group name
- Multiple packages updated
- Lockfile workflow uses `uv lock --upgrade` (full)

#### 8. Pre-commit Autoupdate Workflow

**Objective**: Verify hooks update automatically.

**Steps**:

1. Wait for Monday 10:00 UTC or manually trigger
2. Verify workflow runs `pre-commit autoupdate`
3. Check commits are made to dev branch
4. Verify hooks are at latest versions

#### 9. CI Timeout Handling

**Objective**: Verify monitor job handles long CI gracefully.

**Expected**:

- Monitor polls every 2 minutes
- Waits up to 45 minutes
- Posts timeout comment if needed (this is normal)
- Auto-merge still works when CI eventually passes

#### 10. Workflow Failure Recovery

**Objective**: Verify error handling when lockfile update fails.

**Expected**:

- Failure comment posted with manual instructions
- Link to failed workflow run
- Clear recovery steps

### Success Criteria

- ✅ At least 3 different update types tested
- ✅ Auto-merge works for eligible updates
- ✅ Manual review triggers for restricted updates
- ✅ UV lockfile updates automatically
- ✅ All workflows have successful runs
- ✅ No regressions in CI/CD pipeline

---

## Troubleshooting

### PR Not Auto-Merging

**Symptom**: PR approved but not merging automatically.

**Possible Causes**:

1. CI hasn't finished (wait up to 45 minutes)
2. CI failed (check "Checks" tab)
3. Update type requires manual review (check `needs-manual-review` label)
4. Auto-merge not enabled in repo settings

**Solution**:

- Wait for CI completion
- Fix CI failures if present
- Manually merge if it's a manual-review PR
- Verify repo settings allow auto-merge

### UV Lock Not Updated

**Symptom**: Dependabot PR merged but no lockfile commit.

**Possible Causes**:

1. Workflow still running (check Actions tab)
2. Workflow failed (check Actions tab for errors)
3. `pyproject.toml` wasn't modified (expected, no update needed)

**Solution**:

```bash
# Check workflow status
# Go to: Actions → Update UV Lock After Dependabot Merge

# If failed, manual update:
git checkout dev
git pull origin dev
uv lock --upgrade-package <package-name>
git add uv.lock
git commit -m "chore(deps): update uv.lock after <package> merge"
git push origin dev
```

### CI Taking Too Long

**Symptom**: Monitor job times out after 45 minutes.

**This is Normal**:

- Full CI matrix: 9 build jobs (3 OS × 3 Python versions)
- Plus security scans, docs build, etc.
- Can take 30-60 minutes total

**What Happens**:

- Monitor job times out but posts explanatory comment
- Auto-merge still works when CI eventually passes
- This timeout doesn't indicate a problem

### Merge Conflict

**Symptom**: Dependabot PR has merge conflicts.

**Solution**:

1. Comment: `@dependabot rebase`
2. Wait for Dependabot to rebase
3. CI runs again
4. Auto-merge proceeds if applicable

### Wrong Package in Lockfile

**Symptom**: Lockfile has unexpected versions.

**Cause**: Dependabot doesn't understand `uv.lock`.

**Solution**:

```bash
# Full lockfile rebuild
uv lock --upgrade

# Or specific package
uv lock --upgrade-package <package-name>

# Verify
uv sync --frozen
uv run pytest
```

---

## Monitoring

### Check Dependabot Status

**Via GitHub UI**:

- Go to: Insights → Dependency graph → Dependabot
- View: Update schedules, recent PRs, errors

**Via CLI**:

```bash
# List open Dependabot PRs
gh pr list --label dependencies --state open

# Check workflow runs
gh run list --workflow="dependabot-automerge.yml"
gh run list --workflow="dependabot-uv-lock-update.yml"
```

### Review Auto-Merge Stats

```bash
# Find auto-merged PRs
gh pr list \
  --state merged \
  --label dependencies \
  --search "auto-merge in:body" \
  --limit 20

# Find manual-review PRs
gh pr list \
  --state merged \
  --label needs-manual-review \
  --limit 20
```

---

## Configuration Files

| File                                             | Purpose                          |
| ------------------------------------------------ | -------------------------------- |
| `.github/dependabot.yml`                         | Dependabot update configuration  |
| `.github/workflows/dependabot-automerge.yml`     | Auto-merge logic and validation  |
| `.github/workflows/dependabot-uv-lock-update.yml`| UV lockfile automation           |
| `.github/workflows/pre-commit-autoupdate.yml`    | Pre-commit hook updates          |
| `.pre-commit-config.yaml`                        | Pre-commit hook versions         |
| `uv.lock`                                        | UV dependency lockfile           |
| `pyproject.toml`                                 | Python dependencies              |

---

## Best Practices

### For Maintainers

- Review manual-review PRs within 48 hours
- Don't disable Dependabot without team discussion
- Keep auto-merge rules conservative
- Update this doc when workflows change
- Monitor weekly for Dependabot activity

### For Contributors

- Don't merge Dependabot PRs manually unless approved
- Don't modify `uv.lock` in feature PRs
- Report any Dependabot issues encountered
- Read release notes for major updates you're reviewing

---

## Additional Resources

- **Dependabot Documentation**: <https://docs.github.com/en/code-security/dependabot>
- **UV Documentation**: <https://docs.astral.sh/uv/>
- **Repository Settings**: See [REPOSITORY_CONFIGURATION.md](REPOSITORY_CONFIGURATION.md)
- **Contributing Guide**: See [../CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Maintained By**: @mosh666
**Questions?** See [SUPPORT.md](SUPPORT.md)
