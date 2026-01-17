# Testing Roadmap

> **Last Updated:** 2026-01-17 21:41 UTC


**Comprehensive Test Coverage Plan** for pyMediaManager to achieve production-grade quality across all modules, with special emphasis on the sync engine and GUI components.

---

## 📊 Executive Summary

### Current State

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Total Tests** | 193 | 250+ | +57 tests |
| **Overall Coverage** | 73% | 80% | +7% |
| **Sync Engine Coverage** | 0% | 60% | +60% |
| **GUI Test Proportion** | 26% (50/193) | 40% (100/250) | +50 tests |
| **Integration Tests** | 5% (10/193) | 10% (25/250) | +15 tests |

### Critical Gaps

1. **🔴 Sync Engine (9 modules)** - 0% coverage, fully implemented but untested
2. **🟡 GUI Components** - 50 tests exist but need expansion for sync UI, settings, conflict resolution
3. **🟡 Integration Workflows** - End-to-end scenarios need more coverage
4. **🟢 Core Services** - 95+ tests with good coverage, maintain quality

---

## 🎯 Priority Tiers

### P0: Sync Engine Test Coverage (Critical)

**Goal:** Achieve **60% coverage** for all sync modules

**Impact:** HIGH - Sync engine is fully implemented and in production use, but has zero test coverage. This is the highest-priority testing gap.

**Timeline:** Q1 2026 (Next 3 months)

**Effort:** ~40 hours (8 hours per major module)

#### Modules Requiring Tests

| Module | Lines | Classes | Target Coverage | Estimated Tests |
|--------|-------|---------|----------------|-----------------|
| `file_synchronizer.py` | 431 | `FileSynchronizer`, `FileConflict`, `SyncStatistics` | 60% | 15 tests |
| `backup_tracking.py` | ~300 | `BackupTrackingDatabase` | 65% | 12 tests |
| `scheduled_sync.py` | ~250 | `ScheduledSyncManager`, `SyncSchedule` | 55% | 10 tests |
| `realtime_sync.py` | ~280 | `RealtimeSyncManager`, `RealtimeSyncHandler` | 60% | 12 tests |
| `notifications.py` | ~150 | `NotificationManager` | 70% | 8 tests |
| `crypto_compression.py` | ~320 | `CryptoHelper`, `CompressionHelper` | 65% | 10 tests |
| `bandwidth_throttler.py` | ~180 | `BandwidthThrottler` | 60% | 8 tests |
| `advanced_sync_options.py` | ~200 | `AdvancedSyncOptions`, `SpaceSavingsReport` | 70% | 7 tests |
| `__init__.py` | ~50 | (exports only) | 80% | 3 tests |
| **TOTAL** | ~2,161 | - | **60%** | **85 tests** |

#### Priority Order

1. **file_synchronizer.py** (HIGHEST) - Core sync logic used by all other modules
2. **backup_tracking.py** - SQLite database operations, critical for incremental backups
3. **scheduled_sync.py** - APScheduler integration, user-facing feature
4. **realtime_sync.py** - Watchdog integration, complex async operations
5. **crypto_compression.py** - Security-critical functionality
6. **notifications.py** - User experience, error reporting
7. **bandwidth_throttler.py** - Performance optimization
8. **advanced_sync_options.py** - Configuration validation

#### Test Categories for Sync Modules

Each module should include tests for:

- **Unit Tests** - Individual method behavior
- **Integration Tests** - Interaction with file system, databases
- **Error Handling** - Exception paths, edge cases
- **Performance Tests** - Large file handling, throttling validation
- **Concurrent Operations** - Thread safety, async behavior

#### Example Test Structure

