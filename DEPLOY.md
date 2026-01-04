# Deployment Guide for pyMediaManager v0.0.1

This guide walks through publishing pyMediaManager to GitHub and creating the first release.

## Prerequisites

- GitHub account (mosh666)
- Git configured with GitHub credentials
- Repository access rights

## Step 1: Create GitHub Repository

### Option A: Via GitHub Web Interface (Recommended)

1. Go to https://github.com/new
2. Configure repository:
   - **Owner:** mosh666
   - **Repository name:** pyMM
   - **Description:** Portable Python-based media management application with modern Fluent Design UI
   - **Visibility:** Public
   - **Initialize:** ❌ Do NOT initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Option B: Via GitHub CLI

```bash
gh repo create mosh666/pyMM --public --description "Portable Python-based media management application with modern Fluent Design UI"
```

## Step 2: Push Local Repository to GitHub

After creating the empty repository on GitHub:

```powershell
# Verify remote is configured
git remote -v

# If not configured, add it
git remote add origin https://github.com/mosh666/pyMM.git

# Push all commits and tags
git push -u origin main
git push origin v0.0.1

# Verify push succeeded
git log --oneline --decorate -5
```

**Expected commits to be pushed:**
```
192256f docs: add comprehensive project status document
401fba9 fix: escape sequence warning in docstring
acc0bfb feat: implement portable architecture with drive-root folders
4c55476 feat: implement PySide6 Fluent UI with first-run wizard
cee270f feat: implement plugin system with YAML manifests
5cfbd5e feat: implement core service layer with comprehensive tests
521be18 (tag: v0.0.1) chore: initial project structure with setuptools-scm v0.0.1
```

## Step 3: Verify GitHub Actions Workflows

After pushing, GitHub Actions should automatically trigger:

### CI Workflow (ci.yml)
- **Triggers:** Every push to main
- **Actions:**
  - Run tests with Python 3.12 and 3.13
  - Lint with Ruff, format check with Black
  - Type check with MyPy
  - Upload coverage to Codecov
  - Lint markdown documentation

**Check status:** https://github.com/mosh666/pyMM/actions/workflows/ci.yml

### Build Workflow (build.yml)
- **Triggers:** Manual dispatch or called by release workflow
- **Actions:**
  - Download embeddable Python (3.12 & 3.13)
  - Install dependencies to lib-py{version}/
  - Generate frozen requirements
  - Create portable ZIP archives
  - Generate SHA256 checksums

**Check status:** https://github.com/mosh666/pyMM/actions/workflows/build.yml

## Step 4: Create GitHub Release

### Option A: Automatic Release via Tag Push

Since we already have the `v0.0.1` tag, pushing it triggers the release workflow:

```powershell
git push origin v0.0.1
```

This will:
1. Trigger `.github/workflows/release.yml`
2. Build portable packages for both Python versions
3. Create a GitHub Release with artifacts:
   - `pyMM-v0.0.1-py312-win64.zip`
   - `pyMM-v0.0.1-py313-win64.zip`
   - SHA256 checksums
   - Release notes (if CHANGELOG.md exists)

### Option B: Manual Release via GitHub Web Interface

1. Go to https://github.com/mosh666/pyMM/releases/new
2. Configure release:
   - **Tag:** v0.0.1 (select existing or create new)
   - **Release title:** pyMediaManager v0.0.1 - Initial Release
   - **Description:**
     ```markdown
     # 🎉 pyMediaManager v0.0.1 - Initial Release

     First release of pyMediaManager, a complete Python rewrite of PSmediaManager with modern PySide6 Fluent UI.

     ## Features

     - ✨ Modern Fluent Design UI with PySide6
     - 💾 Fully portable - runs from removable drives
     - 🔌 Plugin system for external tools (digiKam, FFmpeg, Git, etc.)
     - 📁 Project-based workflow with version control integration
     - 🔒 Secure configuration with sensitive data redaction
     - 📊 Comprehensive logging (Rich console + rotating files)

     ## What's Included

     - Embedded Python 3.12 or 3.13 runtime
     - All Python dependencies bundled
     - 9 plugin manifests (6 mandatory, 3 optional)
     - First-run wizard for setup
     - Drive root storage (pyMM.Projects, pyMM.Logs)

     ## Download

     Choose the package matching your preferred Python version:
     - **pyMM-v0.0.1-py313-win64.zip** (Recommended - Python 3.13)
     - **pyMM-v0.0.1-py312-win64.zip** (Python 3.12)

     ## Quick Start

     1. Download and extract to your portable drive (e.g., D:\pyMM)
     2. Run: `python313\python.exe launcher.py`
     3. Complete the first-run wizard
     4. Start managing your media projects!

     ## Documentation

     - 📖 [Architecture Guide](https://github.com/mosh666/pyMM/blob/main/docs/architecture.md)
     - 🤝 [Contributing Guide](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md)
     - 📊 [Project Status](https://github.com/mosh666/pyMM/blob/main/docs/project-status.md)

     ## System Requirements

     - Windows 10 or later (64-bit)
     - At least 500MB free space on portable drive
     - Internet connection for plugin downloads

     ## Known Limitations

     - Windows only (Linux/macOS support planned)
     - Plugin downloads not yet implemented (infrastructure complete)
     - Project management is placeholder (v0.1.0 target)

     ## Credits

     Original PowerShell implementation: [PSmediaManager](https://github.com/mosh666/PSmediaManager)
     ```

