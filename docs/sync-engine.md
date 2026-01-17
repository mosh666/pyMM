# Sync Engine

**Comprehensive Synchronization System** for pyMediaManager Storage Groups.
This guide covers the fully implemented synchronization engine that provides
manual, scheduled, and real-time file synchronization between Master and
Backup drives.

> **Status**: ✅ **Fully Implemented** - All Phase 2 sync features are production-ready

## Overview

The Sync Engine is a sophisticated multi-modal synchronization system built
on top of Storage Groups, providing automated backup workflows with advanced
features including:

- **Manual Sync**: On-demand synchronization with progress tracking
- **Scheduled Sync**: Cron-like scheduling with APScheduler
- **Real-Time Sync**: Watchdog-based file system monitoring
- **Incremental Backup**: SQLite-based change tracking (sync only changed files)
- **Conflict Resolution**: Visual conflict detection and resolution
- **Advanced Options**: Encryption, compression, bandwidth throttling, parallel copying

### Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    Sync Engine Architecture                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌───────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Manual Sync   │  │ Scheduled    │  │ Real-Time Sync  │  │
│  │ UI Trigger    │  │ APScheduler  │  │ Watchdog FS     │  │
│  └───────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│          │                  │                    │            │
│          └──────────────────┼────────────────────┘            │
│                             ▼                                 │
│                   ┌──────────────────┐                        │
│                   │ FileSynchronizer │                        │
│                   │  - sync_directory│                        │
│                   │  - detect_conflicts                       │
│                   │  - calculate_checksum                     │
│                   └────────┬─────────┘                        │
│                            │                                  │
│          ┌─────────────────┼──────────────────┐              │
│          ▼                 ▼                   ▼              │
│  ┌───────────────┐ ┌──────────────┐ ┌─────────────────┐    │
│  │ BackupTracker │ │ Advanced     │ │ Notification    │    │
│  │ SQLite DB     │ │ Options      │ │ Manager         │    │
│  │ - Change log  │ │ - Encryption │ │ - Progress      │    │
│  │ - Checksums   │ │ - Compression│ │ - Conflicts     │    │
│  │ - History     │ │ - Throttling │ │ - Completion    │    │
│  └───────────────┘ └──────────────┘ └─────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Core Modules

The sync engine consists of 9 implemented modules in `app/core/sync/`:

| Module | Purpose | Key Classes |
| -------- | ------- | ------------- |
| `file_synchronizer.py` | Core sync logic | `FileSynchronizer`, `SyncStatistics`, `FileConflict` |
| `backup_tracking.py` | SQLite change tracking | `BackupTrackingDatabase` |
| `scheduled_sync.py` | APScheduler integration | `ScheduledSyncManager`, `SyncSchedule` |
| `realtime_sync.py` | Watchdog file monitoring | `RealtimeSyncHandler`, `RealtimeSyncManager` |
| `notifications.py` | Progress/status callbacks | `NotificationManager` |
| `crypto_compression.py` | AES-256-GCM + GZIP/LZ4 | `CryptoHelper`, `CompressionHelper` |
| `bandwidth_throttler.py` | Token bucket rate limiting | `BandwidthThrottler` |
| `advanced_sync_options.py` | Configuration dataclass | `AdvancedSyncOptions`, `SpaceSavingsReport` |
| `__init__.py` | Public API exports | All public classes |

> **⚠️ Test Coverage:** These 9 modules currently have **0% test coverage**. While the sync engine is fully
> implemented and functional, comprehensive test coverage is needed. See
> [examples/sync/README.md](examples/sync/README.md) for working code examples demonstrating the APIs.
>
> **Contributions Welcome:** Test coverage for sync modules is a high-priority contribution area. See
> [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) for testing guidelines.

---

## Manual Synchronization

Manual sync provides on-demand synchronization with full progress tracking and user control.

### Basic Usage

#### From UI

1. Right-click project → **Properties**
2. Navigate to **Storage** tab
3. Click **"Sync to Backup"** button
4. Progress dialog shows:
   - Files copied/skipped/failed
   - Current file name
   - Transfer speed
   - Estimated time remaining
5. Click **"Cancel"** to abort (in-progress files complete)

#### From API

