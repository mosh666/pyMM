# Justfile for pyMediaManager
# Cross-platform task automation using Python 3.13+
# Last updated: January 8, 2026

# Configure shells for different platforms
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-uc"]

# Variables
python := if os() == "windows" { "python" } else { "python3" }
python_version := "3.13"  # Recommended version (3.12, 3.13, 3.14 supported)

# Default recipe - show available commands
default:
    @just --list

# Install dependencies in development mode
install:
    {{python}} -m pip install --upgrade pip setuptools wheel
    {{python}} -m pip install -e ".[dev]"

# Run full quality check (lint, type-check, test)
check: lint type-check test

# =============================================================================
# Testing Recipes
# =============================================================================

# Run all tests with coverage
test:
    {{python}} -m pytest tests/ --cov=app --cov-report=term-missing

# Run unit tests only
test-unit:
    {{python}} -m pytest tests/unit/ -v

# Run integration tests
test-integration:
    {{python}} -m pytest tests/integration/ -v

# Run GUI tests
test-gui:
    {{python}} -m pytest tests/gui/ -v

# Run tests with HTML coverage report
test-cov:
    {{python}} -m pytest tests/ --cov=app --cov-report=html --cov-report=term
    @echo "Coverage report: htmlcov/index.html"

# Run tests for specific platform
test-platform PLATFORM:
    {{python}} -m pytest tests/ -m {{PLATFORM}} -v

# =============================================================================
# Code Quality Recipes
# =============================================================================

# Run Ruff linter
lint:
    {{python}} -m ruff check .

# Run Ruff linter with auto-fix
lint-fix:
    {{python}} -m ruff check --fix .

# Lint markdown files
lint-md:
    npx --yes markdownlint-cli2 --config .markdownlint.json "**/*.md"

# Run type checker (MyPy)
type-check:
    {{python}} -m mypy app/

# Format code with Ruff
format:
    {{python}} -m ruff format .

# Format and fix all code issues
format-all: format lint-fix

# =============================================================================
# Git & Pre-commit Recipes
# =============================================================================

# Install pre-commit hooks
pre-commit-install:
    {{python}} -m pip install pre-commit
    pre-commit install
    @echo "Pre-commit hooks installed successfully"

# Run pre-commit on all files
pre-commit-run:
    pre-commit run --all-files

# Update pre-commit hooks to latest versions
pre-commit-update:
    pre-commit autoupdate

# Setup git hooks (legacy - use pre-commit-install)
setup-hooks:
    {{python}} scripts/setup_hooks.py

# Validate configuration files
validate-config:
    {{python}} -c "import yaml; yaml.safe_load(open('config/app.yaml')); print('✓ app.yaml valid')"
    {{python}} -c "import yaml; yaml.safe_load(open('config/user.yaml.example')); print('✓ user.yaml.example valid')"
    @echo "Configuration files validated successfully"

# =============================================================================
# Documentation Recipes
# =============================================================================

# Build documentation locally with sphinx-multiversion
docs: _docs-build _docs-redirect

_docs-build:
    {{python}} -m pip install -q sphinx sphinx-multiversion sphinx-rtd-theme myst-parser
    {{python}} -m sphinx_multiversion docs docs/_build/html

_docs-redirect:
    #!{{python}}
    import pathlib
    import sys

    try:
        path = pathlib.Path('docs/_build/html/index.html')
        if path.parent.exists():
            content = '<meta http-equiv="refresh" content="0; url=main/index.html">'
            path.write_text(content, encoding='utf-8')
            print(f"✓ Created redirect at {path}")
        else:
            print(f"⚠ Warning: {path.parent} does not exist, skipping redirect creation")
    except Exception as e:
        print(f"✗ Failed to create redirect: {e}", file=sys.stderr)
        sys.exit(1)

# Serve documentation locally (requires Python http.server)
docs-serve:
    @echo "Starting local documentation server at http://localhost:8000"
    @echo "Press Ctrl+C to stop"
    {{python}} -m http.server 8000 -d docs/_build/html

# Clean documentation build artifacts
docs-clean:
    #!{{python}}
    import shutil
    import pathlib

    docs_build = pathlib.Path('docs/_build')
    if docs_build.exists():
        shutil.rmtree(docs_build)
        print(f"✓ Removed {docs_build}")
    else:
        print(f"ℹ No documentation build to clean")

