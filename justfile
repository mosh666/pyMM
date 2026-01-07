# Justfile for pyMediaManager

# Configure shells for different platforms
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# Variables
python := "python"
version := "3.12"

# Default recipe
default:
    @just --list

# Install dependencies in editable mode
install:
    {{python}} -m pip install pip-tools
    {{python}} -m piptools compile -o requirements.lock pyproject.toml
    {{python}} -m pip install -e .[dev]

# Update lockfile
lock:
    {{python}} -m piptools compile -o requirements.lock pyproject.toml

# Run full quality check (lint, types, tests)
check: lint type-check test

# Run unit tests
test:
    {{python}} -m pytest

# Run unit tests (unit only)
test-unit:
    {{python}} -m pytest tests/unit/

# Run linter (Ruff)
lint:
    {{python}} -m ruff check .

# Run type checker (MyPy)
type-check:
    {{python}} -m mypy .

# Format code
format:
    {{python}} -m ruff format .

# Setup git hooks
setup-hooks:
    {{python}} scripts/setup_hooks.py

# Build documentation locally
docs: _docs-build _docs-redirect

_docs-build:
    {{python}} -m pip install sphinx-multiversion
    {{python}} -m sphinx_multiversion docs docs/_build/html

_docs-redirect:
    #!python
    import pathlib
    import sys

    try:
        path = pathlib.Path('docs/_build/html/index.html')
        if path.parent.exists():
            content = '<meta http-equiv="refresh" content="0; url=main/index.html">'
            path.write_text(content, encoding='utf-8')
            print(f"Created redirect at {path}")
        else:
            print(f"Warning: {path.parent} does not exist, skipping redirect creation")
    except Exception as e:
        print(f"Failed to create redirect: {e}", file=sys.stderr)
        sys.exit(1)

# Clean build artifacts and cache
clean:
    #!python
    import shutil
    import glob
    import os

    # Root patterns
    root_patterns = [
        "python3*", "lib-py3*", "*.zip", "*.sha256", "build", "dist",
        "requirements*.txt", ".coverage", "htmlcov"
    ]

    # Recursive patterns (cleans subdirectories too)
    recursive_patterns = [
        "**/*.egg-info",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "**/__pycache__",
        "**/.ruff_cache"
    ]

    print("Cleaning artifacts...")

    for pattern in root_patterns:
        for p in glob.glob(pattern):
            try:
                if os.path.isdir(p):
                    shutil.rmtree(p)
                else:
                    os.remove(p)
                print(f"Removed {p}")
            except Exception as e:
                print(f"Failed to remove {p}: {e}")

    for pattern in recursive_patterns:
        for p in glob.glob(pattern, recursive=True):
            try:
                if os.path.exists(p):
                     if os.path.isdir(p):
                         shutil.rmtree(p)
                     else:
                         os.remove(p)
                     print(f"Removed {p}")
            except Exception as e:
                print(f"Failed to remove {p}: {e}")

# Build portable distribution (Cross-platform manager)
build v=version:
    {{python}} scripts/build_manager.py --version {{v}}

# Run the application locally
run:
    {{python}} launcher.py
