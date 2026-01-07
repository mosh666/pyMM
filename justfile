# Justfile for pyMediaManager

# Release build version
version := "3.12"

# Install dependencies in editable mode
install:
    pip install pip-tools
    pip-compile -o requirements.lock pyproject.toml
    pip install -e .[dev]

# Update lockfile
lock:
    pip-compile -o requirements.lock pyproject.toml

# Run unit tests
test:
    pytest

# Run linter and type checker
lint:
    ruff check .
    mypy .

# Format code
format:
    ruff format .

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