```python
from app.core.services.storage_group_service import StorageGroupService
from pathlib import Path

# Initialize service
storage_service = StorageGroupService(config_path, storage_service)

# Define progress callback
def progress_callback(current_file: int, total_files: int):
    percent = (current_file / total_files) * 100
    print(f"Progress: {percent:.1f}% ({current_file}/{total_files})")

# Sync to backup
result = storage_service.sync_to_backup(
    group_id="550e8400-e29b-41d4-a716-446655440000",
    source_path=Path("D:/pyMM.Projects/MyProject"),
    progress_callback=progress_callback
)

print(f"Sync complete: {result.files_copied} files copied, {result.bytes_copied} bytes")
```

> **📚 Code Examples:** See [examples/sync/README.md](examples/sync/README.md) for complete working examples:
>
> - [manual_sync.py](examples/sync/manual_sync.py) - One-time sync operation
> - [scheduled_sync_setup.py](examples/sync/scheduled_sync_setup.py) - APScheduler integration
> - [realtime_sync_monitor.py](examples/sync/realtime_sync_monitor.py) - Watchdog monitoring
> - [sync_with_encryption.py](examples/sync/sync_with_encryption.py) - Encrypted sync
> - [sync_history.py](examples/sync/sync_history.py) - Query sync history

### Options

| Parameter | Type | Default | Description |
| ----------- | ------ | ------- | ------------- |
| `skip_existing` | `bool` | `False` | Skip files that already exist at destination |
| `verify_checksums` | `bool` | `False` | Verify file integrity with SHA-256 after copy |
| `incremental` | `bool` | `True` | Use tracking DB to skip unchanged files |

### Return Value: `SyncStatistics`

```python
@dataclass
class SyncStatistics:
    files_copied: int = 0
    files_skipped: int = 0
    files_failed: int = 0
    bytes_copied: int = 0
    conflicts_detected: int = 0
    start_time: datetime
    end_time: datetime | None
```

---

(scheduled-sync)=

## Scheduled Synchronization

Automated syncs using APScheduler with interval-based or cron-based triggers.

### Configuration

#### Interval-Based Schedule

```python
from app.core.sync import ScheduledSyncManager, SyncSchedule

# Create manager
manager = ScheduledSyncManager(
    storage_group_service=group_service,
    notification_callback=lambda gid, status, msg: print(f"{status}: {msg}")
)

# Start scheduler
manager.start()

# Add interval schedule (every 30 minutes)
schedule = manager.add_interval_schedule(
    schedule_id="project-auto-sync",
    group_id="550e8400-e29b-41d4-a716-446655440000",
    project_path=Path("D:/pyMM.Projects/MyProject"),
    interval_minutes=30
)
```

#### Cron-Based Schedule

```python
# Daily at 2:00 AM
schedule = manager.add_cron_schedule(
    schedule_id="nightly-backup",
    group_id="550e8400-e29b-41d4-a716-446655440000",
    project_path=Path("D:/pyMM.Projects/MyProject"),
    cron_expression="0 2 * * *"
)

# Every Monday at 9:00 AM
schedule = manager.add_cron_schedule(
    schedule_id="weekly-sync",
    group_id="550e8400-e29b-41d4-a716-446655440000",
    project_path=Path("D:/pyMM.Projects/MyProject"),
    cron_expression="0 9 * * MON"
)
```

### Cron Expression Format

```text
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

**Common Presets**:

| Expression | Description |
| ------------ | ------------- |
| `0 2 * * *` | Daily at 2:00 AM |
| `0 */4 * * *` | Every 4 hours |
| `0 9 * * MON` | Every Monday at 9:00 AM |
| `0 0 1 * *` | First day of month at midnight |
| `*/15 * * * *` | Every 15 minutes |

### Schedule Management

```python
# List all schedules
schedules = manager.list_schedules()
for schedule in schedules:
    print(f"{schedule.schedule_id}: Next run at {schedule.next_run}")

# Pause/resume schedule
manager.pause_schedule("project-auto-sync")
manager.resume_schedule("project-auto-sync")

# Remove schedule
manager.remove_schedule("project-auto-sync")

# Shutdown scheduler (waits for running jobs)
manager.shutdown(wait=True)
```

### Notification Callback

```python
def notification_callback(group_id: str, status: str, message: str):
    """
    Handle sync notifications.

    Args:
        group_id: Storage group identifier
        status: "started" | "completed" | "failed" | "conflict"
        message: Human-readable status message
    """
    if status == "completed":
        print(f"✓ Sync completed: {message}")
    elif status == "failed":
        print(f"✗ Sync failed: {message}")
    elif status == "conflict":
        print(f"⚠ Conflict detected: {message}")

