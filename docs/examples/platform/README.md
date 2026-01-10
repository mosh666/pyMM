# Platform Abstraction Examples

Examples for writing cross-platform code in pyMediaManager.

## Overview

pyMM provides platform abstraction utilities to handle Windows, Linux, and macOS differences elegantly.

## Basic Examples

**`detect_platform.py`** - Detect current platform
**`platform_paths.py`** - Use platform-specific paths
**`check_platform_features.py`** - Check platform capabilities

## Intermediate Examples

**`platform_config.py`** - Platform-specific configuration
**`conditional_imports.py`** - Import platform-specific modules
**`platform_testing.py`** - Test code on different platforms

## Advanced Examples

**`compatibility_checks.py`** - Validate cross-platform compatibility
**`custom_platform_handler.py`** - Extend platform abstraction
**`ast_validation.py`** - Ensure no direct platform checks

## Key Concepts

- **Platform Detection**: Identify OS at runtime
- **Path Handling**: XDG directories, Windows AppData, macOS ~/Library
- **AST Validation**: Prevent direct `sys.platform` usage
- **Plugin Compatibility**: Declare supported platforms in manifests

## See Also

- {doc}`../../architecture` - Platform Abstraction Section
- {ref}`platform-abstraction` - API Reference Platform Module
- {doc}`../../platform-directories`
