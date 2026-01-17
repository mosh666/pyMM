# Plugin System Examples

> **Last Updated:** 2026-01-17 21:41 UTC


Examples demonstrating pyMediaManager's plugin architecture, installation, and management.

## Overview

pyMM uses a manifest-based plugin system with SHA-256 verification. Plugins extend
functionality for different media management tools (Git, digiKam, etc.).

## Basic Examples

**`list_plugins.py`** - List all available and installed plugins
**`check_plugin_status.py`** - Check if specific plugins are installed
**`get_plugin_metadata.py`** - Read plugin manifest information

## Intermediate Examples

**`install_plugin.py`** - Install a plugin programmatically
**`validate_manifest.py`** - Validate plugin manifest structure
**`check_dependencies.py`** - Verify plugin dependencies are met

## Advanced Examples

**`create_custom_plugin.py`** - Create a new plugin from scratch
**`verify_plugin_signature.py`** - Implement SHA-256 verification
**`platform_specific_plugin.py`** - Handle platform-specific plugin code

## Key Concepts

- **Plugin Manifest**: YAML file defining plugin metadata, dependencies, and files
- **SHA-256 Verification**: Security feature ensuring plugin integrity
- **Plugin Discovery**: Automatic scanning of plugin directories
- **Lazy Loading**: Plugins loaded on-demand for performance

## See Also

- {doc}`../../plugin-development`
- {doc}`../../plugin-catalog`
- {ref}`pluginmanager` - API Reference PluginManager
