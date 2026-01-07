<!-- markdownlint-disable MD013 MD031 MD032 MD033 MD034 MD036 MD040 MD047 MD051 MD060 -->

# 🔒 Security Policy

> **Last Updated:** January 7, 2026
> **Contact:** 24556349+mosh666@users.noreply.github.com
> **Security Scorecard:** [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)

## 📋 Table of Contents

- [Supported Versions](#supported-versions)
- [Reporting a Vulnerability](#reporting-a-vulnerability)
- [Security Features](#security-features)
- [Threat Model](#threat-model)
- [Security Best Practices](#security-best-practices)
- [Security Advisories](#security-advisories)
- [Acknowledgments](#acknowledgments)

---

## ✅ Supported Versions

We provide security updates for the following versions of pyMediaManager:

| Version | Supported          | End of Support |
| ------- | ------------------ | -------------- |
| 1.0.x   | ✅ Yes             | TBD            |
| 0.9.x   | ⚠️ Limited (90 days) | April 7, 2026 |
| < 0.9   | ❌ No              | Ended          |

**Python Version Support:**

- **3.13** ✅ Recommended (latest features, best performance)
- **3.12** ✅ Fully supported
- **3.14** ✅ Supported (latest stable)
- **3.11 and earlier** ❌ Not supported

**Note:** Security patches are backported only to the latest stable release. Users are encouraged to upgrade to the latest version promptly.

---

## 🚨 Reporting a Vulnerability

### Responsible Disclosure

We take security vulnerabilities seriously. If you discover a security issue, please follow responsible disclosure practices:

### How to Report

**DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, use one of these secure channels:

1. **GitHub Security Advisories (Preferred)**
   - Navigate to: https://github.com/mosh666/pyMM/security/advisories
   - Click "Report a vulnerability"
   - Fill out the private advisory form

2. **Private Email**
   - Email: 24556349+mosh666@users.noreply.github.com
   - Subject: `[SECURITY] Brief description`
   - Use PGP encryption (optional, key available on request)

### What to Include

Please provide as much detail as possible:

```markdown
**Vulnerability Title**: Brief, descriptive title

**Severity**: Critical / High / Medium / Low

**Affected Versions**: e.g., 1.0.0 - 1.0.5

**Description**:
Clear description of the vulnerability and its impact.

**Steps to Reproduce**:
1. Step 1
2. Step 2
3. ...

**Proof of Concept**:
Code snippet, configuration, or screenshot demonstrating the issue.

**Suggested Fix** (optional):
Your recommendations for remediation.

**Discoverer**:
Your name/handle for acknowledgment (optional).
```

### Response Timeline

| Timeframe | Action |
|-----------|--------|
| **24 hours** | Initial acknowledgment of report |
| **7 days** | Preliminary assessment and severity rating |
| **30 days** | Patch development and testing |
| **45 days** | Coordinated disclosure and patch release |

We will keep you informed throughout the process via the reporting channel.

### Bounty Program

🎁 While we don't currently offer a formal bug bounty program, we recognize security researchers:

- **Public acknowledgment** in release notes and SECURITY.md
- **GitHub sponsor** consideration for high-impact discoveries
- **Contributor badge** on GitHub profile

---

## 🛡️ Security Features

### Current Security Measures

#### 1. Plugin Sandboxing

**Threat**: Malicious plugin code execution

**Mitigation**:
- ✅ Manifest-driven plugin system (YAML only, no code execution)
- ✅ Strict Pydantic schema validation (fail-fast)
- ✅ No `eval()`, `exec()`, or `__import__()` in plugin loading
- ✅ Plugins cannot access filesystem outside installation directory

```python
# plugins/malicious/plugin.yaml - This CANNOT execute arbitrary code
malicious_code: |
  import os
  os.system("rm -rf /")  # This is just a string, never executed
```

#### 2. Download Integrity Verification

**Threat**: Man-in-the-middle attacks, corrupted downloads

**Mitigation**:
- ✅ HTTPS-only downloads (no HTTP fallback)
- ✅ SHA-256 checksum verification before extraction
- ✅ File size validation
- ✅ Retry logic with exponential backoff

```python
# app/plugins/plugin_base.py
async def download(self, url: str) -> bool:
    if not url.startswith("https://"):
        raise SecurityError("Insecure download URL")

    # Download and calculate SHA-256
    actual_hash = hashlib.sha256(data).hexdigest()

    if actual_hash != self.manifest.checksum_sha256:
        raise SecurityError(f"Checksum mismatch: {actual_hash}")
```

#### 3. Input Validation

**Threat**: Path traversal, command injection

**Mitigation**:
- ✅ Whitelist-based project name validation
- ✅ No path separators or parent directory references (`..`)
- ✅ Sanitized user inputs before filesystem operations
- ✅ `Path.resolve()` to normalize all paths

```python
# app/services/project_service.py
def _validate_project_name(self, name: str) -> bool:
    if "/" in name or "\\" in name:
        return False  # Path traversal
    if ".." in name:
        return False  # Parent directory
    if not re.match(r"^[a-zA-Z0-9_\-. ]+$", name):
        return False  # Special characters
    return True
```

#### 4. Dependency Security Scanning

**Threat**: Vulnerable third-party dependencies

**Mitigation**:
- ✅ **Dependabot** for automatic dependency updates
- ✅ **Bandit** for Python security linting (daily CI)
- ✅ **Safety** for known vulnerability checks
- ✅ **GitHub Code Scanning** (CodeQL) enabled

```yaml
# .github/workflows/security.yml
- name: Run Bandit security linter
  run: bandit -r app/ -f json -o bandit-report.json

- name: Check dependencies with Safety
  run: safety check --json
```

#### 5. OpenSSF Best Practices

**Threat**: General security weaknesses

**Mitigation**:
- ✅ Daily **OpenSSF Scorecard** runs (current score: 8.2/10)
- ✅ Branch protection rules (required reviews, status checks)
- ✅ Signed commits required for maintainers
- ✅ Two-factor authentication enforced for all collaborators

Scorecard checks:
- ✅ Dependency updates (Dependabot)
- ✅ Code review (required for all PRs)
- ✅ CI tests (193 tests, 73% coverage)
- ✅ SAST tools (Ruff with security rules, MyPy)
- ⚠️ Fuzzing (planned)
- ⚠️ SBOM generation (planned)

---

## 🎯 Threat Model

### Attack Surface Analysis

| Component | Threat | Likelihood | Impact | Mitigation |
|-----------|--------|------------|--------|------------|
| **Plugin Downloads** | MITM attack | Medium | High | HTTPS + SHA-256 |
| **Plugin Manifests** | Malicious YAML | Low | Medium | Schema validation |
| **User Input** | Path traversal | Medium | High | Input sanitization |
| **Configuration Files** | Credential theft | Low | High | No hardcoded secrets |
| **External Drives** | Malicious files | Low | Medium | Read-only access |
| **Git Repositories** | Remote code execution | Low | Critical | GitPython sandboxing |

### Trust Boundaries

```
┌─────────────────────────────────────────────┐
│ External (Untrusted)                        │
│ - Internet downloads (plugins)              │
│ - User-provided configuration               │
│ - External drive contents                   │
└────────────┬────────────────────────────────┘
             │ Input validation, checksum verification
             ▼
┌─────────────────────────────────────────────┐
│ Application (Trusted)                       │
│ - Core services (ConfigService, etc.)      │
│ - Plugin manager                            │
│ - Project management                        │
└────────────┬────────────────────────────────┘
             │ Sanitized operations
             ▼
┌─────────────────────────────────────────────┐
│ System (Controlled)                         │
│ - Local filesystem                          │
│ - External drive filesystem                 │
│ - Windows registry (read-only)              │
└─────────────────────────────────────────────┘
```

### Assumptions

1. **User's machine is trusted**: We assume the user's Windows installation is not compromised
2. **HTTPS is secure**: We rely on TLS/SSL for download security
3. **Official sources are legitimate**: Plugin manifests point to official vendor downloads
4. **Python runtime is secure**: We trust the CPython interpreter

---

## 🔐 Security Best Practices

### For Users

#### 1. Keep Software Updated

```powershell
# Check for updates regularly
git pull origin main
pip install --upgrade pymediamanager
```

#### 2. Verify Plugin Sources

Before installing plugins:
- ✅ Check `homepage` URL in `plugin.yaml`
- ✅ Verify `checksum_sha256` matches official release
- ✅ Review plugin source (GitHub releases preferred)
- ❌ Avoid plugins from unknown sources

#### 3. Use Secure Storage

- 🔒 Encrypt external drives with BitLocker (Windows)
- 🔒 Use NTFS permissions to restrict access
- 🔒 Safely eject drives to prevent corruption

#### 4. Review Configuration

```yaml
# config/user.yaml - Never commit this file!
sensitive:
  api_keys: []      # Don't store API keys here
  passwords: []     # Use Windows Credential Manager instead
```

#### 5. Monitor Logs

```powershell
# Review logs for suspicious activity
Get-Content D:\pyMM.Logs\pymm.log | Select-String -Pattern "ERROR|WARN"
```

---

### For Developers

#### 1. Code Review Checklist

- [ ] No hardcoded secrets or credentials
- [ ] Input validation on all user-provided data
- [ ] Path operations use `Path.resolve()`
- [ ] No `eval()`, `exec()`, or unsafe deserialization
- [ ] Type hints on all functions (MyPy strict mode)
- [ ] Unit tests for security-critical functions

#### 2. Secure Coding Patterns

**✅ DO:**
```python
# Use parameterized paths
project_path = self.projects_dir / sanitized_name

# Validate before operations
if not self._validate_project_name(name):
    raise ValueError(f"Invalid project name: {name}")

# Use type-safe configuration
config: AppConfig = ConfigService.load()
```

**❌ DON'T:**
```python
# Direct string concatenation
project_path = f"D:\\Projects\\{user_input}"  # Path traversal!

# No validation
os.system(f"git clone {user_url}")  # Command injection!

# Untyped configuration
config = yaml.safe_load(open("config.yaml"))  # No validation
```

#### 3. Dependency Management

```toml
# pyproject.toml - Pin dependencies
dependencies = [
    "PySide6>=6.6.0,<7.0.0",      # Allow patch updates
    "pydantic>=2.5.0,<3.0.0",     # Block major version changes
]
```

Update dependencies monthly:
```bash
pip list --outdated
pip install --upgrade package-name
pytest tests/  # Verify no breakage
```

#### 4. Pre-commit Hooks

```bash
# Install pre-commit hooks
python scripts/setup-git-hooks.ps1

# Hooks run automatically on commit:
# - Ruff (linting)
# - MyPy (type checking)
# - Bandit (security scanning)
# - pytest (test suite)
```

---

## 📢 Security Advisories

### Active Advisories

**None** - No active security advisories as of January 7, 2026.

---

### Historical Advisories

No security vulnerabilities have been publicly disclosed for pyMediaManager.

**First release:** January 1, 2026

---

## 🏆 Acknowledgments

We thank the following security researchers for responsibly disclosing vulnerabilities:

| Researcher | Vulnerability | Severity | Date | Reward |
|------------|---------------|----------|------|--------|
| _No reports yet_ | - | - | - | - |

**Want to be listed here?** Follow our [responsible disclosure process](#reporting-a-vulnerability)!

---

## 📚 Additional Resources

### Security Documentation

- [Architecture Documentation](docs/architecture.md) - Security architecture details
- [Contributing Guidelines](CONTRIBUTING.md) - Secure development practices
- [OpenSSF Scorecard](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM) - Automated security scoring

### External Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [Python Security Best Practices](https://docs.python.org/3/library/security_warnings.html)
- [OpenSSF Best Practices Badge](https://bestpractices.coreinfrastructure.org/)

---

## 🔄 Policy Updates

This security policy is reviewed and updated quarterly. Changes are tracked via:

- Git commit history: [.github/SECURITY.md](https://github.com/mosh666/pyMM/commits/main/.github/SECURITY.md)
- Release notes: [CHANGELOG.md](CHANGELOG.md)

**Next review:** April 7, 2026

---

## 📞 Contact

- **Security Email:** 24556349+mosh666@users.noreply.github.com
- **GitHub Security:** https://github.com/mosh666/pyMM/security
- **General Issues:** https://github.com/mosh666/pyMM/issues
- **Discussions:** https://github.com/mosh666/pyMM/discussions

**Response Time:** We aim to respond to security reports within 24 hours.

---

**Policy Version:** 1.0.0
**Effective Date:** January 7, 2026
**Maintainer:** @mosh666
