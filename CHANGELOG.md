# CHANGELOG

<!-- version list -->

## v0.1.0-beta.1 (2026-01-17)

### Continuous Integration

- Fix workflow_dispatch permission error by using workflow_run trigger
  ([`2734124`](https://github.com/mosh666/pyMM/commit/27341246dc3b63c700923600b857a0dd6e9aaf1e))

- Add 'CI - Tests and Linting' to workflow_run triggers in docs.yml - Remove update-docs-site job
  that used createWorkflowDispatch - Documentation now builds automatically when CI or Semantic
  Release completes - Resolves 403 'Resource not accessible by integration' error

BREAKING CHANGE: Documentation workflow no longer supports manual dispatch from other workflows. Use
  workflow_run trigger instead for automatic builds after CI/release completion.

### Breaking Changes

- Documentation workflow no longer supports manual dispatch from other workflows. Use workflow_run
  trigger instead for automatic builds after CI/release completion.


## v0.0.1-beta.1 (2026-01-17)

### Bug Fixes

- **docs**: Add type annotations to Sphinx configuration functions
  ([`768178f`](https://github.com/mosh666/pyMM/commit/768178fd49956f6261f3dfb05f418524ade86409))

- **scripts**: Add missing type annotations for mypy strict compliance
  ([`c18f440`](https://github.com/mosh666/pyMM/commit/c18f440b0f2f7d4eadc9645fb6eb4c56764e3d08))

- **scripts**: Improve type handling for dict operations in performance scripts
  ([`bd4de5b`](https://github.com/mosh666/pyMM/commit/bd4de5b57902336b028dd0de1e51a18b355ef359))

- **tests**: Add tmp_path parameter to test functions in __main__ blocks
  ([`5eb2062`](https://github.com/mosh666/pyMM/commit/5eb206244b5cb87de28b0915c33ca0c7d9f41d30))

- **tests**: Add type parameters to generic types in fixtures and conftest
  ([`52a2127`](https://github.com/mosh666/pyMM/commit/52a21275436d478598716efffe60e6b664ad3961))

- **tests**: Resolve enum comparison and Any return type issues
  ([`3414b7b`](https://github.com/mosh666/pyMM/commit/3414b7b364de8b73869918eb5af743088e36bc28))
