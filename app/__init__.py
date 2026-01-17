"""pyMediaManager - Portable media management application."""

# ruff: noqa: I001  # Prevent shadowing (Python 3.12)
import platform as _platform
from importlib.metadata import PackageNotFoundError, version
from typing import Optional

try:
    from ._version import version as __version__
except ImportError:
    try:
        __version__ = version("pyMediaManager")
    except PackageNotFoundError:
        __version__ = "0.0.0-dev"

# Extract commit ID from version string if available (e.g., "0.1.0b9.post1+g8d85556f5")
__commit_id__: str | None = None
if "+" in __version__ and __version__.split("+")[1].startswith("g"):
    __commit_id__ = __version__.split("+")[1][1:]  # Remove 'g' prefix

__all__ = [
    "__commit_id__",
    "__version__",
]