manager = ScheduledSyncManager(
    storage_group_service=group_service,
    notification_callback=notification_callback
)
```

---

(realtime-sync)=

## Real-Time Synchronization

File system watching with watchdog for automatic synchronization on file changes.

### Configuration

```python
from app.core.sync import RealtimeSyncManager

# Create manager
manager = RealtimeSyncManager(
    storage_group_service=group_service,
    notification_callback=lambda gid, event, paths: print(f"{event}: {len(paths)} files")
)

# Enable real-time sync for a project
watch_id = manager.enable_realtime_sync(
    group_id="550e8400-e29b-41d4-a716-446655440000",
    watch_path=Path("D:/pyMM.Projects/MyProject"),
    debounce_seconds=0.5  # Wait 500ms before processing events
)

# Check if enabled
is_active = manager.is_realtime_sync_enabled(watch_id)
print(f"Real-time sync active: {is_active}")

# List all watchers
watchers = manager.list_realtime_watchers()
for watcher in watchers:
    print(f"{watcher['watch_id']}: {watcher['watch_path']}")

# Disable real-time sync
manager.disable_realtime_sync(watch_id)
```

### Event Handling

The real-time sync handler monitors these file system events:

| Event | Action |
| ------- | -------- |
| `created` | Copy new file to backup |
| `modified` | Update file on backup |
| `deleted` | Propagate deletion to backup |
| `moved` | Handle move/rename on backup |

### Debouncing

Rapid file changes are batched to prevent excessive syncs:

```python
# Short debounce for interactive editing (fast response)
watch_id = manager.enable_realtime_sync(
    group_id=group_id,
    watch_path=project_path,
    debounce_seconds=0.3  # 300ms
)

# Longer debounce for heavy processing (batch changes)
watch_id = manager.enable_realtime_sync(
    group_id=group_id,
    watch_path=project_path,
    debounce_seconds=2.0  # 2 seconds
)
```

### Sync Loop Prevention

The handler includes built-in protection against sync loops:

- `_sync_in_progress` flag prevents recursive sync triggers
- Events on destination path are ignored
- Only source (Master) drive events are processed

---

(incremental-backup)=

## Incremental Backup

SQLite-based change tracking for efficient incremental synchronization.

### How It Works

The `BackupTrackingDatabase` maintains a SQLite database at `~/.pymm/backup_tracking.db` with:

- File checksums (SHA-256)
- Last modified timestamps
- File sizes
- Sync history
- Schema version for migrations

### Incremental Sync Logic

```text
For each file in source:
  1. Calculate SHA-256 checksum
  2. Query tracking database for last sync record
  3. Compare checksum + mtime + size
  4. If changed → copy file
  5. If unchanged → skip (log as skipped)
  6. Update tracking record
```

### Database Schema

```sql
CREATE TABLE file_sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    last_synced TIMESTAMP NOT NULL,
    file_size INTEGER NOT NULL,
    operation_type TEXT NOT NULL,  -- "sync" | "restore" | "delete"
    UNIQUE(group_id, relative_path)
);

CREATE TABLE sync_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id TEXT NOT NULL,
    operation_type TEXT NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    files_copied INTEGER DEFAULT 0,
    files_skipped INTEGER DEFAULT 0,
    files_failed INTEGER DEFAULT 0,
    bytes_copied INTEGER DEFAULT 0,
    status TEXT NOT NULL  -- "running" | "completed" | "failed" | "cancelled"
);
```

### API Usage

```python
from app.core.sync import BackupTrackingDatabase
from pathlib import Path

# Initialize database
db = BackupTrackingDatabase(Path("~/.pymm/backup_tracking.db"))

# Check if file needs sync
needs_sync = db.needs_sync(
    group_id="550e8400...",
    relative_path="Media/RAW/IMG_1234.CR2",
    checksum="abc123...",
    mtime=datetime(2026, 1, 14, 10, 30),
    size=25000000
)

if needs_sync:
    # Copy file...

    # Update tracking record
    db.update_file_record(
        group_id="550e8400...",
        relative_path="Media/RAW/IMG_1234.CR2",
        checksum="abc123...",
        size=25000000,
        operation_type="sync"
    )

