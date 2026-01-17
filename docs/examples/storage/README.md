# Storage Detection Examples

> **Last Updated:** 2026-01-17 21:41 UTC
\nExamples for working with storage devices and drive detection in pyMediaManager.

## Overview

pyMM can detect and work with local drives, USB devices, and network storage across Windows, Linux, and macOS.

## Basic Examples

**`list_drives.py`** - List all available drives
**`check_drive_status.py`** - Check drive availability and space
**`portable_detection.py`** - Detect portable mode drives

## Intermediate Examples

**`monitor_drive_changes.py`** - Watch for drive connections/disconnections
**`validate_drive.py`** - Check if drive meets project requirements
**`drive_info.py`** - Get detailed drive information

## Advanced Examples

**`cross_platform_storage.py`** - Handle platform-specific storage
**`network_drives.py`** - Work with network-mounted storage
**`custom_storage_backend.py`** - Implement custom storage detection

## Key Concepts

- **Drive Detection**: Platform-specific discovery of storage devices
- **Portable Mode**: Detect pyMM installations on USB drives
- **Drive Monitoring**: React to storage changes (plug/unplug)
- **Cross-Platform**: Unified API across Windows/Linux/macOS

## See Also

- {ref}`storage-management` - User Guide Storage Management
- {ref}`storageservice` - API Reference StorageService
- {doc}`../../platform-directories`
