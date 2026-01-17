#!/usr/bin/env python3
"""Read and display configuration values.

This example demonstrates:
- Loading configuration
- Accessing nested config values
- Understanding config structure
"""

import logging

from app.services.config_service import ConfigService

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> None:
    """Read and display current configuration."""
    # Initialize config service
    config_service = ConfigService()

    # Load configuration
    config = config_service.load_config()

    # Application settings

    # UI settings

    # Logging settings
    if config.logging.file_enabled:
        pass

    # Plugin settings

    # Project settings
    if config.projects.template_directories:
        for _template_dir in config.projects.template_directories:
            pass

    # Git settings
    if hasattr(config, "git") and config.git.user_name:
        pass

    # Config file location


if __name__ == "__main__":
    main()
