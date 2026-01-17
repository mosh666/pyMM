<!-- markdownlint-disable MD013 MD022 MD031 MD032 MD033 MD036 MD040 MD051 MD060 -->

# 🏗️ Architecture Documentation

> **Project:** pyMediaManager (pyMM) v0.y.z (Beta)
> **Python Support:** 3.12, 3.13, 3.14 (3.13 recommended, 3.14 fully supported)
> **Last Updated:** January 14, 2026
> **Status:** ✅ Production Ready (193 tests, 73% coverage, 100% docstring coverage, 0 mypy errors)
> **Versioning:** v0.y.z enforced with multi-layer protection until v1.0.0 release
> **Storage Groups:** Phase 1 & Phase 2 complete (sync engine fully implemented)
> **Build System:** uv (10-100x faster) + Hatchling (PEP 517) + hatch-vcs (git tag versioning)
> **Critical Gap:** ⚠️ Sync engine (9 modules) has 0% test coverage - see [examples](examples/sync/README.md)

## 📚 Table of Contents

- [Overview](architecture-overview)
- [High-Level Architecture](#high-level-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Design Patterns](#design-patterns)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Module Dependencies](#module-dependencies)
- [Security Architecture](#security-architecture)
- [Testing Strategy](#testing-strategy)
- [Performance Considerations](#performance-considerations)
- [Extension Points](#extension-points)

---

(architecture-overview)=

## 🎯 Overview

pyMediaManager (pyMM) is a **portable, Python-based media management application** designed to run entirely from external drives (USB, portable HDDs) without requiring system installation. The architecture emphasizes:

- **🚀 Portability**: Zero system footprint, runs from any drive
- **🔒 Type Safety**: Modern Python with full type hints using native generics
- **🧩 Modularity**: Clean separation of concerns with dependency injection
- **🔌 Extensibility**: Plugin-based architecture for external tools
- **🗄️ Storage Groups**: Master/backup drive pairing with Phase 2 sync (fully implemented)
- **🔄 Advanced Sync**: Real-time and scheduled synchronization engine (9 modules)
- **🧹 Resource Management**: Proper cleanup of database connections and file handles
- **⚡ Performance**: Async operations, lazy loading, resource pooling
- **🧪 Testability**: 193 tests with 73% coverage using pytest (⚠️ sync modules have zero test coverage)
- **📦 CI/CD**: Automated releases, MSI installer, supply chain security with attestation

### Key Architectural Principles

1. **Separation of Concerns**: Clear boundaries between UI, business logic, and data layers
2. **Dependency Injection**: Services injected via constructor, no global state
3. **Single Responsibility**: Each module has one well-defined purpose
4. **Open/Closed Principle**: Extensible through plugins without modifying core
5. **Type Safety**: Strict MyPy checks with `list[T]`, `dict[K, V]` syntax
6. **Fail-Fast**: Early validation with Pydantic models

---

(high-level-architecture)=

## 🏛️ High-Level Architecture

```{mermaid}
graph TB
    subgraph "Presentation Layer"
        UI[PySide6 UI Components]
        MW[Main Window]
        Dialogs[Dialogs & Wizards]
        Views[Plugin/Project/Storage Views]
    end

    subgraph "Application Layer"
        PS[Project Service]
        PM[Plugin Manager]
        GS[Git Service]
    end

    subgraph "Core Services Layer"
        CS[Config Service]
        LS[Logging Service]
        FSS[File System Service]
        SS[Storage Service]
        SGS[Storage Group Service]
        SyncEngine[Sync Engine]
    end

    subgraph "Domain Layer"
        Models[Domain Models]
        Schema[Pydantic Schemas]
    end

    subgraph "Infrastructure Layer"
        FileIO[File System]
        Network[HTTP/HTTPS]
        Git[Git Repository]
        WMI[Windows WMI]
    end

    UI --> MW
    MW --> Dialogs
    MW --> Views
    Dialogs --> PS
    Dialogs --> PM
    Views --> PS
    Views --> PM
    Views --> SS
    PS --> GS
    PS --> FSS
    PS --> Models
    PM --> FSS
    PM --> CS
    GS --> Git
    CS --> FileIO
    LS --> FileIO
    FSS --> FileIO
    SS --> WMI
    SS --> FileIO
    Models --> Schema
    PM --> Network
```

### Layer Responsibilities

| Layer | Responsibility | Technologies |
|-------|---------------|--------------|
| **Presentation** | User interface, event handling, view rendering | PySide6, QFluentWidgets |
| **Application** | Business logic, orchestration, workflows | Python 3.13, asyncio |
| **Core Services** | Cross-cutting concerns, infrastructure | YAML, Rich, Pydantic |
| **Domain** | Business entities, validation rules | Dataclasses, Pydantic |
| **Infrastructure** | External integrations, I/O operations | aiohttp, GitPython, WMI |

### Detailed Component Dependencies

```{mermaid}
graph TB
    subgraph "UI Layer - PySide6 + QFluentWidgets"
        MW[MainWindow]
        PV[ProjectView]
        PluginV[PluginView]
        StorageV[StorageView]
        SettingsD[SettingsDialog]
        ProjectW[ProjectWizard]
    end

    subgraph "Application Services"
        PS[ProjectService]
        CS[ConfigService]
        LS[LoggingService]
    end

    subgraph "Plugin System"
        PM[PluginManager]
        PB[PluginBase]
        STD[SystemToolDetector]
    end

    subgraph "Storage & Git"
        SS[StorageService]
        GS[GitService]
        FSS[FileSystemService]
    end

    subgraph "Domain Models"
        Project[Project Model]
        PluginManifest[PluginManifest Model]
        AppConfig[AppConfig Model]
        DriveInfo[DriveInfo Model]
    end

    subgraph "External Systems"
        WMI[WMI - Windows]
        UDisks[UDisks2 - Linux]
        DiskUtil[diskutil - macOS]
        GitHub[GitHub API]
        FileIO[File System I/O]
        Network[HTTP Client - aiohttp]
    end

    subgraph "Configuration Files"
        AppYAML[config/app.yaml]
        UserYAML[storage/config/user.yaml]
        PluginYAML[plugins/*/plugin.yaml]
    end

    MW --> PS
    MW --> CS
    MW --> PM
    MW --> SS
    MW --> LS

    PV --> PS
    PluginV --> PM
    StorageV --> SS
    SettingsD --> CS
    ProjectW --> PS

    PS --> GS
    PS --> FSS
    PS --> Project

    PM --> PB
    PM --> STD
    PM --> PluginManifest
    PM --> Network

    CS --> AppConfig
    CS --> AppYAML
    CS --> UserYAML

    SS --> DriveInfo
    SS --> WMI
    SS --> UDisks
    SS --> DiskUtil

    PB --> PluginYAML
    PB --> Network
    PB --> FileIO
    PB --> GitHub

    GS --> FileIO
    FSS --> FileIO
    LS --> FileIO

    style MW fill:#4CAF50,color:#fff
    style PS fill:#2196F3,color:#fff
    style PM fill:#FF9800,color:#fff
    style SS fill:#9C27B0,color:#fff
    style CS fill:#F44336,color:#fff
```

---

(core-components)=

## 🧩 Core Components

### 1. Configuration Service (`app/core/services/config_service.py`)

**Purpose**: Layered configuration management with environment and user overrides.

```python
class ConfigService:
    """
    Manages application configuration with three layers:
    1. Default config (built-in)
    2. Environment config (config/app.yaml)
    3. User config (storage device config/user.yaml)
    """

    def __init__(self, app_dir: Path, storage_dir: Path | None = None):
        self.app_dir = app_dir
        self.storage_dir = storage_dir
        self.config: AppConfig = self._load_config()

    def _load_config(self) -> AppConfig:
        """Load and merge configuration layers."""
        # 1. Start with defaults from Pydantic models
        config = AppConfig()

        # 2. Override with environment config
        env_config = self.app_dir / "config" / "app.yaml"
        if env_config.exists():
            config = self._merge_config(config, env_config)

        # 3. Override with user config (highest priority)
        if self.storage_dir:
            user_config = self.storage_dir / "config" / "user.yaml"
            if user_config.exists():
                config = self._merge_config(config, user_config)

        return config
```

**Key Features**:
- ✅ Type-safe configuration with Pydantic models
- ✅ Hierarchical config merging
- ✅ Sensitive field redaction in logs
- ✅ Runtime config updates with validation

**Configuration Resolution Flowchart**:

```{mermaid}
flowchart TD
    Start([Load Configuration]) --> Init[Initialize with Pydantic Defaults]
    Init --> CheckEnv{config/app.yaml<br/>exists?}

    CheckEnv -->|Yes| LoadEnv[Load Environment Config]
    CheckEnv -->|No| CheckUser
    LoadEnv --> MergeEnv[Deep Merge with Defaults]
    MergeEnv --> CheckUser

    CheckUser{storage_dir/<br/>config/user.yaml<br/>exists?}
    CheckUser -->|Yes| LoadUser[Load User Config]
    CheckUser -->|No| Validate
    LoadUser --> MergeUser[Deep Merge with Current]
    MergeUser --> Validate

    Validate[Pydantic Validation] --> ValidCheck{Valid?}
    ValidCheck -->|Yes| ApplyEnv[Apply Environment Variables]
    ValidCheck -->|No| Error[Raise ValidationError]

    ApplyEnv --> Redact[Redact Sensitive Fields in Logs]
    Redact --> Done([Configuration Ready])

    style Start fill:#4CAF50,color:#fff
    style Done fill:#4CAF50,color:#fff
    style Error fill:#f44336,color:#fff
    style MergeEnv fill:#2196F3,color:#fff
    style MergeUser fill:#2196F3,color:#fff
```

**Configuration Precedence** (highest to lowest):
1. 🔴 **User config** (`storage_dir/config/user.yaml`) - Highest priority
2. 🟡 **Environment config** (`config/app.yaml`) - Application defaults
3. 🟢 **Pydantic defaults** - Hardcoded fallbacks
4. 🔵 **Environment variables** - Override any value (applied after merging)

---

### 2. Plugin Manager (`app/plugins/plugin_manager.py`)

**Purpose**: Discover, install, and manage external tool plugins.

```python
class PluginManager:
    """
    Plugin lifecycle management:
    - Discovery: Load YAML manifests from plugins/ directory
    - Validation: Pydantic schema validation (fail-fast)
    - Installation: Download, verify checksum, extract
    - Execution: PATH registration, version detection
    """

    def __init__(self, plugins_dir: Path, manifests_dir: Path):
        self.plugins_dir = plugins_dir  # e.g., D:\pyMM.Plugins
        self.manifests_dir = manifests_dir  # e.g., ./plugins
        self.plugins: dict[str, PluginBase] = {}
        self.manifests: dict[str, PluginManifest] = {}

    def discover_plugins(self) -> int:
        """
        Discover plugins from YAML manifests.

        Returns:
            Number of plugins discovered
        """
        manifest_files = self.manifests_dir.rglob("plugin.yaml")
        for manifest_file in manifest_files:
            manifest = self._load_manifest(manifest_file)
            plugin = SimplePluginImplementation(manifest, self.plugins_dir)
            self.plugins[manifest.name] = plugin
        return len(self.plugins)

    async def install_plugin(
        self,
        plugin_name: str,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """
        Install plugin with progress tracking.

        Args:
            plugin_name: Name of plugin to install
            progress_callback: Optional (current_bytes, total_bytes) -> None

        Returns:
            True if installation succeeded
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return False

        # Download with SHA-256 verification
        if not await plugin.download(progress_callback):
            return False

        # Extract to plugin directory
        if not await plugin.extract():
            return False

        # Validate installation
        return plugin.validate_installation()
```

**Key Features**:
- ✅ Manifest-driven (no code execution during load)
- ✅ SHA-256 checksum verification
- ✅ Async downloads with progress tracking
- ✅ Retry logic with exponential backoff
- ✅ GitHub release asset support

**Plugin System Class Diagram**:

```{mermaid}
classDiagram
    class PluginManager {
        -dict~str,PluginBase~ plugins
        -dict~str,PluginManifest~ manifests
        -Path plugins_dir
        -Path manifests_dir
        +discover_plugins() int
        +install_plugin(name, callback) bool
        +uninstall_plugin(name) bool
        +get_plugin(name) PluginBase
        +list_plugins() list~PluginBase~
        -_load_manifest(path) PluginManifest
        -_validate_manifest(manifest) bool
    }

    class PluginBase {
        <<abstract>>
        +PluginManifest manifest
        +Path install_dir
        +download(callback) bool*
        +extract() bool*
        +validate_installation() bool*
        +get_version() str*
        +is_installed() bool
        +get_executable_path() Path
    }

    class SimplePluginImplementation {
        -aiohttp.ClientSession _session
        -Path _temp_file
        +download(callback) bool
        +extract() bool
        +validate_installation() bool
        +get_version() str
        -_verify_checksum(file) bool
        -_retry_download(url, retries) bool
    }

    class GitHubReleasePlugin {
        -str _repo_uri
        -str _asset_pattern
        +download(callback) bool
        +_fetch_latest_release() dict
        +_match_asset(assets) dict
    }

    class PluginManifest {
        +str name
        +str version
        +str description
        +str homepage
        +bool mandatory
        +bool enabled
        +SourceConfig source
        +CommandConfig command
        +list~str~ dependencies
        +validate() bool
    }

    class SourceConfig {
        +str type
        +str uri
        +str asset_pattern
        +str checksum_sha256
        +int file_size
    }

    class CommandConfig {
        +str path
        +str executable
        +bool register_to_path
        +list~str~ args
    }

    class SystemToolDetector {
        +detect_installed_tools() dict~str,str~
        +is_tool_available(name) bool
        +get_tool_version(name) str
        -_check_path(executable) bool
        -_parse_version(output) str
    }

    PluginManager "1" --> "*" PluginBase : manages
    PluginManager "1" --> "*" PluginManifest : loads
    PluginBase <|-- SimplePluginImplementation : implements
    PluginBase <|-- GitHubReleasePlugin : implements
    PluginBase "1" --> "1" PluginManifest : has
    PluginManifest "1" --> "1" SourceConfig : contains
    PluginManifest "1" --> "1" CommandConfig : contains
    PluginManager ..> SystemToolDetector : uses

    style PluginManager fill:#4CAF50,color:#fff
    style PluginBase fill:#2196F3,color:#fff
    style PluginManifest fill:#FF9800,color:#fff
```

**Plugin Lifecycle State Machine**:

```{mermaid}
stateDiagram-v2
    [*] --> Discovered : discover_plugins()

    Discovered --> Downloading : install_plugin()
    Downloading --> VerifyingChecksum : download complete
    Downloading --> Failed : network error

    VerifyingChecksum --> Extracting : SHA-256 match
    VerifyingChecksum --> Failed : checksum mismatch

    Extracting --> Validating : extract complete
    Extracting --> Failed : extraction error

    Validating --> Installed : executable found + version ok
    Validating --> Failed : validation failed

    Installed --> Updating : new version available
    Installed --> Uninstalling : uninstall_plugin()

    Updating --> Downloading : fetch update

    Uninstalling --> Removed : directory deleted
    Removed --> [*]

    Failed --> Discovered : retry / clear error
    Failed --> [*] : manual intervention

    note right of Installed
        Plugin registered in PATH
        Ready for use
    end note

    note right of Failed
        Error logged with details
        Cleanup performed
    end note
```

**Plugin Manifest Schema** (`plugin.yaml`):

```yaml
name: Git
version: 2.47.1
description: Distributed version control system
homepage: https://git-scm.com
mandatory: false
enabled: true

source:
  type: github  # or 'url' for direct downloads
  uri: git-for-windows/git
  asset_pattern: "PortableGit-*-64-bit.7z.exe"
  checksum_sha256: "abc123..."
  file_size: 52428800

command:
  path: cmd
  executable: git.exe
  register_to_path: true

dependencies: []
```

---

### 3. Storage Service (`app/core/services/storage_service.py`)

**Purpose**: External drive detection and validation for portable operation.

```python
class StorageService:
    """
    Detects and validates external storage devices using:
    - WMI queries (Win32_LogicalDisk, Win32_DiskDrive)
    - Drive type enumeration (USB, removable)
    - Performance heuristics (read/write speed)
    """

    def get_external_drives(self) -> list[DriveInfo]:
        """
        Get all external drives using WMI.

        Returns:
            List of DriveInfo objects with metadata
        """
        import wmi
        c = wmi.WMI()

        drives = []
        for disk in c.Win32_LogicalDisk(DriveType=2):  # Removable
            drives.append(DriveInfo(
                letter=disk.DeviceID,
                label=disk.VolumeName or "Unknown",
                filesystem=disk.FileSystem,
                total_size=int(disk.Size or 0),
                free_space=int(disk.FreeSpace or 0),
                drive_type="Removable"
            ))

        for disk in c.Win32_LogicalDisk(DriveType=3):  # Fixed
            # Check if actually external via bus type
            if self._is_external_fixed_drive(disk):
                drives.append(...)

        return drives

    def _is_external_fixed_drive(self, disk) -> bool:
        """Detect external fixed drives (USB HDDs) vs internal."""
        # Query Win32_DiskDriveToDiskPartition association
        # Check InterfaceType for USB/1394
        ...
```

**Key Features**:
- ✅ WMI-based drive detection (Windows)
- ✅ USB vs internal drive discrimination
- ✅ Drive health monitoring
- ✅ Real-time removal detection

**Storage Service Component Architecture**:

```{mermaid}
graph TB
    subgraph "Client Layer"
        UI[UI Components]
        ProjectService[Project Service]
    end

    subgraph "Storage Service"
        API[StorageService API]
        Cache[Drive Cache]
        Monitor[Change Monitor]
    end

    subgraph "Platform Abstraction"
        Detector{Platform Detector}
        WinImpl[Windows Implementation]
        LinuxImpl[Linux Implementation]
        MacImpl[macOS Implementation]
    end

    subgraph "Windows Platform - WMI Based"
        WMI[WMI Queries]
        LogicalDisk[Win32_LogicalDisk]
        DiskDrive[Win32_DiskDrive]
        DiskPartition[Win32_DiskDriveToDiskPartition]
        USBController[Win32_USBController]
    end

    subgraph "Linux Platform - sysfs/udisks2"
        UDisks[UDisks2 DBus]
        Sysfs[/sys/block/]
        Lsblk[lsblk command]
    end

    subgraph "macOS Platform - diskutil"
        DiskUtil[diskutil command]
        IOKit[IOKit framework]
    end

    subgraph "Data Models"
        DriveInfo[DriveInfo]
        DriveType[DriveType enum]
    end

    UI --> API
    ProjectService --> API
    API --> Cache
    API --> Monitor
    API --> Detector

    Detector -->|Windows| WinImpl
    Detector -->|Linux| LinuxImpl
    Detector -->|macOS| MacImpl

    WinImpl --> WMI
    WMI --> LogicalDisk
    WMI --> DiskDrive
    WMI --> DiskPartition
    WMI --> USBController

    LinuxImpl --> UDisks
    LinuxImpl --> Sysfs
    LinuxImpl --> Lsblk

    MacImpl --> DiskUtil
    MacImpl --> IOKit

    WinImpl --> DriveInfo
    LinuxImpl --> DriveInfo
    MacImpl --> DriveInfo
    DriveInfo --> DriveType

    style API fill:#4CAF50,color:#fff
    style Detector fill:#2196F3,color:#fff
    style WinImpl fill:#FF9800,color:#fff
    style LinuxImpl fill:#FF9800,color:#fff
    style MacImpl fill:#FF9800,color:#fff
    style DriveInfo fill:#9C27B0,color:#fff
```

**Drive Detection Sequence (Windows)**:

```{mermaid}
sequenceDiagram
    participant Client
    participant SS as StorageService
    participant WMI as WMI Interface
    participant OS as Windows OS

    Client->>SS: get_external_drives()
    SS->>SS: Check cache (5s TTL)

    alt Cache Valid
        SS-->>Client: Return cached drives
    else Cache Expired
        SS->>WMI: Query Win32_LogicalDisk
        WMI->>OS: WQL: SELECT * WHERE DriveType=2 OR DriveType=3
        OS-->>WMI: Disk metadata
        WMI-->>SS: Logical disk objects

        loop For each disk
            SS->>WMI: Query Win32_DiskDriveToDiskPartition
            WMI->>OS: Get physical disk association
            OS-->>WMI: Physical disk info
            WMI-->>SS: Bus type (USB/SATA/NVMe)

            alt USB Bus Type
                SS->>SS: Mark as External
            else SATA/NVMe
                SS->>WMI: Query Win32_USBController
                WMI->>OS: Check USB connection
                OS-->>WMI: USB status
                WMI-->>SS: External status
            end

            SS->>SS: Create DriveInfo object
        end

        SS->>SS: Update cache
        SS-->>Client: Return drive list
    end
```

---

### 4. Synchronization Engine (`app/core/sync/`)

**Purpose**: Phase 2 Storage Groups synchronization with master↔backup drive sync.

**Status**: ✅ Fully implemented (9 modules, zero test coverage - contributions welcome!)

```python
# Core synchronization modules
from app.core.sync.file_synchronizer import FileSynchronizer
from app.core.sync.backup_tracking import BackupTrackingDatabase
from app.core.sync.scheduled_sync import ScheduledSyncManager
from app.core.sync.realtime_sync import RealtimeSyncManager
from app.core.sync.crypto_compression import CryptoHelper, CompressionHelper
from app.core.sync.bandwidth_throttler import BandwidthThrottler
from app.core.sync.advanced_sync_options import AdvancedSyncOptions
```

**Sync Engine Architecture**:

```{mermaid}
graph TB
    subgraph "User Interface"
        StorageView[Storage Groups View]
        SyncDialog[Advanced Sync Dialog]
        ConflictDialog[Conflict Resolution]
    end

    subgraph "Sync Orchestration"
        SyncManager[Sync Manager]
        ScheduledSync[ScheduledSyncManager<br/>APScheduler]
        RealtimeSync[RealtimeSyncManager<br/>watchdog]
    end

    subgraph "Sync Core"
        FileSynchronizer[FileSynchronizer]
        AdvancedOptions[AdvancedSyncOptions]
        ConflictResolver[Conflict Resolver]
    end

    subgraph "Sync Support Services"
        BackupDB[BackupTrackingDatabase<br/>SQLite]
        Crypto[CryptoHelper<br/>AES-256-GCM]
        Compression[CompressionHelper<br/>GZIP/LZ4]
        Throttler[BandwidthThrottler<br/>Token Bucket]
    end

    subgraph "File System"
        MasterDrive[Master Drive]
        BackupDrive[Backup Drive]
    end

    StorageView --> SyncManager
    SyncDialog --> AdvancedOptions
    ConflictDialog --> ConflictResolver

    SyncManager --> ScheduledSync
    SyncManager --> RealtimeSync
    SyncManager --> FileSynchronizer

    ScheduledSync --> FileSynchronizer
    RealtimeSync --> FileSynchronizer

    FileSynchronizer --> BackupDB
    FileSynchronizer --> Crypto
    FileSynchronizer --> Compression
    FileSynchronizer --> Throttler
    FileSynchronizer --> ConflictResolver

    FileSynchronizer --> MasterDrive
    FileSynchronizer --> BackupDrive

    BackupDB --> MasterDrive
    BackupDB --> BackupDrive

    style SyncManager fill:#4CAF50,color:#fff
    style FileSynchronizer fill:#2196F3,color:#fff
    style BackupDB fill:#FF9800,color:#fff
    style ScheduledSync fill:#9C27B0,color:#fff
    style RealtimeSync fill:#9C27B0,color:#fff
```

**Key Components**:

#### 4.1 FileSynchronizer
Core synchronization logic with bidirectional sync support.

```python
class FileSynchronizer:
    """
    Master↔Backup synchronization engine.

    Sync Modes:
    - bidirectional: Two-way sync with conflict detection
    - master_to_backup: One-way sync (master is source of truth)
    - backup_to_master: Restore from backup
    """

    def __init__(self, storage_group: StorageGroup):
        self.storage_group = storage_group
        self.tracking_db = BackupTrackingDatabase(
            db_path=storage_group.backup_path / ".pymm_sync" / "tracking.db",
            storage_group_id=storage_group.id
        )

    def synchronize(
        self,
        options: AdvancedSyncOptions | None = None
    ) -> SyncResult:
        """
        Execute synchronization with conflict detection.

        Returns:
            SyncResult with files_copied, files_deleted,
            conflicts, errors
        """
        if options is None:
            options = AdvancedSyncOptions()

        # 1. Scan both drives for changes
        master_files = self._scan_directory(
            self.storage_group.master_path,
            options.exclude_patterns
        )
        backup_files = self._scan_directory(
            self.storage_group.backup_path,
            options.exclude_patterns
        )

        # 2. Detect conflicts
        conflicts = self._detect_conflicts(master_files, backup_files)

        # 3. Execute sync operations
        results = self._execute_sync(
            master_files,
            backup_files,
            conflicts,
            options
        )

        # 4. Update tracking database
        self.tracking_db.record_sync(results)

        return results

    def resolve_conflict(
        self,
        path: Path,
        resolution: ConflictResolution
    ) -> bool:
        """
        Resolve file conflict.

        Resolution Types:
        - KEEP_MASTER: Use master version
        - KEEP_BACKUP: Use backup version
        - KEEP_BOTH: Rename one version
        - SKIP: Manual resolution required
        """
        ...
```

#### 4.2 BackupTrackingDatabase
SQLite-based incremental backup tracking with checksum validation.

```python
class BackupTrackingDatabase:
    """
    Track file backup history with SHA-256 checksums.

    Database Schema:
    - backup_history: file_path, checksum, timestamp, size
    - sync_operations: operation_id, start_time, end_time, status
    - conflict_log: file_path, conflict_type, resolution, timestamp
    """

    def record_backup(
        self,
        file_path: Path,
        checksum: str,
        size: int
    ) -> None:
        """Record successful backup with metadata."""
        ...

    def needs_backup(self, file_path: Path) -> bool:
        """
        Check if file needs backup.

        Returns True if:
        - File not in database
        - Checksum differs from last backup
        - File size changed
        """
        ...

    def get_backup_history(
        self,
        file_path: Path,
        limit: int = 10
    ) -> list[BackupRecord]:
        """Get file backup history."""
        ...
```

#### 4.3 ScheduledSyncManager
APScheduler-based automatic synchronization.

```python
class ScheduledSyncManager:
    """
    Scheduled sync using cron expressions.

    Example Schedules:
    - "0 * * * *": Every hour
    - "*/15 * * * *": Every 15 minutes
    - "0 2 * * *": Daily at 2:00 AM
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs: dict[str, Job] = {}

    def add_schedule(
        self,
        storage_group_id: str,
        cron_expression: str,
        storage_group: StorageGroup
    ) -> None:
        """Add sync schedule for storage group."""
        job = self.scheduler.add_job(
            func=self._execute_sync,
            trigger=CronTrigger.from_crontab(cron_expression),
            args=[storage_group],
            id=storage_group_id
        )
        self.jobs[storage_group_id] = job

    def _execute_sync(self, storage_group: StorageGroup) -> None:
        """Execute scheduled sync with error handling."""
        synchronizer = FileSynchronizer(storage_group)
        try:
            results = synchronizer.synchronize()
            self._log_sync_results(results)
        except Exception as e:
            self._handle_sync_error(storage_group, e)
```

#### 4.4 RealtimeSyncManager
Watchdog-based file system monitoring for real-time sync.

```python
class RealtimeSyncManager:
    """
    Real-time file sync with watchdog monitoring.

    Features:
    - Debouncing (avoid excessive syncing)
    - File stability detection
    - Event coalescing
    """

    def __init__(
        self,
        storage_group: StorageGroup,
        debounce_seconds: float = 2.0
    ):
        self.storage_group = storage_group
        self.debounce_seconds = debounce_seconds
        self.observer = Observer()
        self.event_handler = SyncEventHandler(
            storage_group,
            debounce_seconds
        )

    def start(self) -> None:
        """Start file system monitoring."""
        self.observer.schedule(
            self.event_handler,
            path=str(self.storage_group.master_path),
            recursive=True
        )
        self.observer.start()

    def stop(self) -> None:
        """Stop monitoring gracefully."""
        self.observer.stop()
        self.observer.join()
```

#### 4.5 CryptoHelper & CompressionHelper
Optional encryption and compression for secure backups.

```python
class CryptoHelper:
    """
    AES-256-GCM encryption for backups.

    Security:
    - PBKDF2 key derivation (100,000 iterations)
    - 96-bit random nonce per file
    - Authenticated encryption (GCM mode)
    """

    def encrypt_file(
        self,
        plaintext_path: Path,
        encrypted_path: Path
    ) -> None:
        """Encrypt file with AES-256-GCM."""
        ...

class CompressionHelper:
    """
    GZIP/LZ4 compression for space savings.

    Algorithms:
    - GZIP: High compression ratio (slower)
    - LZ4: Fast compression (lower ratio)
    """

    def compress_file(
        self,
        source_path: Path,
        compressed_path: Path
    ) -> None:
        """Compress file with selected algorithm."""
        ...
```

**Sync Execution Flow**:

```{mermaid}
sequenceDiagram
    participant User
    participant StorageView
    participant SyncManager
    participant FileSynchronizer
    participant BackupDB
    participant FileSystem

    User->>StorageView: Click "Sync Now"
    StorageView->>SyncManager: trigger_sync(storage_group)

    SyncManager->>FileSynchronizer: synchronize()

    FileSynchronizer->>FileSystem: Scan master drive
    FileSystem-->>FileSynchronizer: File list with metadata

    FileSynchronizer->>FileSystem: Scan backup drive
    FileSystem-->>FileSynchronizer: File list with metadata

    FileSynchronizer->>BackupDB: Query backup history
    BackupDB-->>FileSynchronizer: Previous checksums

    FileSynchronizer->>FileSynchronizer: Detect conflicts

    alt No Conflicts
        FileSynchronizer->>FileSystem: Copy changed files
        FileSystem-->>FileSynchronizer: Success
        FileSynchronizer->>BackupDB: Update tracking
    else Conflicts Detected
        FileSynchronizer->>StorageView: Show conflict dialog
        User->>StorageView: Select resolution
        StorageView->>FileSynchronizer: resolve_conflict()
        FileSynchronizer->>FileSystem: Apply resolution
    end

    FileSynchronizer-->>SyncManager: SyncResult
    SyncManager-->>StorageView: Display results
    StorageView-->>User: "Sync complete: X files copied"
```

**Sync Database Schema**:

```sql
-- Backup history tracking
CREATE TABLE backup_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    checksum_sha256 TEXT NOT NULL,
    timestamp INTEGER NOT NULL,  -- Unix timestamp (UTC)
    size_bytes INTEGER NOT NULL,
    backup_location TEXT NOT NULL,
    UNIQUE(file_path, timestamp)
);

-- Sync operation log
CREATE TABLE sync_operations (
    operation_id TEXT PRIMARY KEY,
    storage_group_id TEXT NOT NULL,
    start_time INTEGER NOT NULL,
    end_time INTEGER,
    status TEXT NOT NULL,  -- 'running', 'completed', 'failed'
    files_copied INTEGER DEFAULT 0,
    files_deleted INTEGER DEFAULT 0,
    conflicts INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0
);

-- Conflict resolution log
CREATE TABLE conflict_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    conflict_type TEXT NOT NULL,  -- 'modification', 'deletion', 'type'
    resolution TEXT NOT NULL,     -- 'keep_master', 'keep_backup', 'keep_both'
    resolved_at INTEGER NOT NULL,
    resolved_by TEXT
);

CREATE INDEX idx_backup_file_path ON backup_history(file_path);
CREATE INDEX idx_backup_timestamp ON backup_history(timestamp);
CREATE INDEX idx_sync_storage_group ON sync_operations(storage_group_id);
CREATE INDEX idx_conflict_file_path ON conflict_log(file_path);
```

**Performance Characteristics**:

| Operation | Time Complexity | Notes |
|-----------|----------------|-------|
| File scan | O(n) | n = number of files |
| Checksum calculation | O(m) | m = total file size |
| Conflict detection | O(n log n) | Sort + compare |
| Database query | O(log n) | B-tree index |
| Sync execution | O(k × m) | k = changed files |

**See Also**:
- [Sync Engine Documentation](sync-engine.md) - Comprehensive user guide
- [Storage Groups](storage-groups.md) - Phase 1 & 2 feature overview
- {ref}`sync-engine-api` - Complete API documentation

---

### 5. Project Service (`app/services/project_service.py`)

**Purpose**: Project lifecycle management with optional Git integration.

```python
class ProjectService:
    """
    Project management operations:
    - Create: Initialize directory structure + metadata
    - Load: Deserialize project.yaml
    - Update: Modify metadata with validation
    - Delete: Remove project directory
    - Git Integration: Optional repository initialization
    """

    def __init__(
        self,
        projects_dir: Path,
        git_service: GitService,
        file_system_service: FileSystemService
    ):
        self.projects_dir = projects_dir
        self.git_service = git_service
        self.fs_service = file_system_service

    def create_project(
        self,
        name: str,
        description: str = "",
        template: str | None = None,
        enable_git: bool = False
    ) -> Project:
        """
        Create new project with optional Git repository.

        Args:
            name: Project name (validated, no special chars)
            description: Project description
            template: Template name (e.g., 'video', 'photo')
            enable_git: Initialize Git repository

        Returns:
            Project object with metadata

        Raises:
            ValueError: If project name invalid or already exists
        """
        # Validate name
        if not self._validate_project_name(name):
            raise ValueError(f"Invalid project name: {name}")

        # Create directory structure
        project_path = self.projects_dir / name
        if project_path.exists():
            raise ValueError(f"Project already exists: {name}")

        project_path.mkdir(parents=True)

        # Apply template if specified
        if template:
            self._apply_template(project_path, template)

        # Initialize Git if requested
        if enable_git:
            self.git_service.init_repository(project_path)

        # Create metadata
        project = Project(
            name=name,
            path=str(project_path),
            description=description,
            created_at=datetime.now(UTC),
            git_enabled=enable_git
        )

        # Save project.yaml
        self._save_metadata(project)

        return project
```

**Project Templates**:

| Template | Structure | Features |
|----------|-----------|----------|
| `video` | `raw/`, `edited/`, `exports/`, `scripts/` | FFmpeg presets |
| `photo` | `raw/`, `processed/`, `exports/`, `archives/` | DigiKam integration |
| `audio` | `recordings/`, `mixed/`, `masters/` | Audio plugin configs |

**Project Lifecycle State Machine**:

```{mermaid}
stateDiagram-v2
    [*] --> Creating : create_project()

    Creating --> DirectorySetup : validate name
    DirectorySetup --> TemplateApplication : mkdir success
    TemplateApplication --> GitInit : template applied

    GitInit --> MetadataCreation : Git enabled
    DirectorySetup --> MetadataCreation : Git disabled

    MetadataCreation --> Created : project.yaml saved
    Created --> Active : first file added

    Active --> Migrating : migration requested
    Active --> GitEnabled : enable Git
    Active --> Archived : archive()

    Migrating --> Active : migration complete
    GitEnabled --> Active : repo initialized

    Archived --> Active : restore()
    Archived --> Deleted : delete_project()

    Active --> Deleted : delete_project()
    Deleted --> [*]

    note right of Created
        Empty project
        Metadata only
    end note

    note right of Active
        Files exist
        Ready for work
    end note

    note right of Archived
        Read-only
        Timestamp preserved
    end note
```

**Project Service Class Relationships**:

```{mermaid}
classDiagram
    class ProjectService {
        -Path projects_dir
        -GitService git_service
        -FileSystemService fs_service
        -dict~str,Project~ _cache
        +create_project(name, desc, template, git) Project
        +load_project(name) Project
        +list_projects() list~Project~
        +update_project(project) bool
        +delete_project(name) bool
        +archive_project(name) bool
        +restore_project(name) bool
        -_validate_project_name(name) bool
        -_apply_template(path, template) None
        -_save_metadata(project) None
    }

    class Project {
        +str name
        +str path
        +str description
        +datetime created_at
        +datetime modified_at
        +bool git_enabled
        +bool archived
        +dict~str,Any~ metadata
        +validate() bool
        +to_dict() dict
        +from_dict(data) Project
    }

    class GitService {
        +Logger logger
        +init_repository(path) bool
        +get_status(path) GitStatus
        +commit(path, message) bool
        +create_branch(path, name) bool
        +is_repository(path) bool
    }

    class FileSystemService {
        +create_directory(path) bool
        +copy_directory(src, dst) bool
        +delete_directory(path) bool
        +list_directory(path) list~Path~
        +get_directory_size(path) int
        +watch_directory(path, callback) None
    }

    class TemplateManager {
        -dict~str,Template~ templates
        +get_template(name) Template
        +apply_template(path, template) None
        +list_templates() list~str~
    }

    class Template {
        +str name
        +list~str~ directories
        +list~FileTemplate~ files
        +dict~str,Any~ settings
    }

    ProjectService "1" --> "*" Project : manages
    ProjectService --> GitService : uses
    ProjectService --> FileSystemService : uses
    ProjectService ..> TemplateManager : uses
    TemplateManager "1" --> "*" Template : contains

    style ProjectService fill:#4CAF50,color:#fff
    style Project fill:#2196F3,color:#fff
    style GitService fill:#FF9800,color:#fff
    style FileSystemService fill:#FF9800,color:#fff
```

---

### 5. Git Service (`app/services/git_service.py`)

**Purpose**: Git repository management for project version control.

```python
class GitService:
    """
    Git operations using GitPython:
    - Repository initialization with .gitignore
    - Branch management
    - Commit creation
    - Status queries
    """

    def init_repository(self, path: Path) -> bool:
        """
        Initialize Git repository with default configuration.

        Args:
            path: Project directory path

        Returns:
            True if successful
        """
        from git import Repo

        try:
            repo = Repo.init(path)

            # Create default .gitignore
            gitignore = path / ".gitignore"
            gitignore.write_text(
                "*.tmp\n"
                "*.log\n"
                ".DS_Store\n"
                "Thumbs.db\n"
            )

            # Initial commit
            repo.index.add([".gitignore"])
            repo.index.commit("Initial commit")

            return True
        except Exception as e:
            self.logger.error(f"Failed to init repository: {e}")
            return False
```

---

### 6. Logging Service (`app/core/logging_service.py`)

**Purpose**: Structured logging with console and file outputs.

```python
class LoggingService:
    """
    Multi-handler logging system:
    - Console: Rich formatting with colors/emojis
    - File: Rotating logs (10MB max, 5 backups)
    - Structured: JSON output option
    """

    def setup_logging(self, config: LoggingConfig, logs_dir: Path) -> None:
        """
        Configure root logger with handlers.

        Args:
            config: Logging configuration from ConfigService
            logs_dir: Directory for log files
        """
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, config.level.value))

        # Console handler with Rich
        if config.console_enabled:
            from rich.logging import RichHandler
            console_handler = RichHandler(
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_path=False
            )
            root_logger.addHandler(console_handler)

        # File handler with rotation
        if config.file_enabled:
            from logging.handlers import RotatingFileHandler
            log_file = logs_dir / "pymm.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=config.max_file_size,
                backupCount=config.backup_count,
                encoding="utf-8"
            )
            file_handler.setFormatter(
                logging.Formatter(config.format)
            )
            root_logger.addHandler(file_handler)
```

---

(data-flow)=

## 🌊 Data Flow

### Plugin Installation Flow

```{mermaid}
sequenceDiagram
    participant User
    participant UI as Plugin View
    participant PM as Plugin Manager
    participant Plugin as SimplePlugin
    participant FS as File System
    participant Net as Network

    User->>UI: Click "Install Git"
    UI->>PM: install_plugin("Git", progress_cb)
    PM->>Plugin: download(progress_cb)

    Plugin->>Net: GET source_uri
    Net-->>Plugin: Stream bytes
    Plugin->>Plugin: Verify SHA-256
    Plugin->>FS: Save to temp file
    Plugin-->>PM: True (download OK)

    PM->>Plugin: extract()
    Plugin->>FS: Extract to plugins_dir/git/
    Plugin-->>PM: True (extract OK)

    PM->>Plugin: validate_installation()
    Plugin->>FS: Check git.exe exists
    Plugin->>Plugin: Test --version
    Plugin-->>PM: True (valid)

    PM-->>UI: Installation complete
    UI-->>User: Show success message
```

### Project Creation Flow

```{mermaid}
sequenceDiagram
    participant User
    participant Wizard as Project Wizard
    participant PS as Project Service
    participant GS as Git Service
    participant FS as File System Service

    User->>Wizard: Fill form (name, template, Git)
    Wizard->>PS: create_project(...)

    PS->>PS: Validate name
    PS->>FS: Create project directory
    PS->>FS: Apply template structure

    alt Git Enabled
        PS->>GS: init_repository(path)
        GS->>FS: Create .git/
        GS->>FS: Create .gitignore
        GS->>GS: Initial commit
    end

    PS->>FS: Save project.yaml
    PS-->>Wizard: Project object
    Wizard-->>User: Show success + open project
```

### Application Startup Flow

```{mermaid}
sequenceDiagram
    participant User
    participant Launcher as launcher.py
    participant MW as MainWindow
    participant CS as ConfigService
    participant SS as StorageService
    participant PM as PluginManager
    participant LS as LoggingService
    participant PS as ProjectService

    User->>Launcher: Launch application
    Launcher->>Launcher: Detect platform (Windows/Linux/macOS)
    Launcher->>Launcher: Resolve app_dir (portable vs installed)

    Launcher->>LS: setup_logging(config, logs_dir)
    LS->>LS: Configure Rich console handler
    LS->>LS: Configure rotating file handler
    LS-->>Launcher: Logging ready

    Launcher->>SS: Detect external drives
    SS->>SS: Query WMI/UDisks2/diskutil
    SS-->>Launcher: List of external drives

    alt External drive detected
        Launcher->>CS: ConfigService(app_dir, storage_dir)
        CS->>CS: Load config layers (default → app.yaml → user.yaml)
        CS-->>Launcher: Merged configuration
    else No external drive
        Launcher->>CS: ConfigService(app_dir, None)
        CS->>CS: Load config layers (default → app.yaml)
        CS-->>Launcher: Configuration (non-portable mode)
    end

    Launcher->>PM: PluginManager(plugins_dir, manifests_dir)
    PM->>PM: discover_plugins()
    PM->>PM: Load YAML manifests
    PM-->>Launcher: Plugins discovered

    Launcher->>PS: ProjectService(projects_dir, git_service, fs_service)
    PS->>PS: Load project cache
    PS-->>Launcher: Projects loaded

    Launcher->>MW: MainWindow(config, services)
    MW->>MW: Initialize UI components
    MW->>CS: subscribe(on_config_changed)
    MW->>MW: Apply theme from config
    MW->>MW: Restore window geometry
    MW-->>User: Application ready

    Note over User,MW: User can now:<br/>- Create projects<br/>- Install plugins<br/>- Change settings<br/>- Browse storage
```

### Complete System Interaction Flow

```{mermaid}
graph LR
    subgraph "User Actions"
        A1[Create Project]
        A2[Install Plugin]
        A3[Change Settings]
        A4[Browse Storage]
    end

    subgraph "UI Layer"
        MW[MainWindow]
        ProjectW[Project Wizard]
        PluginV[Plugin View]
        SettingsD[Settings Dialog]
        StorageV[Storage View]
    end

    subgraph "Service Layer"
        PS[Project Service]
        PM[Plugin Manager]
        CS[Config Service]
        SS[Storage Service]
    end

    subgraph "Infrastructure"
        FS[File System]
        Net[Network]
        Git[Git]
        Platform[Platform APIs]
    end

    subgraph "Data"
        Config[Configuration Files]
        Projects[Project Directories]
        Plugins[Plugin Installations]
        Logs[Log Files]
    end

    A1 --> ProjectW
    A2 --> PluginV
    A3 --> SettingsD
    A4 --> StorageV

    ProjectW --> PS
    PluginV --> PM
    SettingsD --> CS
    StorageV --> SS

    PS --> FS
    PS --> Git
    PS --> Projects

    PM --> Net
    PM --> FS
    PM --> Plugins

    CS --> FS
    CS --> Config

    SS --> Platform
    SS --> FS

    MW -.-> PS
    MW -.-> PM
    MW -.-> CS
    MW -.-> SS

    FS --> Logs

    style MW fill:#4CAF50,color:#fff
    style PS fill:#2196F3,color:#fff
    style PM fill:#FF9800,color:#fff
    style CS fill:#F44336,color:#fff
    style SS fill:#9C27B0,color:#fff
```

---

(design-patterns)=

## 🎨 Design Patterns

### 1. Dependency Injection

All services receive dependencies via constructor, enabling:
- **Testability**: Mock dependencies in unit tests
- **Flexibility**: Swap implementations without changing consumers
- **Explicit Dependencies**: Clear API contracts

```python
class ProjectService:
    def __init__(
        self,
        projects_dir: Path,
        git_service: GitService,
        file_system_service: FileSystemService
    ):
        self.projects_dir = projects_dir
        self.git_service = git_service
        self.fs_service = file_system_service
```

### 2. Strategy Pattern

Plugin manifest supports multiple source types:

```python
class PluginBase(ABC):
    @abstractmethod
    async def download(self, progress_callback) -> bool:
        """Strategy varies by source_type (url, github)."""

class URLPluginStrategy(PluginBase):
    async def download(self, progress_callback) -> bool:
        # Direct URL download
        ...

class GitHubPluginStrategy(PluginBase):
    async def download(self, progress_callback) -> bool:
        # GitHub Releases API + asset matching
        ...
```

### 3. Observer Pattern

Configuration changes notify observers:

```python
class ConfigService:
    def __init__(self):
        self._observers: list[Callable[[AppConfig], None]] = []

    def subscribe(self, callback: Callable[[AppConfig], None]) -> None:
        self._observers.append(callback)

    def update_config(self, new_config: AppConfig) -> None:
        self.config = new_config
        for observer in self._observers:
            observer(new_config)
```

**Observer Pattern Sequence**:

```{mermaid}
sequenceDiagram
    participant UI as Settings Dialog
    participant CS as ConfigService
    participant O1 as Observer: MainWindow
    participant O2 as Observer: PluginManager
    participant O3 as Observer: LoggingService

    UI->>CS: subscribe(on_config_changed)
    Note over UI,CS: Register callback

    O1->>CS: subscribe(update_theme)
    O2->>CS: subscribe(reload_plugins)
    O3->>CS: subscribe(update_log_level)

    Note over CS: _observers = [<br/>  on_config_changed,<br/>  update_theme,<br/>  reload_plugins,<br/>  update_log_level<br/>]

    UI->>UI: User changes log level
    UI->>CS: update_config(new_config)

    CS->>CS: Validate new_config
    CS->>CS: self.config = new_config

    Note over CS: Notify all observers
    CS->>UI: on_config_changed(new_config)
    CS->>O1: update_theme(new_config)
    CS->>O2: reload_plugins(new_config)
    CS->>O3: update_log_level(new_config)

    O3->>O3: Set logger level to new value
    O3-->>CS: Acknowledged

    CS-->>UI: Update complete
```

### 4. Repository Pattern

Storage service abstracts drive access:

```python
class StorageService:
    """Repository for external drives."""

    def get_all(self) -> list[DriveInfo]:
        """Get all drives."""
        ...

    def get_by_letter(self, letter: str) -> DriveInfo | None:
        """Get specific drive."""
        ...

    def is_external(self, path: Path) -> bool:
        """Check if path is on external drive."""
        ...
```

### 5. Resource Management Pattern

Services that manage resources (databases, file handles, background processes) implement proper cleanup:

```python
class StorageGroupService:
    """
    Service with resource cleanup support.

    Manages SQLite connections, file watchers, and background processes.
    """

    def __init__(
        self,
        config_path: Path,
        storage_service: StorageService | None = None,
        tracking_db_path: Path | None = None,
    ) -> None:
        self._tracking_db = BackupTrackingDatabase(tracking_db_path)
        self._realtime_manager = RealtimeSyncManager(...)
        # ... other initialization

    def close(self) -> None:
        """
        Close all resources and database connections.

        This method should be called when the service is no longer needed
        to ensure proper cleanup of database connections and real-time watchers.
        """
        logger.debug("Closing StorageGroupService resources")

        # Stop real-time sync watchers
        try:
            if hasattr(self, "_realtime_manager"):
                self._realtime_manager.stop_all()
        except Exception:
            logger.exception("Error stopping real-time manager")

        # Close database connection
        try:
            if hasattr(self, "_tracking_db"):
                self._tracking_db.close()
        except Exception:
            logger.exception("Error closing tracking database")

        logger.debug("StorageGroupService resources closed")

    def __del__(self) -> None:
        """Destructor to ensure cleanup on garbage collection."""
        self.close()
```

**Resource Management Benefits:**
- ✅ Eliminates ResourceWarning messages about unclosed connections
- ✅ Prevents resource leaks in long-running applications
- ✅ Proper cleanup on application exit or service destruction
- ✅ Exception handling ensures partial cleanup on errors
- ✅ Compatible with Python's garbage collection via `__del__()`

**Usage Pattern:**
```python
# Explicit cleanup (recommended)
service = StorageGroupService(config_path, storage_service)
try:
    service.sync_to_backup(...)
finally:
    service.close()

# Context manager support (future enhancement)
with StorageGroupService(config_path) as service:
    service.sync_to_backup(...)
# Automatic cleanup on exit
```

---

(technology-stack)=

## 🛠️ Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.13 (recommended) | Type-safe, async-capable |
| **GUI Framework** | PySide6 | 6.6+ | Qt bindings for Python |
| **UI Library** | QFluentWidgets | 1.5+ | Fluent Design components |
| **Configuration** | Pydantic | 2.5+ | Type-safe config models |
| **YAML Parser** | PyYAML | 6.0+ | Manifest parsing |
| **Git Integration** | GitPython | 3.1+ | Repository management |
| **HTTP Client** | aiohttp | 3.9+ | Async downloads |
| **Console UI** | Rich | 13.7+ | Formatted terminal output |
| **WMI** | wmi | 1.5+ (Windows) | Drive detection |

### Development Tools

| Category | Tool | Purpose | Configuration |
|----------|------|---------|---------------|
| **Linting** | Ruff | 40+ rules + security | `pyproject.toml` |
| **Type Checking** | MyPy | Strict mode | `pyproject.toml` |
| **Security** | Ruff (S rules) | Security checks | `pyproject.toml` |
| **Testing** | pytest | 193 tests, 73% coverage | `pyproject.toml` |
| **Pre-commit** | pre-commit | Git hooks | `.pre-commit-config.yaml` |
| **CI/CD** | GitHub Actions | Automated releases, build, test | `.github/workflows/` |
| **Versioning** | python-semantic-release | Automated semantic versioning | `pyproject.toml` |
| **Changelog** | python-semantic-release | Auto-generated from commits | `CHANGELOG.md` |

---

## CI/CD Release Pipeline

### Overview

pyMediaManager uses a fully automated release system built on GitHub Actions and python-semantic-release following 2026 best practices. The pipeline handles versioning, changelog generation, artifact building, and deployment with zero manual intervention.

### 2026 CI/CD Best Practices

The project implements modern GitHub Actions patterns optimized for efficiency, security, and reproducibility:

**Resource Optimization:**
- **Concurrency Groups:** 6 workflows use concurrency control to cancel redundant runs on rapid pushes
- **Artifact Lifecycle:** Automated cleanup deletes artifacts older than 7 days (saves storage costs)
- **Smart Scheduling:** Daily beta releases (1 AM UTC) and cleanup (2 AM UTC) during low-traffic hours

**Build Reproducibility:**
- **Pinned Runners:** Release builds use specific runner versions (`windows-2022`, `ubuntu-22.04`)
- **CI Security:** Test workflows use `-latest` for automatic security updates
- **Version Locking:** All GitHub Actions pinned to specific major versions (v4-v7)

**Security & Supply Chain:**
- **Artifact Attestation:** Build provenance for all release artifacts
- **CodeQL Analysis:** Daily security scans with extended query packs
- **Dependency Review:** Automated review blocking GPL licenses
- **SARIF Uploads:** Security findings integrated into GitHub Security tab

**Workflow Coverage (11 Total):**
1. `ci.yml` - Tests, linting, type checking (concurrency: cancel-in-progress)
2. `build.yml` - Multi-platform builds (pinned runners for releases)
3. `docs.yml` - Sphinx documentation (concurrency: cancel-in-progress)
4. `semantic-release.yml` - Automated versioning (concurrency: queue)
5. `cleanup-beta-releases.yml` - Artifact & release cleanup (daily)
6. `security.yml` - CodeQL, dependency review (concurrency: cancel-in-progress)
7. `scorecard.yml` - OpenSSF security scorecard (weekly)
8. `codeql.yml` - Advanced CodeQL scanning
9. `labeler.yml` - PR auto-labeling (concurrency: cancel-in-progress)
10. `dependabot-automerge.yml` - Automated dependency updates
11. `update-docs.yml` - README statistics updates

### Release Workflow Architecture

```{mermaid}
graph TD
    A[Dev Branch Push/Schedule] --> B{Check Changes}
    B -->|No Changes| C[Skip - Summary Note]
    B -->|New Commits| D[Calculate Next Version]
    D --> E[Create Beta Tag v0.y.z-beta.N]
    E --> F[Update CHANGELOG.md]
    F --> G[Build Artifacts Matrix]
    G --> H[Windows ZIP]
    G --> I[Linux AppImage]
    G --> J[macOS DMG]
    H --> K[Upload to GitHub Release]
    I --> K
    J --> K
    K --> L[Mark as Latest Beta]
    K --> M[Rebuild Documentation]

    N[Main Branch Push] --> O[Calculate Stable Version]
    O --> P[Create Stable Tag v0.y.z]
    P --> Q[Update CHANGELOG.md]
    Q --> R[Build Artifacts Matrix]
    R --> S[Upload to GitHub Release]
    S --> T[Rebuild Documentation]

    U[Weekly Cleanup] --> V[Delete Betas >30 Days Old]
    V --> W[Preserve Latest Beta]
```

### Workflow Components

#### 1. Semantic Release (`.github/workflows/semantic-release.yml`)

**Triggers:**
- **Push** to `main` or `dev` branches
- **Schedule** (daily at 00:00 UTC)
- **Manual** via workflow_dispatch

**Jobs:**

1. **check-changes**
   - Compares current HEAD with latest tag
   - Counts commits since last release
   - Exits silently if no changes (with workflow summary)
   - Respects "force" flag for manual triggers

2. **semantic-release**
   - Runs python-semantic-release v9.8.0
   - Parses conventional commits for version calculation
   - Creates git tag and GitHub release
   - Updates CHANGELOG.md automatically
   - Concurrency: Queues releases on same branch (`cancel-in-progress: false`)

3. **build**
   - Calls build.yml workflow
   - Matrix: Python 3.12/3.13/3.14 × Windows/Linux/macOS (all platforms)
   - Passes calculated version to build

4. **upload-assets**
   - Downloads all build artifacts
   - Uploads to GitHub release
   - Adds "Latest Beta" badge for dev releases
   - Generates SHA256 checksums

**Outputs:**
- Workflow summary with version, changelog excerpt, download links
- GitHub release with artifacts and automated release notes

#### 2. Build Workflow (`.github/workflows/build.yml`)

**Runner Images (2026 Best Practices):**
- **Release Builds:** Pinned versions for reproducibility
  - Windows: `windows-2022`
  - Linux: `ubuntu-22.04`
  - macOS: `macos-13` (Intel x86_64), `macos-14` (ARM64)
- **CI Builds:** Use `-latest` for automatic security updates

**Platforms:**
- **Windows:** Embedded Python + PyInstaller → ZIP (all versions) + MSI (Python 3.13 only)
- **Linux:** PyInstaller + AppImage → AppImage
- **macOS:** PyInstaller + create-dmg → DMG (Intel x86_64 and ARM64)

**Matrix Testing:**
- Python versions: 3.12, 3.13, 3.14
- Platform-specific dependencies auto-installed
- Artifacts expire after 30 days (see cleanup workflow)

**Build Artifacts:**
- ZIP/DMG/AppImage with SHA256 checksums
- MSI installer for Windows (Python 3.13)
- Supply chain security: Artifact attestation enabled

#### 3. Documentation Workflow (`.github/workflows/docs.yml`)

**Triggers:**
- Push/PR with docs changes
- **Workflow run** completion of semantic-release
- Manual trigger

**Actions:**
- Builds Sphinx documentation with `sphinx-multiversion`
- Generates version switcher including beta tags
- Deploys to GitHub Pages
- Supports both `main` and `dev` branch docs

#### 4. Beta Cleanup Workflow (`.github/workflows/cleanup-beta-releases.yml`)

**Schedule:** Daily at 02:00 UTC

**Actions:**
1. **Workflow Artifact Cleanup** (New in 2026)
   - Deletes workflow artifacts older than 7 days
   - Saves storage costs and prevents accumulation
   - Reports deleted count and freed space in workflow summary
   - Required permission: `actions: write`

2. **Beta Release Cleanup**
   - Lists all beta releases (tag contains `-beta.`)
   - Keeps latest 3 beta releases (configurable)
   - Deletes older beta releases via GitHub CLI
   - Dry-run mode available for testing

**Manual Trigger Options:**
- `dry_run`: Preview deletions without executing
- `keep_count`: Number of latest betas to keep (default: 3)

### Version Calculation Rules

#### Pre-v1.0.0 Versioning (Current State)

| Commit Type | Example Commit | Version Bump | Example |
|-------------|----------------|--------------|---------|
| `feat:` | `feat: add new feature` | Minor | 0.1.0 → 0.2.0 |
| `fix:` | `fix: resolve bug` | Patch | 0.1.0 → 0.1.1 |
| `feat!:` or `BREAKING CHANGE:` | `feat!: redesign API` | Minor | 0.1.0 → 0.2.0 |
| `perf:` | `perf: optimize query` | Patch | 0.1.0 → 0.1.1 |

**Excluded from changelog:** `chore`, `ci`, `refactor`, `style`, `test`, `docs`, `build`

**Beta releases:** Append `-beta.N` counter (e.g., `v0.2.0-beta.1`, `v0.2.0-beta.2`)

#### Post-v1.0.0 Versioning (Future)

Breaking changes will bump major version (1.0.0 → 2.0.0) following standard semantic versioning.

### Configuration

**`pyproject.toml`:**
```toml
[tool.semantic_release]
major_on_zero = false  # Keep 0.y.z until manual v1.0.0
tag_format = "v{version}"
commit_parser = "conventional"
version_toml = []  # Disable - use hatch-vcs
version_variables = []

[tool.semantic_release.branches.dev]
match = "dev"
prerelease = true
prerelease_token = "beta"

[tool.semantic_release.branches.main]
match = "main"
prerelease = false

[tool.semantic_release.changelog]
changelog_file = "CHANGELOG.md"
mode = "update"
exclude_commit_patterns = [
    "^chore\\(.+\\)?: .+",
    "^ci\\(.+\\)?: .+",
    # ... see pyproject.toml for full list
]
```

**Version Source:** `hatch-vcs` reads git tags directly (no conflicts with python-semantic-release)

### Security and Permissions

**Required Permissions:**
- `contents: write` - Create tags and releases
- `issues: write` - Post release notifications (future)
- `pull-requests: write` - Comment on PRs (future)

**Token:** Uses `secrets.GITHUB_TOKEN` (automatically provided by GitHub Actions)

**Branch Protection:**
- Semantic-release commits bypass protection via GitHub App authentication
- Manual commits still require PR review

### Branch Protection Setup

The repository uses branch protection rules to maintain code quality while supporting automated workflows. This section provides step-by-step instructions for configuring branch protection in the GitHub web interface.

#### Configuring `dev` Branch Protection

The `dev` branch is the primary development branch where all new features, fixes, and dependency updates are merged.

**Step 1: Access Branch Protection Settings**

1. Navigate to your repository on GitHub: `https://github.com/mosh666/pyMM`
2. Click **Settings** (requires admin permissions)
3. Select **Branches** from the left sidebar
4. Click **Add branch protection rule** (or edit existing rule for `dev`)

**Step 2: Configure Branch Name Pattern**

- **Branch name pattern:** `dev`
- This will apply rules specifically to the `dev` branch

**Step 3: Enable Required Status Checks**

✅ **Require status checks to pass before merging**
- Check this box to ensure all CI checks pass before any PR can be merged
- This applies to both manual PRs and automated Dependabot PRs

**Required checks:**
- GitHub will show a list of recent status checks from your workflows
- Select all checks from the `CI` workflow:
  - `lint` (Ruff code linting)
  - `type-check` (MyPy type checking)
  - `test (3.12, ubuntu-latest)` (and other matrix combinations)
- Or enable **Require branches to be up to date before merging** to require any checks that run

✅ **Require branches to be up to date before merging**
- Optional but recommended
- Ensures the PR branch has the latest changes from `dev` before merging

**Step 4: Configure Pull Request Reviews**

✅ **Require a pull request before merging**
- Check this box to enforce the PR workflow

✅ **Require approvals**
- Set **Required number of approvals before merging:** `1`
- This ensures manual PRs get reviewed by a human

**Step 5: Configure Bypass Rules for Dependabot**

✅ **Allow specified actors to bypass required pull requests**
- Click **Add actor**
- Search for and select: `dependabot[bot]`
- This allows Dependabot PRs to bypass the review requirement
- ⚠️ **Important**: Dependabot PRs still must pass all status checks (CI)

**Bypass permissions:**
- `dependabot[bot]` bypasses: Review requirement only
- `dependabot[bot]` must pass: All status checks
- Manual PRs require: 1 review + all status checks

**Step 6: Additional Recommended Settings**

❌ **Require linear history** - Optional (enforces rebase/squash)
❌ **Require deployments to succeed** - Not needed for `dev` branch
✅ **Do not allow bypassing the above settings** - Recommended for consistency
✅ **Restrict who can push to matching branches** - Optional (limit to maintainers)

**Step 7: Save Changes**

- Scroll to the bottom and click **Create** (or **Save changes** if editing)
- The branch protection rules are now active

#### Dependabot Auto-Merge Workflow

The repository includes an automated workflow (`.github/workflows/dependabot-automerge.yml`) that:

1. **Detects Dependabot PRs**: Triggers only on PRs opened by `dependabot[bot]` targeting `dev`
2. **Posts Information**: Comments with full dependency details, versions, and update types
3. **Auto-Approves**: Automatically approves the PR (satisfying the bypass requirement)
4. **Enables Auto-Merge**: Uses `gh pr merge --auto --merge` to queue the PR for merging
5. **Monitors CI**: Waits for status checks with retry logic (3 attempts, 5 minute intervals)
6. **Handles Failures**: Posts explanatory comments if CI checks fail repeatedly

**Workflow Permissions:**
```yaml
permissions:
  contents: write       # To enable merge operations
  pull-requests: write  # To approve and comment on PRs
```

**Notification Management:**

To reduce notification noise from automated Dependabot PRs, configure your GitHub notification settings:

1. Go to `https://github.com/settings/notifications`
2. Under **Watching**, click **Custom** for the `mosh666/pyMM` repository
3. Configure notification preferences:
   - ✅ **Participating**: Get notified when you're mentioned or involved
   - ⚠️ **Pull requests**: Choose based on preference
     - Option A: Disable to reduce Dependabot PR noise
     - Option B: Enable and use email filters to auto-archive Dependabot notifications
4. **Email Filters** (Gmail example):
   - Filter: `from:notifications@github.com subject:"[mosh666/pyMM]" "dependabot"`
   - Action: Skip Inbox, Apply label "GitHub/Dependabot"

**Manual Review Override:**

If you need to manually review a Dependabot PR:
1. Dependabot PRs will still have the auto-approve and auto-merge enabled
2. To prevent auto-merge: Disable auto-merge via PR interface or comment `@dependabot cancel merge`
3. Request changes or add review comments as needed
4. The PR will only merge after all checks pass and requested changes are resolved

#### Configuring `main` Branch Protection

The `main` branch receives only stable releases via merges from `dev`. Different protection rules apply:

**Recommended Settings:**
- ✅ **Require a pull request before merging** with **2 required reviews**
- ✅ **Require status checks to pass before merging** (all CI checks)
- ✅ **Require branches to be up to date before merging**
- ✅ **Require conversation resolution before merging**
- ❌ **Do not** add bypass rules for `dependabot[bot]` (not needed - it targets `dev`)
- ✅ **Restrict who can push to matching branches** to repository maintainers only

**Rationale:**
- Higher review requirement ensures stable release quality
- No automated merges to `main` - all merges are deliberate `dev` → `main` promotions
- Only maintainers can initiate stable releases

### Monitoring and Debugging

**View Workflow Runs:**
```bash
gh run list --workflow=semantic-release.yml --limit 10
gh run view <run-id> --log
```

**Preview Next Version:**
```bash
just release-preview
# Or: semantic-release version --print
```

**Force Manual Release:**
1. GitHub UI: Actions → Semantic Release → Run workflow
2. Select branch (`dev` or `main`)
3. Enable "force" checkbox
4. Click "Run workflow"

**Troubleshooting:** See [Troubleshooting Guide](troubleshooting.md)

---

### Modern Python Features Used

```python
# Native generics (PEP 585)
plugins: dict[str, PluginBase] = {}
manifests: list[PluginManifest] = []

# Structural pattern matching (PEP 634)
match source_type:
    case "url":
        return URLDownloader(url)
    case "github":
        return GitHubDownloader(repo, asset_pattern)
    case _:
        raise ValueError(f"Unknown source: {source_type}")

# Union types with | (PEP 604)
def get_version(self) -> str | None:
    ...

# Dataclasses with slots (PEP 681)
@dataclass(slots=True)
class DriveInfo:
    letter: str
    label: str
    filesystem: str
```

---

(directory-structure)=

## 📁 Directory Structure

```
pyMM/
├── app/                          # Application source code
│   ├── __init__.py              # Package initialization, version
│   ├── main.py                   # Entry point, QApplication setup
│   ├── py.typed                  # PEP 561 type marker
│   │
│   ├── core/                     # Core services (infrastructure)
│   │   ├── logging_service.py   # Logging configuration
│   │   └── services/
│   │       ├── config_service.py    # Configuration management
│   │       ├── file_system_service.py  # File operations
│   │       └── storage_service.py   # Drive detection (WMI)
│   │
│   ├── models/                   # Domain models
│   │   └── project.py           # Project entity
│   │
│   ├── plugins/                  # Plugin system
│   │   ├── plugin_base.py       # PluginBase ABC, PluginManifest
│   │   ├── plugin_manager.py    # Discovery, installation
│   │   └── plugin_schema.py     # Pydantic validation schemas
│   │
│   ├── services/                 # Application services
│   │   ├── git_service.py       # Git operations (GitPython)
│   │   └── project_service.py   # Project CRUD operations
│   │
│   └── ui/                       # User interface
│       ├── main_window.py       # Main application window
│       ├── components/
│       │   └── first_run_wizard.py  # Initial setup wizard
│       ├── dialogs/
│       │   ├── project_browser.py   # Project selection
│       │   ├── project_wizard.py    # New project creation
│       │   └── settings_dialog.py   # Application settings
│       └── views/
│           ├── plugin_view.py   # Plugin management UI
│           ├── project_view.py  # Project list/details
│           └── storage_view.py  # Drive status display
│
├── config/                       # Configuration files
│   ├── app.yaml                 # Default application config
│   └── user.yaml.example        # User config template
│
├── docs/                         # Documentation
│   ├── architecture.md          # This file
│   ├── plugin-development.md    # Plugin creation guide
│   ├── installation.md          # Installation guide
│   ├── getting-started.md       # Getting started guide
│   ├── features.md              # Features and usage
│   └── configuration.md         # Configuration guide
│
├── plugins/                      # Plugin manifests
│   ├── git/plugin.yaml
│   ├── ffmpeg/plugin.yaml
│   └── ...
│
├── templates/                    # Project templates (base, default, photo-management, video-editing)
│   ├── base/
│   │   ├── template.yaml        # Base template metadata
│   │   └── README.md            # Template documentation
│   ├── default/
│   │   ├── template.yaml        # Default template (extends base)
│   │   └── README.md
│   ├── photo-management/
│   │   ├── template.yaml        # Photography workflow template
│   │   └── README.md
│   ├── video-editing/
│   │   ├── template.yaml        # Video editing template
│   │   └── README.md
│   └── test/
│       ├── template.yaml        # Test template for unit tests
│       └── README.md
│
├── scripts/                      # Build and maintenance scripts
│   ├── build_manager.py    # Create distributable package
│   ├── setup-git-hooks.ps1      # Install pre-commit hooks (Windows)
│   └── setup-git-hooks.sh       # Install pre-commit hooks (Unix)
│
├── tests/                        # Test suite (193 tests, 73% coverage)
│   ├── conftest.py              # pytest fixtures and configuration
│   ├── unit/                    # Unit tests (isolated)
│   ├── integration/             # Integration tests (multi-component)
│   └── gui/                     # GUI tests (pytest-qt)
│
├── .github/                      # GitHub configuration
│   ├── workflows/               # CI/CD pipelines
│   │   ├── ci.yml              # Test, lint, type-check
│   │   ├── build.yml           # Build distributable
│   │   ├── release.yml         # Create GitHub releases
│   │   └── scorecard.yml       # OpenSSF security scoring
│   ├── CODE_OF_CONDUCT.md      # Contributor Covenant 2.1
│   ├── SECURITY.md             # Security policy
│   └── PULL_REQUEST_TEMPLATE.md # PR checklist
│
├── launcher.py                   # Application launcher script
├── pyproject.toml               # PEP 621 project metadata
├── README.md                    # Project overview
├── CHANGELOG.md                 # Keep a Changelog format
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
└── Dockerfile                   # Container image (development)
```

---

(module-dependencies)=

## 🔗 Module Dependencies

### Dependency Graph

```{mermaid}
graph TD
    UI[app.ui]
    Services[app.services]
    Core[app.core.services]
    Plugins[app.plugins]
    Models[app.models]

    UI --> Services
    UI --> Core
    UI --> Plugins

    Services --> Core
    Services --> Plugins
    Services --> Models

    Plugins --> Core
    Plugins --> Models

    Models -.-> Pydantic
    Core -.-> Rich
    Core -.-> WMI
    Plugins -.-> aiohttp
    Services -.-> GitPython
```

### Import Rules

1. **No Circular Dependencies**: Enforced by strict import order
2. **UI Depends on Everything**: Presentation layer imports from all layers
3. **Core is Independent**: No dependencies on app.services or app.ui
4. **Models are Pure**: Only dataclasses/Pydantic, no business logic

### Example: Proper Dependency Injection

```python
# main.py - Composition root
def main():
    # 1. Initialize core services (no dependencies)
    config_service = ConfigService(app_dir, storage_dir)
    logging_service = LoggingService()
    fs_service = FileSystemService()

    # 2. Initialize application services (depend on core)
    git_service = GitService()
    plugin_manager = PluginManager(plugins_dir, manifests_dir)
    project_service = ProjectService(
        projects_dir,
        git_service,
        fs_service
    )

    # 3. Initialize UI (depends on everything)
    main_window = MainWindow(
        config_service,
        plugin_manager,
        project_service
    )

    main_window.show()
```

---

(security-architecture)=

## 🔒 Security Architecture

### Threat Model

| Threat | Mitigation | Status |
|--------|-----------|--------|
| **Malicious Plugins** | No code execution, manifest-only | ✅ Implemented |
| **MITM Attacks** | HTTPS only, SHA-256 verification | ✅ Implemented |
| **Path Traversal** | Input validation, Path.resolve() | ✅ Implemented |
| **Dependency Vulnerabilities** | Dependabot, Ruff security checks | ✅ Automated |
| **Sensitive Data Leaks** | Config redaction, no hardcoded secrets | ✅ Implemented |

### Security Features

1. **Plugin Sandboxing**
   - Plugins are data files (YAML), not executable Python
   - SimplePluginImplementation handles all operations
   - No `eval()`, `exec()`, or `__import__()` calls

2. **Download Security**
   ```python
   async def download(self, progress_callback) -> bool:
       """Download with integrity verification."""
       # 1. HTTPS only
       if not self.manifest.source_uri.startswith("https://"):
           raise ValueError("Insecure URL")

       # 2. Download to temp file
       temp_file = tempfile.mktemp(suffix=".download")

       # 3. Calculate SHA-256 during download
       hasher = hashlib.sha256()
       async with aiohttp.ClientSession() as session:
           async with session.get(url) as response:
               async for chunk in response.content.iter_chunked(8192):
                   hasher.update(chunk)
                   f.write(chunk)

       # 4. Verify checksum before extraction
       if hasher.hexdigest() != self.manifest.checksum_sha256:
           raise SecurityError("Checksum mismatch")
   ```

3. **Input Validation**
   ```python
   def _validate_project_name(self, name: str) -> bool:
       """Validate project name for path traversal."""
       if not name:
           return False

       # No path separators
       if "/" in name or "\\" in name:
           return False

       # No special chars
       if not re.match(r"^[a-zA-Z0-9_\-. ]+$", name):
           return False

       # No parent directory references
       if ".." in name:
           return False

       return True
   ```

4. **OpenSSF Scorecard**
   - Daily automated security scoring
   - Checks: SAST, dependency updates, signed releases
   - Badge: [![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)

---

(testing-strategy)=

## 🧪 Testing Strategy

### Test Pyramid

```
         /\
        /  \        E2E Tests (GUI workflow)
       /____\       10 tests (5%)
      /      \
     / Integ  \     Integration Tests (multi-component)
    /__________\    38 tests (20%)
   /            \
  /    Unit      \  Unit Tests (isolated, mocked)
 /________________\ 145 tests (75%)
```

### Test Organization

| Directory | Purpose | Count | Coverage |
|-----------|---------|-------|----------|
| `tests/unit/` | Isolated component tests | 145 | 85% |
| `tests/integration/` | Multi-component workflows | 38 | 65% |
| `tests/gui/` | UI interaction tests | 10 | 45% |

### Testing Tools

```python
# pytest with plugins
pytest>=7.4.0
pytest-qt>=4.3.0        # PySide6 testing
pytest-cov>=4.1.0       # Coverage reporting
pytest-asyncio>=0.23.0  # Async test support
pytest-mock>=3.12.0     # Mocking utilities

# Run tests
pytest tests/                          # All tests
pytest tests/unit/                     # Unit only
pytest --cov=app --cov-report=html    # With coverage
pytest -v --tb=short                   # Verbose, short traceback
```

### Example Test

```python
# tests/unit/test_plugin_manager.py
import pytest
from pathlib import Path
from app.plugins.plugin_manager import PluginManager

@pytest.fixture
def plugin_manager(tmp_path: Path) -> PluginManager:
    """Create PluginManager with temp directories."""
    plugins_dir = tmp_path / "plugins"
    manifests_dir = tmp_path / "manifests"
    plugins_dir.mkdir()
    manifests_dir.mkdir()
    return PluginManager(plugins_dir, manifests_dir)

def test_discover_plugins_empty(plugin_manager: PluginManager):
    """Test discovery with no manifests."""
    count = plugin_manager.discover_plugins()
    assert count == 0
    assert len(plugin_manager.plugins) == 0

def test_discover_plugins_valid(plugin_manager: PluginManager):
    """Test discovery with valid manifest."""
    # Create test manifest
    git_dir = plugin_manager.manifests_dir / "git"
    git_dir.mkdir()
    manifest = git_dir / "plugin.yaml"
    manifest.write_text("""
name: Git
version: 2.47.1
description: Version control
homepage: https://git-scm.com
mandatory: false
enabled: true
source:
  type: url
  uri: https://example.com/git.zip
  checksum_sha256: "abc123"
command:
  path: cmd
  executable: git.exe
dependencies: []
    """)

    count = plugin_manager.discover_plugins()
    assert count == 1
    assert "Git" in plugin_manager.plugins

@pytest.mark.asyncio
async def test_install_plugin_success(plugin_manager: PluginManager, mocker):
    """Test successful plugin installation."""
    # Mock download and extract
    mock_download = mocker.patch.object(
        SimplePluginImplementation,
        "download",
        return_value=True
    )
    mock_extract = mocker.patch.object(
        SimplePluginImplementation,
        "extract",
        return_value=True
    )
    mock_validate = mocker.patch.object(
        SimplePluginImplementation,
        "validate_installation",
        return_value=True
    )

    # Add plugin
    manifest = PluginManifest(
        name="TestPlugin",
        version="1.0.0",
        mandatory=False,
        enabled=True,
        source_type="url",
        source_uri="https://example.com/test.zip"
    )
    plugin_manager.plugins["TestPlugin"] = SimplePluginImplementation(
        manifest,
        plugin_manager.plugins_dir
    )

    # Install
    result = await plugin_manager.install_plugin("TestPlugin")

    assert result is True
    mock_download.assert_called_once()
    mock_extract.assert_called_once()
    mock_validate.assert_called_once()
```

### CI/CD Testing

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install uv
        uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - name: Install dependencies
        run: uv sync --all-extras
      - name: Run tests
        run: pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

---

(performance-considerations)=

## ⚡ Performance Considerations

### Optimization Strategies

1. **Lazy Loading**
   - UI views load on-demand
   - Plugins discovered on first access
   - Project list loaded incrementally

2. **Async Operations**
   ```python
   # Download multiple plugins concurrently
   async def install_all(self, plugin_names: list[str]) -> dict[str, bool]:
       tasks = [
           self.install_plugin(name)
           for name in plugin_names
       ]
       results = await asyncio.gather(*tasks, return_exceptions=True)
       return dict(zip(plugin_names, results))
   ```

3. **Caching**
   - Configuration cached in memory
   - Drive list cached with 30s TTL
   - Git status cached until file changes

4. **Resource Pooling**
   ```python
   # Reuse HTTP sessions
   class PluginManager:
       def __init__(self):
           self._http_session: aiohttp.ClientSession | None = None

       async def get_session(self) -> aiohttp.ClientSession:
           if self._http_session is None:
               self._http_session = aiohttp.ClientSession()
           return self._http_session
   ```

### Performance Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Application Startup | ~1.2s | Cold start with config load |
| Plugin Discovery | ~50ms | 10 plugins |
| Project List Load | ~100ms | 50 projects |
| Git Status Check | ~80ms | Medium repository |
| Plugin Download | ~10s | 50MB over 10Mbps |

---

(extension-points)=

## 🔌 Extension Points

### Adding New Plugin Source Types

```python
# app/plugins/plugin_base.py
class CustomSourcePlugin(PluginBase):
    """Support for custom package managers."""

    async def download(self, progress_callback) -> bool:
        # Implement custom download logic
        # e.g., Chocolatey, winget, pip
        ...
```

### Adding New Project Templates

```python
# app/services/project_service.py
TEMPLATES = {
    "video": VideoTemplate(),
    "photo": PhotoTemplate(),
    "audio": AudioTemplate(),
    "custom": CustomTemplate(),  # <-- Add here
}
```

### Adding New Configuration Sources

```python
# app/core/services/config_service.py
def _load_config(self) -> AppConfig:
    config = AppConfig()

    # 1. Defaults
    # 2. Environment config
    # 3. User config
    # 4. Remote config (new)
    if self._remote_config_enabled:
        config = self._merge_remote_config(config)

    return config
```

---

## 📊 Metrics and Monitoring

### Code Quality Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Coverage | ≥70% | 73% | ✅ |
| Type Coverage | 100% | 100% | ✅ |
| Ruff Violations | 0 | 0 | ✅ |
| MyPy Errors | 0 | 0 | ✅ |
| Ruff Security | 0 | 0 | ✅ |
| OpenSSF Score | ≥7.0 | 8.2 | ✅ |

### Runtime Metrics (Future)

```python
# Example: Add metrics collection
from prometheus_client import Counter, Histogram

plugin_downloads = Counter(
    "plugin_downloads_total",
    "Total plugin downloads",
    ["plugin_name", "status"]
)

download_duration = Histogram(
    "plugin_download_duration_seconds",
    "Plugin download duration",
    ["plugin_name"]
)

@download_duration.labels("Git").time()
async def download_plugin(name: str) -> bool:
    try:
        result = await self.install_plugin(name)
        plugin_downloads.labels(name, "success").inc()
        return result
    except Exception:
        plugin_downloads.labels(name, "failure").inc()
        raise
```

---

## 🌍 Cross-Platform Architecture

### Platform Abstraction Strategy

pyMediaManager implements comprehensive platform abstraction to ensure consistent behavior across Windows, Linux, and macOS while leveraging platform-specific features when available.

#### Storage Service Platform Abstraction

The `StorageService` uses the **Strategy Pattern** with platform-specific implementations:

```python
# Abstract base class
class StoragePlatform(ABC):
    @abstractmethod
    def get_drives(self) -> list[Drive]:
        """Get all available storage drives."""

    @abstractmethod
    def get_drive_info(self, path: Path) -> Drive | None:
        """Get information about a specific drive."""

# Platform implementations
class WindowsStorage(StoragePlatform):
    """Windows implementation using WMI and ctypes."""
    def get_drives(self) -> list[Drive]:
        import wmi
        c = wmi.WMI()
        logical_disks = c.Win32_LogicalDisk()
        # ... implementation

class LinuxStorage(StoragePlatform):
    """Linux implementation using pyudev."""
    def get_drives(self) -> list[Drive]:
        import pyudev
        context = pyudev.Context()
        # ... implementation

class MacOSStorage(StoragePlatform):
    """macOS implementation using diskutil."""
    def get_drives(self) -> list[Drive]:
        result = subprocess.run(
            ["diskutil", "list", "-plist"],
            # ... implementation
        )

# Platform detection and selection
def create_storage_platform() -> StoragePlatform:
    if sys.platform == "win32":
        return WindowsStorage()
    elif sys.platform == "darwin":
        return MacOSStorage()
    elif sys.platform.startswith("linux"):
        return LinuxStorage()
    else:
        raise NotImplementedError(f"Unsupported platform: {sys.platform}")
```

**Benefits:**
- Single interface for all storage operations
- Platform-specific optimizations
- Easy to test with mock implementations
- Extensible to new platforms

#### Privilege Escalation Dialogs

Different platforms require different approaches for elevated privileges:

```python
# Linux: pkexec (PolicyKit)
class LinuxPrivilegeDialog:
    @staticmethod
    def run_with_privileges(
        command: list[str],
        timeout: int = 30
    ) -> tuple[int, str, str]:
        result = subprocess.run(
            ["pkexec", *command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return (result.returncode, result.stdout, result.stderr)

# macOS: Full Disk Access prompts
class MacOSPermissionDialog(MessageBoxBase):
    """Guide users through System Settings for Full Disk Access."""
    def __init__(self, reason: str, parent: QWidget | None = None):
        # Show dialog explaining how to grant permissions
        # ... implementation

# Windows: UAC (User Account Control)
# Handled by os.startfile() with 'runas' verb
```

#### Platform-Specific Directory Structures

Following platform conventions for configuration and data storage:

```python
def get_platform_config_dir() -> Path:
    """Get platform-specific configuration directory."""
    if sys.platform == "win32":
        # Windows: %APPDATA%\pyMM
        return Path(os.environ["APPDATA"]) / "pyMM"
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/pyMM
        return Path.home() / "Library" / "Application Support" / "pyMM"
    else:
        # Linux: $XDG_CONFIG_HOME/pyMM or ~/.config/pyMM
        config_home = os.environ.get("XDG_CONFIG_HOME")
        if config_home:
            return Path(config_home) / "pyMM"
        return Path.home() / ".config" / "pyMM"

def get_platform_data_dir() -> Path:
    """Get platform-specific data directory."""
    if sys.platform == "win32":
        return Path(os.environ["APPDATA"]) / "pyMM"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "pyMM"
    else:
        data_home = os.environ.get("XDG_DATA_HOME")
        if data_home:
            return Path(data_home) / "pyMM"
        return Path.home() / ".local" / "share" / "pyMM"

def get_platform_cache_dir() -> Path:
    """Get platform-specific cache directory."""
    if sys.platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "pyMM" / "Cache"
    elif sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "pyMM"
    else:
        cache_home = os.environ.get("XDG_CACHE_HOME")
        if cache_home:
            return Path(cache_home) / "pyMM"
        return Path.home() / ".cache" / "pyMM"
```

**Platform Directory Standards:**
- **Windows**: AppData (roaming and local)
- **macOS**: ~/Library/Application Support and ~/Library/Caches
- **Linux**: XDG Base Directory Specification

#### Linux udev Rules Installer

For automatic USB device detection on Linux:

```python
class LinuxUdevInstaller:
    """Installer for pyMediaManager udev rules on Linux systems."""

    RULES_FILENAME = "99-pymm-usb.rules"
    RULES_DIR = Path("/etc/udev/rules.d")

    def install(self, use_privilege_dialog: bool = True) -> UdevInstallResult:
        """Install udev rules with optional GUI elevation."""
        if not self.is_linux():
            return UdevInstallResult(status=UdevInstallStatus.NOT_LINUX, ...)

        if use_privilege_dialog:
            # Use pkexec with GUI prompt
            returncode, stdout, stderr = LinuxPrivilegeDialog.run_with_privileges(
                command=["cp", temp_file, str(self.rules_path)],
                timeout=30
            )
        else:
            # Direct installation (requires root)
            if os.geteuid() != 0:
                return UdevInstallResult(status=UdevInstallStatus.PERMISSION_DENIED, ...)

        # Reload udev rules
        self._reload_udev_rules()
        return UdevInstallResult(status=UdevInstallStatus.SUCCESS, ...)
```

**udev Rules Content:**
```ini
# pyMediaManager USB Storage Detection Rules
ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="disk", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", ENV{DEVTYPE}=="partition", \
    TAG+="systemd", ENV{SYSTEMD_WANTS}+="pymm-usb-notify@%k.service"

ACTION=="add", SUBSYSTEM=="block", ENV{ID_BUS}=="usb", \
    GROUP="plugdev", MODE="0660"
```

### Platform-Specific Dependencies

Managed through optional dependency groups in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    "pytest>=9.0.0",
    "pytest-cov>=6.0.0",
    "ruff>=0.11.0",
    # ... other dev dependencies
]

# Platform-specific dependencies installed conditionally
# Linux: uv pip install --system pyudev>=0.24.1
# Windows: uv pip install --system pywin32>=306 wmi>=1.5.1
# macOS: No additional dependencies
```

**CI/CD Integration:**
```yaml
- name: Install platform-specific Python dependencies (Linux)
  if: runner.os == 'Linux'
  run: uv pip install --system pyudev>=0.24.1

- name: Install platform-specific Python dependencies (Windows)
  if: runner.os == 'Windows'
  run: uv pip install --system pywin32>=306 wmi>=1.5.1
```

### Testing Cross-Platform Code

```python
import sys
import pytest
from unittest.mock import patch

class TestStorageService:
    @pytest.mark.skipif(sys.platform != "linux", reason="Linux-only test")
    def test_linux_storage(self):
        """Test Linux-specific storage implementation."""
        storage = LinuxStorage()
        drives = storage.get_drives()
        assert all(isinstance(d, Drive) for d in drives)

    @patch("sys.platform", "win32")
    def test_windows_platform_detection(self):
        """Test platform detection returns Windows storage."""
        platform = create_storage_platform()
        assert isinstance(platform, WindowsStorage)

    @patch("sys.platform", "darwin")
    def test_macos_platform_detection(self):
        """Test platform detection returns macOS storage."""
        platform = create_storage_platform()
        assert isinstance(platform, MacOSStorage)
```

### Plugin System: Hybrid Executable Resolution

The plugin system supports both system-installed tools and portable versions:

```python
class ExecutableSource(str, Enum):
    """Source of plugin executable."""
    SYSTEM = "system"
    PORTABLE = "portable"
    AUTO = "auto"

class PluginPreferences(BaseModel):
    """User preferences for a specific plugin."""
    execution_preference: ExecutionPreference = ExecutionPreference.AUTO
    enabled: bool = True
    notes: str = ""

# Resolution order:
# 1. Check user preference (SYSTEM/PORTABLE/AUTO)
# 2. If AUTO, try system first, then portable
# 3. Validate version constraints
# 4. Cache successful resolution
```

**Configuration Example:**
```yaml
# config/plugins.yaml
plugin_preferences:
  git:
    execution_preference: system  # Prefer system Git
    enabled: true
    notes: "Using system Git for better integration"

  ffmpeg:
    execution_preference: portable  # Always use portable FFmpeg
    enabled: true
    notes: "Portable version includes custom codecs"
```

---

## 🚀 Future Architecture Enhancements

### Planned Improvements

1. **Plugin Marketplace**
   - Central repository of community plugins
   - Automated discovery and updates
   - Rating and review system

2. **Cloud Sync**
   - Optional project metadata sync
   - Cross-device project access
   - Backup to cloud storage (OneDrive, Dropbox)

3. **Scripting API**
   - Python API for automation
   - Batch operations (mass rename, convert)
   - Custom workflows

4. **Performance Profiling**
   - Built-in profiler integration
   - Memory leak detection
   - Bottleneck identification

---

## 📚 References

- [PEP 621 - Storing project metadata in pyproject.toml](https://peps.python.org/pep-0621/)
- [PEP 585 - Type Hinting Generics In Standard Collections](https://peps.python.org/pep-0585/)
- [PEP 604 - Allow writing union types as X | Y](https://peps.python.org/pep-0604/)
- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/)
- [OpenSSF Scorecard](https://securityscorecards.dev/)

---

**Document Version:** 1.0.0
**Last Review:** January 7, 2026
**Maintainer:** @mosh666
**Status:** ✅ Current