```python
# tests/unit/sync/test_file_synchronizer.py
import pytest
from pathlib import Path
from app.core.sync.file_synchronizer import FileSynchronizer, SyncStatistics

class TestFileSynchronizer:
    """Test suite for FileSynchronizer."""

    @pytest.fixture
    def sync_manager(self, tmp_path):
        """Create FileSynchronizer with temporary directories."""
        master = tmp_path / "master"
        backup = tmp_path / "backup"
        master.mkdir()
        backup.mkdir()
        return FileSynchronizer(master, backup)

    def test_sync_empty_directories(self, sync_manager):
        """Test syncing empty directories returns no operations."""
        stats = sync_manager.sync_directory()
        assert stats.files_copied == 0
        assert stats.files_skipped == 0

    def test_sync_new_files(self, sync_manager, tmp_path):
        """Test syncing new files from master to backup."""
        # Create test file in master
        test_file = tmp_path / "master" / "test.txt"
        test_file.write_text("content")

        stats = sync_manager.sync_directory()
        assert stats.files_copied == 1
        assert (tmp_path / "backup" / "test.txt").exists()

    # Add 13+ more tests...
```

**Reference Implementation:** See [docs/examples/sync/README.md](examples/sync/README.md) for working code examples demonstrating sync APIs.

---

### P1: GUI Test Expansion (High Priority)

**Goal:** Expand GUI tests from **26% to 40%** of total test suite (50 → 100 tests)

**Impact:** MEDIUM-HIGH - GUI is user-facing, needs comprehensive coverage for sync dialogs, settings, conflict resolution

**Timeline:** Q2 2026

**Effort:** ~30 hours

#### Current GUI Test Distribution

| Test File | Current Tests | Target Tests | Focus Areas |
|-----------|---------------|--------------|-------------|
| `test_first_run_wizard.py` | 12 | 15 | Add wizard navigation, validation edge cases |
| `test_project_dialogs.py` | 25 | 30 | Add project template selection, error handling |
| `test_views.py` | 13 | 20 | Add filter/search, context menus, refresh |
| `test_migration_ui.py` | 0 | 5 | NEW - Test plugin migration UI |
| `test_tool_version_dialog.py` | 0 | 5 | NEW - Test tool version detection display |
| **NEW** `test_sync_dialogs.py` | 0 | 15 | NEW - Sync progress, conflict resolution, scheduling |
| **NEW** `test_settings_dialogs.py` | 0 | 10 | NEW - Preferences, plugin config, storage groups |
| **TOTAL** | 50 | 100 | +50 tests |

#### New Test Files Needed

##### 1. test_sync_dialogs.py (15 tests)

Test sync-related UI components:

- Sync progress dialog (5 tests)
  - Progress bar updates
  - Cancel operation
  - Speed calculation display
  - Error message display
  - Completion notification
- Conflict resolution dialog (7 tests)
  - Conflict list display
  - Resolution option selection (keep master, keep backup, skip)
  - Batch resolution actions
  - Preview file differences
  - Apply resolution and sync
- Sync schedule dialog (3 tests)
  - Schedule creation/editing
  - Cron expression validation
  - Schedule list management

##### 2. test_settings_dialogs.py (10 tests)

Test settings and preferences UI:

- General preferences (3 tests)
  - Theme selection
  - Language selection
  - Auto-update toggles
- Plugin preferences (3 tests)
  - Plugin enable/disable
  - Plugin version selection
  - Plugin configuration editing
- Storage group preferences (4 tests)
  - Master/backup pairing
  - Sync options configuration
  - udev rules installation UI

#### GUI Testing Best Practices

- Use `pytest-qt` fixtures (`qtbot`) for all GUI tests
- Mock long-running operations (file sync, network requests)
- Test keyboard shortcuts and accessibility
- Verify proper cleanup of dialog windows
- Test responsive behavior with different window sizes

---

### P2: Integration Test Expansion (Medium Priority)

**Goal:** Expand integration tests from **5% to 10%** of suite (10 → 25 tests)

**Impact:** MEDIUM - End-to-end workflows ensure components work together

**Timeline:** Q3 2026

**Effort:** ~15 hours

#### New Integration Test Areas

