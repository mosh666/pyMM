# Sync Engine Examples

> **Last Updated:** 2026-01-17 21:41 UTC


This directory contains minimal standalone examples demonstrating the sync engine APIs.

## Examples

### 1. `manual_sync.py`

Performs a manual one-time sync between master and backup drives.

**Usage:**

```bash
python manual_sync.py <storage_group_id>
```

### 2. `scheduled_sync_setup.py`

Sets up scheduled sync with cron-like expressions using APScheduler.

**Usage:**

```bash
python scheduled_sync_setup.py
```

### 3. `realtime_sync_monitor.py`

Demonstrates real-time file watching with watchdog for automatic sync.

**Usage:**

```bash
python realtime_sync_monitor.py <watch_directory>
```

### 4. `sync_with_encryption.py`

Shows how to enable encryption and compression for secure backups.

**Usage:**

```bash
python sync_with_encryption.py <storage_group_id>
```

### 5. `sync_history.py`

Queries sync history and displays backup tracking metadata.

**Usage:**

```bash
python sync_history.py <storage_group_id>
```

## Requirements

These examples require the pyMediaManager environment. Run from the project root:

```bash
# Using uv
uv run python docs/examples/sync/manual_sync.py <group_id>

# Or activate virtual environment first
.venv/Scripts/activate  # Windows
source .venv/bin/activate  # Linux/macOS
python docs/examples/sync/manual_sync.py <group_id>
```

## Configuration

Examples use the configuration from `config/storage_groups.yaml` and `config/app.yaml`. Ensure:

1. Storage groups are configured
2. Master and backup drives are connected
3. Projects are assigned to storage groups

## API Documentation

For complete sync engine API reference, see:

- [docs/sync-engine.md](../../sync-engine.md)
- {ref}`sync-engine-api`

## Warning

⚠️ **Test Coverage:** The sync engine currently has 0% test coverage. Use these examples as reference
implementations, but be aware that the sync modules are under active development and may have edge cases.
Contributions to sync engine tests are highly encouraged!
