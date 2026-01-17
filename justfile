# Justfile for pyMediaManager
# Cross-platform task automation using Python 3.13+
# Last updated: January 15, 2026
#
# Quick Reference:
#   Setup:       just install, just dev-setup, just upgrade-deps
#   Running:     just run, just run-portable VERSION, just run-debug
#   Testing:     just test, just test-portable VERSION, just test-portable-all
#   Quality:     just check, just lint-fix, just security-check
#   Building:    just build [VERSION] [ARCH] [FORMAT], just build-and-test VERSION
#   Docs:        just docs, just docs-serve, just update-plugin-catalog
#   Maintenance: just clean-all, just uv-cache-clean
#   Full guide:  docs/build-system.md

# Configure shells for different platforms
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set shell := ["bash", "-uc"]

# Variables
python := "uv run python"
python_version := "3.13"  # Recommended version (3.12, 3.13, 3.14 all fully supported)

# Default recipe - show available commands
default:
    @just --list

# Cleanup tmp directory before tests (private helper)
[private]
[windows]
_cleanup-tmp-pre:
    $tmpDir = Join-Path $env:TEMP 'pyMM_test'; if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue }

[private]
[unix]
_cleanup-tmp-pre:
    #!/usr/bin/env bash
    tmpdir="${TMPDIR:-/tmp}/pyMM_test"
    if [ -d "$tmpdir" ]; then rm -rf "$tmpdir" 2>/dev/null || true; fi

# Cleanup tmp directory after tests (private helper)
[private]
[windows]
_cleanup-tmp:
    $tmpDir = Join-Path $env:TEMP 'pyMM_test'; if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue; Write-Host '  Cleaned up temp directory' -ForegroundColor Gray }

[private]
[unix]
_cleanup-tmp:
    #!/usr/bin/env bash
    tmpdir="${TMPDIR:-/tmp}/pyMM_test"
    if [ -d "$tmpdir" ]; then rm -rf "$tmpdir" 2>/dev/null && echo "  Cleaned up temp directory" || true; fi

# Install dependencies in development mode
[group('setup')]
[doc("Install all dependencies using uv")]
install:
    @echo "{{BOLD}}{{BLUE}}📦 Installing pyMediaManager dependencies...{{NORMAL}}"
    @echo "  {{CYAN}}→ Syncing dependencies...{{NORMAL}}"
    uv sync --all-extras
    @echo "{{GREEN}}✓ Installation complete!{{NORMAL}}"

# Complete development environment setup (install + pre-commit hooks)
[group('setup')]
[doc("Set up complete development environment (dependencies + pre-commit hooks)")]
dev-setup: install pre-commit-install
    @echo ""
    @echo "{{BOLD}}{{GREEN}}╔═══════════════════════════════════════╗{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}║   Development Setup Complete! ✓       ║{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}╚═══════════════════════════════════════╝{{NORMAL}}"
    @echo ""
    @echo "{{CYAN}}Next steps:{{NORMAL}}"
    @echo "  • Run the app:  {{YELLOW}}just run{{NORMAL}}"
    @echo "  • Run tests:    {{YELLOW}}just test{{NORMAL}}"
    @echo "  • Quality check: {{YELLOW}}just check{{NORMAL}}"

# Upgrade all dependencies and update lockfile
[group('setup')]
[doc("Upgrade all dependencies to latest compatible versions and update uv.lock")]
upgrade-deps:
    @echo "{{BOLD}}{{BLUE}}🔄 Upgrading dependencies...{{NORMAL}}"
    @echo "  {{CYAN}}→ Running uv lock --upgrade...{{NORMAL}}"
    uv lock --upgrade
    @echo "  {{CYAN}}→ Syncing upgraded dependencies...{{NORMAL}}"
    uv sync --all-extras
    @echo "{{GREEN}}✓ Dependencies upgraded successfully!{{NORMAL}}"
    @echo "{{YELLOW}}⚠  Don't forget to test and commit the updated uv.lock file{{NORMAL}}"