1. **End-to-End Sync Workflows** (8 tests)
   - Create project → Configure storage group → Manual sync → Verify backup
   - Create project → Schedule sync → Trigger schedule → Verify backup
   - Create project → Enable real-time sync → Modify files → Verify auto-sync
   - Multi-project sync with different schedules
   - Sync with encryption enabled
   - Sync with compression enabled
   - Sync with bandwidth throttling
   - Conflict detection and resolution workflow

2. **Plugin Integration Workflows** (5 tests)
   - Download plugin → Install → Detect in project → Uninstall
   - Multi-plugin project with dependencies
   - Plugin update workflow
   - Plugin preference persistence
   - Plugin tool version detection

3. **Storage Group Workflows** (7 tests)
   - Create storage group → Pair drives → Sync → Verify tracking database
   - Storage group with multiple projects
   - Master drive disconnection handling
   - Backup drive disconnection handling
   - Drive swap detection and warning
   - Space availability checks
   - Incremental backup validation

---

## 📋 Module-by-Module Test Requirements

### Sync Engine Modules

#### 1. file_synchronizer.py

**Classes to Test:**
- `FileSynchronizer` - Core sync logic
- `FileConflict` - Conflict representation
- `SyncStatistics` - Sync result tracking

**Required Test Coverage:**

```python
# Core functionality (8 tests)
- test_sync_empty_directories()
- test_sync_new_files()
- test_sync_modified_files()
- test_sync_deleted_files()
- test_sync_with_subdirectories()
- test_sync_large_files()
- test_sync_preserves_timestamps()
- test_sync_preserves_permissions()

# Conflict detection (4 tests)
- test_detect_conflict_modified_both()
- test_detect_conflict_deleted_master()
- test_detect_conflict_deleted_backup()
- test_detect_conflict_size_mismatch()

# Error handling (3 tests)
- test_sync_handles_permission_error()
- test_sync_handles_disk_full()
- test_sync_handles_invalid_paths()
```

**Reference:** [docs/examples/sync/manual_sync_example.py](examples/sync/manual_sync_example.py)

---

#### 2. backup_tracking.py

**Classes to Test:**
- `BackupTrackingDatabase` - SQLite change tracking

**Required Test Coverage:**

```python
# Database operations (5 tests)
- test_create_database()
- test_record_file_sync()
- test_get_last_sync_time()
- test_get_file_checksum()
- test_get_sync_history()

# Change detection (4 tests)
- test_detect_new_files()
- test_detect_modified_files()
- test_detect_deleted_files()
- test_incremental_backup_logic()

# Database integrity (3 tests)
- test_database_migration()
- test_concurrent_access()
- test_corrupted_database_recovery()
```

**Reference:** [docs/examples/sync/backup_tracking_example.py](examples/sync/backup_tracking_example.py)

---

#### 3. scheduled_sync.py

**Classes to Test:**
- `ScheduledSyncManager` - APScheduler integration
- `SyncSchedule` - Schedule configuration

**Required Test Coverage:**

```python
# Schedule management (4 tests)
- test_add_schedule()
- test_remove_schedule()
- test_update_schedule()
- test_list_schedules()

# Cron expression validation (3 tests)
- test_parse_cron_expression()
- test_invalid_cron_expression()
- test_cron_next_run_time()

# Execution (3 tests)
- test_schedule_triggers_sync()
- test_schedule_respects_timezone()
- test_schedule_handles_errors()
```

**Reference:** [docs/examples/sync/scheduled_sync_example.py](examples/sync/scheduled_sync_example.py)

---

#### 4. realtime_sync.py

**Classes to Test:**
- `RealtimeSyncManager` - Watchdog manager
- `RealtimeSyncHandler` - File system event handler

**Required Test Coverage:**

```python
# File system monitoring (5 tests)
- test_start_monitoring()
- test_stop_monitoring()
- test_detect_file_created()
- test_detect_file_modified()
- test_detect_file_deleted()

# Event handling (4 tests)
- test_debouncing_rapid_changes()
- test_ignore_backup_directory_events()
- test_handle_directory_events()
- test_filter_excluded_patterns()

# Error handling (3 tests)
- test_handle_sync_error()
- test_handle_observer_error()
- test_restart_after_crash()
```

