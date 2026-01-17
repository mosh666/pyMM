#!/usr/bin/env python3
"""
pyMediaManager Launcher
Entry point for the portable Python application.

This script configures the environment to ensure valid import paths:
1. Portable Mode: Adds embedded `lib-pyX.Y` folders to sys.path.
2. Source Mode: Adds the project root to sys.path.
3. UV Detection: Adds bundled uv executable to PATH if present.

It then hands off execution to `app.main.run_application()`.
"""

import logging
import os
from pathlib import Path
import sys

# Determine application root (where launcher.py resides)
APP_ROOT = Path(__file__).parent.resolve()

# Detect Python version to load correct lib directory
PYTHON_VERSION = f"py{sys.version_info.major}{sys.version_info.minor}"

# Configure sys.path for portable environment
# Priority: app code -> version-specific libs -> Python stdlib
lib_dir = APP_ROOT / f"lib-{PYTHON_VERSION}"
if not lib_dir.exists():
    # Fallback to generic lib/ directory
    lib_dir = APP_ROOT / "lib"

if lib_dir.exists():
    sys.path.insert(0, str(lib_dir))

# Ensure APP_ROOT is in path so 'app' package can be imported
sys.path.insert(0, str(APP_ROOT))

# Add bundled uv to PATH if present (for portable distributions)
# Check platform-specific uv binary locations
uv_paths = [
    APP_ROOT / "bin" / "uv.exe",  # Windows portable
    APP_ROOT / "bin" / "uv",  # Linux/macOS portable
    APP_ROOT / "uv.exe",  # Windows root
    APP_ROOT / "uv",  # Linux/macOS root
]

for uv_path in uv_paths:
    if uv_path.exists():
        bin_dir = str(uv_path.parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
        break

# Initialize basic logging for launcher errors
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)


def main() -> int:
    """Main entry point for pyMediaManager."""
    try:
        # Import after path setup
        from app.main import run_application

        return run_application()
    except ImportError:
        logger.exception("Failed to import application")
        logger.exception("APP_ROOT: %s", APP_ROOT)
        logger.exception("PYTHON_VERSION: %s", PYTHON_VERSION)
        logger.exception("lib_dir: %s", lib_dir)
        logger.exception("sys.path: %s", sys.path)
        return 1
    except Exception as e:
        logger.critical("Application crashed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