# Get sync history
history = db.get_sync_history(group_id="550e8400...", limit=50)
for op in history:
    print(f"{op['start_time']}: {op['files_copied']} files ({op['bytes_copied']} bytes)")
```

---

(conflict-resolution-workflow)=

## Conflict Resolution

Automatic conflict detection with manual resolution workflow.

### Conflict Types

| Conflict Type | Description | Resolution Options |
| --------------- | ------------- | ------------------- |
| `modified_both` | File changed on both Master and Backup | Keep Master, Keep Backup, Keep Both |
| `deleted_master` | File deleted on Master but exists on Backup | Delete Backup, Keep Backup |
| `deleted_backup` | File deleted on Backup but exists on Master | Restore to Backup, Delete Master |
| `size_mismatch` | File sizes differ significantly | Keep Larger, Keep Master, Keep Backup |

### Conflict Detection

```python
from app.core.services.storage_group_service import StorageGroupService

conflicts = storage_service.detect_conflicts(
    group_id="550e8400...",
    path=Path("D:/pyMM.Projects/MyProject")
)

for conflict in conflicts:
    print(f"Conflict: {conflict.relative_path}")
    print(f"  Type: {conflict.conflict_type}")
    print(f"  Master: {conflict.master_size} bytes @ {conflict.master_mtime}")
    print(f"  Backup: {conflict.backup_size} bytes @ {conflict.backup_mtime}")
```

### Resolution Workflow

```python
# Resolve conflicts programmatically
resolutions = {
    "Media/Photo1.jpg": "keep_master",
    "Media/Photo2.jpg": "keep_backup",
    "Media/Photo3.jpg": "keep_both",  # Renames backup to Photo3_backup.jpg
}

storage_service.resolve_conflicts(
    group_id="550e8400...",
    resolutions=resolutions
)
```

### UI Resolution

The Conflict Resolution Dialog (`ConflictResolutionDialog`) provides:

- **Visual Diff**: Side-by-side comparison of file metadata
- **Preview**: Image/video preview if applicable
- **Batch Actions**: Apply same resolution to multiple conflicts
- **Skip Option**: Defer resolution to later

---

(advanced-sync-options)=

## Advanced Sync Options

Comprehensive advanced features for enterprise and professional use cases.

### Configuration Class

```python
from app.core.sync import AdvancedSyncOptions, CompressionType, EncryptionType
from pathlib import Path

options = AdvancedSyncOptions(
    # Bandwidth throttling
    enable_bandwidth_limit=True,
    bandwidth_limit_mbps=10.0,  # 10 MB/s

    # Encryption
    enable_encryption=True,
    encryption_type=EncryptionType.AES_256_GCM,
    encryption_password="MySecurePassword123!",
    encryption_key_file=None,  # Or Path to key file

    # Compression
    enable_compression=True,
    compression_type=CompressionType.GZIP,
    compression_level=6,  # 1-9 for GZIP

    # Parallel copying
    enable_parallel_copy=True,
    max_parallel_files=4,

    # Reporting
    calculate_space_savings=True
)

# Serialize to dict for storage
config_dict = options.to_dict()

# Deserialize from dict
loaded_options = AdvancedSyncOptions.from_dict(config_dict)
```

(bandwidth-throttling)=

### Bandwidth Throttling

Token bucket algorithm for rate limiting:

```python
from app.core.sync import BandwidthThrottler

# Create throttler (10 MB/s)
throttler = BandwidthThrottler(rate_limit_mbps=10.0)

# Acquire tokens before copying data
chunk_size = 8192  # 8 KB
throttler.acquire(chunk_size)

# Copy file chunk
with open(source, 'rb') as src, open(dest, 'wb') as dst:
    while chunk := src.read(chunk_size):
        throttler.acquire(len(chunk))  # Wait if over rate limit
        dst.write(chunk)
```

**Benefits**:

- Preserves system performance during large syncs
- Prevents network saturation on NAS/remote drives
- Configurable per-project or per-sync
- Smooth burst handling for small files

(encryption-options)=

### Encryption

AES-256-GCM encryption for secure backups:

```python
from app.core.sync import CryptoHelper
from pathlib import Path

# Password-based encryption
helper = CryptoHelper(password="MySecurePassword123!")

# Encrypt file
encrypted_path = helper.encrypt_file(
    input_path=Path("Media/Photo.jpg"),
    output_path=Path("Backup/Media/Photo.jpg.encrypted")
)