**Reference:** [docs/examples/sync/realtime_sync_example.py](examples/sync/realtime_sync_example.py)

---

#### 5. notifications.py

**Classes to Test:**
- `NotificationManager` - Progress and status callbacks

**Required Test Coverage:**

```python
# Progress tracking (4 tests)
- test_report_progress()
- test_progress_percentage_calculation()
- test_progress_speed_calculation()
- test_progress_eta_calculation()

# Notifications (4 tests)
- test_notify_sync_started()
- test_notify_sync_completed()
- test_notify_sync_failed()
- test_notify_conflict_detected()
```

**Reference:** [docs/examples/sync/notifications_example.py](examples/sync/notifications_example.py)

---

#### 6. crypto_compression.py

**Classes to Test:**
- `CryptoHelper` - AES-256-GCM encryption
- `CompressionHelper` - GZIP/LZ4 compression

**Required Test Coverage:**

```python
# Encryption (5 tests)
- test_encrypt_decrypt_roundtrip()
- test_encrypt_with_password()
- test_decrypt_with_wrong_password()
- test_encrypt_large_file()
- test_key_derivation()

# Compression (5 tests)
- test_compress_decompress_roundtrip()
- test_gzip_compression()
- test_lz4_compression()
- test_compress_already_compressed()
- test_compression_ratio_calculation()
```

**Reference:** [docs/examples/sync/crypto_compression_example.py](examples/sync/crypto_compression_example.py)

---

#### 7. bandwidth_throttler.py

**Classes to Test:**
- `BandwidthThrottler` - Token bucket rate limiting

**Required Test Coverage:**

```python
# Rate limiting (4 tests)
- test_throttle_respects_limit()
- test_burst_allowance()
- test_token_refill_rate()
- test_throttle_calculation_accuracy()

# Configuration (2 tests)
- test_set_bandwidth_limit()
- test_disable_throttling()

# Performance (2 tests)
- test_throttle_large_transfer()
- test_throttle_multiple_files()
```

**Reference:** [docs/examples/sync/bandwidth_throttling_example.py](examples/sync/bandwidth_throttling_example.py)

---

#### 8. advanced_sync_options.py

**Classes to Test:**
- `AdvancedSyncOptions` - Configuration dataclass
- `SpaceSavingsReport` - Compression/encryption metrics

**Required Test Coverage:**

```python
# Configuration (4 tests)
- test_default_options()
- test_validate_options()
- test_invalid_options_raise_error()
- test_serialize_deserialize()

# Space savings (3 tests)
- test_calculate_space_savings()
- test_compression_ratio()
- test_encryption_overhead()
```

**Reference:** [docs/examples/sync/advanced_options_example.py](examples/sync/advanced_options_example.py)

---

## 🛠️ Contribution Guidelines

### Getting Started with Sync Engine Testing

1. **Review Existing Examples**
   - Browse [docs/examples/sync/](examples/sync/) for working implementations
   - Each example demonstrates real usage patterns
   - Adapt examples into test fixtures and assertions

2. **Set Up Test Environment**
   ```bash
   # Clone repository
   git clone https://github.com/mosh666/pyMM.git
   cd pyMM

   # Install dependencies with UV
   uv sync --all-extras

   # Run existing tests to verify setup
   pytest tests/unit/ -v
   ```

3. **Create Test File Structure**
   ```bash
   # Create new test directory for sync modules
   mkdir -p tests/unit/sync
   touch tests/unit/sync/__init__.py
   touch tests/unit/sync/test_file_synchronizer.py
   ```

