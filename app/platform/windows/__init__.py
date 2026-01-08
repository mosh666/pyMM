"""
Windows-specific platform utilities for pyMediaManager.

This module provides Windows-specific functionality that cannot be abstracted
in a cross-platform way. Currently serves as a placeholder for future utilities.

Implemented functionality:
- (Future) Windows Registry helpers
- (Future) Windows-specific file association handling
- (Future) Windows notification system integration

For storage detection, see app.core.services.storage_service.WindowsStorage
which is kept co-located with other storage implementations for discoverability.

Note:
    All platform detection should use app.core.platform.Platform enum
    instead of direct sys.platform checks.

Example:
    from app.core.platform import is_windows, Platform

    if is_windows():
        from app.platform.windows import some_windows_utility
        some_windows_utility()
"""

from __future__ import annotations

__all__: list[str] = []

# Future Windows-specific utilities will be added here
# For now, Windows storage detection is in app.core.services.storage_service.WindowsStorage