# Run full quality check (lint, type-check, test)
[group('quality')]
[doc("Run comprehensive quality checks: format, lint, type-check, docs validation, and tests")]
check: format-all lint lint-md type-check docs-linkcheck docs-spelling check-docstrings check-docs test _cleanup-tmp
    @echo ""
    @echo "{{BOLD}}{{GREEN}}╔═══════════════════════════════════════╗{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}║   All Quality Checks Passed! ✓        ║{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}╚═══════════════════════════════════════╝{{NORMAL}}"

# Run all tests with coverage
[group('testing')]
test: _cleanup-tmp-pre
    @echo "{{BOLD}}{{BLUE}}🧪 Running test suite...{{NORMAL}}"
    {{python}} -m pytest tests/ --cov=app --cov-report=term-missing
    @echo "{{GREEN}}✓ All tests passed!{{NORMAL}}"

# Run unit tests only
[group('testing')]
test-unit: _cleanup-tmp-pre
    {{python}} -m pytest tests/unit/ --basetemp=.pytest_tmp -v

# Run integration tests
[group('testing')]
test-integration:
    {{python}} -m pytest tests/integration/ -v

# Run GUI tests
[group('testing')]
test-gui:
    {{python}} -m pytest tests/gui/ -v

# Run tests with HTML coverage report
[group('testing')]
test-cov:
    {{python}} -m pytest tests/ --cov=app --cov-report=html --cov-report=term
    @echo "Coverage report: htmlcov/index.html"

# Run tests for specific platform
[group('testing')]
test-platform PLATFORM:
    {{python}} -m pytest tests/ -m {{PLATFORM}} -v

# Run Ruff linter
[group('quality')]
lint:
    {{python}} -m ruff check .

# Run Ruff linter with auto-fix
[group('quality')]
lint-fix:
    {{python}} -m ruff check --fix .

# Lint markdown files
[group('quality')]
lint-md: _check-npx
    npx --yes markdownlint-cli2 --config .markdownlint.json "**/*.md"

# Run type checker (MyPy)
[group('quality')]
type-check:
    {{python}} -m mypy app/ docs/ scripts/ tests/ launcher.py

# Check Python docstring coverage
[group('quality')]
check-docstrings:
    {{python}} -m interrogate --fail-under 100 app/ -vv

# Check documentation formatting
[group('quality')]
check-docs:
    {{python}} -m doc8 docs/ --max-line-length 100 --ignore-path docs/_build

# Format code with Ruff
[group('quality')]
format:
    {{python}} -m ruff format .

# Format and fix all code issues
[group('quality')]
format-all: format lint-fix

# Install pre-commit hooks
# Note: 'uv tool install' installs pre-commit globally and persists across sessions
# See docs/getting-started-dev.md for more details on uv tool management
[group('git')]
pre-commit-install:
    @echo "{{BLUE}}🔧 Installing pre-commit hooks...{{NORMAL}}"
    uv tool install pre-commit
    uv run pre-commit install
    uv run pre-commit install --hook-type commit-msg --hook-type pre-push
    @echo "{{GREEN}}✓ Pre-commit hooks installed successfully{{NORMAL}}"

# Run pre-commit on all files
[group('git')]
pre-commit-run:
    uv run pre-commit run --all-files

# Update pre-commit hooks to latest versions
[group('git')]
pre-commit-update:
    uv run pre-commit autoupdate

# Run semantic-release in dry-run mode to preview version changes
# Note: Uses 'uv tool run' for ephemeral, version-locked execution (latest v9.x)
[group('git')]
release-dry-run:
    uv tool run 'python-semantic-release>=9.15.0,<10.0.0' version --print

# Validate configuration files
[group('git')]
validate-config:
    {{python}} -c "import yaml; yaml.safe_load(open('config/app.yaml')); print('✓ app.yaml valid')"
    {{python}} -c "import yaml; yaml.safe_load(open('config/user.yaml.example')); print('✓ user.yaml.example valid')"
    @echo "{{GREEN}}✓ Configuration files validated successfully{{NORMAL}}"