4. **Write Your First Test**
   ```python
   # tests/unit/sync/test_file_synchronizer.py
   import pytest
   from pathlib import Path
   from app.core.sync.file_synchronizer import FileSynchronizer

   class TestFileSynchronizer:
       @pytest.fixture
       def sync_dirs(self, tmp_path):
           """Create temporary master and backup directories."""
           master = tmp_path / "master"
           backup = tmp_path / "backup"
           master.mkdir()
           backup.mkdir()
           return {"master": master, "backup": backup}

       @pytest.fixture
       def synchronizer(self, sync_dirs):
           """Create FileSynchronizer instance."""
           return FileSynchronizer(
               master_dir=sync_dirs["master"],
               backup_dir=sync_dirs["backup"]
           )

       def test_sync_empty_directories(self, synchronizer):
           """Test syncing empty directories."""
           stats = synchronizer.sync_directory()
           assert stats.files_copied == 0
           assert stats.files_skipped == 0
           assert stats.files_failed == 0
   ```

5. **Run Your Tests**
   ```bash
   # Run single test file
   pytest tests/unit/sync/test_file_synchronizer.py -v

   # Run with coverage
   pytest tests/unit/sync/test_file_synchronizer.py --cov=app.core.sync.file_synchronizer

   # Run all sync tests
   pytest tests/unit/sync/ -v
   ```

### Testing Best Practices

#### General Guidelines

- **One concept per test** - Each test should verify one behavior
- **Arrange-Act-Assert pattern** - Set up, execute, verify
- **Descriptive names** - Test name should describe what's being tested
- **Use fixtures** - Share setup code with pytest fixtures
- **Mock external dependencies** - File systems, networks, databases (use `tmp_path`, `pytest-mock`)
- **Test error paths** - Don't just test happy paths
- **Keep tests fast** - Use small files, mock slow operations

#### Sync-Specific Guidelines

- **Use tmp_path fixture** - All file operations should use pytest's `tmp_path`
- **Clean up resources** - Close file handles, stop threads, disconnect databases
- **Test with real files** - Don't mock Path objects, use actual temporary files
- **Verify checksums** - Ensure file integrity after sync operations
- **Test concurrent access** - Sync engine may have multiple threads
- **Mock time-dependent operations** - Use `freezegun` or `pytest-mock` for time-based tests

#### Example: Comprehensive Sync Test

```python
import pytest
from pathlib import Path
from datetime import datetime
from app.core.sync.file_synchronizer import FileSynchronizer, FileConflict

class TestFileSynchronizerConflicts:
    """Test conflict detection in FileSynchronizer."""

    @pytest.fixture
    def sync_setup(self, tmp_path):
        """Create master/backup dirs with FileSynchronizer."""
        master = tmp_path / "master"
        backup = tmp_path / "backup"
        master.mkdir()
        backup.mkdir()

        synchronizer = FileSynchronizer(master, backup)

        return {
            "master": master,
            "backup": backup,
            "sync": synchronizer
        }

    def test_detect_modified_both_conflict(self, sync_setup):
        """Test conflict when file modified in both master and backup."""
        # Arrange - Create file in both locations with different content
        master_file = sync_setup["master"] / "test.txt"
        backup_file = sync_setup["backup"] / "test.txt"

        master_file.write_text("master content")
        backup_file.write_text("backup content")

        # Simulate different modification times
        import time
        time.sleep(0.1)
        master_file.touch()  # Make master newer

        # Act - Run sync (with dry-run to detect conflicts)
        conflicts = sync_setup["sync"].detect_conflicts()

        # Assert - Should detect modified_both conflict
        assert len(conflicts) == 1
        conflict = conflicts[0]
        assert conflict.conflict_type == "modified_both"
        assert conflict.relative_path == "test.txt"
        assert conflict.master_mtime is not None
        assert conflict.backup_mtime is not None
        assert conflict.master_mtime > conflict.backup_mtime

    def test_resolve_conflict_keep_master(self, sync_setup):
        """Test resolving conflict by keeping master version."""
        # Arrange - Create conflicting files
        master_file = sync_setup["master"] / "test.txt"
        backup_file = sync_setup["backup"] / "test.txt"

        master_file.write_text("master content")
        backup_file.write_text("backup content")

        # Act - Resolve conflict by keeping master
        conflicts = sync_setup["sync"].detect_conflicts()
        sync_setup["sync"].resolve_conflict(conflicts[0], resolution="keep_master")

        # Assert - Backup should now match master
        assert backup_file.read_text() == "master content"
```

