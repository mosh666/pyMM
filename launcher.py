#!/usr/bin/env python3
"""
pyMediaManager Launcher
Entry point for the portable Python application.
Configures paths for embeddable Python and launches the main application.
"""

import logging
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

sys.path.insert(0, str(APP_ROOT / "app"))

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
    except ImportError as e:
        logger.error("Failed to import application: %s", e)
        logger.error("APP_ROOT: %s", APP_ROOT)
        logger.error("PYTHON_VERSION: %s", PYTHON_VERSION)
        logger.error("lib_dir: %s", lib_dir)
        logger.error("sys.path: %s", sys.path)
        return 1
    except Exception as e:
        logger.critical("Application crashed: %s", e, exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
