"""
macOS-specific platform utilities for pyMediaManager.

This module provides macOS-specific functionality that cannot be abstracted
in a cross-platform way. Currently serves as a placeholder for future utilities.

Implemented functionality:
- (Future) macOS plist handling
- (Future) macOS Keychain integration
- (Future) macOS notification center integration
- (Future) macOS sandbox/entitlements handling

For storage detection, see app.core.services.storage_service.MacOSStorage
which is kept co-located with other storage implementations for discoverability.

Note:
    All platform detection should use app.core.platform.Platform enum
    instead of direct sys.platform checks.

Example:
    from app.core.platform import is_macos, Platform

    if is_macos():
        from app.platform.macos import some_macos_utility
        some_macos_utility()
"""

from __future__ import annotations

__all__: list[str] = []

# Future macOS-specific utilities will be added here
# For now, macOS storage detection is in app.core.services.storage_service.MacOSStorage