# Decrypt file
decrypted_path = helper.decrypt_file(
    input_path=Path("Backup/Media/Photo.jpg.encrypted"),
    output_path=Path("Restored/Media/Photo.jpg")
)
```

**Key Features**:

- **Algorithm**: AES-256-GCM (authenticated encryption)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Nonce**: 96-bit unique nonce per file
- **Salt**: 16-byte random salt per file
- **Authentication Tag**: 16-byte tag for integrity verification

**Security Warning**:

⚠️ **Password/key required for restoration** - Store credentials securely! Lost passwords = unrecoverable data.

(compression-options)=

### Compression

GZIP or LZ4 compression to reduce backup size:

```python
from app.core.sync import CompressionHelper, CompressionType

# GZIP compression (higher ratio, slower)
helper = CompressionHelper(
    compression_type=CompressionType.GZIP,
    compression_level=6  # 1-9, default 6
)

# Compress file
compressed_path = helper.compress_file(
    input_path=Path("Media/Video.mp4"),
    output_path=Path("Backup/Media/Video.mp4.gz")
)

# LZ4 compression (faster, lower ratio)
helper = CompressionHelper(
    compression_type=CompressionType.LZ4,
    compression_level=3  # 1-12
)

# Decompress file
decompressed_path = helper.decompress_file(
    input_path=Path("Backup/Media/Video.mp4.gz"),
    output_path=Path("Restored/Media/Video.mp4")
)
```

**Compression Levels**:

| Level | GZIP | LZ4 | Use Case |
| ------- | ------ | ----- | ---------- |
| 1 | Fast, low ratio | Fastest | Real-time sync |
| 6 | Balanced (default) | Balanced | General use |
| 9 | Slow, high ratio | Maximum | Archival |

### Parallel Copying

Multi-threaded file transfers for improved performance:

```python
from concurrent.futures import ThreadPoolExecutor
import shutil

# Configure parallel copying
options = AdvancedSyncOptions(
    enable_parallel_copy=True,
    max_parallel_files=4  # 2-16 threads
)

# Implementation (simplified)
with ThreadPoolExecutor(max_workers=options.max_parallel_files) as executor:
    futures = []
    for file_path in files_to_copy:
        future = executor.submit(shutil.copy2, file_path, dest_path)
        futures.append(future)

    # Wait for completion
    for future in futures:
        future.result()
```

**Performance Notes**:

| Storage Type | Recommended Threads | Rationale |
| -------------- | --------------------- | ----------- |
| SSD | 8-16 | High random I/O performance |
| HDD | 2-4 | Sequential access faster |
| Network (NAS) | 4-8 | Bandwidth-dependent |
| USB 3.0+ | 4-8 | Parallel transfers benefit |

### Space Savings Report

Calculate compression/deduplication savings:

```python
from app.core.sync import SpaceSavingsReport

report = SpaceSavingsReport(
    original_size=1000000000,  # 1 GB
    compressed_size=650000000,  # 650 MB
    files_processed=1234
)

print(f"Compression ratio: {report.compression_ratio:.2f}")  # 1.54
print(f"Space saved: {report.space_saved_bytes / 1e6:.0f} MB")  # 350 MB
print(f"Space saved: {report.space_saved_percent:.1f}%")  # 35.0%
```

---

## Sync History & Logs

Complete audit trail of all sync operations.

### Viewing History

```python
from app.core.sync import BackupTrackingDatabase

db = BackupTrackingDatabase(Path("~/.pymm/backup_tracking.db"))

# Get recent operations
history = db.get_sync_history(
    group_id="550e8400...",
    limit=50  # Last 50 operations
)

for op in history:
    print(f"Operation {op['id']}:")
    print(f"  Type: {op['operation_type']}")
    print(f"  Status: {op['status']}")
    print(f"  Start: {op['start_time']}")
    print(f"  Duration: {op['end_time'] - op['start_time']}")
    print(f"  Files: {op['files_copied']} copied, {op['files_skipped']} skipped")
    print(f"  Bytes: {op['bytes_copied']:,}")
