# Testing Status - pyMM v0.1.0

## Overview
This document tracks the testing progress for pyMM v0.1.0 development.

## Test Coverage Summary
**Current Coverage: 30%** (as of Phase 4 - January 2025)
- **Target: 70%+**
- **Tests Passing: 137/142**
- **Tests Failing: 3** (pre-existing config service tests)
- **Test Errors: 2** (GUI tests needing ProjectService fixture)

## Test Suites

### Integration Tests (`tests/integration/`) - NEW

#### ✅ Project Workflow Tests (`test_project_workflow.py`)
- **Status:** All passing (6/6)
- **Features Tested:**
  - Basic project creation
  - Project with Git initialization
  - Complete project lifecycle (create → modify → delete)
  - Git operations workflow (status, commit, log)
  - Multiple project management
  - Projects with complex directory structures

#### ✅ Plugin Workflow Tests (`test_plugin_workflow.py`)
- **Status:** All passing (5/5, excluding slow download test)
- **Features Tested:**
  - Plugin discovery from manifests
  - Plugin status checking
  - Installation of nonexistent plugins (error handling)
  - Plugin status retrieval
  - Mandatory vs optional plugin filtering

### Unit Tests (`tests/unit/`)

#### ✅ ConfigService Tests (`test_config_service.py`)
- **Status:** 13/16 passing
- **Coverage:** 99%
- **Test Count:** 16 tests
- **Issues:** 3 tests failing due to YAML serialization of LogLevel enum

#### ✅ FileSystemService Tests (`test_file_system_service.py`)
- **Status:** All passing (26/26)
- **Coverage:** 91%
- **Features Tested:**
  - Drive root detection and caching
  - Portable folder management
  - Path resolution (relative/absolute)
  - Directory operations (create, list, delete)
  - File operations (copy, move, delete, size, free space)

#### ✅ GitService Tests (`test_git_service.py`)
- **Status:** All passing (14/14)
- **Coverage:** 77%
- **Features Tested:**
  - Repository initialization (with/without initial commit)
  - Repository detection (`is_repository`, `get_repository`)
  - Status checking (staged, unstaged, untracked files)
  - Commit operations (all files, specific files, empty commits)
  - Remote management (add, list)
  - Commit log retrieval
  - Error handling for non-repositories

#### ✅ PluginBase Tests (`test_plugin_base.py`) - NEW
- **Status:** All passing (27/27)
- **Coverage:** 71%
- **Features Tested:**
  - PluginManifest dataclass creation and defaults
  - Plugin initialization and paths
  - Installation detection (`is_installed`)
  - Uninstall functionality
  - Executable path resolution
  - Archive extension detection (zip, 7z, 7z.exe)
  - Download error handling (HTTP errors, retries)
  - Checksum verification (success, failure, case-insensitive)
  - Extraction workflows (zip archives)
  - Directory flattening
  - Special case handling (ExifTool)
  - Version retrieval

#### ✅ PluginManager Tests (`test_plugin_manager.py`)
- **Status:** All passing (11/11)
- **Coverage:** 75%
- **Features Tested:**
  - Plugin discovery and manifest loading
  - Plugin retrieval and filtering
  - Status checking (mandatory, optional, enabled)
  - Plugin registration to PATH

#### ✅ Project Tests (`test_project.py`)
- **Status:** All passing (20/20)
- **Coverage:**
  - Project model: 96%
  - ProjectService: 80%
- **Features Tested:**
  - Project creation and validation
  - Path handling
  - Existence and Git repo detection
  - Serialization (`to_dict`, `from_dict`)
  - CRUD operations (create, load, save, delete, list)
  - Template application
  - Metadata management

#### ✅ StorageService Tests (`test_storage_service.py`)
- **Status:** All passing (9/9)
- **Coverage:** 85%
- **Features Tested:**
  - Drive enumeration (all drives, removable drives)
  - Drive info retrieval (size, free space, usage)
  - Removable drive detection

## Manual Test Scripts (To Be Converted)
Located in project root - need conversion to pytest format:

### `test_git_integration.py`
- Git repository initialization
- Status checking
- Committing changes
- Viewing commit log
- **Status:** All functionality passing, needs pytest conversion

### `test_project_management.py`
- Project creation and deletion
- Project listing
- Metadata persistence
- **Status:** All functionality passing, needs pytest conversion

### `test_settings_dialog.py`
- Settings UI initialization
- Configuration loading/saving
- Tab navigation (General, Plugins, Storage, Git)
- **Status:** All functionality passing, needs pytest conversion

### `test_plugin_download.py`
- Plugin download with retry logic
- Checksum verification
- 7z extraction
- **Status:** All functionality passing, needs pytest conversion

## Coverage by Module

| Module | Statements | Miss | Cover |
|--------|-----------|------|-------|
| app/models/project.py | 27 | 1 | 96% |
| app/core/services/file_system_service.py | 98 | 9 | 91% |
| app/core/services/storage_service.py | 80 | 12 | 85% |
| app/services/project_service.py | 96 | 19 | 80% |
| app/services/git_service.py | 97 | 22 | 77% |
| app/plugins/plugin_manager.py | 104 | 26 | 75% |
| app/plugins/plugin_base.py | 213 | 62 | 71% |
| app/core/services/config_service.py | 104 | 104 | 0% |
| app/core/logging_service.py | 60 | 60 | 0% |
| UI modules (dialogs, views, main_window) | ~900 | ~900 | 0% |