# Scan dependencies for known security vulnerabilities
# Note: Uses 'uv tool run' for ephemeral execution of pip-audit
[group('quality')]
security-check:
    @echo "{{BLUE}}🔒 Scanning dependencies for vulnerabilities...{{NORMAL}}"
    uv tool run pip-audit --desc --skip-editable
    @echo "{{GREEN}}✓ Security scan complete{{NORMAL}}"

# Pre-release validation (security, tests, build preview)
[group('quality')]
[doc("Run comprehensive pre-release checks (security, tests, build validation)")]
release-check: security-check test build-dry-run
    @echo ""
    @echo "{{BOLD}}{{GREEN}}╔═══════════════════════════════════════╗{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}║   Release Validation Complete! ✓      ║{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}╚═══════════════════════════════════════╝{{NORMAL}}"
    @echo ""
    @echo "{{CYAN}}Ready for release! Next steps:{{NORMAL}}"
    @echo "  • Preview version: {{YELLOW}}just release-dry-run{{NORMAL}}"
    @echo "  • Build release:   {{YELLOW}}just build{{NORMAL}}"

# Update README.md with current project statistics
[group('documentation')]
update-docs:
    {{python}} scripts/update_readme_stats.py --verbose

# Update README.md (dry-run to preview changes)
[group('documentation')]
update-docs-dry:
    {{python}} scripts/update_readme_stats.py --dry-run

# Update plugin catalog from YAML manifests (auto-generate)
[group('documentation')]
[doc("Auto-generate plugin catalog from plugin YAML manifests")]
update-plugin-catalog:
    @echo "{{BOLD}}{{BLUE}}📋 Updating plugin catalog...{{NORMAL}}"
    {{python}} scripts/update_plugin_catalog.py --verbose
    @echo "{{GREEN}}✓ Plugin catalog updated successfully{{NORMAL}}"

# Update plugin catalog (dry-run to preview changes)
[group('documentation')]
update-plugin-catalog-dry:
    @echo "{{BOLD}}{{BLUE}}📋 Plugin catalog dry-run (preview mode)...{{NORMAL}}"
    {{python}} scripts/update_plugin_catalog.py --dry-run

# Build documentation locally with sphinx-multiversion
[group('documentation')]
[doc("Build multi-version documentation with Sphinx (output: docs/_build/html)")]
docs: _docs-fetch-releases _docs-build _docs-redirect
    @echo "{{GREEN}}✓ Documentation built successfully!{{NORMAL}}"
    @echo "  View at: {{CYAN}}docs/_build/html/index.html{{NORMAL}}"

[private]
_docs-fetch-releases:
    @echo "{{BLUE}}🔍 Fetching GitHub release tags...{{NORMAL}}"
    {{python}} scripts/get_release_tags.py

[private]
_docs-build:
    @echo "{{BLUE}}📚 Building multiversion documentation...{{NORMAL}}"
    {{python}} -m sphinx_multiversion docs docs/_build/html

[private]
[script('python3')]
_docs-redirect:
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

# Check documentation for broken links
[group('documentation')]
docs-linkcheck:
    {{python}} -m sphinx.cmd.build -b linkcheck docs docs/_build/linkcheck
    @echo "✓ Link check complete - see docs/_build/linkcheck/output.txt"

# Check documentation spelling
[group('documentation')]
docs-spelling:
    {{python}} -m sphinx.cmd.build -b spelling docs docs/_build/spelling
    @echo "✓ Spelling check complete - see docs/_build/spelling/output.txt"

# Serve documentation locally (requires Python http.server)
[group('documentation')]
docs-serve:
    @echo "Starting local documentation server at http://localhost:8000"
    @echo "Press Ctrl+C to stop"
    {{python}} -m http.server 8000 -d docs/_build/html

# Open built documentation in default browser (Windows)
[group('documentation')]
[windows]
open-docs:
    start docs\_build\html\index.html