```

### Sync History Dialog (UI)

The `SyncHistoryDialog` provides:

- **Paginated List**: 50/100/200/500/All operations
- **Operation Details**: Type, status, timestamps, file counts, bytes transferred
- **Color-Coded Status**:
  - 🟢 Green: Completed
  - 🔴 Red: Failed
  - 🟡 Yellow: Cancelled
- **Export Options**: CSV, JSON
- **Refresh**: Real-time updates

### Export Formats

#### CSV Export

```text
Operation ID,Type,Status,Files Copied,Files Skipped,Files Failed,Bytes Copied,Duration (s),Start Time,End Time
1,sync,completed,1234,567,0,4500000000,145.3,2026-01-14 10:00:00,2026-01-14 10:02:25
2,sync,completed,45,1756,0,250000000,12.8,2026-01-14 14:30:00,2026-01-14 14:30:13
```

#### JSON Export

```json
{
  "operations": [
    {
      "id": 1,
      "group_id": "550e8400-e29b-41d4-a716-446655440000",
      "operation_type": "sync",
      "status": "completed",
      "start_time": "2026-01-14T10:00:00Z",
      "end_time": "2026-01-14T10:02:25Z",
      "files_copied": 1234,
      "files_skipped": 567,
      "files_failed": 0,
      "bytes_copied": 4500000000
    }
  ],
  "export_time": "2026-01-14T15:45:00Z",
  "total_operations": 1
}
```

---

## Troubleshooting

### Common Issues

#### Issue: Sync very slow on network drives

**Cause**: Network latency and bandwidth limitations

**Solutions**:

1. Enable bandwidth throttling to prevent saturation:

   ```python
   options.enable_bandwidth_limit = True
   options.bandwidth_limit_mbps = 5.0  # 5 MB/s
   ```

2. Reduce parallel copying to avoid overwhelming network:

   ```python
   options.enable_parallel_copy = True
   options.max_parallel_files = 2  # Fewer threads
   ```

3. Enable compression to reduce network traffic:

   ```python
   options.enable_compression = True
   options.compression_type = CompressionType.LZ4  # Fast compression
   options.compression_level = 1
   ```

#### Issue: Real-time sync not detecting changes

**Cause**: Watchdog observer not started or debounce too long

**Solutions**:

1. Verify watcher is active:

   ```python
   watchers = manager.list_realtime_watchers()
   print(f"Active watchers: {len(watchers)}")
   ```

2. Reduce debounce time:

   ```python
   watch_id = manager.enable_realtime_sync(
       group_id=group_id,
       watch_path=path,
       debounce_seconds=0.3  # Shorter debounce
   )
   ```

3. Check file system permissions (Windows: Administrator, Linux: inotify limits)

#### Issue: Conflicts detected after sync

**Cause**: Files modified on both Master and Backup

**Solutions**:

1. Use conflict resolution dialog to manually review
2. Prefer Master (or Backup) for batch resolution:

   ```python
   resolutions = {path: "keep_master" for path in conflict_paths}
   storage_service.resolve_conflicts(group_id, resolutions)
   ```

3. Enable encryption to prevent direct Backup edits:

   ```python
   options.enable_encryption = True
   ```

#### Issue: Scheduled sync not running

**Cause**: Scheduler not started or schedule disabled

**Solutions**:

1. Verify scheduler is running:

   ```python
   if not manager.scheduler.running:
       manager.start()
   ```

2. Check schedule is enabled:

   ```python
   schedules = manager.list_schedules()
   for schedule in schedules:
       if not schedule.enabled:
           manager.resume_schedule(schedule.schedule_id)
   ```

3. Verify cron expression is valid:

   ```python
   # Test cron expression
   from apscheduler.triggers.cron import CronTrigger
   trigger = CronTrigger.from_crontab("0 2 * * *")
   print(f"Next run: {trigger.get_next_fire_time(None, datetime.now())}")
   ```

#### Issue: Out of disk space on Backup

**Cause**: Backup drive smaller than Master, or compression disabled

**Solutions**:

1. Enable compression:

   ```python
   options.enable_compression = True
   options.compression_type = CompressionType.GZIP
   options.compression_level = 9  # Maximum compression
   ```

2. Use selective sync (exclude large files):

   ```python
   # Implement custom file filter
   def should_sync_file(path: Path) -> bool:
       return path.stat().st_size < 100_000_000  # Skip files > 100 MB
   ```

3. Upgrade to larger Backup drive

---

## Performance Optimization

### Benchmarking

Use the `SyncStatistics` object to measure performance:

```python
result = storage_service.sync_to_backup(group_id, source_path)