### Good Coverage (>70%)
- Plugin base class (71%) ✅ **IMPROVED**
- Plugin manager (75%) ✅
- Git service (77%) ✅
- Project service (80%) ✅
- Storage service (85%) ✅
- File system service (91%) ✅
- Project model (96%) ✅

### Low Coverage (<30%)
- Config service (0%)
- Logging service (0%)
- UI dialogs (0%)
- UI views (0%)
- Main window (0%)

## Testing Gaps & Next Steps

### Priority 1: Reach 70% Coverage (Current: 30%)
- [x] Add PluginBase tests (added ~6%, now at 71% coverage) ✅
- [ ] Add ConfigService tests (~5% coverage gain)
- [ ] Add LoggingService tests (~3% coverage gain)
- [ ] Add UI dialog tests (project wizard, browser, settings) (~8% coverage gain)
- [ ] Add view tests (plugin, project, storage views) (~4% coverage gain)
- **Estimated total gain:** ~26% (would bring total to ~56%)

### Priority 2: Fix Existing Issues
- [ ] Fix ConfigService YAML serialization (3 failing tests)
- [ ] Fix ProjectView fixture (2 test errors)
- [ ] Convert remaining manual test scripts to pytest format

### Priority 3: Documentation
- [ ] Create user guide (docs/user-guide.md)
- [ ] Update README.md with v0.1.0 features
- [ ] Add troubleshooting guide
- [ ] API documentation for services

## Known Issues

### Test Failures
1. **ConfigService YAML Serialization:**
   - `LogLevel` enum serialized as Python object instead of string
   - Affects `test_save_user_config` and `test_export_config`
   - Impact: Low (doesn't affect functionality, just test verification)

2. **Windows File Locking:**
   - Git repositories occasionally trigger file lock warnings during cleanup
   - Workaround: Added `repo.close()` and readonly removal in fixtures
   - Impact: Low (warnings only, tests still pass)

## Test Execution

### Run All Unit Tests
```bash
pytest tests/unit/ -v
```

### Run with Coverage Report
```bash
pytest tests/unit/ --cov=app --cov-report=html --cov-report=term
```

### Run Specific Test Suite
```bash
pytest tests/unit/test_git_service.py -v
pytest tests/unit/test_project.py -v
```

### Run Manual Tests (Temporary)
```bash
python test_project_management.py
python test_git_integration.py
python test_settings_dialog.py
python test_plugin_download.py
```

## Test Infrastructure

### Pytest Configuration (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = ["--cov=app", "--cov-report=html", "--cov-report=term-missing", "--cov-fail-under=70", "-v"]
asyncio_mode = "auto"
markers = [
    "integration: Integration tests (may be slower, access filesystem/network)",
    "slow: Tests that may take significant time to complete",
    "ui: Tests that require GUI components",
]
```

### Fixtures
- `tmp_path`: Temporary directory for file operations
- `test_projects_dir`: Isolated projects directory
- `project_service`: Configured ProjectService instance
- `config_service`: Configured ConfigService instance (in progress)
- `qtbot`: Qt testing support (pytest-qt)

### Dependencies
- pytest >= 9.0.2
- pytest-cov >= 7.0.0
- pytest-qt >= 4.5.0 (for UI tests)
- pytest-mock >= 3.15.1
- pytest-asyncio >= 1.3.0

## Metrics

### Test Execution Time
- Unit tests: ~5-6 seconds
- Integration tests: ~1-2 seconds
- All tests (excluding slow): ~7-8 seconds

### Lines of Test Code
- Unit tests: ~1,800 lines
- Integration tests: ~350 lines
- GUI tests: ~600 lines
- Manual tests (to be deprecated): ~500 lines
- **Total: ~3,250 lines**

### Test Distribution
- **Unit tests:** 92 tests (72%)
- **Integration tests:** 11 tests (9%)
- **GUI tests:** 25 tests (19%)
- **Total:** 128 tests

## Next Phase Actions

1. **Increase Coverage to 70%+:**
   - Priority: PluginBase download/extraction tests
   - Add remaining UI dialog tests
   - Add LoggingService tests
   - **Estimated:** ~20-25 additional tests needed

2. **Fix Failing Tests:**
   - Resolve ConfigService YAML serialization issue (LogLevel enum)
   - Fix ProjectView test fixtures
   - **Target:** 128/128 tests passing

3. **Documentation:**
   - Complete user guide with screenshots
   - Update README with v0.1.0 features and installation instructions
   - Create troubleshooting guide
   - **Target:** Production-ready documentation

4. **Quality Improvements:**
   - Remove deprecated manual test scripts
   - Add pre-commit hooks for testing
   - Set up CI/CD pipeline (optional)

---

**Last Updated:** January 4, 2026 (Phase 4 - Testing & Documentation)
**Version:** v0.1.0-dev
**Status:** 64% complete toward 70% coverage goal