# Open built documentation in default browser (macOS)
[group('documentation')]
[macos]
open-docs:
    open docs/_build/html/index.html

# Open built documentation in default browser (Linux)
[group('documentation')]
[linux]
open-docs:
    xdg-open docs/_build/html/index.html

# Clean documentation build artifacts
[group('maintenance')]
[script('python3')]
docs-clean:
    import shutil
    import pathlib

    docs_build = pathlib.Path('docs/_build')
    if docs_build.exists():
        shutil.rmtree(docs_build)
        print(f"✓ Removed {docs_build}")
    else:
        print(f"ℹ No documentation build to clean")

# Build portable distribution for specified version (Windows)
[group('build')]
[doc("Build portable distribution (default: Python 3.13, current platform, all formats)")]
[windows]
build VERSION=python_version ARCH="" FORMAT="" DRY_RUN="":
    $cmd = "{{python}} scripts/build_manager.py --version {{VERSION}}"; if ("{{ARCH}}" -ne "") { $cmd += " --arch {{ARCH}}" }; if ("{{FORMAT}}" -ne "") { $cmd += " --format {{FORMAT}}" }; if ("{{DRY_RUN}}" -ne "") { $cmd += " --dry-run" }; Invoke-Expression $cmd

# Build portable distribution for specified version (Unix)
[group('build')]
[doc("Build portable distribution (default: Python 3.13, current platform, all formats)")]
[unix]
build VERSION=python_version ARCH="" FORMAT="" DRY_RUN="":
    #!/usr/bin/env bash
    set -euo pipefail
    cmd="{{python}} scripts/build_manager.py --version {{VERSION}}"
    [ -n "{{ARCH}}" ] && cmd="$cmd --arch {{ARCH}}"
    [ -n "{{FORMAT}}" ] && cmd="$cmd --format {{FORMAT}}"
    [ -n "{{DRY_RUN}}" ] && cmd="$cmd --dry-run"
    eval "$cmd"

# Validate build parameters without creating files
[group('build')]
[doc("Preview build configuration without creating distribution")]
build-dry-run VERSION=python_version:
    {{python}} scripts/build_manager.py --version {{VERSION}} --dry-run

# Build and immediately test portable distribution
[group('build')]
[doc("Build portable distribution and run validation tests")]
build-and-test VERSION=python_version: (build VERSION) (test-portable VERSION)
    @echo ""
    @echo "{{BOLD}}{{GREEN}}╔═══════════════════════════════════════╗{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}║   Build and Test Complete! ✓          ║{{NORMAL}}"
    @echo "{{BOLD}}{{GREEN}}╚═══════════════════════════════════════╝{{NORMAL}}"

# Test portable distribution (extract, verify structure, test imports)
[group('build')]
[doc("Validate portable distribution by extracting and testing imports")]
test-portable VERSION=python_version:
    @echo "{{BLUE}}🧪 Testing portable distribution for Python {{VERSION}}...{{NORMAL}}"
    {{python}} scripts/test_portable_build.py --version {{VERSION}}
    @echo "{{GREEN}}✓ Portable build validation passed{{NORMAL}}"

# Test all portable distributions (Windows)
[group('build')]
[doc("Test all portable Python distributions and report failures")]
[windows]
test-portable-all:
    @echo "{{BOLD}}{{BLUE}}🧪 Testing all portable distributions...{{NORMAL}}"
    $ErrorActionPreference = 'Continue'; $failed = 0; foreach ($version in @('3.12', '3.13', '3.14')) { Write-Host "`n  Testing Python $version..." -ForegroundColor Cyan; $result = & just test-portable $version 2>&1; if ($LASTEXITCODE -ne 0) { Write-Host "  {{YELLOW}}✗ Python $version test failed{{NORMAL}}" -ForegroundColor Yellow; $failed++ } else { Write-Host "  {{GREEN}}✓ Python $version test passed{{NORMAL}}" -ForegroundColor Green } }; Write-Host ""; if ($failed -eq 0) { Write-Host "{{GREEN}}✓ All portable build tests passed!{{NORMAL}}" -ForegroundColor Green } else { Write-Host "{{RED}}✗ $failed version(s) failed{{NORMAL}}" -ForegroundColor Red; exit 1 }

