# Docker CI Testing Guide

## Overview

This guide explains how to run a complete CI pipeline locally using Docker, mimicking what happens in GitHub Actions.

## Quick Start

### Run Complete CI Pipeline

```bash
just ci-docker
```

This command:

1. Builds a Docker image with all dependencies
2. Runs linting (ruff)
3. Runs type checking (mypy)
4. Runs the full test suite with coverage

### Individual Commands

#### Build Docker Image Only

```bash
just ci-docker-build
```

#### Run Tests Only (requires image to be built first)

```bash
just ci-docker-test
```

#### Interactive Debug Shell

```bash
just ci-docker-shell
```

This opens an interactive bash shell inside the Docker container where you can:

- Run commands manually
- Debug issues
- Inspect the environment

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
- Includes git for setuptools-scm version detection

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
