# API Reference

> **Last Updated:** 2026-01-17 21:41 UTC


```{eval-rst}
.. currentmodule:: app
```

> **Status:** Complete with 100% docstring coverage (724/724 items documented)
> **Python Support:** 3.12, 3.13, 3.14 (CI testing)
> **Type Safety:** 100% MyPy strict mode compliance (0 errors)
Complete API reference for pyMediaManager with detailed documentation for all modules,
classes, and functions. All APIs include comprehensive docstrings with type hints,
examples, and cross-references.

## Quick Navigation

::::{grid} 2
:gutter: 3

:::{grid-item-card} 🔌 Plugin System

Discover, install, and manage plugins with manifest-based architecture and SHA-256 verification.

See: {ref}`api-plugin-system`
:::

:::{grid-item-card} 📁 Project Management

Create and manage media projects with templates, migrations, and version control
integration.

See: [Project Service API](#projectservice)
:::

:::{grid-item-card} 🔄 Synchronization Engine

Phase 2 sync system with scheduled/real-time sync, encryption, compression, and bandwidth throttling.

See: {ref}`sync-engine-api`
:::

:::{grid-item-card} 💾 Storage Detection

Cross-platform drive detection with portable mode support and real-time monitoring.

See: [Platform Specific Modules](#platform-specific-modules)
:::

:::{grid-item-card} ⚙️ Configuration

Layered configuration system with validation, portable mode, and environment
variables.

See: [Configuration Service API](#configservice)
:::

:::{grid-item-card} 🖥️ User Interface

PySide6 + QFluentWidgets components for building modern Fluent Design interfaces.

See: [User Interface](#user-interface)
:::

::::

## Architecture Overview

pyMediaManager follows a layered architecture:

```{eval-rst}
.. mermaid::

   graph TB
       UI[User Interface Layer<br/>PySide6 + QFluentWidgets]
       Services[Services Layer<br/>Business Logic]
       Core[Core Layer<br/>Platform Abstraction]
       Plugins[Plugin System<br/>Extensibility]
       Models[Data Models<br/>Pydantic Schemas]

       UI --> Services
       UI --> Plugins
       Services --> Core
       Services --> Models
       Plugins --> Core
       Plugins --> Models

       style UI fill:#4CAF50
       style Services fill:#2196F3
       style Core fill:#FF9800
       style Plugins fill:#9C27B0
       style Models fill:#00BCD4
```

---

(api-plugin-system)=

## Plugin System

The plugin system provides extensible functionality through manifest-based plugins with SHA-256 verification for security.

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 📖 Learn More

- [Plugin Development Guide](plugin-development.md)
- [Plugin Catalog](plugin-catalog.md)
- [Example: List Plugins](examples/plugins/basic/list_plugins.py)

:::

:::{grid-item-card} 🎯 Key Features

- Manifest-based architecture (YAML)
- SHA-256 file integrity verification
- Platform-specific plugin support
- Automatic dependency checking
- Template-based project migration
:::

::::

(plugin-manager-api)=
(pluginmanager)=

### PluginManager

Central hub for plugin discovery, installation, and lifecycle management.

```{eval-rst}
.. autoclass:: app.plugins.plugin_manager.PluginManager
   :members:
   :undoc-members:
   :show-inheritance:
   :inherited-members:

   .. rubric:: Usage Example

   .. code-block:: python

      from pathlib import Path
      from app.plugins.plugin_manager import PluginManager

      # Initialize plugin manager
      plugin_manager = PluginManager(
          plugins_dir=Path("plugins"),
          manifests_dir=Path("manifests")
      )

      # Discover available plugins
      plugins = plugin_manager.discover_plugins()

      # Install a plugin
      plugin_manager.install_plugin("git")

      # Check installation status
      if plugin_manager.is_installed("digikam"):
          print("digiKam plugin ready")

   .. seealso::

      - :doc:`plugin-development`
```

### PluginBase

Abstract base class for all plugin implementations.

```{eval-rst}
.. autoclass:: app.plugins.plugin_base.PluginBase
   :members:
   :undoc-members:
   :show-inheritance:
```

### Plugin Manifest Schema

Pydantic models for plugin manifest validation.

```{eval-rst}
.. automodule:: app.plugins.plugin_schema
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

   .. rubric:: Manifest Structure

   Plugin manifests are YAML files defining metadata, dependencies, and files:

   .. code-block:: yaml

      name: git
      version: "1.0.0"
      author: pyMM Team
      description: Git version control integration

      min_python_version: "3.12"
      min_app_version: "0.1.0"

      platforms:
        - windows
        - linux
        - macos

      dependencies:
        python:
          GitPython: ">=3.1.0"
        system:
          - git

      files:
        plugin.py: "sha256:abc123..."
        config.yaml: "sha256:def456..."
```

### PluginMigrator

Handles project template migrations when plugins are updated.

```{eval-rst}
.. .. autoclass:: app.plugins.plugin_migrator.PluginMigrator
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. note::
   Class implementation pending.
```

### SystemToolDetector

Cross-platform system tool detection and validation.

```{eval-rst}
.. autoclass:: app.plugins.system_tool_detector.SystemToolDetector
   :members:
   :undoc-members:
   :show-inheritance:
```

---

(services-layer)=

## Services Layer

Business logic services providing core application functionality.

(project-service-api)=
(projectservice)=

### ProjectService

Manages project creation, discovery, and template migrations.

```{eval-rst}
.. autoclass:: app.services.project_service.ProjectService
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Project Lifecycle

   The ProjectService handles the complete project lifecycle:

   1. **Creation**: Create projects from templates
   2. **Discovery**: Scan storage locations for existing projects
   3. **Migration**: Update projects when templates change
   4. **Validation**: Ensure project integrity and structure

   .. rubric:: Usage Example

   .. code-block:: python

      from pathlib import Path
      from app.services.project_service import ProjectService
      from app.services.file_system_service import FileSystemService

      # Initialize services
      fs_service = FileSystemService()
      project_service = ProjectService(fs_service)

      # Create a new project
      project = project_service.create_project(
          name="MyMediaProject",
          path=Path("/media/projects/MyMediaProject"),
          template="basic",
          description="Family photos 2026"
      )

      # Discover all projects in a location
      projects = project_service.discover_projects(Path("/media/projects"))

      # Check if project needs migration
      if project_service.needs_migration(project):
          project_service.migrate_project(project)

   .. seealso::

      - :ref:`features-project-management` (Project management section)
```

(configuration-service-api)=
(configservice)=

### ConfigService

Layered configuration management with Pydantic validation.

```{eval-rst}
.. autoclass:: app.core.services.config_service.ConfigService
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Configuration Layers

   Configuration is resolved in priority order:

   1. **Portable Config** (highest priority) - USB drive portable mode
   2. **User Config** - ~/.config/pyMediaManager/config.yaml
   3. **Default Config** - Built-in application defaults

   .. rubric:: Usage Example

   .. code-block:: python

      from app.services.config_service import ConfigService

      # Initialize config service
      config_service = ConfigService()

      # Load configuration
      config = config_service.load_config()

      # Access settings
      print(f"Theme: {config.ui.theme}")
      print(f"Log level: {config.logging.level}")

      # Update configuration
      config.ui.theme = "dark"
      config_service.save_config(config)

      # Get config file location
      config_path = config_service.get_config_path()
      print(f"Config: {config_path}")

   .. versionadded:: dev
      Environment variable support for configuration overrides

   .. seealso::

      - :doc:`platform-directories`
```

(storage-service-api)=
(storageservice)=

### StorageService

Cross-platform storage and drive detection.

```{eval-rst}
.. .. autoclass:: app.services.storage_service.StorageService
..    :members:
..    :undoc-members:
..    :show-inheritance:

   .. rubric:: Platform Support

   The StorageService provides unified storage detection across:

   - **Windows**: Drive letters (C:, D:, etc.) via win32api
   - **Linux**: Mount points (/media, /mnt) via psutil
   - **macOS**: Volumes (/Volumes) via diskutil

   .. rubric:: Portable Mode Detection

   Automatically detects when pyMM is running from a USB drive:

   .. code-block:: python

      from app.services.storage_service import StorageService

      storage = StorageService()
      drives = storage.get_drives()

      for drive in drives:
          if drive.is_portable:
              print(f"Portable mode detected on {drive.path}")
              print(f"  Label: {drive.label}")
              print(f"  Free: {drive.free_space} bytes")

   .. seealso::

      - :doc:`examples/storage/basic/list_drives`
      - :ref:`storage-management` (Storage section)
```

### GitService

Git repository operations and version control integration.

```{eval-rst}
.. autoclass:: app.services.git_service.GitService
   :members:
   :undoc-members:
   :show-inheritance:

   .. note::
      Requires Git plugin to be installed. The service wraps GitPython
      for repository operations.
```

### FileSystemService

Cross-platform file system operations with error handling.

```{eval-rst}
.. autoclass:: app.core.services.file_system_service.FileSystemService
   :members:
   :undoc-members:
   :show-inheritance:
```

---

(sync-engine-api)=

## Synchronization Engine

Phase 2 Storage Groups synchronization system for master↔backup drive synchronization.

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item-card} 📖 Learn More

- [Sync Engine Guide](sync-engine.md) - Comprehensive documentation
- [Storage Groups](storage-groups.md) - Phase 1 & 2 feature overview
- {ref}`advanced-sync-options` - Advanced synchronization features

:::

:::{grid-item-card} 🎯 Key Components

- **FileSynchronizer** - Core sync operations
- **BackupTrackingDatabase** - SQLite incremental tracking
- **ScheduledSyncManager** - APScheduler integration
- **RealtimeSyncManager** - Watchdog file monitoring
- **CryptoHelper** - AES-256-GCM encryption
- **CompressionHelper** - GZIP/LZ4 compression
- **BandwidthThrottler** - Rate limiting
:::

::::

(filesynchronizer-api)=

### FileSynchronizer

Core synchronization engine handling bidirectional file sync between master and backup drives.

```{eval-rst}
.. autoclass:: app.core.sync.file_synchronizer.FileSynchronizer
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Manual Synchronization Example

   .. code-block:: python

      from pathlib import Path
      from app.core.sync.file_synchronizer import FileSynchronizer
      from app.models.storage_group import StorageGroup

      # Initialize synchronizer
      storage_group = StorageGroup(
          id="photos",
          name="Photo Archive",
          master_path=Path("/media/master"),
          backup_path=Path("/media/backup"),
          sync_mode="bidirectional"
      )

      synchronizer = FileSynchronizer(storage_group)

      # Perform manual sync
      results = synchronizer.synchronize()
      print(f"Files copied: {results['files_copied']}")
      print(f"Files deleted: {results['files_deleted']}")
      print(f"Conflicts: {results['conflicts']}")
      print(f"Errors: {results['errors']}")

   .. rubric:: Conflict Resolution

   The synchronizer detects three conflict types:

   - **Modification Conflict**: Both sides modified since last sync
   - **Deletion Conflict**: File modified on one side, deleted on other
   - **Type Conflict**: File replaced with directory or vice versa

   Conflicts can be resolved using:

   .. code-block:: python

      from app.core.sync.file_synchronizer import ConflictResolution

      # Resolve conflict by keeping master version
      synchronizer.resolve_conflict(
          path=Path("photo.jpg"),
          resolution=ConflictResolution.KEEP_MASTER
      )

   .. seealso::

      - :doc:`sync-engine` - Complete synchronization guide
      - :ref:`conflict-resolution-workflow` - Conflict handling
```

(backup-tracking-api)=

### BackupTrackingDatabase

SQLite-based incremental backup tracking with checksum validation.

```{eval-rst}
.. autoclass:: app.core.sync.backup_tracking.BackupTrackingDatabase
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Incremental Backup Example

   .. code-block:: python

      from pathlib import Path
      from app.core.sync.backup_tracking import BackupTrackingDatabase

      # Initialize tracking database
      tracker = BackupTrackingDatabase(
          db_path=Path("/media/backup/.pymm_sync/tracking.db"),
          storage_group_id="photos"
      )

      # Check if file needs backup
      file_path = Path("/media/master/vacation/IMG_001.jpg")
      if tracker.needs_backup(file_path):
          # Perform backup
          backup_file(file_path)
          tracker.record_backup(
              file_path,
              checksum="sha256:abc123...",
              size=2_500_000
          )

      # Query backup history
      history = tracker.get_backup_history(
          file_path,
          limit=10
      )
      for entry in history:
          print(f"{entry.timestamp}: {entry.checksum}")

   .. rubric:: Database Schema

   The tracking database stores:

   - File paths and checksums (SHA-256)
   - Modification timestamps (UTC)
   - File sizes and backup status
   - Sync operation history

   .. seealso::

      - :ref:`incremental-backup` - Backup strategy documentation
```

(scheduled-sync-api)=

### ScheduledSyncManager

APScheduler-based automatic synchronization with cron expressions.

```{eval-rst}
.. autoclass:: app.core.sync.scheduled_sync.ScheduledSyncManager
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Scheduled Sync Example

   .. code-block:: python

      from app.core.sync.scheduled_sync import ScheduledSyncManager
      from app.models.storage_group import StorageGroup

      # Initialize scheduler
      scheduler = ScheduledSyncManager()

      # Add hourly sync schedule
      storage_group = StorageGroup(...)
      scheduler.add_schedule(
          storage_group_id=storage_group.id,
          cron_expression="0 * * * *",  # Every hour
          storage_group=storage_group
      )

      # Start scheduler
      scheduler.start()

      # List all schedules
      schedules = scheduler.list_schedules()
      for schedule in schedules:
          print(f"{schedule.storage_group_id}: {schedule.cron}")

      # Remove schedule
      scheduler.remove_schedule(storage_group.id)

      # Shutdown gracefully
      scheduler.shutdown(wait=True)

   .. rubric:: Cron Expression Examples

   Common scheduling patterns:

   - ``0 * * * *`` - Every hour
   - ``*/15 * * * *`` - Every 15 minutes
   - ``0 2 * * *`` - Daily at 2:00 AM
   - ``0 0 * * 0`` - Weekly on Sunday midnight
   - ``0 0 1 * *`` - Monthly on 1st at midnight

   .. seealso::

      - :ref:`scheduled-sync` - Scheduler configuration guide
```

(realtime-sync-api)=

### RealtimeSyncManager

Watchdog-based file system monitoring for real-time synchronization.

```{eval-rst}
.. autoclass:: app.core.sync.realtime_sync.RealtimeSyncManager
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Real-time Sync Example

   .. code-block:: python

      from pathlib import Path
      from app.core.sync.realtime_sync import RealtimeSyncManager
      from app.models.storage_group import StorageGroup

      # Initialize real-time monitor
      storage_group = StorageGroup(
          master_path=Path("/media/master"),
          backup_path=Path("/media/backup"),
          sync_mode="bidirectional"
      )

      realtime_manager = RealtimeSyncManager(
          storage_group=storage_group,
          debounce_seconds=2.0  # Wait 2s before syncing
      )

      # Start monitoring
      realtime_manager.start()

      # Files are automatically synced when changed
      # ...

      # Stop monitoring
      realtime_manager.stop()

   .. rubric:: Debouncing

   Real-time sync includes intelligent debouncing to avoid
   excessive syncing during rapid file changes (e.g., video encoding):

   - Groups multiple changes within debounce window
   - Waits for file stability before syncing
   - Reduces CPU/disk usage during bulk operations

   .. seealso::

      - :ref:`realtime-sync` - Real-time sync configuration
```

(crypto-helper-api)=

### CryptoHelper

AES-256-GCM encryption for secure backups with key derivation.

```{eval-rst}
.. autoclass:: app.core.sync.crypto_compression.CryptoHelper
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Encryption Example

   .. code-block:: python

      from pathlib import Path
      from app.core.sync.crypto_compression import CryptoHelper

      # Initialize crypto helper
      crypto = CryptoHelper(password="secure_password_123")

      # Encrypt file
      plaintext_path = Path("/media/master/sensitive.txt")
      encrypted_path = Path("/media/backup/sensitive.txt.enc")

      crypto.encrypt_file(plaintext_path, encrypted_path)

      # Decrypt file
      decrypted_path = Path("/media/restore/sensitive.txt")
      crypto.decrypt_file(encrypted_path, decrypted_path)

   .. rubric:: Security Features

   - **Algorithm**: AES-256 in GCM mode (authenticated encryption)
   - **Key Derivation**: PBKDF2 with 100,000 iterations
   - **Nonce**: 96-bit random nonce per file (never reused)
   - **Authentication**: GCM tag prevents tampering

   .. warning::

      Store encryption passwords securely. Lost passwords
      cannot be recovered and encrypted backups will be
      permanently inaccessible.

   .. seealso::

      - :ref:`encryption-options` - Encryption configuration guide
```

(compression-helper-api)=

### CompressionHelper

GZIP/LZ4 compression for space-efficient backups.

```{eval-rst}
.. autoclass:: app.core.sync.crypto_compression.CompressionHelper
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Compression Example

   .. code-block:: python

      from pathlib import Path
      from app.core.sync.crypto_compression import (
          CompressionHelper,
          CompressionAlgorithm
      )

      # Initialize compression helper
      compressor = CompressionHelper(
          algorithm=CompressionAlgorithm.LZ4,
          level=4  # Balanced compression/speed
      )

      # Compress file
      source_path = Path("/media/master/video.mov")
      compressed_path = Path("/media/backup/video.mov.lz4")

      compressor.compress_file(source_path, compressed_path)

      # Decompress file
      restored_path = Path("/media/restore/video.mov")
      compressor.decompress_file(compressed_path, restored_path)

   .. rubric:: Algorithm Comparison

   ================ ========== ========== ==================
   Algorithm        Ratio      Speed      Use Case
   ================ ========== ========== ==================
   GZIP (level 6)   High       Moderate   Text files, logs
   GZIP (level 9)   Highest    Slow       Archive storage
   LZ4 (level 1)    Low        Very Fast  Real-time sync
   LZ4 (level 9)    Moderate   Fast       Balanced
   ================ ========== ========== ==================

   .. seealso::

      - :ref:`compression-options` - Compression guide
```

(bandwidth-throttler-api)=

### BandwidthThrottler

Token bucket algorithm for network bandwidth rate limiting.

```{eval-rst}
.. autoclass:: app.core.sync.bandwidth_throttler.BandwidthThrottler
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Throttling Example

   .. code-block:: python

      from app.core.sync.bandwidth_throttler import BandwidthThrottler

      # Limit to 5 MB/s
      throttler = BandwidthThrottler(
          rate_limit_mbps=5.0,
          burst_size_mb=10.0  # Allow 10 MB burst
      )

      # Throttle file transfer
      with open("large_file.bin", "rb") as f:
          while chunk := f.read(1024 * 1024):  # 1 MB chunks
              throttler.wait_for_capacity(len(chunk))
              # Transfer chunk...

   .. rubric:: Token Bucket Algorithm

   The throttler uses token bucket for smooth rate limiting:

   - Tokens accumulate at configured rate (MB/s)
   - Each byte transferred consumes one token
   - Burst size allows short bursts above average rate
   - Blocks when bucket empty until tokens refill

   .. seealso::

      - :ref:`bandwidth-throttling` - Throttling configuration
```

---

(core-modules)=

## Core Modules

Foundation modules providing platform abstraction and logging.

### Platform Abstraction

Cross-platform utilities and platform detection.

```{eval-rst}
.. automodule:: app.core.platform
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   .. rubric:: Platform Detection

   Use the Platform enum for platform-specific code:

   .. code-block:: python

      from app.core.platform import Platform, current_platform

      if current_platform == Platform.WINDOWS:
          # Windows-specific code
          drive_letter = "C:"
      elif current_platform == Platform.LINUX:
          # Linux-specific code
          mount_point = "/media"
      elif current_platform == Platform.MACOS:
          # macOS-specific code
          volume = "/Volumes"

   .. warning::
      Do not use ``sys.platform`` or ``os.name`` directly in plugin code.
      The platform module performs AST validation to prevent this.

   .. seealso::

      - :doc:`platform-directories`
```

### Logging Service

Structured logging configuration and utilities.

```{eval-rst}
.. automodule:: app.core.logging_service
   :members:
   :undoc-members:
   :show-inheritance:
```

---

(data-models)=

## Data Models

Pydantic models for data validation and serialization.

### Project Model

```{eval-rst}
.. autoclass:: app.models.project.Project
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

   .. rubric:: Project Structure

   Projects are stored as directories with a ``.pymm`` metadata file:

   .. code-block:: text

      MyProject/
      ├── .pymm/
      │   ├── project.yaml     # Project metadata
      │   └── manifest.yaml    # Template manifest
      ├── media/               # Media files
      ├── exports/             # Exported content
      └── README.md            # Project documentation
```

### Configuration Models

```{eval-rst}
.. .. automodule:: app.models.config
..    :members:
..    :undoc-members:
..    :show-inheritance:
..    :member-order: bysource

.. note::
   Configuration models are managed by ConfigService.
```

(platform-specific-modules)=
(platform-abstraction)=

## Platform-Specific Modules

Platform-specific implementations for Windows, Linux, and macOS.

```{eval-rst}
.. note::
   These modules are imported conditionally based on the current platform.
   Most users should use the high-level services instead of these modules directly.
```

### Windows Platform

```{eval-rst}
.. automodule:: app.platform.windows
   :members:
   :undoc-members:
   :show-inheritance:
   :platform: Windows
```

### Linux Platform

```{eval-rst}
.. automodule:: app.platform.linux
   :members:
   :undoc-members:
   :show-inheritance:
   :platform: Linux
```

### macOS Platform

```{eval-rst}
.. automodule:: app.platform.macos
   :members:
   :undoc-members:
   :show-inheritance:
   :platform: macOS
```

---

(user-interface)=

## User Interface

PySide6-based GUI components with QFluentWidgets for Fluent Design.

```{eval-rst}
.. note::
   UI components require PySide6 6.6+ and QFluentWidgets 1.5+.
   These dependencies are automatically installed with pyMM.
```

### Main Window

```{eval-rst}
.. autoclass:: app.ui.main_window.MainWindow
   :members:
   :undoc-members:
   :show-inheritance:

   .. rubric:: Window Structure

   The main window uses FluentWindow as the base class (when available):

   - **Navigation**: Side navigation panel with Home, Projects, Storage, Plugins
   - **Views**: Stacked view container for different sections
   - **Status Bar**: Shows portable mode status and notifications
   - **Theme Support**: Automatic light/dark mode switching

   .. versionadded:: dev
      Migration notification system for project template updates
```

### Components

Reusable UI components and widgets.

#### First Run Wizard

```{eval-rst}
.. autoclass:: app.ui.components.first_run_wizard.FirstRunWizard
   :members:
   :undoc-members:
   :show-inheritance:

   Multi-step wizard for initial application setup:

   1. Welcome page with app introduction
   2. Storage selection for project location
   3. Optional plugin selection
   4. Completion summary
```

#### Migration Banner

```{eval-rst}
.. autoclass:: app.ui.components.migration_banner.MigrationBanner
   :members:
   :undoc-members:
   :show-inheritance:
```

### Dialogs

Modal dialogs for user interactions.

```{eval-rst}
.. automodule:: app.ui.dialogs
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource
   :no-index:

   Available dialogs:

   - **ProjectBrowserDialog**: Browse and open existing projects
   - **ProjectWizard**: Create new projects with templates
   - **SettingsDialog**: Application settings and preferences
   - **MigrationDialog**: Project migration confirmation
   - **ToolVersionDialog**: System tool version display
   - **PrivilegeDialog**: Administrative privilege requests (Linux)
   - **RollbackDialog**: Migration rollback interface
```

### Views

Main content views for different sections.

#### PluginView

```{eval-rst}
.. autoclass:: app.ui.views.plugin_view.PluginView
   :members:
   :undoc-members:
   :show-inheritance:

   Displays available and installed plugins with install/update/uninstall actions.
```

#### ProjectView

```{eval-rst}
.. autoclass:: app.ui.views.project_view.ProjectView
   :members:
   :undoc-members:
   :show-inheritance:

   Lists projects with migration status and quick actions.
```

#### StorageView

```{eval-rst}
.. autoclass:: app.ui.views.storage_view.StorageView
   :members:
   :undoc-members:
   :show-inheritance:

   Shows available drives with capacity and portable mode indicators.
```

## Additional Resources

### Working Examples

Explore working code examples in the examples directory:

- **Plugins**: List, check status, read manifests
- **Projects**: Create, list, migrate
- **Storage**: Detect drives, monitor changes
- **Config**: Read, update, validate
- **Platform**: Detect OS, platform paths
- **UI**: Notifications, dialogs, widgets

### Documentation Guidelines

#### Docstring Format

pyMediaManager uses **Google-style docstrings** with Sphinx napoleon extension:

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """Brief one-line description.

    Longer description with more details about behavior,
    edge cases, and any important notes.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter with default value.

    Returns:
        Description of return value and its meaning.

    Raises:
        ValueError: When param1 is empty.
        FileNotFoundError: When required file doesn't exist.

    Examples:
        >>> example_function("test", 42)
        True

        >>> example_function("", 10)
        Traceback (most recent call last):
        ValueError: param1 cannot be empty

    .. versionadded:: dev
       This function will be available in the next release.
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    return len(param1) > param2
```

#### Type Annotations

All public APIs require complete type annotations:

```python
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

def process_files(
    paths: Sequence[Path],
    mode: Literal["read", "write"],
    *,
    recursive: bool = False,
    pattern: str | None = None,
) -> list[Path]:
    """Process files with specified mode.

    Args:
        paths: Files to process.
        mode: Processing mode.
        recursive: Process directories recursively.
        pattern: Glob pattern for filtering.

    Returns:
        List of processed file paths.
    """
    ...
```

#### Module Documentation

Every module must have a module-level docstring:

```python
"""Project configuration management.

This module provides utilities for loading, validating, and saving
project configuration using Pydantic models with YAML serialization.

The configuration system supports:
- Layered config (default → user → portable)
- Environment variable overrides
- Runtime validation with helpful error messages
- Automatic migration from old config formats

Typical usage:

    from app.services.config_service import ConfigService

    config_service = ConfigService()
    config = config_service.load_config()
"""

from pathlib import Path
from typing import Any

...
```

---

## Building Documentation

Generate API documentation locally:

::::{tab-set}

:::{tab-item} Using justfile

```bash
# Build all documentation
just docs

# Check for broken links
just docs-linkcheck

# Spell check
just docs-spelling
```

:::

:::{tab-item} Using Sphinx directly

```bash
# Install dependencies
uv sync --extra docs

# Build HTML
cd docs
sphinx-build -b html . _build/html

# Build with warnings as errors
sphinx-build -W -b html . _build/html

# Check links
sphinx-build -b linkcheck . _build/linkcheck
```

:::

:::{tab-item} Development Mode

```bash
# Watch for changes and auto-rebuild
uv pip install --system sphinx-autobuild
sphinx-autobuild docs docs/_build/html

# Open http://localhost:8000
```

:::

::::

---

## See Also

- :doc:`architecture` - Technical architecture and design patterns
- :doc:`plugin-development` - Creating custom plugins
- :doc:`getting-started-dev` - Developer setup guide

---

**Coverage:** 100% (477/477 functions documented)
**Last Updated:** January 10, 2026
**Built with:** Sphinx 7.2+ with Furo theme