duration = (result.end_time - result.start_time).total_seconds()
throughput = result.bytes_copied / duration / 1e6  # MB/s

print(f"Sync completed in {duration:.1f}s")
print(f"Throughput: {throughput:.2f} MB/s")
print(f"Files: {result.files_copied} copied, {result.files_skipped} skipped")
```

### Optimization Strategies

| Scenario | Recommended Settings |
| ---------- | ---------------------- |
| **Fast SSD to SSD** | `parallel_copy=True`, `max_parallel_files=8`, `incremental=True` |
| **HDD to HDD** | `parallel_copy=False`, `incremental=True`, `compression=False` |
| **Network (NAS)** | `bandwidth_limit=5-10 MB/s`, `parallel_copy=True (4 threads)`, `compression=True` |
| **Real-time editing** | `debounce_seconds=0.3`, `incremental=True`, `compression=False` |
| **Archival backup** | `compression=True`, `level=9`, `encryption=True`, `incremental=False` |

---

## API Reference

### FileSynchronizer

```python
class FileSynchronizer:
    def __init__(
        self,
        chunk_size: int = 8192,
        tracking_db: BackupTrackingDatabase | None = None
    )

    def sync_directory(
        self,
        source: Path,
        destination: Path,
        progress_callback: Callable[[int, int], None] | None = None,
        cancel_event: Event | None = None,
        skip_existing: bool = False,
        verify_checksums: bool = False,
        group_id: str | None = None,
        incremental: bool = True
    ) -> SyncStatistics

    def detect_conflicts(
        self,
        source: Path,
        destination: Path,
        group_id: str | None = None
    ) -> list[FileConflict]

    def calculate_checksum(self, file_path: Path) -> str
```

### BackupTrackingDatabase

```python
class BackupTrackingDatabase:
    def __init__(self, db_path: Path)

    def needs_sync(
        self,
        group_id: str,
        relative_path: str,
        checksum: str,
        mtime: datetime,
        size: int
    ) -> bool

    def update_file_record(
        self,
        group_id: str,
        relative_path: str,
        checksum: str,
        size: int,
        operation_type: str
    ) -> None

    def get_sync_history(
        self,
        group_id: str,
        limit: int = 50
    ) -> list[dict[str, Any]]

    def start_sync_operation(
        self,
        group_id: str,
        operation_type: str
    ) -> int

    def complete_sync_operation(
        self,
        operation_id: int,
        stats: SyncStatistics,
        status: str
    ) -> None
```

### ScheduledSyncManager

```python
class ScheduledSyncManager:
    def __init__(
        self,
        storage_group_service: StorageGroupService,
        notification_callback: Callable[[str, str, str], None] | None = None
    )

    def start(self) -> None
    def shutdown(self, wait: bool = True) -> None

    def add_interval_schedule(
        self,
        schedule_id: str,
        group_id: str,
        project_path: Path,
        interval_minutes: int
    ) -> SyncSchedule

    def add_cron_schedule(
        self,
        schedule_id: str,
        group_id: str,
        project_path: Path,
        cron_expression: str
    ) -> SyncSchedule

    def list_schedules(self) -> list[SyncSchedule]
    def pause_schedule(self, schedule_id: str) -> None
    def resume_schedule(self, schedule_id: str) -> None
    def remove_schedule(self, schedule_id: str) -> None
```

### RealtimeSyncManager

```python
class RealtimeSyncManager:
    def __init__(
        self,
        storage_group_service: StorageGroupService,
        notification_callback: Callable[[str, str, list[Path]], None] | None = None
    )

    def enable_realtime_sync(
        self,
        group_id: str,
        watch_path: Path,
        debounce_seconds: float = 0.5
    ) -> str

    def disable_realtime_sync(self, watch_id: str) -> None

    def is_realtime_sync_enabled(self, watch_id: str) -> bool

    def list_realtime_watchers(self) -> list[dict[str, Any]]
```

---

## Related Documentation

- [Storage Groups](storage-groups.md) - Storage group configuration and management
- [Features](features.md) - Overview of sync features in pyMediaManager
- [Architecture](architecture.md) - System architecture and design patterns
- [API Reference](api-reference.md) - Complete API documentation
- [Configuration](configuration.md) - Application and user configuration

---

**Version**: 2.0
**Status**: ✅ Fully Implemented (Phase 2 Complete)
**Last Updated**: 2026-01-14