# =============================================================================
# Build & Distribution Recipes
# =============================================================================

# Build portable distribution for specified version
build VERSION=python_version:
    {{python}} scripts/build_manager.py --version {{VERSION}}

# Run the application locally
run:
    {{python}} launcher.py

# Run application with debug logging
run-debug:
    {{python}} launcher.py --log-level DEBUG

# =============================================================================
# Plugin Management Recipes
# =============================================================================

# Show what would change when migrating plugins to v2 schema (dry-run)
migrate-plugins-dry:
    {{python}} -m app.plugins.plugin_migrator dry-run --plugins-dir plugins

# Migrate all plugins to v2 schema with backups
migrate-plugins:
    {{python}} -m app.plugins.plugin_migrator migrate --plugins-dir plugins

# Migrate a specific plugin to v2 schema
migrate-plugin NAME:
    {{python}} -m app.plugins.plugin_migrator migrate --plugins-dir plugins --plugin {{NAME}}

# Rollback all plugin migrations
rollback-plugins:
    {{python}} -m app.plugins.plugin_migrator rollback --plugins-dir plugins

# Rollback a specific plugin migration
rollback-plugin NAME:
    {{python}} -m app.plugins.plugin_migrator rollback --plugins-dir plugins --plugin {{NAME}}

# =============================================================================
# Docker & CI Recipes
# =============================================================================

# Build and run complete Docker CI pipeline
ci-docker: ci-docker-build ci-docker-test

# Build Docker image for CI testing (multi-platform support)
ci-docker-build PYTHON_VER=python_version PLATFORM="linux/amd64":
    docker build \
        --build-arg PYTHON_VERSION={{PYTHON_VER}} \
        --platform {{PLATFORM}} \
        -t pymm-ci:{{PYTHON_VER}} \
        -t pymm-ci:latest \
        .

# Build for multiple Python versions
ci-docker-build-all:
    @echo "Building for Python 3.12, 3.13, 3.14..."
    @just ci-docker-build 3.12
    @just ci-docker-build 3.13
    @just ci-docker-build 3.14

# Run complete CI pipeline in Docker (lint, type-check, test)
ci-docker-test IMAGE="pymm-ci:latest":
    @echo "==> Running linting in Docker..."
    docker run --rm {{IMAGE}} python -m ruff check .
    @echo ""
    @echo "==> Running type checking in Docker..."
    docker run --rm {{IMAGE}} python -m mypy app/
    @echo ""
    @echo "==> Running tests in Docker..."
    docker run --rm {{IMAGE}} bash -c "\
        export QT_QPA_PLATFORM=offscreen; \
        export DISPLAY=:99; \
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & \
        sleep 2; \
        pytest tests/ --cov=app --cov-report=term"

# Run interactive shell in Docker container for debugging
ci-docker-shell IMAGE="pymm-ci:latest":
    docker run --rm -it {{IMAGE}} /bin/bash

# Clean Docker images and containers
ci-docker-clean:
    @echo "Cleaning pyMM Docker images..."
    docker images | grep pymm-ci | awk '{print $3}' | xargs -r docker rmi -f || true
    @echo "Docker cleanup complete"

# =============================================================================
# Cleanup Recipes
# =============================================================================

# Clean build artifacts and cache (using pathlib for cross-platform)
clean:
    #!{{python}}
    from pathlib import Path
    import shutil

    # Root level patterns to clean
    root_patterns = [
        "build", "dist", "*.egg-info", ".coverage", ".coverage.*",
        "htmlcov", "*.zip", "*.sha256", "get-pip.py"
    ]

    # Recursive patterns (cleans subdirectories)
    recursive_patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
    ]

    print("🧹 Cleaning artifacts...")
    removed_count = 0

    # Clean root patterns
    for pattern in root_patterns:
        for path in Path(".").glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  ✓ Removed {path}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to remove {path}: {e}")

    # Clean recursive patterns
    for pattern in recursive_patterns:
        for path in Path(".").rglob(pattern.replace("**/", "")):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"  ✓ Removed {path}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to remove {path}: {e}")

    print(f"\n✨ Cleanup complete! Removed {removed_count} items.")

# Clean everything (includes docs build)
clean-all: clean docs-clean
    @echo "✨ Complete cleanup finished!"