# Test all portable distributions (Unix)
[group('build')]
[doc("Test all portable Python distributions and report failures")]
[unix]
test-portable-all:
    #!/usr/bin/env bash
    set -uo pipefail
    echo -e "\033[1m\033[34m🧪 Testing all portable distributions...\033[0m"
    failed=0
    for version in 3.12 3.13 3.14; do
        echo -e "\n  Testing Python $version..."
        if ! just test-portable "$version"; then
            echo -e "\033[33m  ✗ Python $version test failed\033[0m"
            failed=$((failed + 1))
        else
            echo -e "\033[32m  ✓ Python $version test passed\033[0m"
        fi
    done
    echo ""
    if [ $failed -eq 0 ]; then
        echo -e "\033[1m\033[32m✓ All portable build tests passed!\033[0m"
    else
        echo -e "\033[1m\033[31m✗ $failed version(s) failed\033[0m"
        exit 1
    fi

# Run application in development mode (uses virtual environment)
[group('run')]
[doc("Run application in development mode using uv virtual environment")]
run:
    @echo "{{BLUE}}🚀 Starting pyMediaManager (development mode)...{{NORMAL}}"
    {{python}} launcher.py

# Run application from portable build (Windows)
[group('run')]
[doc("Run application from portable distribution (specify Python version: 3.12, 3.13, or 3.14)")]
[windows]
[script('python3')]
run-portable VERSION=python_version:
    import platform
    import subprocess
    import sys
    from pathlib import Path

    version = "{{VERSION}}"
    arch = "x64" if platform.machine().endswith('64') else "x86"
    dist_dir = Path("dist")

    # Look for extracted directory first
    pattern = f"pyMM-*-py{version}-win-{arch}"
    dirs = list(dist_dir.glob(pattern))

    if not dirs:
        # Look for ZIP file and extract it
        zip_pattern = f"pyMM-*-py{version}-win-{arch}.zip"
        zips = sorted(dist_dir.glob(zip_pattern), key=lambda p: p.stat().st_mtime, reverse=True)
        if zips:
            import zipfile
            zip_file = zips[0]
            print(f"🚀 Starting pyMediaManager (portable mode - Python {version})...")
            print(f"  Extracting: {zip_file.name}")
            extract_path = zip_file.with_suffix('')
            with zipfile.ZipFile(zip_file, 'r') as zf:
                zf.extractall(extract_path)
            dirs = [extract_path]
        else:
            print(f"Error: No portable distribution found for Python {version}", file=sys.stderr)
            print(f"Expected: dist/{pattern}", file=sys.stderr)
            print(f"Build it first: just build {version}")
            sys.exit(1)

    # Use most recent build
    portable_dir = sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    python_exe = portable_dir / "python.exe"
    launcher = portable_dir / "launcher.py"

    print(f"🚀 Starting pyMediaManager (portable mode - Python {version})...")
    print(f"  Using: {portable_dir.name}")

    subprocess.run([str(python_exe), str(launcher)])

# Run application from portable build (Linux)
[group('run')]
[doc("Run application from portable distribution (specify Python version: 3.12, 3.13, or 3.14)")]
[linux]
run-portable VERSION=python_version:
    #!/usr/bin/env bash
    set -euo pipefail
    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64) ARCH="x64" ;;
        aarch64) ARCH="arm64" ;;
        *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
    esac
    PORTABLE_PATTERN="dist/pyMM-*-py{{VERSION}}-linux-${ARCH}.AppImage"
    PORTABLE=$(ls -t $PORTABLE_PATTERN 2>/dev/null | head -1 || true)
    if [ -z "$PORTABLE" ]; then
        echo "Error: No portable AppImage found for Python {{VERSION}}"
        echo "Expected: $PORTABLE_PATTERN"
        echo "Build it first: just build {{VERSION}}"
        exit 1
    fi
    echo "🚀 Starting pyMediaManager (portable mode - Python {{VERSION}})..."
    echo "  Using: $PORTABLE"
    chmod +x "$PORTABLE"
    "$PORTABLE"

