"""pyMediaManager - Portable media management application."""

from importlib.metadata import PackageNotFoundError, version

try:
    from ._version import commit_id as __commit_id__  # type: ignore[attr-defined]
    from ._version import version as __version__
except ImportError:
    try:
        __version__ = version("pyMediaManager")
    except PackageNotFoundError:
        __version__ = "0.0.0-dev"
    __commit_id__ = None

__all__ = [
    "__commit_id__",
    "__version__",
]
