# Storage Groups

**Storage Groups** enable Master/Backup drive relationships for data redundancy in
pyMediaManager. This feature provides professional-grade failover support for media
projects stored on removable drives.

## Overview

Storage Groups pair two removable drives in a Master/Backup configuration:

- **Master Drive**: Primary storage location for active project work
- **Backup Drive**: Secondary storage for redundancy and failover

When a project is assigned to a Storage Group, pyMediaManager automatically handles
drive resolution and synchronization:

- If Master drive is connected → use Master
- If only Backup drive is connected → prompt user to use Backup
- If neither drive is connected → prevent project opening with error

**Phase 2 Status:** ✅ **Fully Implemented** - The sync engine is complete with manual, scheduled,
and real-time synchronization. See [Sync Engine Documentation](sync-engine.md) for details.

> **📚 Code Examples:** See [examples/storage/README.md](examples/storage/README.md) for working code:
>
> - [list_storage_groups.py](examples/storage/list_storage_groups.py) - List all groups
> - [create_storage_group.py](examples/storage/create_storage_group.py) - Create new group
> - [detect_drives.py](examples/storage/detect_drives.py) - Drive detection
> - [storage_group_status.py](examples/storage/storage_group_status.py) - Check status

### Quick Setup

Storage Groups can be configured in two ways:

1. **First-Run Wizard** (Recommended for new installations)
   - During initial setup, the wizard includes an optional "Storage Groups" page
   - Select Master and Backup drives from detected removable drives
   - Name your storage group (e.g., "Photo Archive 2026")
   - Skip if you prefer to configure later

2. **Storage Management View** (Anytime after setup)
   - Navigate to Storage tab in the main window
   - Click "📁 Manage Storage Groups" button
   - Create, edit, or delete storage groups as needed

## Phase 1: Current Features (v2.0)

The initial implementation focuses on **relationship tracking** without automatic
synchronization:

### ✅ Implemented Features

1. **Drive Pairing**
   - Create named Storage Groups pairing Master and Backup drives
   - Multi-strategy drive matching (serial number + label/size fallback)
   - Cross-platform compatibility (Windows, Linux, macOS)

2. **Drive Resolution**
   - Automatic Master drive detection on project open
   - User-prompted Backup drive selection when Master unavailable
   - Error blocking when both drives disconnected (prevents data loss)

3. **UI Management**
   - Storage View with Group Role column (Master/Backup badges)
   - "Manage Storage Groups" dialog for CRUD operations
   - Two-step drive selection wizard (select Master → select Backup)
   - Validation warnings (duplicate assignments, same drive, non-removable)

4. **Project Integration**
   - Optional `storage_group_id` field in Project metadata
   - Automatic drive resolution in `ProjectService.load_project()`
   - Path adjustment when using Backup drive

5. **Configuration**
   - YAML-based persistence (`config/storage_groups.yaml`)
   - In-memory caching for performance
   - Schema versioning for future migrations

### Drive Matching Strategy

Storage Groups use multi-strategy drive identification for cross-platform
compatibility:

#### Strategy 1: Serial Number (Preferred)

