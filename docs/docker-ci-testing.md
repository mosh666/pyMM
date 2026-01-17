# Docker CI Testing Guide

## Overview

This guide explains how to run a complete CI pipeline locally using Docker, mimicking what happens in
GitHub Actions. All commands use the modernized Just task runner with 2026 features (colored output,
safety confirmations, dependency validation).

## Quick Start

### Run Complete CI Pipeline

```bash
just ci-docker
```

This command will:

1. **Validate** that Docker is installed (with helpful error if missing)
2. **Build** a Docker image with all dependencies
3. **Run** the complete CI pipeline:
   - 🔍 Linting (ruff)
   - 🔬 Type checking (mypy)
   - 🧪 Full test suite with coverage

**Output includes:**

- 📦 Colored section headers for each stage
- ✅ Success indicators for each check
- 📊 Test coverage report

### Individual Commands

#### Build Docker Image Only

```bash
just ci-docker-build

# Build for specific Python version
just ci-docker-build 3.12
just ci-docker-build 3.13

# Build for multiple versions
just ci-docker-build-all
```

**Features:**

- Validates Docker availability before building
- Multi-platform support (linux/amd64, linux/arm64)
- Progress indicators during build

#### Run Tests Only (requires image to be built first)

```bash
just ci-docker-test

# Or use a specific image
just ci-docker-test pymm-ci:3.12
```

**Features:**

- 🎨 Colored output with section headers
- ▶️ Progress indicators for each test phase
- Visual box showing pipeline execution

#### Interactive Debug Shell

```bash
just ci-docker-shell

# Or use a specific image
just ci-docker-shell pymm-ci:3.12
```

This opens an interactive bash shell inside the Docker container where you can:

- Run commands manually
- Debug issues
- Inspect the environment
- Run specific tests

#### Cleanup (⚠️ With Safety Prompts)

```bash
# Remove Docker images (prompts: "Remove all pymm-ci Docker images?")
just ci-docker-clean

# Remove build cache (prompts: "This will delete ALL Docker build cache. Continue?")
just ci-docker-build-delete
```

**Safety Features:**

- `[confirm]` prompts prevent accidental deletion
- Clear warning messages about scope of deletion
- Can be bypassed with `--yes` flag in CI environments

## What Gets Tested

The Docker CI pipeline runs the same checks as the GitHub Actions CI:

1. **Linting**: `ruff check .`
   - Code style and quality checks
   - PEP 8 compliance
   - Common Python mistakes

2. **Type Checking**: `mypy .`
   - Static type analysis
   - Type hint validation

3. **Tests**: `pytest tests/ --cov=app`
   - All unit and integration tests
   - Code coverage analysis
   - GUI tests (using xvfb for headless display)

## Docker Image Details

- Base: `python:3.12-slim-bookworm`
- Includes all PySide6/Qt dependencies for GUI testing
- Uses xvfb for headless GUI testing
- Includes git for hatch-vcs version detection

## Troubleshooting

### Build Fails

- Ensure Docker is running
- Check Docker has enough disk space
- Try `docker system prune` to clean up old images

### Tests Fail

- Run `just ci-docker-shell` to debug interactively
- Check if tests pass locally: `just test`
- Compare with GitHub Actions logs

### Image is Too Large

The image is large (~1.5GB) because it includes:

- PySide6 and all Qt libraries
- X11 and graphics libraries for GUI testing
- All dev dependencies

This is normal for a complete testing environment.

## CI/CD Integration

The Docker setup matches the GitHub Actions configuration in `.github/workflows/ci.yml`:

- Same Python version (3.12)
- Same testing commands
- Same dependencies

Running `just ci-docker` before pushing gives you confidence that CI will pass.