3. **Attach files** (if building manually):
   - Run build workflow manually to generate artifacts
   - Download artifacts from workflow run
   - Upload ZIP files and checksums

4. Click "Publish release"

### Option C: Manual Build and Release

If GitHub Actions don't run automatically:

```powershell
# Navigate to project directory
cd D:\pyMM

# Run manual build script (create if needed)
python tools/build_portable.py --python-version 3.12
python tools/build_portable.py --python-version 3.13

# This will create:
# dist/pyMM-v0.0.1-py312-win64.zip
# dist/pyMM-v0.0.1-py313-win64.zip
# dist/checksums.txt

# Upload to GitHub Release manually
```

## Step 5: Verify Release

After release is published:

1. **Check Release Page:** https://github.com/mosh666/pyMM/releases/tag/v0.0.1
2. **Download Test:**
   - Download one of the ZIP files
   - Extract to a test location (e.g., E:\test-pyMM)
   - Verify directory structure
   - Check python313\ folder exists
   - Check lib-py313\ folder has packages

3. **Functional Test:**
   ```powershell
   # Extract to test drive
   E:\test-pyMM\python313\python.exe E:\test-pyMM\launcher.py
   ```
   
   - First-run wizard should appear
   - Storage page should detect removable drives
   - Plugin page should list 9 plugins
   - Main window should open after wizard

4. **Verify Portable Folders:**
   - Check E:\pyMM.Projects exists
   - Check E:\pyMM.Logs exists
   - Verify log file is being written

## Step 6: Post-Release Tasks

### Update Repository Settings

1. **About Section:**
   - Add description
   - Add topics: `python`, `pyside6`, `fluent-design`, `media-management`, `portable`, `windows`
   - Add website (if applicable)

2. **Branch Protection (optional):**
   - Settings → Branches → Add rule for `main`
   - Require pull request reviews
   - Require status checks to pass

3. **Codecov Integration:**
   - Go to https://codecov.io
   - Add repository mosh666/pyMM
   - Copy CODECOV_TOKEN to repository secrets

### Create Project Board (optional)

1. Go to https://github.com/mosh666/pyMM/projects
2. Create project: "pyMediaManager Development"
3. Add columns: Todo, In Progress, Done
4. Link issues from docs/project-status.md "Next Steps"

### Create Initial Issues

Based on the project status "Future Enhancements":

```markdown
- [ ] #1: Implement plugin download functionality
- [ ] #2: Build project creation wizard
- [ ] #3: Add Git integration (clone, commit, push)
- [ ] #4: Integrate digiKam database
- [ ] #5: Create settings persistence UI
- [ ] #6: Add Linux/macOS support
- [ ] #7: Implement auto-update mechanism
- [ ] #8: Add plugin version checking
```

## Troubleshooting

### Problem: "Repository not found" error

**Solution:**
```powershell
# Remove existing remote
git remote remove origin

# Re-add with correct URL
git remote add origin https://github.com/mosh666/pyMM.git

# Try push again
git push -u origin main
```

### Problem: Authentication failed

**Solution:**
```powershell
# Configure Git credentials (Windows)
git config --global credential.helper wincred

# Or use GitHub CLI
gh auth login

# Or use SSH instead of HTTPS
git remote set-url origin git@github.com:mosh666/pyMM.git
```

### Problem: GitHub Actions not running

**Solution:**
1. Check Actions tab is enabled in repository settings
2. Verify workflow files are in `.github/workflows/`
3. Check workflow syntax with: `gh workflow view`
4. Manually trigger with: `gh workflow run build.yml`

### Problem: Build workflow fails

**Solution:**
1. Check workflow run logs
2. Verify Python download URLs are current
3. Check for missing dependencies in pyproject.toml
4. Test build locally first

## Next Steps After Deployment

1. **Monitor First Release:**
   - Watch for issues/bug reports
   - Check Codecov for coverage trends
   - Monitor GitHub Insights for activity

2. **Community Building:**
   - Create discussion forum
   - Add CONTRIBUTORS.md
   - Create issue templates
   - Set up pull request template

3. **Documentation:**
   - Add screenshots to README
   - Record demo video
   - Create user guide
   - Write plugin development tutorial

4. **Development:**
   - Start v0.1.0 milestone
   - Implement plugin downloads
   - Build project management features
   - Expand test coverage to 90%+

## Success Checklist

- [ ] GitHub repository created
- [ ] All commits pushed to main branch
- [ ] v0.0.1 tag pushed
- [ ] CI workflow passed
- [ ] Build workflow completed
- [ ] Release published with artifacts
- [ ] Release download tested
- [ ] Application runs from portable ZIP
- [ ] First-run wizard works
- [ ] Portable folders created at drive root
- [ ] Logs written successfully
- [ ] Repository settings configured
- [ ] Codecov integrated
- [ ] Initial issues created

---

**Document Version:** 1.0  
**Last Updated:** January 4, 2026  
**Status:** Ready for deployment
