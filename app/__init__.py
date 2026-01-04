"""pyMediaManager - Portable media management application."""

from importlib.metadata import version, PackageNotFoundError

try:
    from ._version import version as __version__
    from ._version import commit_id as __commit_id__
except ImportError:
    try:
        __version__ = version("pyMediaManager")
    except PackageNotFoundError:
        __version__ = "0.0.0-dev"
    __commit_id__ = None