# Run application from portable build (macOS)
[group('run')]
[doc("Run application from portable distribution (specify Python version: 3.12, 3.13, or 3.14)")]
[macos]
run-portable VERSION=python_version:
    #!/usr/bin/env bash
    set -euo pipefail
    PORTABLE_APP="dist/pyMM.app"
    if [ ! -d "$PORTABLE_APP" ]; then
        echo "Error: Portable app not found at $PORTABLE_APP"
        echo "Build it first: just build {{VERSION}}"
        exit 1
    fi
    echo "🚀 Starting pyMediaManager (portable mode - Python {{VERSION}})..."
    echo "  Using: $PORTABLE_APP"
    open "$PORTABLE_APP"

# Run application in development mode with debug logging
[group('run')]
[doc("Run application in development mode with DEBUG log level")]
run-debug:
    @echo "{{BLUE}}🚀 Starting pyMediaManager (development mode - DEBUG logging)...{{NORMAL}}"
    {{python}} launcher.py --log-level DEBUG

# Show what would change when migrating plugins to v2 schema (dry-run)
[group('plugins')]
migrate-plugins-dry:
    {{python}} -m app.plugins.plugin_migrator dry-run --plugins-dir plugins

# Migrate all plugins to v2 schema with backups
[group('plugins')]
[doc("Migrate all plugins to v2 schema format with automatic backups")]
migrate-plugins:
    {{python}} -m app.plugins.plugin_migrator migrate --plugins-dir plugins

# Migrate a specific plugin to v2 schema
[group('plugins')]
migrate-plugin NAME:
    {{python}} -m app.plugins.plugin_migrator migrate --plugins-dir plugins --plugin {{NAME}}

# Rollback all plugin migrations
[group('plugins')]
[confirm]
rollback-plugins:
    {{python}} -m app.plugins.plugin_migrator rollback --plugins-dir plugins

# Rollback a specific plugin migration
[group('plugins')]
rollback-plugin NAME:
    {{python}} -m app.plugins.plugin_migrator rollback --plugins-dir plugins --plugin {{NAME}}

# Build and run complete Docker CI pipeline
[group('docker')]
[doc("Build Docker image and run full CI pipeline (lint, type-check, test) in container")]
ci-docker: ci-docker-build ci-docker-test

# Build Docker image for CI testing (multi-platform support)
[group('docker')]
ci-docker-build PYTHON_VER=python_version PLATFORM="linux/amd64": _check-docker
    docker build \
        --build-arg PYTHON_VERSION={{PYTHON_VER}} \
        --platform {{PLATFORM}} \
        --target test \
        -t pymm-ci:{{PYTHON_VER}} \
        -t pymm-ci:latest \
        .

# Build for multiple Python versions
[group('docker')]
ci-docker-build-all:
    @echo "Building for Python 3.12, 3.13, 3.14..."
    @just ci-docker-build 3.12
    @just ci-docker-build 3.13
    @just ci-docker-build 3.14

# Run complete CI pipeline in Docker (lint, type-check, test)
[group('docker')]
ci-docker-test IMAGE="pymm-ci:latest": _check-docker
    @echo "{{BOLD}}{{CYAN}}╔═══════════════════════════════════════╗{{NORMAL}}"
    @echo "{{BOLD}}{{CYAN}}║     Running CI Pipeline in Docker     ║{{NORMAL}}"
    @echo "{{BOLD}}{{CYAN}}╚═══════════════════════════════════════╝{{NORMAL}}"
    @echo ""
    @echo "{{YELLOW}}▶ Running linting...{{NORMAL}}"
    docker run --rm {{IMAGE}} python -m ruff check app/
    @echo ""
    @echo "{{YELLOW}}▶ Running type checking...{{NORMAL}}"
    docker run --rm {{IMAGE}} python -m mypy app/ docs/ scripts/ tests/ launcher.py
    @echo ""
    @echo "{{YELLOW}}▶ Running tests...{{NORMAL}}"
    docker run --rm {{IMAGE}} bash -c "\
        export QT_QPA_PLATFORM=offscreen; \
        export DISPLAY=:99; \
        Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 & \
        sleep 2; \
        pytest tests/ --cov=app --cov-report=term"

