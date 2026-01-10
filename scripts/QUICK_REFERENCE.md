# 📝 Quick Reference: Documentation Auto-Update

## 🎯 What Was Implemented

✅ **3 Solutions Complete:**

1. Python script for manual README updates
2. GitHub Action for automated post-release updates
3. Dynamic sections in README.md with HTML markers

---

## 🚀 Quick Start

### Test It Locally

```bash
# Preview what would change (safe - no writes)
just update-docs-dry

# Apply changes to README.md
just update-docs

# Or use Python directly:
python scripts/update_readme_stats.py --verbose
```

### First Commit

```bash
# Review changes
git status
git diff README.md

# Commit everything
git add .
git commit -m "feat: add documentation auto-update system

- Add update_readme_stats.py script for manual updates
- Add update-docs.yml workflow for post-release automation
- Add dynamic sections to README.md (stats, plugin list)
- Update justfile with update-docs commands"

# Push when ready (DON'T push yet - you said you'll do it manually!)
```

---

## 📋 New Files Created

| File | Purpose |
| ---- | ------- |
| `scripts/update_readme_stats.py` | Main update script |
| `.github/workflows/update-docs.yml` | Automated workflow |
| `scripts/README_AUTO_UPDATE.md` | Detailed documentation |
| `scripts/IMPLEMENTATION_SUMMARY.md` | Implementation summary |
| `scripts/QUICK_REFERENCE.md` | This file |

---

## 🔄 Modified Files

| File | Changes |
| ---- | ------- |
| `README.md` | Added 2 auto-generated sections with HTML markers |
| `justfile` | Added `update-docs` and `update-docs-dry` commands |

---

## 🤖 GitHub Action Details

**Workflow:** `.github/workflows/update-docs.yml`

**Triggers:**

- ✅ After semantic-release (main/dev)
- ✅ Weekly (Sundays 3 AM UTC)
- ✅ Manual dispatch

**What It Does:**

1. Updates README statistics
2. Commits with `[skip ci]` to prevent loops
3. Verifies CHANGELOG.md sync
4. Triggers docs site rebuild

**First Run:** Will happen automatically after your next release or you can trigger manually via GitHub Actions UI.

---

## 📊 What Gets Updated

### Project Statistics Section

- Python versions (from pyproject.toml)
- Plugin count
- Test count
- Coverage percentage
- Lines of code
- Documentation lines

### Plugin List Section

- All plugins in `plugins/` directory
- Status (configured vs not configured)
- Alphabetically sorted

---

## 🔧 Commands Reference

```bash
# Preview changes (dry-run)
just update-docs-dry
python scripts/update_readme_stats.py --dry-run

# Apply updates
just update-docs
python scripts/update_readme_stats.py

# Verbose output
python scripts/update_readme_stats.py --verbose

# Help
python scripts/update_readme_stats.py --help
```

---

## 🛡️ Safety Features

✅ **No Commit Loops**

- Workflow uses `[skip ci]`
- Only updates between HTML markers
- No pre-commit hook (you control when to run)

✅ **Preserves Manual Content**

- Only touches marked sections
- Marketing copy untouched
- CHANGELOG.md left to semantic-release

✅ **Safe Testing**

- Dry-run mode previews changes
- No writes without confirmation
- Git-friendly output

---

## 📖 Documentation

For detailed information, see:

- **[scripts/IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - What was built and why
- **[scripts/README_AUTO_UPDATE.md](README_AUTO_UPDATE.md)** - How to use and extend the system
- **[.github/workflows/update-docs.yml](../.github/workflows/update-docs.yml)** - Workflow configuration

---

## 🎯 Typical Workflow

### Developer (Manual)

```bash
# 1. Make code changes (add plugin, write tests, etc.)
git add app/ tests/ plugins/

# 2. Update documentation to reflect changes
just update-docs

# 3. Review the updates
git diff README.md

# 4. Commit everything together
git commit -m "feat: add new feature with updated docs"

# 5. Push (you do this manually)
```

### CI/CD (Automated)

```text
Push to dev → Semantic Release → Update-Docs Workflow
                ↓                        ↓
        Creates v0.5.0-beta.1    Updates README stats
                                 Commits + Pushes
```

---

## ⚠️ Important Notes

1. **CHANGELOG.md** - Do NOT auto-update this! It's managed by semantic-release
2. **Badges** - Already dynamic via shields.io, no update needed
3. **Marketing Content** - Keep manual for quality control
4. **Testing** - Always dry-run first when testing new sections

---

## 🐛 Troubleshooting

**Script fails to find files:**

- Ensure you're running from project root (`D:\pyMM`)
- Check `PROJECT_ROOT` in script points to correct location

**Workflow doesn't trigger:**

- Check semantic-release completed successfully
- Verify workflow file is on correct branch
- Look at Actions tab for error messages

**Wrong statistics shown:**

- Run tests first: `just test-cov` (generates coverage data)
- Ensure htmlcov/index.html exists
- Check pyproject.toml classifiers are current

**Git commit loop:**

- Verify `[skip ci]` is in commit message
- Check workflow only triggers on main/dev branches
- Don't add pre-commit hook without careful testing

---

## 🎉 You're All Set

The documentation auto-update system is now fully operational. Test it locally, review the changes, and commit
when ready. The GitHub Action will take care of future updates automatically after releases.

**Questions?** See the detailed documentation in `scripts/README_AUTO_UPDATE.md`
