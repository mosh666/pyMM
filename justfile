# Justfile for pyMediaManager

set shell := ["powershell", "-c"]

# Release build version
version := "3.12"

# Install dependencies in editable mode
install:
    python -m pip install pip-tools
    python -m piptools compile -o requirements.lock pyproject.toml
    python -m pip install -e .[dev]

# Update lockfile
lock:
    python -m piptools compile -o requirements.lock pyproject.toml

# Run unit tests
test:
    python -m pytest

# Run linter and type checker
lint:
    python -m ruff check .
    python -m mypy .

# Format code
format:
    python -m ruff format .

# Setup git hooks
setup-hooks:
    powershell -ExecutionPolicy Bypass -File scripts/setup-git-hooks.ps1


# Clean build artifacts and cache
clean:
    -rm -rf python3* lib-py3* *.zip *.sha256 build/ dist/ *.egg-info .pytest_cache .mypy_cache __pycache__
    -rm requirements*.txt

# Build portable distribution for Windows
build v=version:
    python scripts/build_distribution.py --version {{v}}

# Run the application locally
run:
    python launcher.py

# Run type checking only
type-check:
    python -m mypy .

# Run unit tests only
test-unit:
    python -m pytest tests/unit/