# Run interactive shell in Docker container for debugging
[group('docker')]
ci-docker-shell IMAGE="pymm-ci:latest": _check-docker
    docker run --rm -it {{IMAGE}} /bin/bash

# Clean Docker images and containers (cross-platform)
[group('docker')]
[confirm("Remove all pymm-ci Docker images?")]
[script('python3')]
ci-docker-clean:
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
[group('docker')]
[confirm("This will delete ALL Docker build cache (not just pyMM). Continue?")]
[script('python3')]
ci-docker-build-delete:
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

# Check if Docker is available
[private]
[script('python3')]
_check-docker:
    import shutil
    import sys

    if not shutil.which('docker'):
        print("Error: Docker is not installed or not in PATH. Install Docker to use this recipe.", file=sys.stderr)
        sys.exit(1)

# Check if npx is available
[private]
[script('python3')]
_check-npx:
    import shutil
    import sys

    if not shutil.which('npx'):
        print("Error: npx is not installed or not in PATH. Install Node.js/npm to use this recipe.", file=sys.stderr)
        sys.exit(1)

# Clean build artifacts and cache (using pathlib for cross-platform)
[group('maintenance')]
[script('python3')]
clean:
    from pathlib import Path
    import shutil
    import stat
    import sys

    def handle_remove_readonly(func, path, exc):
        """
        Error handler for Windows readonly files.
        If the error is due to an access error (read only file),
        it attempts to add write permission and then retries.
        """
        import os
        if not os.access(path, os.W_OK):
            # Add write permission and retry
            os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
            func(path)
        else:
            raise

    # Root level patterns to clean
    root_patterns = [
        "build", "dist", "*.egg-info", ".coverage", ".coverage.*",
        "htmlcov", "*.zip", "*.sha256", "get-pip.py", "performance_*.json",
        "interrogate_badge.svg"
    ]

    # Recursive patterns (cleans subdirectories)
    recursive_patterns = [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/.pytest_tmp",
        "**/.mypy_cache",
        "**/.ruff_cache",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
        "**/.venv",
        "**/test_projects"
    ]

    print("🧹 Cleaning artifacts...")
    removed_count = 0

    # Clean root patterns
    for pattern in root_patterns:
        for path in Path(".").glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path, onerror=handle_remove_readonly)
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
                    shutil.rmtree(path, onerror=handle_remove_readonly)
                else:
                    path.unlink()
                print(f"  ✓ Removed {path}")
                removed_count += 1
            except Exception as e:
                print(f"  ✗ Failed to remove {path}: {e}")

    print(f"\n✨ Cleanup complete! Removed {removed_count} items.")

# Show UV cache information
[group('maintenance')]
uv-cache-info:
    @echo "{{BLUE}}💾 UV Cache Information{{NORMAL}}"
    @echo ""
    uv cache dir
    @echo ""
    uv cache info

# Clean UV cache directory
[group('maintenance')]
[confirm("Remove all UV cache? This will re-download packages on next use.")]
uv-cache-clean:
    @echo "{{BLUE}}🧹 Cleaning UV cache...{{NORMAL}}"
    uv cache clean
    @echo "{{GREEN}}✓ UV cache cleaned{{NORMAL}}"

# Clean everything (includes docs build)
[group('maintenance')]
[confirm]
clean-all: _cleanup-tmp docs-clean clean
    @echo "✨ Complete cleanup finished!"
