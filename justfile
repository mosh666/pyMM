# Justfile for pyMediaManager

# Configure shells for different platforms
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

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
    python -c "import subprocess, sys, pathlib; script = pathlib.Path('scripts/setup-git-hooks.sh' if sys.platform != 'win32' else 'scripts/setup-git-hooks.ps1'); subprocess.run(['bash', str(script)] if sys.platform != 'win32' else ['pwsh.exe', '-ExecutionPolicy', 'Bypass', '-File', str(script)], check=True)"

# Build documentation locally
docs:
    python -m pip install sphinx-multiversion
    python -m sphinx_multiversion docs docs/_build/html
    python -c "import pathlib; pathlib.Path('docs/_build/html/index.html').write_text('<meta http-equiv=\"refresh\" content=\"0; url=main/index.html\">', encoding='utf-8')"

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
