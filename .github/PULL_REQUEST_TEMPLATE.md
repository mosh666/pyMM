<!-- markdownlint-disable MD009 MD013 MD022 MD024 MD031 MD032 MD033 MD034 MD036 MD041 MD051 -->

# 🔄 Pull Request

## 📝 Description

<!-- Provide a clear and concise description of the changes -->

### Type of Change

<!-- Check all that apply -->

- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📚 Documentation update
- [ ] 🎨 Code style/formatting (no functional changes)
- [ ] ♻️ Refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🧪 Test coverage improvement
- [ ] 🔧 Configuration/build changes
- [ ] 🔒 Security fix

### Related Issues

<!-- Link to related issues using #issue_number -->

Closes #
Related to #

---

## 🎯 Motivation and Context

<!-- Why is this change required? What problem does it solve? -->

**Problem:**

**Solution:**

**Alternatives Considered:**

---

## 🔍 Changes Made

<!-- Provide a detailed list of changes -->

### Core Changes

-
-
-

### Files Modified

<!-- List key files changed and their purpose -->

- `app/path/to/file.py`: Description of changes
- `tests/path/to/test.py`: Test coverage for changes
- `docs/path/to/doc.md`: Documentation updates

---

## ✅ Testing

### Test Coverage

<!-- Describe the tests you added or modified -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] GUI tests added/updated (if applicable)
- [ ] Manual testing performed

### Test Results

```bash
# Paste test output here
pytest tests/ -v --cov=app --cov-report=term

# Example:
# ===== 193 passed, 73% coverage =====
```

### Manual Testing Steps

<!-- Steps to manually verify the changes -->

1.
2.
3.

### Test Environment

- **OS:** Windows 10 / Windows 11 / Linux / macOS
- **Python Version:** 3.12 / 3.13 / 3.14
- **PySide6 Version:** 6.6.x / 6.7.x
- **QFluentWidgets Version:** 1.5.x

---

## 📸 Screenshots/Videos

<!-- If applicable, add screenshots or videos to demonstrate the changes -->

### Before

<!-- Screenshot or description of behavior before changes -->

### After

<!-- Screenshot or description of behavior after changes -->

---

## 🔒 Security Considerations

<!-- Address any security implications of this change -->

- [ ] No security implications
- [ ] Security review required
- [ ] Includes security fix (link to private advisory if applicable)

**Security Impact:**

---

## 📚 Documentation

<!-- Check all that apply -->

- [ ] Code comments added/updated
- [ ] Docstrings added/updated (Google style)
- [ ] Type hints added/updated
- [ ] README.md updated (if needed)
- [ ] User guide updated (`docs/user-guide.md`)
- [ ] Architecture docs updated (`docs/architecture.md`)
- [ ] Plugin development guide updated (`docs/plugin-development.md`)
- [ ] CHANGELOG.md updated (follow Keep a Changelog format)

---

## ✨ Code Quality

### Linting and Type Checking

<!-- Confirm all checks pass -->

- [ ] `ruff check app/ tests/` passes (0 violations, includes security)
- [ ] `ruff format app/ tests/ --check` passes
- [ ] `mypy app/ --strict` passes (0 errors)

```bash
# Paste linting output here
ruff check app/ tests/
# All checks passed!

mypy app/ --strict
# Success: no issues found
```

### Pre-commit Hooks

- [ ] Pre-commit hooks installed (`python scripts/setup-git-hooks.ps1`)
- [ ] All pre-commit checks pass

---

## 🚀 Performance Impact

<!-- Describe any performance implications -->

- [ ] No performance impact
- [ ] Performance improved (provide benchmarks)
- [ ] Performance degraded (justify why acceptable)

**Benchmarks:**

| Operation | Before | After | Change |
|-----------|--------|-------|--------|
| Example   | 1.2s   | 0.8s  | -33%   |

---

## 🔧 Breaking Changes

<!-- If breaking changes, describe migration path -->

- [ ] No breaking changes
- [ ] Breaking changes (describe below)

**Migration Guide:**

<!-- If breaking changes, provide step-by-step migration instructions -->

---

## 🎨 Code Style Compliance

<!-- Confirm adherence to project standards -->

- [ ] Modern Python syntax (`list[T]`, `dict[K, V]`, `str | None`)
- [ ] Type hints on all functions and methods
- [ ] Docstrings follow Google style guide
- [ ] Functions are single-purpose (SOLID principles)
- [ ] No global state or mutable defaults
- [ ] Error handling uses exceptions (not return codes)

---

## 📦 Dependencies

<!-- List any new dependencies or version changes -->

### Added Dependencies

<!-- If adding new dependencies, justify why -->

- `package-name==1.2.3`: Reason for addition

### Updated Dependencies

- `package-name`: 1.2.3 → 1.2.4 (reason)

### Removed Dependencies

- `package-name`: No longer needed because...

**Dependency Check:**

- [ ] `pip check` passes (no dependency conflicts)
- [ ] All dependencies pinned with version constraints
- [ ] No CVEs in new dependencies (check with `safety check`)

---

## 🌍 Internationalization

<!-- If applicable, address i18n concerns -->

- [ ] No user-facing strings added
- [ ] User-facing strings added to translation files
- [ ] UI text follows Microsoft Fluent Design guidelines

---

## ♿ Accessibility

<!-- If UI changes, address accessibility -->

- [ ] No UI changes
- [ ] UI changes are keyboard accessible
- [ ] UI changes support high-contrast themes
- [ ] Screen reader compatibility verified

---

## 📋 Checklist

<!-- Confirm all requirements are met -->

### Required

- [ ] I have read the [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines
- [ ] I have read and agree to the [Code of Conduct](CODE_OF_CONDUCT.md)
- [ ] My code follows the project's code style (Ruff + MyPy)
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings or errors
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

### Optional (Recommended)

- [ ] I have squashed my commits into logical units
- [ ] I have rebased my branch on the latest `dev` branch
- [ ] I have run the full test suite (`pytest tests/`)
- [ ] I have checked code coverage (`pytest --cov=app`)
- [ ] I have run security checks (included in `ruff check`)
- [ ] I have verified the application starts and runs correctly

---

## 💬 Additional Context

<!-- Add any other context about the pull request here -->

---

## 🏷️ PR Metadata

<!-- This section is auto-populated by GitHub, but you can add labels manually -->

**Target Branch:** `dev` / `main`

**Reviewers:** @mosh666

**Labels:**
<!-- Add relevant labels -->
- `enhancement` / `bug` / `documentation` / `security`
- `priority: high` / `priority: medium` / `priority: low`
- `area: core` / `area: plugins` / `area: ui` / `area: testing`

**Milestone:** v1.0.1 / v1.1.0

---

## 📞 Questions?

If you have questions about this PR or need help, feel free to:

- 💬 Comment on this PR
- 📧 Email: 24556349+mosh666@users.noreply.github.com
- 💡 Start a [Discussion](https://github.com/mosh666/pyMM/discussions)

---

**Thank you for contributing to pyMediaManager! 🎉**

<!--
Reviewer Notes:
- Check all items in the checklist
- Verify tests pass in CI
- Review code for security issues
- Ensure documentation is complete
- Test functionality manually if GUI changes
-->
