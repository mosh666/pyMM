<!-- markdownlint-disable MD013 MD031 MD040 MD051 MD060 -->

<div align="center">

# pyMediaManager

## 🎬 Cross-Platform Portable Media Management Application

[![Python](https://img.shields.io/badge/Python-3.12%20|%203.13%20|%203.14-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![License](https://img.shields.io/github/license/mosh666/pyMM?style=flat&color=blue)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux%20|%20macOS-0078D6?style=flat&logo=windows)](https://github.com/mosh666/pyMM)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?style=flat&logo=qt)](https://wiki.qt.io/Qt_for_Python)

[![CI](https://github.com/mosh666/pyMM/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/mosh666/pyMM/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/mosh666/pyMM/branch/main/graph/badge.svg)](https://codecov.io/gh/mosh666/pyMM)
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/mosh666/pyMM/badge)](https://securityscorecards.dev/viewer/?uri=github.com/mosh666/pyMM)
[![Code style: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

[Features](#features) • [Quick Start](#quick-start) • [Documentation](#documentation) • [Contributing](#contributing)

</div>

---

<p align="left">
<b>pyMediaManager (pyMM)</b> is a fully portable, cross-platform media management application designed to run entirely from USB drives without system installation. Built with PySide6 and a modern Fluent Design interface, it offers professional-grade tools for organizing media projects across <b>Windows, Linux, and macOS</b>. It features an extensible plugin system with unified, platform-aware drive detection and storage management.
</p>

---

## ✨ Features

- **🎨 Modern Fluent UI** - Responsive interface built with PySide6 and QFluentWidgets.
- **💾 100% Portable** - Runs from external drives with zero system footprint on any supported OS.
- **🔌 Extensible Plugin System** - manage external tools (Git, FFmpeg, ExifTool) via YAML manifests.
- **⚡ Smart Drive Detection** - Unified storage API supporting:
  - **Windows:** WMI / Win32 APIs
  - **Linux:** udisks2 / sysfs
  - **macOS:** diskutil / IOKit
- **📁 Project Management** - Metadata-rich project organization with templates and Git integration.

---

## 🚀 Quick Start

### Portable Installation (End Users)

pyMediaManager is self-contained. Extract the release to your preferred location:

**Windows** (`D:\pyMM\`):
```text
pyMM/
├── python313/       # Embedded Python runtime
├── app/             # Application code
└── launcher.py      # Entry point
```

**Linux** (`/opt/pyMM` or `/media/usb/pyMM`):
```text
pyMM/
├── python313/       # Embedded runtime
├── app/
└── launcher.py
```

**macOS** (`/Applications/pyMM` or `/Volumes/USB/pyMM`):
```text
pyMM/
├── python313/       # Embedded runtime
├── app/
└── launcher.py
```

**To Run:**
- **Windows:** `.\pyMediaManager.exe` or `python launcher.py`
- **Linux/macOS:** `./pyMediaManager` or `python3 launcher.py`

### Developer Setup

**Prerequisites:**
- Python 3.13 (recommended), 3.12, or 3.14
- Git 2.30+
- **[just](https://github.com/casey/just)** (recommended task runner)

```bash
# 1. Clone
git clone https://github.com/mosh666/pyMM.git
cd pyMM

# 2. Setup (creates venv, installs dependencies & hooks)
just install

# 3. Verify
just check      # Runs lint, type-check, and tests
just --list     # Show all available build/test recipes

# 4. Run
python launcher.py
```

---

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

| Document | Description |
|----------|-------------|
| [**User Guide**](docs/user-guide.md) | Installation, features, configuration, templates |
| [**Plugin Catalog**](docs/plugin-catalog.md) | Official plugins and usage examples |
| [**Troubleshooting**](docs/troubleshooting.md) | Solutions for common issues per platform |
| [**Migration Guide**](docs/migration-guide.md) | Upgrading plugins from v0.x to v1.x |
| [**Architecture**](docs/architecture.md) | Technical design, directory structure, services |
| [**API Reference**](docs/api-reference.md) | Developer API documentation |
| [**Plugin Development**](docs/plugin-development.md) | Creating custom plugins via YAML |

---

## 🧪 Quality & Security

We adhere to strict 2026 Python best practices:

- **Type Safety:** 100% typed codebase (MyPy strict mode).
- **Testing:** 193+ tests with >73% coverage (pytest).
- **Security:**
  - Weekly OpenSSF Scorecard analysis (Saturdays 01:30 UTC).
  - CodeQL & Ruff security scanning (S-prefix rules).
  - Dependabot for daily dependency updates.
- **CI/CD:** Matrix testing on Python 3.12, 3.13, 3.14 across OSs.

---

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for style guides and workflows.

**Quick Workflow:**
1. Fork & Clone
2. `just install`
3. Create branch `feat/my-feature`
4. `just test` & `just lint`
5. Push & PR

---

## 📄 License

MIT License - see [LICENSE](LICENSE).

<div align="center">
  <b>Made with ❤️ by <a href="https://github.com/mosh666">mosh666</a></b>
</div>
