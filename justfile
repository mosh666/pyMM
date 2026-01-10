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
check: format-all lint lint-md type-check check-docstrings check-docs test

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
    npx --yes markdownlint-cli2 --config .markdownlint.json "**/*.md" "#.venv" "#node_modules" "#htmlcov"

# Run type checker (MyPy)
type-check:
    {{python}} -m mypy app/

# Check Python docstring coverage
check-docstrings:
    {{python}} -m interrogate --fail-under 100 app/ -vv

# Check documentation formatting
check-docs:
    {{python}} -m doc8 docs/ --max-line-length 100 --ignore-path docs/_build --ignore-path docs/locales

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
    {{python}} -m pre_commit install
    {{python}} -m pre_commit install --hook-type commit-msg --hook-type pre-push
    @echo "Pre-commit hooks installed successfully"

# Run pre-commit on all files
pre-commit-run:
    {{python}} -m pre_commit run --all-files

# Update pre-commit hooks to latest versions
pre-commit-update:
    {{python}} -m pre_commit autoupdate

# Run semantic-release in dry-run mode to preview version changes
release-dry-run:
    {{python}} -m pip install python-semantic-release
    {{python}} -m semantic_release version --print

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
    {{python}} -m pip install -q sphinx furo sphinx-multiversion myst-parser sphinx-copybutton sphinx-tabs sphinx-design sphinx-notfound-page sphinxcontrib-mermaid sphinxcontrib-spelling sphinxcontrib-redirects
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

# Extract translatable strings from documentation for i18n
docs-gettext:
    {{python}} -m sphinx.cmd.build -b gettext docs docs/_build/gettext
    @echo "✓ Translatable strings extracted to docs/_build/gettext"

# Update translation files for German locale
docs-translate:
    {{python}} -m pip install -q sphinx-intl
    {{python}} -m sphinx_intl update -p docs/_build/gettext -l de
    @echo "✓ German translation files updated in docs/locales/de/LC_MESSAGES/"

# Build German documentation
docs-build-de:
    {{python}} -m pip install -q sphinx furo sphinx-multiversion myst-parser sphinx-copybutton sphinx-tabs sphinx-design sphinx-notfound-page sphinxcontrib-mermaid sphinxcontrib-spelling sphinxcontrib-redirects sphinx-intl
    {{python}} -m sphinx.cmd.build -b html -D language=de docs docs/_build/html-de
    @echo "✓ German documentation built to docs/_build/html-de"

# Build all language versions of documentation
docs-build-all: docs docs-build-de
    @echo "✓ All documentation versions built"

# Check documentation for broken links
docs-linkcheck:
    {{python}} -m sphinx.cmd.build -b linkcheck docs docs/_build/linkcheck
    @echo "✓ Link check complete - see docs/_build/linkcheck/output.txt"

# Check documentation spelling
docs-spelling:
    {{python}} -m pip install -q sphinxcontrib-spelling
    {{python}} -m sphinx.cmd.build -b spelling docs docs/_build/spelling
    @echo "✓ Spelling check complete - see docs/_build/spelling/output.txt"

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
        --target test \
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

# Clean Docker images and containers (cross-platform)
ci-docker-clean:
    #!{{python}}
    import subprocess
    import sys

    print("🧹 Cleaning pyMM Docker images...")

    try:
        # List all pymm-ci images using docker's built-in filtering
        result = subprocess.run(
            ["docker", "images", "--filter", "reference=pymm-ci", "-q"],
            capture_output=True,
            text=True,
            check=False
        )

        image_ids = result.stdout.strip().split('\n')
        image_ids = [img for img in image_ids if img]  # Filter empty strings

        if image_ids:
            print(f"Found {len(image_ids)} image(s) to remove")
            for img_id in image_ids:
                try:
                    subprocess.run(
                        ["docker", "rmi", "-f", img_id],
                        check=True,
                        capture_output=True
                    )
                    print(f"  ✓ Removed image {img_id}")
                except subprocess.CalledProcessError as e:
                    print(f"  ✗ Failed to remove {img_id}: {e.stderr.decode()}")
        else:
            print("No pymm-ci images found")

        print("✨ Docker cleanup complete")
    except FileNotFoundError:
        print("✗ Error: Docker is not installed or not in PATH", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error during cleanup: {e}", file=sys.stderr)
        sys.exit(1)

# Clean Docker build cache and records (cross-platform)
ci-docker-build-delete:
    #!{{python}}
    import subprocess
    import sys

    print("🧹 Cleaning Docker build cache and records...")

    try:
        # Get build cache info before deletion
        result = subprocess.run(
            ["docker", "builder", "du"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            print("\nCurrent build cache:")
            print(result.stdout)

        # Prune all build cache (not just dangling)
        print("\n🗑️  Removing all build cache...")
        prune_result = subprocess.run(
            ["docker", "builder", "prune", "-a", "-f"],
            capture_output=True,
            text=True,
            check=True
        )

        print(prune_result.stdout.strip())
        print("✨ Docker build cache cleanup complete")

    except subprocess.CalledProcessError as e:
        print(f"✗ Error during build cache cleanup: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("✗ Error: Docker is not installed or not in PATH", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        sys.exit(1)

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
