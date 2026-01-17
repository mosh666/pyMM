# Documentation Auto-Update System

> **Last Updated:** 2026-01-17 21:41 UTC


This directory contains scripts for automatically updating documentation with current project statistics.

## Overview

The documentation auto-update system keeps README.md and other documentation files synchronized with the
current state of the codebase. It uses HTML comment markers to identify sections that can be safely
auto-generated.

## Components

### 1. Update Script (`update_readme_stats.py`)

Python script that updates dynamic sections in README.md:

- **Project statistics** (Python versions, plugin count, test count, coverage)
- **Plugin list table** with status indicators
- **Lines of code** metrics

**Usage:**

```bash
# Update README.md
python scripts/update_readme_stats.py

# Preview changes without writing
python scripts/update_readme_stats.py --dry-run

# Verbose output
python scripts/update_readme_stats.py --verbose
```

**Just commands:**

```bash
# Update documentation
just update-docs

# Preview changes
just update-docs-dry
```

### 2. GitHub Actions Workflow (`.github/workflows/update-docs.yml`)

Automated workflow that runs in three scenarios:

1. **After Semantic Release** - Updates docs when new versions are released
2. **Weekly Schedule** - Sunday at 3 AM UTC
3. **Manual Trigger** - Via workflow dispatch

The workflow:

- Updates README.md statistics
- Verifies CHANGELOG.md is synced (handled by semantic-release)
- Triggers documentation site rebuild
- Commits changes with `[skip ci]` to avoid loops

### 3. HTML Comment Markers

Sections in README.md are wrapped with markers for safe auto-updates:

```markdown
<!-- AUTO-GENERATED:STATS:START -->
... generated content ...
<!-- AUTO-GENERATED:STATS:END -->

<!-- AUTO-GENERATED:PLUGIN_LIST:START -->
... generated content ...
<!-- AUTO-GENERATED:PLUGIN_LIST:END -->
```

## Adding New Auto-Generated Sections

To add a new auto-generated section:

1. **Add marker to README.md:**

   ```markdown
   <!-- AUTO-GENERATED:MY_SECTION:START -->
   (initial content - will be replaced)
   <!-- AUTO-GENERATED:MY_SECTION:END -->
   ```

2. **Update `scripts/update_readme_stats.py`:**

   ```python
   def generate_my_section() -> str:
       """Generate content for my section."""
       return "My generated content"

   # In main():
   updates = {
       "STATS": generate_stats_section(),
       "PLUGIN_LIST": generate_plugin_table(),
       "MY_SECTION": generate_my_section(),  # Add here
   }
   ```

3. **Test locally:**

   ```bash
   just update-docs-dry
   ```

## Best Practices

### DO ✅

- Use for factual, objective data (counts, versions, lists)
- Keep markers clearly visible in README source
- Test with `--dry-run` before committing
- Review auto-generated changes before pushing

### DON'T ❌

- Auto-generate marketing copy or prose
- Update files tracked by other automation (CHANGELOG.md is handled by semantic-release)
- Create circular dependencies (don't auto-update files that trigger the workflow)
- Modify sections outside the markers

## Workflow Integration

### Pre-Commit Hook (Optional)

To run updates before each commit, add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: update-readme
      name: Update README Statistics
      entry: python scripts/update_readme_stats.py
      language: system
      pass_filenames: false
      always_run: true
```

**Note:** Not enabled by default to avoid commit loops. Use manual `just update-docs` instead.

### Pre-Push Hook (Safer)

For validation before pushing, add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: check-readme-sync
      name: Check README is synced
      entry: python scripts/update_readme_stats.py --dry-run
      language: system
      pass_filenames: false
      always_run: true
      stages: [pre-push]
```

## Maintenance

### Updating Statistics Sources

The script reads from:

- `pyproject.toml` - Python versions, dependencies
- `plugins/` - Plugin directories and manifests
- `tests/` - Test files
- `htmlcov/index.html` - Coverage data

If these locations change, update the corresponding functions in `update_readme_stats.py`.

### Debugging

Enable verbose mode to see what's being updated:

```bash
python scripts/update_readme_stats.py --verbose
```

Check GitHub Actions logs:

- Go to Actions → Update Documentation
- View run details for commit messages and summaries

## Security Considerations

- Workflow uses `GITHUB_TOKEN` with `contents: write` permission
- Commits are attributed to `github-actions[bot]`
- `[skip ci]` prevents infinite workflow loops
- No external data sources - all data from local repository

## Related Documentation

- [README.md](../README.md) - Main documentation with auto-generated sections
- [CHANGELOG.md](../CHANGELOG.md) - Release notes (managed by semantic-release)
- [.github/workflows/update-docs.yml](../.github/workflows/update-docs.yml) - Automation workflow
- [.github/workflows/semantic-release.yml](../.github/workflows/semantic-release.yml) - Release automation