- **Platforms**: Windows (WMI), Linux (udev), macOS (DiskArbitration)
- **Method**: Exact serial number match
- **Reliability**: Highest (hardware-level identification)
- **Limitation**: Not always available (some drives/platforms don't expose serial)

#### Strategy 2: Label + Size (Fallback)

- **Platforms**: All (universal)
- **Method**: Volume label exact match + total size within ±5% tolerance
- **Reliability**: Good for consistent labeling
- **Limitation**: User must maintain unique, stable labels

**Example Matching Logic**:

```python
# Strategy 1: Serial number exact match
if drive1.serial_number and drive2.serial_number:
    return drive1.serial_number == drive2.serial_number

# Strategy 2: Label + Size with 5% tolerance
label_match = drive1.label.lower() == drive2.label.lower()
size_tolerance = drive2.total_size * 0.05
size_match = abs(drive1.total_size - drive2.total_size) <= size_tolerance
return label_match and size_match
```

## Usage Guide

### Creating a Storage Group

1. **Navigate to Storage View**
   - Open pyMediaManager
   - Click "Storage Management" in navigation

2. **Launch Storage Groups Dialog**
   - Click "📁 Manage Storage Groups" button
   - Storage Groups management window opens

3. **Add New Group**
   - Click "Add Group" button
   - Enter group name (e.g., "Photo Archive 2026")
   - Optional: Add description
   - Click "Select Master..." → choose primary drive from list
   - Click "Select Backup..." → choose secondary drive from list
   - Click "Save"

**Requirements**:

- Both drives must be **removable** (USB/external)
- Both drives must be **currently connected**
- Drives must have **different identities** (serial/label/size)
- Drives cannot already be assigned to another group

### Assigning Projects to Groups

**Phase 1**: Projects can be assigned via metadata editing (manual)

```json
{
  "name": "My Photo Project",
  "path": "D:/pyMM.Projects/MyPhotoProject",
  "storage_group_id": "550e8400-e29b-41d4-a716-446655440000",
  "description": "My photography project",
  "created_at": "2026-01-12T10:00:00Z"
}
```

**Phase 2**: UI integration in Project Wizard and Properties dialog (planned)

### Drive Resolution Flow

When opening a project assigned to a Storage Group:

```text
┌─────────────────────────────────────┐
│ User opens project                  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│ Check if Master drive connected?    │
└────┬────────────────────┬───────────┘
     │ YES                │ NO
     ▼                    ▼
┌─────────────┐  ┌───────────────────────────────┐
│ Use Master  │  │ Check if Backup connected?    │
└─────────────┘  └────┬──────────────────┬───────┘
                      │ YES              │ NO
                      ▼                  ▼
           ┌───────────────────┐  ┌──────────────┐
           │ Prompt user:      │  │ Show error:  │
           │ "Use Backup?" ── │  │ "No drives   │
           │ [Yes] [No]       │  │ available"   │
           └─┬─────────┬───────┘  └──────────────┘
             │ Yes     │ No
             ▼         ▼
       ┌──────────┐  ┌──────────────┐
       │ Use      │  │ Cancel open  │
       │ Backup   │  │              │
       └──────────┘  └──────────────┘
```

### Editing and Deleting Groups

**Edit Group**:

1. Select group in table
2. Click "Edit Group" or double-click row
3. Modify name, description, or drives
4. Click "Save"

**Delete Group**:

1. Select group in table
2. Click "Delete Group"
3. Confirm deletion
4. **Note**: Only removes group relationship—files are NOT deleted

### Viewing Group Status

The Storage Groups dialog shows real-time status:

| Status         | Icon | Description                      |
|----------------|------|----------------------------------|
| Both Connected | ✓    | Master and Backup both available |
| Partial        | ⚠    | Only one drive connected         |
| Disconnected   | ✗    | Neither drive connected          |

The Storage View shows drive roles:

| Badge         | Icon | Description                |
|---------------|------|----------------------------|
| Master        | 🔵   | Master drive in group      |
| Backup        | 🟢   | Backup drive in group      |
| Unassigned    | —    | Not part of any group      |

**Tooltip Information**: Hover over Group Role column to see:

- Group name
- Paired drive details
- Connection status

## Configuration

### YAML Structure

Storage Groups are stored in `config/storage_groups.yaml`:

```yaml
version: 1
groups:
  - id: "550e8400-e29b-41d4-a716-446655440000"
    name: "Photo Archive 2026"
    created: "2026-01-12T10:00:00"
    modified: "2026-01-12T10:00:00"
    description: "Primary storage for photo projects"
    master_drive:
      serial_number: "1234567890ABC"
      label: "PhotoMaster"
      total_size: 2000000000000
    backup_drive:
      serial_number: "9876543210XYZ"
      label: "PhotoBackup"
      total_size: 2000000000000
```

**Fields**:

- `version`: Schema version (for migrations)
- `id`: UUID v4 identifier (auto-generated)
- `name`: User-friendly group name
- `created`/`modified`: ISO 8601 timestamps
- `description`: Optional notes
- `master_drive`/`backup_drive`:
  - `serial_number`: Hardware serial (may be null)
  - `label`: Volume label (required)
  - `total_size`: Capacity in bytes (required)

### Application Configuration

In `config/app.yaml`:

```yaml
paths:
  storage_groups_file: storage_groups.yaml
```

The file is loaded relative to the config directory.

## API Reference

### Service Layer

**StorageGroupService** (`app.core.services.storage_group_service`):

```python
# Initialize service
from app.core.services.storage_group_service import StorageGroupService
from app.core.services.storage_service import StorageService
from pathlib import Path

storage_service = StorageService()
config_path = Path("config/storage_groups.yaml")
group_service = StorageGroupService(config_path, storage_service)

# CRUD Operations
group = group_service.create_group(
    name="My Group",
    master_drive=DriveIdentity(...),
    backup_drive=DriveIdentity(...),
    description="Optional"
)

groups = group_service.list_groups()
group = group_service.get_group(group_id)
group_service.update_group(group_id, name="New Name")
group_service.delete_group(group_id)

# Drive Resolution
path = group_service.resolve_drive(group_id, project_name, parent_widget)
# Returns: Path to Master/Backup, or None if unavailable/cancelled

backup_path = group_service.get_backup_path(group_id)
# Returns: Path to Backup if connected, None otherwise

# Drive Role Detection
role_info = group_service.get_drive_role(drive_info)
# Returns: (DriveGroup, DriveRole) or None
```

### Data Models

**DriveGroup** (`app.models.storage_group`):

```python
from app.models.storage_group import DriveGroup, DriveIdentity, DriveRole

# DriveIdentity
identity = DriveIdentity(
    serial_number="ABC123",  # May be None
    label="MyDrive",
    total_size=2000000000000
)

# Check if two identities match
if identity1.matches(identity2):
    print("Same drive!")

# DriveGroup
group = DriveGroup(
    name="My Group",
    master_drive=master_identity,
    backup_drive=backup_identity,
    description="Optional description"
)

# Get drive by role
master = group.get_drive_by_role(DriveRole.MASTER)
backup = group.get_drive_by_role(DriveRole.BACKUP)
```

### Project Integration

**Project Model** (`app.models.project`):

```python
from app.models.project import Project

project = Project(
    name="My Project",
    path=Path("D:/pyMM.Projects/MyProject"),
    storage_group_id="550e8400-e29b-41d4-a716-446655440000"  # Optional
)

# Check if project has storage group
if project.storage_group_id:
    print("Project uses storage group redundancy")
```

**ProjectService** (`app.services.project_service`):

```python
from app.services.project_service import ProjectService

# Initialize with storage group support
project_service = ProjectService(
    projects_dir=Path("D:/pyMM.Projects"),
    storage_group_service=storage_group_service
)

# Load project (automatic drive resolution)
try:
    project = project_service.load_project(project_path, parent_widget)
    # Project path automatically adjusted to available drive
except RuntimeError as e:
    print(f"Cannot open project: {e}")
```

## Phase 2: Implemented Features

The following features are **fully implemented and available** in the current release:

### 1. Sync Functionality ✅ **Implemented**

**Manual Trigger** ✅ **Implemented**:

- UI button: "Sync to Backup" in project context menu
- Progress dialog with file transfer status
- Conflict detection and resolution prompts

**Scheduled Sync** ✅ **Implemented**:

- APScheduler-based scheduling (interval + cron triggers)
- Interval presets (every 15/30/60 minutes)
- Cron presets (daily at 2 AM, weekly on Monday, etc.)
- Custom cron expression support
- Per-project schedule configuration in Project Properties
- Background execution with notification callbacks
- Pause/resume capability
- Sync history logs via SQLite tracking

**Real-Time Sync** ✅ **Implemented**:

- File system watcher on Master drive (watchdog library)
- Automatic file replication to Backup on detection
- Configurable debouncing (default 500ms, adjustable)
- Event batching for rapid changes (create/modify/delete/move)
- Sync loop prevention with _sync_in_progress flag
- Background event processor thread
- Per-project real-time sync toggle in Project Properties
- Visual status indicator ("⚡ Real-Time Sync: Active" in green)
- Lifecycle management (start/stop/status watchers)

**API**:

```python
# ✅ Fully Implemented and Available
group_service.sync_to_backup(group_id, source_path, progress_callback)
group_service.restore_from_backup(group_id, target_path, progress_callback)
group_service.detect_conflicts(group_id, path)
group_service.verify_sync_status(group_id, path)
group_service.resolve_conflicts(group_id, resolutions)
group_service.get_sync_history(group_id, limit=50)
group_service.enable_realtime_sync(group_id, watch_path, debounce_seconds, notification_callback)
group_service.disable_realtime_sync(watch_id)
group_service.is_realtime_sync_enabled(watch_id)
group_service.list_realtime_watchers()
```

### 2. Conflict Resolution UI ✅ **Implemented**

**Features**:

- Visual diff viewer for conflicting files
- User choices:
  - Keep Master version
  - Keep Backup version
  - Keep both (rename with suffix)
  - Manual merge
- Batch conflict resolution
- Skip/abort options

**Use Cases**:

- Files modified on both drives while disconnected
- User edited Backup files directly
- Sync interrupted mid-operation

### 3. Incremental Backup Support ✅ **Implemented**

**Features**:

- Delta sync (only changed files)
- SQLite change tracking database with schema versioning
- Timestamp + size + checksum comparison (SHA-256)
- `needs_sync()` optimization for skip_unchanged logic
- Bandwidth/speed optimization via selective copying
- Comprehensive sync operation logging

**Benefits**:

- Faster sync operations (skips unchanged files)
- Reduced disk I/O and bandwidth usage
- Lower power consumption (portable scenarios)
- Detailed audit trail for compliance

**Implementation**:

- `BackupTrackingDatabase` class manages SQLite database
- Tracks: operation history, file states, checksums, sync timestamps
- Schema migration support for future updates
- File-level tracking with relative paths and metadata

### 4. Project Settings UI ✅ **Implemented**

**Features**:

- Project Properties dialog with Storage tab
- Dropdown to assign/change Storage Group
- "Create Group from Project" quick action
- Real-time drive status indicators (Master/Backup connectivity)
- Manual sync buttons (Sync to Backup / Restore from Backup)
- Conflict detection and resolution integration
- Scheduled sync configuration
- Real-time sync toggle with status display
- View Sync History button for audit logs

**Workflow**:

1. Right-click project → Properties
2. Navigate to "Storage" tab
3. Select Storage Group from dropdown
4. Configure sync options (scheduled, real-time)
5. Click "Apply"

### 5. Sync History & Logs UI ✅ **Implemented**

**Features**:

- `SyncHistoryDialog` with paginated operation list (50/100/200/500/All)
- Displays: operation ID, type, status, files copied, bytes, duration, timestamp
- Color-coded status indicators (green=completed, red=failed, yellow=cancelled)
- Detail panel with operation metadata and file lists
- Export to CSV for spreadsheet analysis
- Export to JSON for programmatic processing
- Refresh functionality for real-time monitoring

**Use Cases**:

- Audit trail for compliance
- Troubleshooting sync failures
- Performance analysis (speed, file counts)
- Verifying backup completeness

### 6. Advanced Sync Features ✅ **Implemented**

**Configuration UI**:

- `AdvancedSyncOptionsDialog` in Project Properties
- Per-project advanced sync configuration
- Persistent settings in project metadata

**Bandwidth Throttling** ✅ **Implemented**:

**Use Case**: Large video projects with separated storage:

- **Footage Group**: Raw footage on Group A (Master: 8TB, Backup: 8TB)
- **Renders Group**: Rendered outputs on Group B (Master: 4TB, Backup: 4TB)
- **Assets Group**: Graphics/audio on Group C (Master: 2TB, Backup: 2TB)

**Configuration**:

```yaml
# In project metadata
storage_groups:
  - role: "footage"
    group_id: "group-a-id"
    subpath: "footage"
  - role: "renders"
    group_id: "group-b-id"
    subpath: "renders"
  - role: "assets"
    group_id: "group-c-id"
    subpath: "assets"
```

**Benefits**:

- Optimize storage allocation by media type
- Independent backup strategies per content type
- Cost savings (smaller backups for low-priority content)

### 7. Advanced Features ✅ **Completed**

**Configuration UI**:

- `AdvancedSyncOptionsDialog` in Project Properties
- Per-project advanced sync configuration
- Persistent settings in project metadata

**Bandwidth Throttling** ✅ **Implemented**:

- Token bucket algorithm for rate limiting
- Configurable MB/s limit (0.1 - 1000 MB/s)
- Preserves system performance during large syncs
- Smooth burst handling for small files
- Real-time throttling without blocking UI

**Encryption** ✅ **Implemented**:

- AES-256-GCM encryption for backup files
- Password-based key derivation (PBKDF2, 100k iterations)
- Optional key file support for automated workflows
- 96-bit nonce + 16-byte salt per file
- Authentication tag for integrity verification
- Warning: requires password/key for restoration

**Compression** ✅ **Implemented**:

- GZIP compression (standard, wide compatibility)
- LZ4 compression (fast, lower ratio)
- Configurable compression levels (1-9 for GZIP)
- Automatic fallback (LZ4 → GZIP if library unavailable)
- Space savings calculation and reporting

**Parallel Copying** ✅ **Implemented**:

- ThreadPoolExecutor for concurrent file transfers
- Configurable parallelism (2-16 files simultaneously)
- Optimal for small files on SSDs
- May reduce performance on HDDs (user configurable)

**Space Savings Reporting** ✅ **Implemented**:

- `SpaceSavingsReport` class with metrics
- Original vs compressed size tracking
- Compression ratio calculation
- Space saved percentage
- Files processed counter

**Implementation Classes**:

- `AdvancedSyncOptions`: Configuration data class with serialization
- `BandwidthThrottler`: Token bucket rate limiter
- `CryptoHelper`: AES-256-GCM encryption/decryption
- `CompressionHelper`: GZIP/LZ4 compression utilities
- `SpaceSavingsReport`: Space savings metrics

## Phase 3: Future Enhancements (Roadmap)

The following features are planned for future releases:

### 1. Multi-Group Support per Project ⏳ **Planned**

**Use Case**: Large video projects with separated storage:

- **Footage Group**: Raw footage on Group A (Master: 8TB, Backup: 8TB)
- **Renders Group**: Rendered outputs on Group B (Master: 4TB, Backup: 4TB)
- **Assets Group**: Graphics/audio on Group C (Master: 2TB, Backup: 2TB)

**Configuration**:

```yaml
# In project metadata
storage_groups:
  - role: "footage"
    group_id: "group-a-id"
    subpath: "footage"
  - role: "renders"
    group_id: "group-b-id"
    subpath: "renders"
  - role: "assets"
    group_id: "group-c-id"
    subpath: "assets"
```

**Benefits**:

- Optimize storage allocation by media type
- Independent backup strategies per content type
- Cost savings (smaller backups for low-priority content)

## Best Practices

**Recommendation**: Use consistent, descriptive labels

✅ **Good**:

- `PhotoMaster` / `PhotoBackup`
- `Video2026-M` / `Video2026-B`
- `ProjectArchive-A` / `ProjectArchive-B`

❌ **Bad**:

- `MyDrive` / `MyDrive` (ambiguous)
- `USB` / `USB Drive` (generic)
- `D:` / `E:` (confusing with drive letters)

### 2. Drive Size Matching

**Recommendation**: Use identical or larger Backup drives

- **Ideal**: Master 2TB → Backup 2TB (perfect match)
- **Good**: Master 2TB → Backup 4TB (backup has extra space)
- **Risky**: Master 4TB → Backup 2TB (backup may fill up)

### 3. Connection Discipline

**Recommendation**: Connect drives consistently

- Always connect Master drive first (primary workflow)
- Only connect Backup when Master unavailable or for sync
- Avoid simultaneous Master + Backup connections (prevents accidental direct edits to Backup)

### 4. Backup Verification

**Recommendation**: Periodically verify backups

- Test opening projects from Backup drive
- Verify file integrity with checksums
- Keep backup drives in separate physical locations (fire/theft protection)

### 5. Group Naming

**Recommendation**: Use descriptive, dated names

✅ **Good**:

- `Client-XYZ-2026`
- `Wedding-Photography-Archive`
- `Quarterly-Video-Projects-Q1-2026`

❌ **Bad**:

- `Group 1`
- `Test`
- `Backup`

## Troubleshooting

### Issue: "Drive already assigned to another group"

**Cause**: Drive is already Master or Backup in another group

**Solution**:

1. Navigate to Storage Groups dialog
2. Find existing group using this drive
3. Either:
   - Edit existing group to change drives
   - Delete existing group (if no longer needed)
4. Retry creating new group

### Issue: "Master and Backup cannot be the same drive"

**Cause**: Selected the same physical drive twice

**Solution**:

- Ensure Master and Backup are different physical devices
- Check serial numbers or labels to verify
- If serial numbers unavailable, ensure labels are different

### Issue: "No drives available" when opening project

**Cause**: Neither Master nor Backup drive connected

**Solution**:

1. Connect Master drive (preferred)
2. Or connect Backup drive
3. Retry opening project

**Prevention**: Always keep at least one drive accessible

### Issue: Drive not detected after reconnection

**Cause**: Drive identity changed (reformatted, relabeled, or different partition)

**Solution**:

1. Check drive label matches group configuration
2. Verify drive size hasn't significantly changed
3. If reformatted: Edit group to update drive identity
4. Use "Refresh" button in Storage View to re-detect

### Issue: Project path incorrect after using Backup

**Cause**: Project path not properly resolved

**Workaround**:

1. Close project
2. Reconnect Master drive
3. Reopen project from Master

**Report**: This may indicate a bug—please report with logs

## Security Considerations

### Data Integrity

**Phase 1**:

- No automatic sync = no risk of accidental overwrites
- User controls all file operations
- Groups only track relationships (metadata-only)

**Phase 2** (planned sync):

- Checksums verify integrity
- Conflict detection prevents data loss
- Sync logs provide audit trail

### Access Control

- Storage Group configuration stored in `config/storage_groups.yaml`
- File permissions follow OS-level access control
- No built-in encryption (use OS-level encryption like BitLocker/LUKS)

### Backup Security

**Recommendations**:

- Store Backup drives in separate physical locations
- Use drive encryption (BitLocker, FileVault, LUKS)
- Restrict physical access to backup storage
- Regularly test backup integrity

## Performance

### Caching

**Implementation**: In-memory cache of storage groups

- Groups loaded once on service initialization
- Cache invalidated on CRUD operations
- Manual refresh available via `refresh()` method

**Benefits**:

- Fast group lookups (no disk I/O)
- Reduced YAML parsing overhead
- Responsive UI interactions

### Scalability

**Tested Limits**:

- ✅ 50 groups: No noticeable performance impact
- ✅ 100 groups: < 10ms load time
- ⚠️ 500+ groups: Consider optimization

**Recommendation**: Keep groups under 100 for optimal performance

## Migration Notes

### Upgrading from Pre-Storage-Groups Versions

**Scenario**: Existing projects without `storage_group_id`

**Impact**: No action required

- Projects without `storage_group_id` continue working normally
- No breaking changes to existing projects
- Storage Groups are opt-in

**Adoption**:

1. Create Storage Groups via UI
2. Manually assign projects (edit metadata or use Phase 2 UI)
3. Test with non-critical projects first

### Schema Version Migration

**Current Version**: 1

Future schema changes will include migration logic:

```python
# Example future migration
if config.version == 1:
    # Migrate v1 → v2
    config = migrate_v1_to_v2(config)
    config.version = 2
```

**User Action**: None required (automatic)

## FAQ

**Q: Can I use fixed (internal) drives for Storage Groups?**
A: No, both drives must be removable. This ensures portability and intentional redundancy.

**Q: What happens if I rename a drive?**
A: If serial number matching works, group continues functioning. Otherwise, edit the group to update drive identity.

**Q: Can I have multiple Master drives or multiple Backup drives?**
A: Phase 1 and 2 support 1:1 pairing only. Multi-drive support planned for Phase 3.

**Q: Will Storage Groups sync files automatically?**
A: Yes! Phase 2 sync functionality is fully implemented with manual, scheduled, and real-time sync options.

**Q: Can I use Storage Groups for non-portable projects?**
A: No, groups require removable drives. Fixed drives use standard project paths.

**Q: What if my drive doesn't have a serial number?**
A: Fallback matching uses label + size (±5% tolerance). Ensure unique, stable labels.

**Q: Are Storage Groups required?**
A: No, they're optional. Projects without `storage_group_id` work normally.

**Q: Can I delete a Storage Group if projects are using it?**
A: Yes, but those projects will fail to open until Master drive is connected (group assignment prevents opening).

## Contributing

To extend Storage Groups functionality:

1. **Data Models**: `app.models.storage_group`
2. **Service Layer**: `app.core.services.storage_group_service`
3. **Sync Engine**: `app.core.sync` - 9 fully implemented modules
4. **UI Dialogs**: `app.ui.dialogs.storage_group_dialog`
5. **Storage View**: `app.ui.views.storage_view`

**Phase 3 Enhancement Opportunities**:

- Multi-group support per project
- Cloud storage integration
- Network drive synchronization
- Advanced conflict resolution algorithms

## Related Documentation

- [Getting Started](getting-started.md) - General application usage
- [Features](features.md) - Advanced features and project management
- [Sync Engine](sync-engine.md) - Comprehensive synchronization documentation
- [Architecture](architecture.md) - System design overview
- [API Reference](api-reference.md) - Complete API documentation
- [Plugin Development](plugin-development.md) - Extending pyMediaManager

---

**Version**: 2.0
**Status**: Phase 1 & 2 Complete (Tracking + Sync), Phase 3 Planned
> **Last Updated:** 2026-01-17 21:41 UTC
