# Repository Configuration Guide

> **Last Updated:** 2026-01-17 21:41 UTC
\nComplete guide for configuring GitHub repository settings for the pyMM project.

---

## Table of Contents

1. [Quick Start Checklist](#quick-start-checklist)
2. [Initial Setup](#initial-setup)
3. [Branch Protection](#branch-protection)
4. [Workflow Permissions](#workflow-permissions)
5. [Verification & Testing](#verification--testing)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start Checklist

Complete these 4 essential settings before using GitHub Actions workflows:

### ✅ Required Settings

Navigate to: **Settings → Actions → General → Workflow permissions**

- [ ] Select: **Read and write permissions**
- [ ] Check: ☑️ **Allow GitHub Actions to create and approve pull requests**
- [ ] Click **Save**

Navigate to: **Settings → General → Pull Requests**

- [ ] Check: ☑️ **Allow auto-merge**
- [ ] Click **Save changes**

Create label: **needs-manual-review**

- [ ] Name: `needs-manual-review`
- [ ] Description: `Requires human review before merging`
- [ ] Color: `#fbca04` (yellow)

### 🔍 Quick Verification Script

Run this PowerShell script to verify all settings:

```powershell
Write-Host "🔍 Verifying Repository Configuration..." -ForegroundColor Cyan

# Check auto-merge
$autoMerge = gh api repos/mosh666/pyMM | ConvertFrom-Json | Select-Object -ExpandProperty allow_auto_merge
Write-Host "✓ Auto-merge enabled: $autoMerge" -ForegroundColor $(if ($autoMerge) {"Green"} else {"Red"})

# Check workflow permissions
$perms = gh api repos/mosh666/pyMM/actions/permissions | ConvertFrom-Json
Write-Host "✓ Workflow permissions: $($perms.default_workflow_permissions)" -ForegroundColor $(if ($perms.default_workflow_permissions -eq "write") {"Green"} else {"Yellow"})

# Check label
$label = gh label list --json name | ConvertFrom-Json | Where-Object { $_.name -eq "needs-manual-review" }
Write-Host "✓ Label 'needs-manual-review' exists: $(if ($label) {'Yes'} else {'No'})" -ForegroundColor $(if ($label) {"Green"} else {"Red"})

Write-Host "`n✅ Setup verification complete!" -ForegroundColor Green
```

---

## Initial Setup

### 1. Enable Actions Write Permissions

**Why**: Workflows need to commit lockfile updates, approve PRs, create releases, and upload security scan results.

**Steps**:

1. Go to repository **Settings**
2. Navigate to **Actions** → **General**
3. Scroll down to **Workflow permissions**
4. Select: **Read and write permissions**
5. Check: ☑️ **Allow GitHub Actions to create and approve pull requests**
6. Click **Save**

**Verification**:

```bash
gh api repos/mosh666/pyMM/actions/permissions
```

Expected output:

```json
{
  "enabled": true,
  "allowed_actions": "all",
  "default_workflow_permissions": "write",
  "can_approve_pull_request_reviews": true
}
```

---

### 2. Enable Auto-Merge

**Why**: Allows Dependabot PRs to merge automatically when CI passes.

**Steps**:

1. Go to repository **Settings**
2. Navigate to **General**
3. Scroll down to **Pull Requests** section
4. Check: ☑️ **Allow auto-merge**
5. **Optional**: Also enable:

   - ☑️ **Allow squash merging** (for cleaner history)
   - ☑️ **Automatically delete head branches** (cleanup after merge)
6. Click **Save changes**

**Verification**:

```bash
gh api repos/mosh666/pyMM | jq '.allow_auto_merge'
```

Expected: `true`

---

### 3. Create GitHub Label

**Why**: Used to mark Dependabot PRs that need manual review.

**Label Details**:

- **Name**: `needs-manual-review`
- **Description**: `Requires human review before merging`
- **Color**: `#fbca04` (yellow)

**Steps**:

#### Option A: Via GitHub Web UI

1. Go to repository **Issues** tab
2. Click **Labels** button
3. Click **New label**
4. Enter label details
5. Click **Create label**

#### Option B: Via GitHub CLI

```bash
gh label create needs-manual-review \
  --description "Requires human review before merging" \
  --color "fbca04" \
  --repo mosh666/pyMM
```

#### Option C: Via PowerShell

```powershell
gh label create needs-manual-review `
  --description "Requires human review before merging" `
  --color "fbca04"
```

**Verification**:

```bash
gh label list | grep "needs-manual-review"
```

---

### 4. Configure Code Security

Navigate to: **Settings → Code security and analysis**

**Recommended settings**:

- ☑️ **Dependency graph** (required for Dependabot)
- ☑️ **Dependabot alerts**
- ☑️ **Dependabot security updates**
- ☑️ **Secret scanning**
- ☑️ **Push protection**

---

## Branch Protection

### Current Status

The `dev` branch has basic protection:

- ✅ Required pull request reviews: 1 approval
- ✅ Strict status checks enabled
- ✅ Enforce admins enabled
- ⚠️ No specific status checks configured

### Important: User vs Organization Repositories

This is a **personal user repository** (`mosh666/pyMM`), not an organization repository:

- ❌ **Bypass allowances via API are NOT available** (organization-only feature)
- ✅ **GitHub Auto-Merge works WITHOUT bypass allowances!**
- ✅ **The Dependabot workflow will work as designed**

### How Auto-Merge Works

1. **Workflow approves the PR** using `gh pr review --approve`
   - Satisfies the "1 approval" requirement
   - Approval comes from GitHub Actions with write permissions

2. **Workflow enables auto-merge** using `gh pr merge --auto --merge`
   - Auto-merge queues the PR for merging
   - Merge only proceeds once ALL status checks pass

3. **Status checks are still required**
   - PR won't merge until CI passes
   - Maintains code quality standards

### Configuration Options

#### Option A: Keep Current Settings (Recommended)

**No changes needed!** Current configuration works with auto-merge workflow:

- Dependabot PRs auto-approved by workflow
- Auto-merge waits for CI checks
- Workflow approval satisfies 1 review requirement

#### Option B: Add Specific Status Checks (Optional)

To ensure specific CI jobs must pass:

1. Go to: <https://github.com/mosh666/pyMM/settings/branches>
2. Click "Edit" next to the `dev` branch rule
3. Under "Require status checks to pass before merging":
   - ✅ Enable "Require status checks to pass before merging"
   - ✅ Enable "Require branches to be up to date before merging"
   - Search and select specific checks:
     - `lint`
     - `type-check`
     - `test (3.12, ubuntu-latest)`
     - `test (3.13, ubuntu-latest)`
     - `test (3.14, ubuntu-latest)`
     - `test (3.12, windows-latest)`
     - `test (3.13, windows-latest)`
     - `test (3.14, windows-latest)`
     - `test (3.12, macos-latest)`
     - `test (3.13, macos-latest)`
     - `test (3.14, macos-latest)`
4. Click "Save changes"

#### Option C: Require Any Checks (Flexible)

If you prefer flexibility:

1. Go to: <https://github.com/mosh666/pyMM/settings/branches>
2. Click "Edit" next to the `dev` branch rule
3. Under "Require status checks to pass before merging":
   - ✅ Enable "Require status checks to pass before merging"
   - ✅ Enable "Require branches to be up to date before merging"
   - Do NOT select specific checks
4. Click "Save changes"

This requires any checks that run to pass, but doesn't mandate specific ones.

---

## Workflow Permissions

### Overview

All workflows use the built-in `GITHUB_TOKEN` with explicitly declared permissions. No Personal Access Tokens (PATs) required.

### Permissions Summary Table

| Workflow | Permissions | Token |
| ----------------------------- | ------------------------------------------------------------------------------------------------ | ------------------ |
| **semantic-release.yml** | `contents:write`, `issues:write`, `pull-requests:write`, `id-token:write`, `attestations:write` | ✅ `GITHUB_TOKEN` |
| **cleanup-beta-releases.yml** | `contents:write` | ✅ `GH_TOKEN` |
| **build.yml** | `contents:read`, `id-token:write`, `attestations:write` | ❌ None |
| **ci.yml** | `contents:read`, `pull-requests:read`, `checks:write`, `statuses:write` | ❌ None |
| **dependabot-automerge.yml** | `contents:write`, `pull-requests:write` | ✅ `GITHUB_TOKEN` |
| **dependabot-uv-lock-update.yml** | `contents:write` | ✅ `GITHUB_TOKEN` |
| **pre-commit-autoupdate.yml** | `contents:write`, `pull-requests:write` | ✅ `GITHUB_TOKEN` |
| **update-docs.yml** | `contents:write`, `pull-requests:write` | ✅ `GITHUB_TOKEN` |
| **docs.yml** | `contents:read`, `pages:write`, `id-token:write` | ❌ None |
| **security.yml** | `contents:read`, `security-events:write`, `actions:read` | ❌ None |
| **codeql.yml** | `security-events:write`, `packages:read`, `actions:read`, `contents:read` | ❌ None |
| **scorecard.yml** | `read-all` (top), `security-events:write`, `id-token:write`, `contents:read`, `actions:read` (job) | ❌ None |
| **labeler.yml** | `contents:read`, `pull-requests:write` | ✅ `GITHUB_TOKEN` |

### Permission Details

#### Dependabot Workflows

**dependabot-automerge.yml**:

- `contents:write` - Merge PRs
- `pull-requests:write` - Approve, comment, enable auto-merge

**dependabot-uv-lock-update.yml**:

- `contents:write` - Commit updated lockfile

**pre-commit-autoupdate.yml**:

- `contents:write` - Commit hook updates
- `pull-requests:write` - Create PRs (future use)

#### Release Workflows

**semantic-release.yml**:

- `contents:write` - Create releases, push tags, upload assets
- `issues:write` - Generate release notes with issue references
- `pull-requests:write` - Link PRs to releases
- `id-token:write` - Generate attestations
- `attestations:write` - Write artifact attestations

**cleanup-beta-releases.yml**:

- `contents:write` - Delete old releases

#### Documentation Workflows

**docs.yml**:

- `contents:read` - Read documentation source
- `pages:write` - Deploy to GitHub Pages
- `id-token:write` - Authenticate with Pages

**update-docs.yml**:

- `contents:write` - Commit README statistics updates
- `pull-requests:write` - Create PRs for doc updates (future)

#### CI/CD Workflows

**ci.yml**:

- `contents:read` - Read repository code
- `pull-requests:read` - Read PR information
- `checks:write` - Report check status
- `statuses:write` - Update commit statuses

**build.yml**:

- `contents:read` - Read source code for builds
- `id-token:write` - Generate attestations (future use)
- `attestations:write` - Write attestations (future use)

#### Security Workflows

**security.yml**, **codeql.yml**:

- `contents:read` - Read source code
- `security-events:write` - Upload security scan results
- `actions:read` - Read workflow information
- `packages:read` - Fetch CodeQL packs

**scorecard.yml**:

- `read-all` (top-level for comprehensive analysis)
- `security-events:write` - Upload scorecard SARIF
- `id-token:write` - Authenticate scorecard
- `contents:read`, `actions:read` - Analyze repository

#### Automation Workflows

**labeler.yml**:

- `contents:read` - Read file changes
- `pull-requests:write` - Add labels to PRs

### Security Best Practices

1. **Minimal Permissions Principle**
   - Read-only by default
   - Write permissions only when required
   - Job-level permissions override top-level when more restrictive

2. **No Personal Access Tokens Required**
   - All workflows use built-in `GITHUB_TOKEN`
   - Automatically scoped to repository
   - Expires after workflow completion
   - No maintenance required

3. **Third-party Action Security**
   - All actions pinned to specific versions
   - Official actions: `actions/checkout@v6`, `actions/setup-python@v6`, `github/codeql-action@v4`
   - Verified actions: `ossf/scorecard-action@v2.4.0`
   - Trusted actions: `softprops/action-gh-release@v2`

4. **Concurrency Controls**
   - `semantic-release.yml` - One release at a time per branch
   - `dependabot-automerge.yml` - One merge per PR
   - `ci.yml` - Cancel old runs on new push
   - `docs.yml` - Prevent conflicting deployments

---

## Verification & Testing

### Check Current Settings

```bash
# Full repository info
gh api repos/mosh666/pyMM | jq '{
  name: .name,
  auto_merge: .allow_auto_merge,
  default_branch: .default_branch
}'

# Workflow permissions
gh api repos/mosh666/pyMM/actions/permissions | jq '{
  enabled: .enabled,
  default_workflow_permissions: .default_workflow_permissions,
  can_approve_pull_request_reviews: .can_approve_pull_request_reviews
}'

# Verify label exists
gh label list --json name,color,description | \
  jq '.[] | select(.name == "needs-manual-review")'
```

### Test Workflows

```bash
# Test semantic release (read-only check)
gh workflow run semantic-release.yml --ref dev -f branch=dev -f force=false

# Test beta cleanup (dry run)
gh workflow run cleanup-beta-releases.yml --ref dev -f dry_run=true

# Test pre-commit update
gh workflow run pre-commit-autoupdate.yml

# Check for permission errors
gh run list --workflow=semantic-release.yml --limit 1
gh run list --workflow=dependabot-automerge.yml --limit 5
```

### Verify Workflow Files

```bash
# Check all workflows have permissions declarations
cd .github/workflows
Get-ChildItem *.yml | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $hasPerms = $content -match "permissions:"
    $status = if ($hasPerms) { "✅" } else { "❌" }
    Write-Host "$status $($_.Name)"
}
```

Expected: All workflows show ✅

### Test Auto-Merge Workflow

Create a test PR:

```bash
# Create test branch
git checkout -b test-automerge
echo "# Test" >> README.md
git add README.md
git commit -m "test: verify auto-merge workflow"
git push origin test-automerge

# Create PR targeting dev
gh pr create --base dev --title "Test: Auto-merge workflow" --body "Testing branch protection"

# Watch workflow run
gh run watch
```

Verify:

- CI runs successfully
- For Dependabot PRs: Workflow posts comment and enables auto-merge
- PR merges automatically after CI passes

---

## Troubleshooting

### "Resource not accessible by integration"

**Problem**: Workflow trying to perform an action without proper permissions.

**Solutions**:

1. Check repository settings: **Settings → Actions → General → Workflow permissions**
2. Ensure "Read and write permissions" is selected
3. Verify "Allow GitHub Actions to create and approve pull requests" is checked
4. Wait a few minutes for settings to propagate

### Dependabot PRs Not Auto-Merging

**Problem**: PRs approved but not merging automatically.

**Possible Causes**:

1. CI hasn't finished (wait up to 45 minutes)
2. CI failed (check "Checks" tab)
3. Update type requires manual review (check `needs-manual-review` label)
4. Auto-merge not enabled in repo settings

**Solutions**:

- Wait for CI completion
- Fix CI failures if present
- Manually merge if it's a manual-review PR
- Verify repo settings: `gh api repos/mosh666/pyMM | jq '.allow_auto_merge'`

### "refusing to allow a GitHub App to create or update workflow"

**Problem**: Workflow trying to modify `.github/workflows/` files.

**Solution**: This is a security feature - workflows cannot modify themselves. Use manual review for workflow updates.

### Workflows Not Running

**Problem**: No workflow runs appear for PRs.

**Solutions**:

1. Check `.github/workflows/` files are in `dev` branch
2. Verify workflows have correct trigger conditions
3. Check Actions tab for disabled workflows
4. Ensure Actions are enabled: **Settings → Actions → General**

### Label Not Found Error

**Problem**: Workflow fails with "label not found" error.

**Solutions**:

1. Create the `needs-manual-review` label (see Initial Setup section)
2. Check label name matches exactly (case-sensitive)
3. Verify: `gh label list | grep needs-manual-review`

### "Could not create or update release"

**Problem**: semantic-release workflow fails to create releases.

**Solutions**:

1. Check `contents:write` permission is declared
2. Verify workflow permissions are enabled
3. Check branch protection allows releases

### "Not authorized to access attestations"

**Problem**: Build workflow fails when generating attestations.

**Solutions**:

1. Add `id-token:write` and `attestations:write` permissions
2. Verify Actions have proper permissions enabled

---

## Final Checklist

Before merging to main:

- [ ] Repository settings: "Read and write permissions" enabled
- [ ] Repository settings: "Allow GitHub Actions to create and approve pull requests" enabled
- [ ] Repository settings: "Allow auto-merge" enabled
- [ ] Label `needs-manual-review` created
- [ ] All 13 workflows have `permissions:` declarations
- [ ] Tested semantic-release workflow on dev branch
- [ ] Tested cleanup-beta-releases workflow (dry run)
- [ ] Tested Dependabot auto-merge workflow
- [ ] Verified no permission errors in workflow logs
- [ ] Branch protection configured (optional but recommended)
- [ ] Code security features enabled

---

## Additional Resources

- **GitHub Actions Permissions**: <https://docs.github.com/en/actions/security-guides/automatic-token-authentication>
- **Auto-merge Documentation**: <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/incorporating-changes-from-a-pull-request/automatically-merging-a-pull-request>
- **Branch Protection**: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches>
- **GITHUB_TOKEN Permissions**: <https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token>
- **Artifact Attestations**: <https://docs.github.com/en/actions/security-guides/using-artifact-attestations>
- **Dependabot Configuration**: See [DEPENDABOT.md](DEPENDABOT.md)

---

**Maintained By**: @mosh666
**Questions?** See [SUPPORT.md](SUPPORT.md)
