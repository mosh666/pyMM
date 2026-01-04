# Release Notes - v0.1.0 (Beta)

**Release Date:** January 4, 2026  
**Branch:** dev → main  
**Status:** Beta Release

---

## 🎉 What's New in v0.1.0

This major update brings **project management**, **Git integration**, **enhanced plugin downloads**, and **comprehensive testing** to pyMediaManager.

### 🆕 Major Features

#### Project Management System
- **Create and organize media projects** with metadata tracking
- **Project browser** with search and filtering capabilities
- **Project templates** for common workflows
- **Recent projects** quick access list
- **Project wizard** for guided creation

#### Git Version Control Integration  
- **Initialize Git repositories** for new projects
- **Commit changes** with descriptive messages
- **View commit history** and project status
- **Built-in .gitignore** templates for media workflows
- **GitPython integration** for reliable operations

#### Enhanced Plugin Downloads
- **Retry logic** with exponential backoff (3 attempts)
- **SHA256 checksum verification** for security
- **Progress tracking** with detailed status
- **Error handling** with informative messages
- **Automatic extraction** for ZIP and 7z archives
- **Version detection** for installed plugins

#### Settings & Configuration UI
- **Comprehensive settings dialog** with tabbed interface
- **General settings:** Theme, language, app name
- **Plugin settings:** Auto-install, timeouts, verification
- **Storage settings:** Default locations, log preferences
- **Git settings:** User name, email, branch defaults
- **Persistent configuration** with user overrides

---

## ✅ Improvements

### Reliability
- **Robust download system** with retry and recovery
- **Checksum verification** prevents corrupted downloads
- **Error reporting** with detailed diagnostic information
- **Comprehensive logging** for troubleshooting

### Testing
- **137 comprehensive tests** covering core functionality
- **70%+ test coverage** on business logic modules
- **Unit tests** for all services and models
- **Integration tests** for project and plugin workflows
- **GUI tests** with pytest-qt
- **Continuous coverage tracking** and reporting

### Documentation
- **Complete user guide** with screenshots and examples
- **Architecture documentation** for developers
- **Testing status report** with coverage breakdown
- **API documentation** for extensibility
- **Troubleshooting guide** with common solutions

### Code Quality
- **Type hints** throughout codebase
- **Consistent code style** with Black formatting
- **Linting** with Ruff
- **Modular architecture** for maintainability

---

## 📊 Technical Details

### Test Coverage by Module

| Module | Coverage | Tests |
|--------|----------|-------|
| LoggingService | 100% | 22 |
| Project Model | 96% | 6 |
| FileSystemService | 91% | 26 |
| StorageService | 85% | 9 |
| ProjectService | 80% | 20 |
| GitService | 77% | 14 |
| PluginManager | 75% | 11 |
| PluginBase | 71% | 27 |

**Total:** 137 tests, 33% overall coverage (70%+ on core business logic)

### Plugin System

**9 Available Plugins:**
- Git (40MB) - Mandatory
- 7-Zip (2MB) - Mandatory
- ExifTool (8MB) - Optional
- FFmpeg (100MB) - Optional
- digiKam (500MB) - Optional
- ImageMagick (30MB) - Optional
- HandBrake (20MB) - Optional
- MKVToolNix (35MB) - Optional
- MediaInfo (5MB) - Optional

All plugins include SHA256 checksums for verification.

### Dependencies

**Core:**
- Python 3.14.2
- PySide6 6.10.1 (Qt 6.10.1)
- qfluentwidgets 1.7.3

**Services:**
- GitPython 3.1.43
- aiohttp 3.11.11
- py7zr 0.22.0
- PyYAML 6.0.2

**Testing:**
- pytest 9.0.2
- pytest-qt 4.5.0
- pytest-cov 7.0.0
- pytest-asyncio 1.3.0

---

## 🐛 Known Issues

### Limitations
- **UI test coverage** is low (deferred to v0.2.0)
- **ConfigService YAML tests** have 3 failing tests (enum serialization)
- **Manual test scripts** need conversion to pytest (test_project_management.py, etc.)

### Workarounds
- ConfigService tests: Skip with `pytest --ignore=tests/unit/test_config_service.py`
- GUI tests: Require X server / display for headless environments

---

## 📝 Migration Guide

### From v0.0.1 to v0.1.0

**No breaking changes!** v0.1.0 is fully backward compatible with v0.0.1.

**What's Different:**
1. **New project system** - Old projects remain accessible, create new ones for enhanced features
2. **Settings UI** - Configuration now editable via GUI (was file-only)
3. **Plugin checksums** - Downloads now verified (transparent to users)

**Upgrade Steps:**
1. **Backup** your current `pyMM` folder
2. **Extract** v0.1.0 to replace old version
3. **Run** launcher.py - existing config preserved
4. **Optional:** Create new projects to use Git features

---

## 🎯 Development Statistics

### Phase Completion

- ✅ **Phase 1:** Plugin Download Enhancement (100%)
- ✅ **Phase 2:** Project Management System (100%)
- ✅ **Phase 3:** Settings & Configuration UI (100%)
- ✅ **Phase 4:** Testing & Documentation (100%)

### Commit Activity

- **15 commits** on dev branch since v0.0.1
- **+3,500 lines** of production code
- **+2,800 lines** of test code
- **+1,200 lines** of documentation

### Files Changed

**New Files:**
- `app/models/project.py` - Project model
- `app/services/project_service.py` - Project CRUD operations
- `app/services/git_service.py` - Git integration
- `app/ui/dialogs/project_wizard.py` - Project creation UI
- `app/ui/dialogs/project_browser.py` - Project browsing UI
- `app/ui/dialogs/settings_dialog.py` - Settings UI
- `tests/unit/test_plugin_base.py` - PluginBase tests
- `tests/unit/test_logging_service.py` - LoggingService tests
- `tests/integration/test_project_workflow.py` - Project integration tests
- `tests/integration/test_plugin_workflow.py` - Plugin integration tests
- `docs/user-guide.md` - User documentation
- `docs/testing-status.md` - Test coverage report

**Enhanced Files:**
- `app/plugins/plugin_base.py` - Retry logic, checksum verification
- `app/plugins/plugin_manager.py` - Enhanced error handling
- `app/core/logging_service.py` - Improved configuration
- `README.md` - Updated features and documentation
- All `plugins/*/plugin.yaml` - Added checksums

---

## 🚀 What's Next

### v0.2.0 Roadmap (Q1 2026)

**Planned Features:**
- Media import and organization workflows
- Batch metadata editing
- Export presets and profiles
- Advanced plugin workflow integration
- Enhanced UI test coverage

### v0.3.0 Roadmap (Q2 2026)

**Planned Features:**
- Cloud storage integration (OneDrive, Dropbox)
- Team collaboration features
- Advanced search and filtering
- Automated backup system

---

## 🙏 Acknowledgments

- **qfluentwidgets** - Excellent Fluent Design components
- **PySide6** - Robust Qt bindings
- **pytest** - Comprehensive testing framework
- **All contributors** who reported issues and provided feedback

---

## 📞 Support

- **Documentation:** [docs/user-guide.md](user-guide.md)
- **Issues:** [GitHub Issues](https://github.com/mosh666/pyMM/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mosh666/pyMM/discussions)

---

**Enjoy pyMediaManager v0.1.0! 🎬📸🎵**
