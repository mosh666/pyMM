# Test Suite

This directory contains the comprehensive test suite for pyMediaManager.

## Structure

```
tests/
├── unit/               # Unit tests for individual modules
├── integration/        # Integration tests for workflows
├── gui/               # GUI component tests
├── conftest.py        # Shared pytest fixtures
└── test_*.py          # Manual test scripts for development
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
pytest tests/unit          # Unit tests only
pytest tests/integration   # Integration tests only
pytest tests/gui           # GUI tests only
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific markers
```bash
pytest -m "not slow"       # Exclude slow tests
pytest -m integration      # Integration tests only
pytest -m ui              # UI tests only
```

## Manual Test Scripts

The root-level `test_*.py` files are manual test scripts for development:
- `test_git_integration.py` - Git service testing
- `test_plugin_download.py` - Plugin download testing
- `test_project_management.py` - Project management testing
- `test_settings_dialog.py` - Settings dialog testing

Run these directly with Python:
```bash
python tests/test_git_integration.py
```

## Writing Tests

- Unit tests should focus on individual functions/methods
- Use fixtures from `conftest.py` for common setup
- Mark slow tests with `@pytest.mark.slow`
- Mark integration tests with `@pytest.mark.integration`
- Mark UI tests with `@pytest.mark.ui`