### Code Review Checklist

Before submitting a pull request with new tests:

- [ ] Tests follow naming convention `test_<what_is_being_tested>()`
- [ ] All tests pass locally with `pytest`
- [ ] Coverage increased for target module (run `pytest --cov`)
- [ ] No test flakiness (run tests 5 times: `pytest --count=5`)
- [ ] Tests use appropriate fixtures (`tmp_path`, `qtbot`, mocks)
- [ ] Error paths tested, not just happy paths
- [ ] Tests run in isolation (can run in any order)
- [ ] Cleanup code present (close files, stop threads)
- [ ] Docstrings explain what's being tested
- [ ] No hardcoded paths or timestamps

### Useful pytest Commands

```bash
# Run all tests
pytest

# Run only sync tests
pytest tests/unit/sync/

# Run specific test file
pytest tests/unit/sync/test_file_synchronizer.py

# Run specific test class
pytest tests/unit/sync/test_file_synchronizer.py::TestFileSynchronizer

# Run specific test method
pytest tests/unit/sync/test_file_synchronizer.py::TestFileSynchronizer::test_sync_empty_directories

# Run with coverage report
pytest --cov=app.core.sync --cov-report=html

# Run with verbose output
pytest -v

# Run with print statements visible
pytest -s

# Run failed tests only (from last run)
pytest --lf

# Run until first failure
pytest -x

# Run tests matching pattern
pytest -k "sync"

# Show slowest tests
pytest --durations=10
```

---

## 📈 Success Metrics

### Coverage Targets by Quarter

| Quarter | Overall Coverage | Sync Coverage | GUI Tests | Integration Tests | Total Tests |
|---------|------------------|---------------|-----------|-------------------|-------------|
| **Q1 2026** | 76% | 60% | 60 tests | 12 tests | 220 tests |
| **Q2 2026** | 78% | 65% | 100 tests | 18 tests | 250 tests |
| **Q3 2026** | 80% | 70% | 110 tests | 25 tests | 270 tests |
| **Q4 2026** | 82%+ | 75%+ | 120+ tests | 30+ tests | 300+ tests |

### Definition of Done

A module is considered "adequately tested" when:

1. **Coverage:** ≥60% line coverage for that module
2. **Core paths:** All main execution paths have tests
3. **Error handling:** Exception paths tested with `pytest.raises()`
4. **Edge cases:** Boundary conditions tested (empty inputs, large inputs, invalid inputs)
5. **Integration:** At least one integration test verifying interaction with other modules
6. **Documentation:** Test docstrings explain what's being verified
7. **CI passing:** All tests pass in CI/CD pipeline on Python 3.12, 3.13, 3.14

---

## 🔗 Additional Resources

- **Testing Documentation:** [tests/README.md](../tests/README.md)
- **Sync Engine Examples:** [docs/examples/sync/README.md](examples/sync/README.md)
- **Architecture Overview:** [docs/architecture.md](architecture.md)
- **Contribution Guide:** [CONTRIBUTING.md](../CONTRIBUTING.md)
- **pytest Documentation:** https://docs.pytest.org/
- **pytest-qt Documentation:** https://pytest-qt.readthedocs.io/

---

## 📞 Getting Help

- **GitHub Discussions:** Ask questions about testing approach
- **GitHub Issues:** Report bugs in existing tests or test infrastructure
- **Pull Requests:** Submit new tests for review
- **Discord/Community:** (if applicable) Real-time help with testing challenges

---

**Priority Focus:** The sync engine's 0% test coverage is the highest-priority gap. If you're contributing tests, start with `file_synchronizer.py` and `backup_tracking.py` as these are foundational modules used by all other sync components.

**Remember:** Tests are documentation! Well-written tests help future contributors understand how the code should behave. Write tests that you'd want to read when learning a new module.
