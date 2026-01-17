# Scripts Directory

> **Last Updated:** 2026-01-17 21:41 UTC


Utility scripts for development, CI/CD, and automation.

## Available Scripts

### validate_skip_ci.py

**Purpose:** Pre-commit hook that validates proper use of `[skip ci]` and related skip directives in commit messages.

**Usage:**

```bash
# Automatic (via pre-commit)
pre-commit install
git commit -m "fix: something [skip ci]"  # Validated automatically

# Manual validation
python scripts/validate_skip_ci.py
```

**What it validates:**

- ✅ Blocks `[skip ci]` on code changes in `app/` or `tests/`
- ✅ Blocks `[skip ci]` on workflow changes
- ✅ Blocks `[skip tests]` when tests are modified
- ⚠️  Warns on `[skip ci]` with config changes
- ⚠️  Warns on `[skip tests]` with code changes
- ⚠️  Warns on `[skip lint]` with code changes

**Exit Codes:**

- `0` - Valid usage or no skip directive (allows commit)
- `1` - Invalid usage (blocks commit)
- `2` - Warning only (allows commit with warning)

**Example Output:**

```text
✅ [skip ci] usage validated - appropriate for changes
```

```text
❌ ERROR: [skip ci] cannot be used with code changes in app/
   Changed files: app/core/project.py, app/ui/main_window.py
```

### update_readme_stats.py

**Purpose:** Automatically updates documentation with current project statistics
(plugin count, test count, Python versions, etc.).

**Quick Usage:**

```bash
# Update documentation
just update-docs

# Preview changes
python scripts/update_readme_stats.py --dry-run
```

**Full Documentation:** See [README_AUTO_UPDATE.md](README_AUTO_UPDATE.md) for
complete guide on the documentation auto-update system.

## Integration

The validation script is integrated with pre-commit:

```yaml
# In .pre-commit-config.yaml
- repo: local
  hooks:
    - id: validate-skip-ci
      name: Validate [skip ci] Directives
      entry: python scripts/validate_skip_ci.py
      language: system
      stages: [commit-msg]
```

## Development

To test the validation script:

```bash
# Test with mock commit
echo "fix: bug [skip ci]" | python scripts/validate_skip_ci.py

# Test with actual staged files
git add app/core/something.py
git commit -m "fix: bug [skip ci]"  # Should block
```
