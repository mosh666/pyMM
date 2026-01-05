## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 📝 Documentation update
- [ ] 🔧 Configuration change
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test addition or update
- [ ] 🔨 Build or CI/CD change

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes #
Related to #

## Changes Made

<!-- Provide a detailed list of changes -->

-
-
-

## Testing

<!-- Describe the tests you ran and how to reproduce them -->

### Test Configuration

- **Python Version**:
- **OS**:
- **Testing Method**:

### Test Coverage

- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] Integration tests pass (`pytest tests/integration/`)
- [ ] GUI tests pass (`pytest tests/gui/`)
- [ ] All tests pass (`pytest`)
- [ ] Code coverage maintained or improved
- [ ] Manual testing performed

### How to Test

<!-- Provide step-by-step instructions to test your changes -->

1.
2.
3.

## Code Quality

<!-- Confirm the following checks have passed -->

- [ ] Code follows the project's style guidelines (Ruff)
- [ ] Code is formatted correctly (Ruff format)
- [ ] Type hints are added/updated (MyPy passes)
- [ ] Docstrings are added/updated for new functions/classes
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] No new warnings or errors introduced
- [ ] Code is DRY (Don't Repeat Yourself)
- [ ] Variables and functions have descriptive names

## Documentation

<!-- Confirm documentation is updated -->

- [ ] Updated README.md (if applicable)
- [ ] Updated CHANGELOG.md
- [ ] Updated docstrings and type hints
- [ ] Updated user documentation (docs/user-guide.md)
- [ ] Updated architecture documentation (docs/architecture.md)
- [ ] Added inline comments for complex logic

## Security

<!-- For security-related changes -->

- [ ] No sensitive data exposed in code or logs
- [ ] Security best practices followed
- [ ] Dependencies updated to secure versions
- [ ] Input validation added where needed
- [ ] No SQL injection, XSS, or other common vulnerabilities

## Portability

<!-- Confirm portability requirements are maintained -->

- [ ] No absolute paths used (all paths relative to app root)
- [ ] No system modifications (registry, PATH, etc.)
- [ ] No hardcoded drive letters
- [ ] Works from any drive location
- [ ] Tested on external/removable drive

## Breaking Changes

<!-- If this is a breaking change, describe the impact -->

### Impact

-

### Migration Guide

<!-- Provide instructions for users to migrate from the previous version -->

1.
2.

## Screenshots

<!-- Add screenshots for UI changes -->

### Before

### After

## Performance Impact

<!-- Describe any performance implications -->

- [ ] No significant performance impact
- [ ] Performance improved
- [ ] Performance degraded (explain why it's acceptable)

**Benchmark Results** (if applicable):


## Additional Notes

<!-- Any additional information that reviewers should know -->

## Checklist

<!-- Final checks before submitting -->

- [ ] My code follows the project's contributing guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Reviewer Notes

<!-- Anything specific you want reviewers to focus on -->

---

**By submitting this pull request, I confirm that my contribution is made under the terms of the MIT license.**
