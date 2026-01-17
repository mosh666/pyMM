#!/usr/bin/env python3
"""Detect current platform and display information.

This example demonstrates:
- Using platform detection utilities
- Getting platform information
- Understanding supported platforms
"""

from app.core.platform import Platform, get_platform


def main() -> None:
    """Display platform information."""

    # Get current platform using pyMM's abstraction
    current_platform = get_platform()

    # Show standard library platform info

    # Show platform-specific features

    if current_platform in (Platform.WINDOWS, Platform.LINUX) or current_platform == Platform.MACOS:
        pass


if __name__ == "__main__":
    main()
