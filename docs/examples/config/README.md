# Configuration Management Examples

Examples for working with pyMediaManager's configuration system.

## Overview

pyMM uses a layered configuration system with YAML files, supporting defaults, user settings, and portable mode.

## Basic Examples

**`read_config.py`** - Read configuration values
**`update_config.py`** - Modify and save configuration
**`config_locations.py`** - Show where config files are stored

## Intermediate Examples

**`config_layering.py`** - Understand config layer priority
**`environment_variables.py`** - Use environment variable overrides
**`portable_mode.py`** - Configure portable mode settings

## Advanced Examples

**`custom_validators.py`** - Add configuration validators
**`config_migration.py`** - Migrate old config to new format
**`schema_evolution.py`** - Handle config schema changes

## Key Concepts

- **Config Layers**: Default → User → Portable (highest priority)
- **Validation**: Pydantic models ensure config correctness
- **Portable Mode**: Self-contained config for USB drives
- **Platform Directories**: XDG-compliant config locations

## See Also

- [User Guide Configuration Section](../../configuration.md) - Configuration guide
- {ref}`configservice` - API Reference ConfigService
- {doc}`../../platform-directories`
