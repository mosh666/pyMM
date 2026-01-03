"""pyMediaManager - Portable media management application."""

__version__ = "0.0.1"

try:
    from app._version import version as __version__
except ImportError:
    # Fallback if _version.py doesn't exist (development mode)
    pass
