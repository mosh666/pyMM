"""
Platform-specific package for pyMediaManager.

This package contains platform-specific implementations organized by OS:
- linux/: Linux-specific utilities (udev handling, etc.)
- macos/: macOS-specific utilities (plist, Keychain, etc.)
- windows/: Windows-specific utilities (registry, etc.)

For centralized platform detection, use app.core.platform instead:
    from app.core.platform import Platform, current_platform, is_windows

Storage implementations (WindowsStorage, LinuxStorage, MacOSStorage) are
kept co-located in app.core.services.storage_service for discoverability.
"""

from __future__ import annotations

__all__: list[str] = []
