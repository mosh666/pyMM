#!/usr/bin/env python3
"""
pyMediaManager Launcher
Entry point for the portable Python application.
Configures paths for embeddable Python and launches the main application.
"""

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


def main() -> int:
    """Main entry point for pyMediaManager."""
    try:
        # Import after path setup
        from app.main import run_application

        return run_application()
    except ImportError as e:
        print(f"ERROR: Failed to import application: {e}", file=sys.stderr)
        print(f"\nAPP_ROOT: {APP_ROOT}", file=sys.stderr)
        print(f"PYTHON_VERSION: {PYTHON_VERSION}", file=sys.stderr)
        print(f"lib_dir: {lib_dir}", file=sys.stderr)
        print(f"sys.path: {sys.path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Application crashed: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
