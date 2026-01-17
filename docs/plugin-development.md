<!-- markdownlint-disable MD013 MD022 MD031 MD032 MD033 MD034 MD036 MD040 MD051 MD060 -->

# 🔌 Plugin Development Guide

> **Last Updated:** 2026-01-17 21:41 UTC


> **Python Support:** 3.12, 3.13, 3.14 (3.13 recommended with MSI installer, 3.14 fully supported)
> **Plugin System:** Manifest-driven (YAML-based) with automatic validation
> **Security:** SHA-256 checksum verification, retry logic, progress tracking
> **Code Examples:** See [examples/plugins/README.md](examples/plugins/README.md) for working code

## 📚 Table of Contents

- [Overview](plugin-dev-overview)
- [Quick Start](#quick-start)
- [Plugin Architecture](#plugin-architecture)
- [YAML Manifest Schema](#yaml-manifest-schema)
- [Plugin Types](#plugin-types)
- [Creating Your First Plugin](#creating-your-first-plugin)
- [Advanced Configuration](#advanced-configuration)
- [Testing Plugins](#testing-plugins)
- [Publishing Plugins](#publishing-plugins)
- [Best Practices](#best-practices)
- [Troubleshooting](troubleshooting.md)
- [API Reference](#api-reference)

---

(plugin-dev-overview)=

## 🎯 Overview

pyMediaManager (pyMM) uses a **manifest-driven plugin system** that allows external tools to be managed without writing Python code. Plugins are defined entirely through YAML manifests that describe:

- 📦 **Download Sources**: Direct URLs or GitHub releases
- 🔐 **Security**: SHA-256 checksums for integrity verification
- 📂 **Installation**: Extraction paths and directory structure
- ⚙️ **Configuration**: Command paths, executables, PATH registration
- 🔗 **Dependencies**: Optional plugin dependencies

### Key Benefits

✅ **No Code Required**: Pure data-driven configuration
✅ **Security**: No arbitrary code execution, sandboxed downloads
✅ **Portability**: Plugins install to external drives
✅ **Automatic Updates**: Version tracking and update checks
✅ **Validation**: Strict Pydantic schema validation

---

(quick-start)=

## 🚀 Quick Start

### 5-Minute Plugin Creation

1. **Create plugin directory**:

   ```bash
   mkdir -p plugins/mytool
   ```

2. **Create `plugin.yaml`**:
   ```yaml
   name: MyTool
   version: 1.0.0
   description: My awesome tool
   homepage: https://example.com/mytool
   mandatory: false
   enabled: true

   source:
     type: url
     uri: https://example.com/mytool-1.0.0-win64.zip
     checksum_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
     file_size: 5242880

   command:
     path: bin
     executable: mytool.exe
     register_to_path: false

   dependencies: []
   ```

3. **Test plugin**:
   ```bash
   python -m pytest tests/test_plugin_manager.py -k "test_discover_plugins"
   ```

4. **Install in pyMM**:
   - Launch pyMM
   - Navigate to Plugin View
   - Click "Refresh Plugins"
   - Select "MyTool" and click "Install"

---

(plugin-architecture)=

## 🏗️ Plugin Architecture

### Manifest-Driven Approach

pyMM uses a **strictly manifest-driven** plugin system. External tools are managed entirely by the core application based on YAML declarations—**no custom Python code is executed during plugin loading or installation**.

```{mermaid}
graph LR
    YAML[plugin.yaml] -->|Pydantic| Validation[Schema Validation]
    Validation -->|Pass| Manager[Plugin Manager]
    Validation -->|Fail| Error[Validation Error]
    Manager --> Download[Download & Verify]
    Download --> Extract[Extract to plugins_dir]
    Extract --> Validate[Validate Installation]
    Validate --> Ready[Plugin Ready]
```

### Component Overview

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Plugin Manifest** | Declarative configuration | YAML |
| **PluginManifestSchema** | Validation and type safety | Pydantic 2.5+ |
| **PluginManager** | Discovery, installation, lifecycle | Python 3.13 |
| **SimplePluginImplementation** | Download, extract, validate | aiohttp, shutil |

### Security Model

1. **No Code Execution**: Plugins cannot run arbitrary Python code
2. **Sandboxed Downloads**: Isolated temp directory, HTTPS only
3. **Integrity Verification**: SHA-256 checksum validation
4. **Fail-Fast Validation**: Strict schema enforcement

---

(yaml-manifest-schema)=

## 📋 YAML Manifest Schema

### Complete Schema Reference

```yaml
# Required Fields
name: string                    # Plugin name (alphanumeric, spaces allowed)
version: string                 # Semantic version (e.g., 2.47.1)
description: string             # Brief description
homepage: string                # Official website URL
mandatory: boolean              # Is plugin required for core functionality?
enabled: boolean                # Is plugin enabled by default?

# Source Configuration
source:
  type: string                  # "url" or "github"
  uri: string                   # Download URL or GitHub repo (owner/repo)
  asset_pattern: string         # (GitHub only) Regex for release asset
  checksum_sha256: string       # SHA-256 hash of download file
  file_size: integer            # File size in bytes (optional)

# Command Configuration
command:
  path: string                  # Relative path from plugin root to binary dir
  executable: string            # Executable filename
  register_to_path: boolean     # Add to system PATH?

# Dependencies (optional)
dependencies:
  - string                      # List of plugin names this depends on
```

### Field Validation Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `name` | `str` | ✅ | 1-100 chars, alphanumeric + spaces/hyphens |
| `version` | `str` | ✅ | Semantic versioning (1.0.0, 2.1.3-beta) |
| `description` | `str` | ✅ | 1-500 chars |
| `homepage` | `str` | ✅ | Valid HTTP/HTTPS URL |
| `mandatory` | `bool` | ✅ | `true` or `false` |
| `enabled` | `bool` | ✅ | `true` or `false` |
| `source.type` | `str` | ✅ | `"url"` or `"github"` |
| `source.uri` | `str` | ✅ | URL or `owner/repo` format |
| `source.checksum_sha256` | `str` | ✅ | 64-char hex string |
| `source.file_size` | `int` | ❌ | Positive integer (bytes) |
| `command.path` | `str` | ✅ | Relative path (no `..`) |
| `command.executable` | `str` | ✅ | Filename with extension |
| `command.register_to_path` | `bool` | ✅ | `true` or `false` |
| `dependencies` | `list[str]` | ❌ | List of plugin names |

---

(plugin-types)=

## 🎨 Plugin Types

### 1. URL-Based Plugins

Direct download from a static URL.

**Use Case**: Self-hosted binaries, stable tool versions

```yaml
name: MyTool
version: 3.2.1
description: Custom tool with direct download
homepage: https://example.com
mandatory: false
enabled: true

source:
  type: url
  uri: https://cdn.example.com/releases/mytool-3.2.1-windows-x64.zip
  checksum_sha256: "a1b2c3d4e5f6..."
  file_size: 15728640  # 15 MB

command:
  path: bin
  executable: mytool.exe
  register_to_path: true

dependencies: []
```

**Checksum Generation**:
```powershell
# PowerShell
Get-FileHash mytool-3.2.1-windows-x64.zip -Algorithm SHA256

# Output:
# Algorithm       Hash                                   Path
# ---------       ----                                   ----
# SHA256          A1B2C3D4E5F6...                       mytool-3.2.1-windows-x64.zip
```

---

### 2. GitHub Release Plugins

Download from GitHub Releases with asset pattern matching.

**Use Case**: Open-source tools with regular releases

```yaml
name: Git
version: 2.47.1
description: Distributed version control system
homepage: https://git-scm.com
mandatory: false
enabled: true

source:
  type: github
  uri: git-for-windows/git
  asset_pattern: "PortableGit-.*-64-bit\\.7z\\.exe$"
  checksum_sha256: "f9a9d5c1..."

command:
  path: cmd
  executable: git.exe
  register_to_path: true

dependencies: []
```

**Asset Pattern Matching**:
- Uses Python regex syntax
- Matches against release asset filenames
- Must escape special characters (`\.`, `\$`, etc.)
- Pattern is case-sensitive

**Example Patterns**:
```yaml
# Match specific version
asset_pattern: "tool-1\\.2\\.3-win64\\.zip$"

# Match any version with architecture
asset_pattern: "tool-.*-x64\\.zip$"

# Match portable or installer
asset_pattern: "(Portable|Setup)-.*\\.exe$"
```

---

### 3. Plugins with Dependencies

Plugins that require other plugins to function.

**Use Case**: Tools that depend on runtime libraries

```yaml
name: GitLFS
version: 3.5.1
description: Git extension for large file support
homepage: https://git-lfs.com
mandatory: false
enabled: false

source:
  type: github
  uri: git-lfs/git-lfs
  asset_pattern: "git-lfs-windows-v.*\\.exe$"
  checksum_sha256: "b5c6d7e8..."

command:
  path: ""
  executable: git-lfs.exe
  register_to_path: true

dependencies:
  - Git  # Requires Git plugin to be installed first
```

**Dependency Resolution**:
- Plugin Manager installs dependencies recursively
- Circular dependencies are detected and rejected
- Installation order: dependencies → dependent plugin

---

(creating-your-first-plugin)=

## 🛠️ Creating Your First Plugin

### Example: FFmpeg Plugin

Let's create a complete plugin for FFmpeg, a multimedia framework.

#### Step 1: Research the Tool

1. **Find official source**: https://ffmpeg.org/download.html
2. **Locate Windows builds**: https://github.com/BtbN/FFmpeg-Builds/releases
3. **Choose version**: 7.1 (latest stable)
4. **Download and verify**:
   ```powershell
   # Download
   Invoke-WebRequest -Uri "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" -OutFile "ffmpeg.zip"

   # Calculate SHA-256
   Get-FileHash ffmpeg.zip -Algorithm SHA256

   # Get file size
   (Get-Item ffmpeg.zip).Length
   ```

#### Step 2: Test Extraction

```powershell
# Extract to test directory
Expand-Archive -Path ffmpeg.zip -DestinationPath test-extract

# Verify structure
tree /F test-extract

# Test executable
.\test-extract\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe -version
```

Expected output:
```
test-extract/
└── ffmpeg-master-latest-win64-gpl/
    ├── bin/
    │   ├── ffmpeg.exe
    │   ├── ffplay.exe
    │   └── ffprobe.exe
    ├── LICENSE.txt
    └── README.txt
```

#### Step 3: Create Manifest

```yaml
# plugins/ffmpeg/plugin.yaml
name: FFmpeg
version: 7.1.0
description: Complete multimedia framework for audio/video processing
homepage: https://ffmpeg.org
mandatory: false
enabled: false

source:
  type: github
  uri: BtbN/FFmpeg-Builds
  asset_pattern: "ffmpeg-master-latest-win64-gpl\\.zip$"
  checksum_sha256: "1a2b3c4d5e6f7890abcdef1234567890abcdef1234567890abcdef1234567890"
  file_size: 89478485  # ~85 MB

command:
  # Note: GitHub releases extract to subdirectory
  path: ffmpeg-master-latest-win64-gpl/bin
  executable: ffmpeg.exe
  register_to_path: true

dependencies: []
```

#### Step 4: Validate Schema

```python
# tests/test_ffmpeg_plugin.py
import yaml
from pathlib import Path
from app.plugins.plugin_schema import PluginManifestSchema

def test_ffmpeg_manifest_valid():
    """Test FFmpeg plugin manifest is valid."""
    manifest_file = Path("plugins/ffmpeg/plugin.yaml")

    with open(manifest_file) as f:
        data = yaml.safe_load(f)

    # Pydantic validation
    manifest = PluginManifestSchema(**data)

    assert manifest.name == "FFmpeg"
    assert manifest.version == "7.1.0"
    assert manifest.source.type == "github"
    assert len(manifest.source.checksum_sha256) == 64
```

Run validation:
```bash
pytest tests/test_ffmpeg_plugin.py -v
```

#### Step 5: Test Installation

```python
# Manual test script
import asyncio
from pathlib import Path
from app.plugins.plugin_manager import PluginManager

async def test_ffmpeg_install():
    plugins_dir = Path("D:/pyMM.Plugins")
    manifests_dir = Path("plugins")

    manager = PluginManager(plugins_dir, manifests_dir)
    manager.discover_plugins()

    print(f"Discovered plugins: {list(manager.plugins.keys())}")

    # Install FFmpeg
    success = await manager.install_plugin("FFmpeg", progress_callback=print_progress)

    if success:
        print("✅ FFmpeg installed successfully")
        plugin = manager.plugins["FFmpeg"]
        version = plugin.get_version()
        print(f"Version: {version}")
    else:
        print("❌ Installation failed")

def print_progress(current: int, total: int):
    percent = (current / total) * 100
    print(f"Progress: {percent:.1f}% ({current}/{total} bytes)")

if __name__ == "__main__":
    asyncio.run(test_ffmpeg_install())
```

---

(advanced-configuration)=

## ⚙️ Advanced Configuration

### Multi-Executable Plugins

Some tools provide multiple executables (e.g., FFmpeg has `ffmpeg`, `ffplay`, `ffprobe`).

**Solution**: Use the primary executable in `command.executable`, access others programmatically.

```yaml
command:
  path: bin
  executable: ffmpeg.exe  # Primary tool
  register_to_path: true
```

**Accessing secondary executables**:
```python
plugin = plugin_manager.plugins["FFmpeg"]
ffmpeg_exe = plugin.get_executable_path()  # Returns .../bin/ffmpeg.exe
ffprobe_exe = ffmpeg_exe.parent / "ffprobe.exe"  # Same directory
```

---

### Versioned Command Paths

Tools that include version in directory name:

```yaml
# Example: Node.js portable
command:
  path: node-v20.11.0-win-x64  # Versioned directory
  executable: node.exe
  register_to_path: true
```

**Challenge**: Version changes require manifest update.

**Solution**: Use regex replacement (planned feature):

```yaml
# Future syntax
command:
  path: "node-v{version}-win-x64"
  executable: node.exe
  register_to_path: true
```

---

### Self-Extracting Archives

Some Windows tools use `.exe` self-extractors:

```yaml
source:
  type: url
  uri: https://example.com/tool-portable.exe
  checksum_sha256: "abc123..."
```

**Current Behavior**: PluginManager treats `.exe` files as executables, not archives.

**Workaround**: Use 7-Zip command-line extraction:

```yaml
# If tool provides .7z.exe self-extractor
source:
  uri: https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.1/PortableGit-2.47.1-64-bit.7z.exe
```

Plugin Manager automatically detects `.7z.exe` and extracts with 7-Zip.

---

### Large File Downloads

For files >100MB, consider:

1. **Progress Callbacks**: Show download progress in UI
2. **Resume Support**: Plugin Manager supports HTTP range requests
3. **Timeout Configuration**: Adjust `config.plugins.download_timeout`

```yaml
# pyMM config/user.yaml
plugins:
  download_timeout: 600  # 10 minutes for large files
  parallel_downloads: 1  # Sequential for slow connections
```

---

## 🎓 Your First Plugin: Complete Step-by-Step Tutorial

This comprehensive tutorial walks you through creating a complete plugin from scratch, covering every step from tool selection to submission.

### Tutorial Overview

**What You'll Build:** A plugin for 7-Zip portable
**Time Required:** 45-60 minutes
**Difficulty:** Beginner-friendly

**Learning Objectives:**
- ✅ Research and validate tool sources
- ✅ Generate SHA-256 checksums (Windows/Linux/macOS)
- ✅ Create YAML manifest with proper schema
- ✅ Test plugin installation locally
- ✅ Handle platform-specific considerations
- ✅ Submit plugin to repository

---

### Step 1: Choose Your Tool

**Good candidates for first plugin:**
- ✅ Single executable or simple structure
- ✅ Portable/standalone distribution available
- ✅ Clear version numbering
- ✅ Stable download URLs
- ✅ Active maintenance

**Example choices:**
- 7-Zip portable
- Git portable
- ExifTool
- ImageMagick portable
- Node.js portable

**For this tutorial:** 7-Zip Portable (simple, widely used, stable)

---

### Step 2: Research Tool Distribution

#### Find Official Source

1. Visit [7-Zip official website](https://www.7-zip.org/)
2. Navigate to download section
3. Look for "portable" or "standalone" version
4. Note the download URL structure

**Key information to gather:**
- Official website URL
- Latest version number
- Download URL (prefer HTTPS)
- Archive format (.zip, .7z, .tar.gz)
- Expected file size
- License information

#### Verify URL Stability

```{tabs}
.. tab:: Windows PowerShell

   .. code-block:: powershell

      # Test download URL
      $url = "https://www.7-zip.org/a/7z2408-x64.exe"
      $response = Invoke-WebRequest -Uri $url -Method Head
      Write-Host "Status: $($response.StatusCode)"
      Write-Host "Content-Length: $($response.Headers.'Content-Length')"
      Write-Host "Content-Type: $($response.Headers.'Content-Type')"

.. tab:: Linux/macOS

   .. code-block:: bash

      # Test download URL
      url="https://www.7-zip.org/a/7z2408-x64.exe"
      curl -I "$url"
      # Check Status: 200 OK
```

---

### Step 3: Download and Analyze

#### Download Tool

```{tabs}
.. tab:: Windows PowerShell

   .. code-block:: powershell

      # Download to temp directory
      $url = "https://www.7-zip.org/a/7z2408-x64.exe"
      $output = "$env:TEMP\7z-portable.exe"
      Invoke-WebRequest -Uri $url -OutFile $output

      Write-Host "Downloaded to: $output"
      Write-Host "File size: $((Get-Item $output).Length) bytes"

.. tab:: Linux/macOS

   .. code-block:: bash

      # Download to temp directory
      url="https://www.7-zip.org/a/7z2408-x64.exe"
      output="/tmp/7z-portable.exe"
      curl -L "$url" -o "$output"

      echo "Downloaded to: $output"
      ls -lh "$output"
```

#### Test Extraction

```{tabs}
.. tab:: Windows PowerShell

   .. code-block:: powershell

      # Extract to test directory
      $testDir = "$env:TEMP\7z-test"
      New-Item -ItemType Directory -Force -Path $testDir

      # 7-Zip SFX archives extract themselves
      Start-Process -FilePath $output -ArgumentList "/S /D=$testDir" -Wait

      # View structure
      tree /F $testDir | Select-Object -First 20

.. tab:: Linux/macOS

   .. code-block:: bash

      # Extract to test directory
      testDir="/tmp/7z-test"
      mkdir -p "$testDir"

      # Use 7z or unzip to extract
      7z x "$output" -o"$testDir"

      # View structure
      tree "$testDir" | head -20
```

#### Document Structure

**Example 7-Zip structure:**
```
7z-test/
├── 7z.exe          ← Main executable
├── 7z.dll
├── 7zG.exe
├── 7zFM.exe        ← GUI file manager
├── License.txt
└── readme.txt
```

**Key observations:**
- Main executable: `7z.exe` (command-line)
- Alternative: `7zFM.exe` (GUI)
- No subdirectories (flat structure)
- License included

---

### Step 4: Generate SHA-256 Checksum

**Critical for security:** Always verify file integrity with SHA-256.

```{tabs}
.. tab:: Windows (PowerShell)

   .. code-block:: powershell

      # Generate SHA-256 checksum
      $hash = Get-FileHash -Algorithm SHA256 -Path $output
      $checksum = $hash.Hash.ToLower()

      Write-Host "SHA-256 Checksum:"
      Write-Host $checksum

      # Copy to clipboard (optional)
      $checksum | Set-Clipboard
      Write-Host "`nChecksum copied to clipboard!"

.. tab:: Windows (certutil)

   .. code-block:: cmd

      :: Alternative using certutil
      certutil -hashfile "C:\path\to\7z-portable.exe" SHA256

.. tab:: Linux

   .. code-block:: bash

      # Generate SHA-256 checksum
      checksum=$(sha256sum "$output" | awk '{print $1}')
      echo "SHA-256 Checksum:"
      echo "$checksum"

      # Copy to clipboard (requires xclip)
      echo "$checksum" | xclip -selection clipboard

.. tab:: macOS

   .. code-block:: bash

      # Generate SHA-256 checksum
      checksum=$(shasum -a 256 "$output" | awk '{print $1}')
      echo "SHA-256 Checksum:"
      echo "$checksum"

      # Copy to clipboard
      echo "$checksum" | pbcopy
```

**Example output:**
```
1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

**Save this checksum** - you'll need it for the manifest!

---

### Step 5: Create Plugin Manifest

#### Create Directory Structure

```bash
# Create plugin directory
mkdir -p plugins/7zip
cd plugins/7zip
```

#### Write plugin.yaml

Create `plugins/7zip/plugin.yaml`:

```yaml
# 7-Zip Portable Plugin Manifest
name: 7-Zip
version: 24.08
description: File archiver with high compression ratio
homepage: https://www.7-zip.org/
mandatory: false
enabled: false

source:
  type: url
  uri: https://www.7-zip.org/a/7z2408-x64.exe
  # IMPORTANT: Replace with YOUR actual checksum from Step 4
  checksum_sha256: "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
  file_size: 1612800  # ~1.5 MB (update with actual size)

command:
  path: ""  # Flat structure - executables in root
  executable: 7z.exe  # Command-line version
  register_to_path: true  # Add to PATH for easy access
  args: []  # No default arguments

dependencies: []  # 7-Zip has no dependencies

# Platform-specific notes (comments only)
# - Windows: Native executable (this manifest)
# - Linux: Install via package manager (sudo apt install p7zip-full)
# - macOS: Install via Homebrew (brew install p7zip)
```

#### Validate YAML Syntax

```{tabs}
.. tab:: Python

   .. code-block:: python

      import yaml
      from pathlib import Path

      manifest_file = Path("plugins/7zip/plugin.yaml")

      try:
          with open(manifest_file) as f:
              data = yaml.safe_load(f)
          print("✅ YAML syntax is valid")
          print(f"Plugin name: {data['name']}")
          print(f"Version: {data['version']}")
      except yaml.YAMLError as e:
          print(f"❌ YAML syntax error: {e}")

.. tab:: Online Validator

   Visit https://www.yamllint.com/ and paste your YAML content
```

---

### Step 6: Test Plugin Locally

#### Option A: Unit Test (Recommended)

Create `tests/test_7zip_plugin.py`:

```python
"""Unit tests for 7-Zip plugin."""

import pytest
from pathlib import Path
import yaml
from pydantic import ValidationError

from app.plugins.models import PluginManifest


def test_7zip_manifest_syntax():
    """Test 7-Zip manifest has valid YAML syntax."""
    manifest_file = Path("plugins/7zip/plugin.yaml")

    with open(manifest_file) as f:
        data = yaml.safe_load(f)

    assert data is not None
    assert "name" in data
    assert data["name"] == "7-Zip"


def test_7zip_manifest_schema():
    """Test 7-Zip manifest passes Pydantic validation."""
    manifest_file = Path("plugins/7zip/plugin.yaml")

    try:
        manifest = PluginManifest.from_yaml(manifest_file)
        assert manifest.name == "7-Zip"
        assert manifest.version == "24.08"
        assert manifest.source.type == "url"
        assert len(manifest.source.checksum_sha256) == 64
        print("✅ Manifest validation passed!")
    except ValidationError as e:
        pytest.fail(f"❌ Validation failed: {e}")


def test_7zip_checksum_format():
    """Test SHA-256 checksum is valid hex format."""
    manifest_file = Path("plugins/7zip/plugin.yaml")
    manifest = PluginManifest.from_yaml(manifest_file)

    checksum = manifest.source.checksum_sha256

    # Check length (64 hex characters)
    assert len(checksum) == 64, "SHA-256 must be 64 characters"

    # Check hex format
    try:
        int(checksum, 16)
    except ValueError:
        pytest.fail("Checksum must be valid hexadecimal")

    print(f"✅ Checksum format valid: {checksum[:16]}...")
```

Run tests:
```bash
pytest tests/test_7zip_plugin.py -v
```

#### Option B: Manual Installation Test

```python
"""Manual installation test script."""

import asyncio
from pathlib import Path
from app.plugins.plugin_manager import PluginManager


async def test_7zip_installation():
    """Test 7-Zip plugin installation."""
    # Configure paths
    plugins_dir = Path("D:/pyMM.Plugins")  # Adjust for your system
    manifests_dir = Path("plugins")

    # Create PluginManager
    manager = PluginManager(plugins_dir, manifests_dir)

    # Discover plugins
    count = manager.discover_plugins()
    print(f"📦 Discovered {count} plugins")

    if "7-Zip" not in manager.plugins:
        print("❌ 7-Zip plugin not found!")
        return

    # Install plugin
    print("\n🔽 Installing 7-Zip...")

    def progress_callback(current: int, total: int):
        percent = (current / total) * 100
        print(f"Progress: {percent:5.1f}% ({current:,} / {total:,} bytes)", end="\r")

    success = await manager.install_plugin("7-Zip", progress_callback)

    if success:
        print("\n✅ 7-Zip installed successfully!")

        # Test version detection
        plugin = manager.plugins["7-Zip"]
        version = plugin.get_version()
        print(f"Version detected: {version}")

        # Test executable path
        exe_path = plugin.get_executable_path()
        print(f"Executable: {exe_path}")
        print(f"Exists: {exe_path.exists()}")
    else:
        print("\n❌ Installation failed!")


if __name__ == "__main__":
    asyncio.run(test_7zip_installation())
```

Run manual test:
```bash
python test_7zip_manual.py
```

---

### Step 7: Platform Testing Matrix

Test your plugin across different platforms to ensure compatibility.

#### Testing Checklist

```{eval-rst}
.. list-table::
   :header-rows: 1
   :widths: 30 20 20 30

   * - Test Case
     - Windows
     - Linux
     - macOS
   * - **YAML Syntax**
     - ✅ Required
     - ✅ Required
     - ✅ Required
   * - **Schema Validation**
     - ✅ Required
     - ✅ Required
     - ✅ Required
   * - **Download URL**
     - ✅ Test actual download
     - ⚠️ Not applicable*
     - ⚠️ Not applicable*
   * - **SHA-256 Verification**
     - ✅ Must match
     - N/A
     - N/A
   * - **Extraction**
     - ✅ Test extraction
     - N/A
     - N/A
   * - **Executable Detection**
     - ✅ 7z.exe found
     - N/A
     - N/A
   * - **Version Command**
     - ✅ ``7z --version``
     - N/A
     - N/A
   * - **PATH Registration**
     - ✅ Verify in PATH
     - N/A
     - N/A
```

**Note:** For cross-platform tools, create separate manifests for each OS (e.g., `plugin-windows.yaml`, `plugin-linux.yaml`).

---

### Step 8: Submit Plugin to Repository

#### Pre-Submission Checklist

- [ ] YAML syntax validated
- [ ] Pydantic schema validation passes
- [ ] SHA-256 checksum verified
- [ ] Plugin installs successfully
- [ ] Version detection works
- [ ] All tests pass (`pytest tests/test_7zip_plugin.py`)
- [ ] No hardcoded paths
- [ ] LICENSE.txt exists (if required)
- [ ] README.md added (optional but recommended)

#### Create Plugin README (Optional)

Create `plugins/7zip/README.md`:

```markdown
# 7-Zip Plugin

File archiver with high compression ratio.

## Features

- High compression ratio in 7z format
- Supports multiple archive formats (ZIP, RAR, TAR, etc.)
- Command-line and GUI interfaces included
- Open-source and free

## Installation

Install via pyMM Plugin Manager:
1. Open pyMM
2. Navigate to Plugins tab
3. Find "7-Zip" in list
4. Click "Install"

## Usage

### Command Line

\```bash
# Compress files
7z a archive.7z file1.txt file2.txt

# Extract archive
7z x archive.7z

# List contents
7z l archive.7z
\```

### GUI Mode

Launch `7zFM.exe` from plugin directory for graphical interface.

## Links

- **Homepage**: https://www.7-zip.org/
- **Documentation**: https://www.7-zip.org/faq.html
- **License**: GNU LGPL
```

#### Submit via Pull Request

```bash
# Create feature branch
git checkout -b plugin/add-7zip

# Add plugin files
git add plugins/7zip/plugin.yaml
git add plugins/7zip/README.md
git add tests/test_7zip_plugin.py

# Commit with conventional commit format
git commit -m "feat(plugins): add 7-Zip portable plugin

- Add 7-Zip 24.08 plugin manifest
- Include SHA-256 checksum verification
- Add comprehensive unit tests
- Add plugin README

Tested on Windows 10/11 with Python 3.13"

# Push to your fork
git push origin plugin/add-7zip

# Create pull request
gh pr create --title "feat(plugins): add 7-Zip portable plugin" \
             --body "Adds 7-Zip file archiver plugin.

## Plugin Details
- **Name**: 7-Zip
- **Version**: 24.08
- **Type**: File archiver
- **Size**: ~1.5 MB

## Testing
- ✅ YAML syntax validated
- ✅ Schema validation passes
- ✅ SHA-256 verified
- ✅ Installation tested on Windows 11
- ✅ Version detection works
- ✅ Unit tests pass

## Documentation
- Plugin README included
- Usage examples provided
" \
             --base dev
```

---

### Step 9: Address Review Feedback

Your PR will be reviewed by maintainers. Common feedback includes:

**Checksum Issues:**
```yaml
# ❌ Wrong - partial hash
checksum_sha256: "1234567890abcdef"

# ✅ Correct - full 64 characters
checksum_sha256: "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
```

**File Size Issues:**
```yaml
# ❌ Wrong - human-readable format
file_size: "1.5 MB"

# ✅ Correct - bytes as integer
file_size: 1612800
```

**URL Stability:**
```yaml
# ⚠️ Warning - version-specific URL may break
uri: https://example.com/tool-v1.2.3.zip

# ✅ Better - use "latest" or stable URL
uri: https://example.com/tool-latest.zip
```

---

### Step 10: Celebrate! 🎉

Congratulations! You've successfully created and submitted your first plugin!

**What you learned:**
- ✅ Plugin manifest structure
- ✅ SHA-256 checksum generation
- ✅ YAML validation
- ✅ Testing methodologies
- ✅ Git workflow for contributions
- ✅ Pull request best practices

**Next steps:**
- Create more complex plugins (GitHub releases, dependencies)
- Contribute to plugin documentation
- Help review other plugin submissions
- Explore advanced plugin features

---

(testing-plugins)=

## 🧪 Testing Plugins

### Unit Testing

```python
# tests/unit/test_custom_plugin.py
import pytest
from pathlib import Path
from app.plugins.plugin_manager import PluginManager
from app.plugins.plugin_schema import PluginManifestSchema
import yaml

@pytest.fixture
def plugin_manifest(tmp_path: Path) -> Path:
    """Create temporary plugin manifest."""
    manifest_dir = tmp_path / "mytool"
    manifest_dir.mkdir()

    manifest_file = manifest_dir / "plugin.yaml"
    manifest_file.write_text("""
name: MyTool
version: 1.0.0
description: Test tool
homepage: https://example.com
mandatory: false
enabled: true
source:
  type: url
  uri: https://example.com/mytool.zip
  checksum_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
command:
  path: bin
  executable: mytool.exe
  register_to_path: false
dependencies: []
    """)

    return manifest_file

def test_manifest_schema_valid(plugin_manifest: Path):
    """Test manifest passes Pydantic validation."""
    with open(plugin_manifest) as f:
        data = yaml.safe_load(f)

    manifest = PluginManifestSchema(**data)
    assert manifest.name == "MyTool"

def test_plugin_discovery(tmp_path: Path, plugin_manifest: Path):
    """Test plugin is discovered by PluginManager."""
    plugins_dir = tmp_path / "plugins"
    manifests_dir = plugin_manifest.parent.parent

    manager = PluginManager(plugins_dir, manifests_dir)
    count = manager.discover_plugins()

    assert count == 1
    assert "MyTool" in manager.plugins

@pytest.mark.asyncio
async def test_plugin_download_mock(tmp_path: Path, mocker):
    """Test plugin download with mocked HTTP."""
    # Mock aiohttp response
    mock_response = mocker.AsyncMock()
    mock_response.status = 200
    mock_response.headers = {"Content-Length": "1024"}
    mock_response.content.iter_chunked = mocker.AsyncMock(
        return_value=[b"test" * 256]  # 1024 bytes
    )

    mock_session = mocker.AsyncMock()
    mock_session.get.return_value.__aenter__.return_value = mock_response

    mocker.patch("aiohttp.ClientSession", return_value=mock_session)

    # Create plugin
    from app.plugins.plugin_base import SimplePluginImplementation, PluginManifest

    manifest = PluginManifest(
        name="TestPlugin",
        version="1.0.0",
        mandatory=False,
        enabled=True,
        source_type="url",
        source_uri="https://example.com/test.zip",
        checksum_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )

    plugin = SimplePluginImplementation(manifest, tmp_path)

    # Download (will fail checksum but tests HTTP logic)
    try:
        result = await plugin.download()
    except Exception:
        pass  # Expected: checksum mismatch

    mock_session.get.assert_called_once()
```

### Integration Testing

```python
# tests/integration/test_plugin_workflow.py
import pytest
from pathlib import Path
from app.plugins.plugin_manager import PluginManager

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_plugin_lifecycle(tmp_path: Path):
    """Test complete plugin workflow: discover → install → validate."""
    # This test requires actual plugin manifest and download URL
    # Use small test file (<1MB) for fast execution

    manifests_dir = Path("plugins")
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()

    manager = PluginManager(plugins_dir, manifests_dir)

    # Discover
    count = manager.discover_plugins()
    assert count > 0

    # Choose smallest plugin for testing
    test_plugin = min(
        manager.manifests.values(),
        key=lambda m: m.file_size or float('inf')
    )

    # Install
    success = await manager.install_plugin(test_plugin.name)
    assert success

    # Validate
    plugin = manager.plugins[test_plugin.name]
    assert plugin.validate_installation()

    # Get version
    version = plugin.get_version()
    assert version is not None
```

---

(publishing-plugins)=

## 📤 Publishing Plugins

### Official Plugin Repository

pyMM maintains official plugins in `plugins/` directory:

```
plugins/
├── git/plugin.yaml
├── ffmpeg/plugin.yaml
├── exiftool/plugin.yaml
├── imagemagick/plugin.yaml
└── ...
```

**Contribution Process**:

1. **Fork Repository**:
   ```bash
   git clone https://github.com/mosh666/pyMM.git
   cd pyMM
   git checkout -b add-plugin-xyz
   ```

2. **Create Plugin**:
   ```bash
   mkdir plugins/xyz
   # Create plugins/xyz/plugin.yaml
   ```

3. **Test Plugin**:
   ```bash
   pytest tests/unit/test_plugin_manager.py -k xyz
   pytest tests/integration/ -k plugin
   ```

4. **Validate Quality**:
   ```bash
   # Lint
   ruff check plugins/xyz/plugin.yaml

   # Type check
   mypy app/plugins/

   # Security checks (included in Ruff)
   ruff check app/plugins/ --select=S
   ```

5. **Submit Pull Request**:
   ```bash
   git add plugins/xyz/
   git commit -m "feat(plugins): add XYZ plugin v1.2.3"
   git push origin add-plugin-xyz
   ```

   Open PR at: https://github.com/mosh666/pyMM/compare

---

### Community Plugin Distribution

For unofficial/experimental plugins:

1. **Create Repository**:
   ```
   my-pymm-plugins/
   ├── README.md
   ├── mytool/
   │   └── plugin.yaml
   └── anothertool/
       └── plugin.yaml
   ```

2. **Document Usage**:
   ```markdown
   # My pyMM Plugins

   ## Installation
   1. Download plugin manifest: `mytool/plugin.yaml`
   2. Copy to: `D:\pyMM\plugins\mytool\plugin.yaml`
   3. Restart pyMM
   4. Navigate to Plugin View → Refresh Plugins
   5. Install "MyTool"
   ```

3. **Version Management**:
   - Use semantic versioning in `version` field
   - Update `checksum_sha256` for each release
   - Maintain CHANGELOG.md

---

(best-practices)=

## ✅ Best Practices

### 1. Platform Detection (Python 3.12+)

> **⚠️ Deprecation Notice**: Direct usage of `sys.platform`, `os.name`, or `platform.system()`
> in plugin code is deprecated and will emit `DeprecationWarning` during plugin discovery.
> This behavior can be made strict (raising errors) by setting `strict_platform_checks: true`
> in `config/app.yaml`.

**✅ DO**: Use the centralized Platform module

```python
from app.core.platform import (
    Platform,
    current_platform,
    is_windows,
    is_linux,
    is_macos,
    is_unix,
)

# Simple boolean checks
if is_windows():
    executable = "tool.exe"
else:
    executable = "tool"

# Match statements for platform-specific logic
match current_platform():
    case Platform.WINDOWS:
        config_path = Path(os.environ["APPDATA"]) / "MyTool"
    case Platform.MACOS:
        config_path = Path.home() / "Library" / "Application Support" / "MyTool"
    case Platform.LINUX:
        config_path = Path.home() / ".config" / "mytool"
```

**❌ DON'T**: Use direct platform checks

```python
import sys
import platform

# Deprecated - will emit DeprecationWarning
if sys.platform == "win32":
    ...

# Deprecated
if platform.system() == "Windows":
    ...

# Deprecated
import os
if os.name == "nt":
    ...
```

**Deprecation Timeline**:

- **v2.5.0** (January 2026): DeprecationWarning emitted during plugin discovery
- **v3.0.0** (July 2026): Strict mode becomes default (`strict_platform_checks: true`)
- **v4.0.0** (2027): Direct platform checks will fail plugin validation

**Configuration** (`config/app.yaml`):

```yaml
# Plugin platform usage checking
# When false: Emit DeprecationWarning for sys.platform/os.name/platform.system() usage
# When true: Raise ImportError for deprecated platform usage (enforced in v3.0.0+)
strict_platform_checks: false
```

---

### 2. Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Plugin Name | TitleCase, official spelling | `Git`, `FFmpeg`, `DigiKam` |
| Directory | Lowercase, no spaces | `git/`, `ffmpeg/`, `digikam/` |
| Executable | Exact case, with extension | `git.exe`, `ffmpeg.exe` |

### 2. Version Pinning

**✅ DO**: Pin exact versions
```yaml
version: 2.47.1
source:
  uri: https://example.com/tool-2.47.1.zip
```

**❌ DON'T**: Use "latest" or floating versions
```yaml
version: latest  # Bad!
source:
  uri: https://example.com/tool-latest.zip
```

**Reason**: Ensures reproducible installations, prevents breaking changes.

---

### 3. Checksum Verification

**Always include SHA-256 checksums**:

```powershell
# Windows PowerShell
Get-FileHash tool.zip -Algorithm SHA256 | Select-Object Hash

# Linux/macOS
shasum -a 256 tool.zip
```

**Handling Checksum Changes**:
- If upstream updates file without version change, verify legitimacy
- Contact tool maintainer if suspicious
- Update checksum only after manual verification

---

### 4. File Size Hints

**Include `file_size` for large downloads**:

```yaml
source:
  uri: https://example.com/huge-tool.zip
  checksum_sha256: "abc123..."
  file_size: 524288000  # 500 MB
```

**Benefits**:
- Progress bar accuracy
- Early disk space validation
- Download completion verification

---

### 5. Path Registration

**Use `register_to_path: true` for command-line tools**:

```yaml
command:
  executable: git.exe
  register_to_path: true  # Makes 'git' available in CMD
```

**Use `register_to_path: false` for GUI applications**:

```yaml
command:
  executable: digikam.exe
  register_to_path: false  # Not a CLI tool
```

---

### 6. Dependency Management

**Minimize dependencies**:

```yaml
# ✅ Good: Only essential dependencies
dependencies:
  - Git

# ❌ Bad: Transitive dependencies
dependencies:
  - Git
  - Python  # Git doesn't need Python, user's project might
```

**Circular dependency detection**:

```yaml
# plugin-a.yaml
dependencies:
  - PluginB

# plugin-b.yaml
dependencies:
  - PluginA  # Error: circular dependency!
```

Plugin Manager will detect and reject circular dependencies.

---

### 7. Documentation

**Include comprehensive metadata**:

```yaml
name: MyTool
version: 3.2.1
description: |
  Comprehensive tool description with features:
  - Feature 1: Image processing
  - Feature 2: Video encoding
  - Feature 3: Batch operations
homepage: https://example.com/mytool
```

**Link to documentation**:

```yaml
# Add custom field (allowed by Pydantic extra="allow")
documentation: https://example.com/mytool/docs
license: MIT
repository: https://github.com/example/mytool
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Schema Validation Failed"

**Symptom**:
```
ERROR Plugin manifest validation failed: plugins/mytool/plugin.yaml
ValidationError: 1 validation error for PluginManifestSchema
source.checksum_sha256
  String should match pattern '^[a-f0-9]{64}$'
```

**Solution**: Verify checksum is 64-character hex string (no spaces, lowercase).

```powershell
# Correct format:
checksum_sha256: "a1b2c3d4e5f6..."

# Wrong format:
checksum_sha256: "A1B2C3D4E5F6..."  # Uppercase
checksum_sha256: "a1b2 c3d4 e5f6"    # Spaces
```

---

#### 2. "Checksum Mismatch"

**Symptom**:
```
ERROR Checksum verification failed for MyTool
Expected: abc123...
Actual:   def456...
```

**Causes**:
1. Downloaded file corrupted
2. Wrong checksum in manifest
3. Upstream file changed without version bump

**Solution**:
```powershell
# Re-download and calculate checksum
Invoke-WebRequest -Uri "https://example.com/tool.zip" -OutFile "tool-verify.zip"
Get-FileHash tool-verify.zip -Algorithm SHA256

# Compare with manifest
# If different, update manifest or report upstream issue
```

---

#### 3. "Extraction Failed"

**Symptom**:
```
ERROR Failed to extract MyTool: [WinError 32] The process cannot access the file
```

**Causes**:
1. Archive corrupted
2. Insufficient disk space
3. File in use by another process

**Solution**:
```python
# Enable debug logging
logging:
  level: DEBUG

# Retry installation with verbose output
```

---

#### 4. "Executable Not Found"

**Symptom**:
```
ERROR Validation failed: git.exe not found in D:\pyMM.Plugins\git\cmd\
```

**Causes**:
1. Wrong `command.path` in manifest
2. Archive structure differs from expected

**Solution**:
```powershell
# Manually extract and inspect structure
Expand-Archive tool.zip test-dir
tree /F test-dir

# Update manifest command.path to match actual structure
```

---

#### 5. "GitHub Asset Not Found"

**Symptom**:
```
ERROR No matching asset found for pattern: "tool-.*-win64\.zip$"
Available assets:
  - tool-1.2.3-windows-x64.zip
  - tool-1.2.3-linux-x64.tar.gz
```

**Solution**: Adjust `asset_pattern` to match available assets.

```yaml
# Before (wrong):
asset_pattern: "tool-.*-win64\\.zip$"

# After (correct):
asset_pattern: "tool-.*-windows-x64\\.zip$"
```

---

## � Plugin System v2: Hybrid Executable Resolution

### Overview

Plugin System v2 introduces **hybrid executable resolution** that supports both system-installed tools and portable versions, giving users flexibility in how they configure their environment.

### Key Features

✅ **System Tool Detection**: Automatically finds tools in PATH
✅ **Version Validation**: Ensures system tools meet minimum version requirements
✅ **User Preferences**: Configure per-plugin execution preferences
✅ **Fallback Logic**: Graceful fallback from system to portable
✅ **Plugin Migration**: Automated v1→v2 migration with rollback support

### Platform Configuration

Plugin manifests now support platform-specific configurations:

```yaml
schema_version: 2

name: Git
version: 2.47.1
description: Distributed version control system
homepage: https://git-scm.com
mandatory: false
enabled: true

# Platform configurations (new in v2)
platforms:
  windows:
    source:
      type: github
      uri: git-for-windows/git
      asset_pattern: "PortableGit-.*-64-bit\\.7z\\.exe$"
      checksum_sha256: "f9a9d5c1..."

    command:
      path: cmd
      executable: git.exe
      register_to_path: true

    system_detection:
      executable_name: git
      version_command: ["git", "--version"]
      version_pattern: "git version (\\d+\\.\\d+\\.\\d+)"
      minimum_version: "2.40.0"

  linux:
    system_detection:
      executable_name: git
      version_command: ["git", "--version"]
      version_pattern: "git version (\\d+\\.\\d+\\.\\d+)"
      minimum_version: "2.40.0"

  macos:
    system_detection:
      executable_name: git
      version_command: ["git", "--version"]
      version_pattern: "git version (\\d+\\.\\d+\\.\\d+)"
      minimum_version: "2.40.0"

dependencies: []
```

### System Tool Detection

The `SystemToolDetector` discovers system-installed tools:

```python
from app.plugins.system_tool_detector import SystemToolDetector

detector = SystemToolDetector()

# Detect Git in PATH
result = detector.detect_tool(
    executable_name="git",
    version_command=["git", "--version"],
    version_pattern=r"git version (\d+\.\d+\.\d+)",
    minimum_version="2.40.0"
)

if result:
    print(f"Found: {result.path}")
    print(f"Version: {result.version}")
    print(f"Meets minimum: {result.meets_minimum_version}")
```

### ExecutableSource Enum

Plugins now support explicit source selection:

```python
class ExecutableSource(str, Enum):
    """Source of plugin executable."""
    SYSTEM = "system"      # Use system-installed tool
    PORTABLE = "portable"  # Use portable version
    AUTO = "auto"          # Try system first, fallback to portable
```

### User Preferences

Users can configure per-plugin execution preferences:

```yaml
# config/plugins.yaml
plugin_preferences:
  git:
    execution_preference: system  # Always use system Git
    enabled: true
    notes: "Using system Git for better integration"

  ffmpeg:
    execution_preference: portable  # Always use portable FFmpeg
    enabled: true
    notes: "Portable version includes custom codecs"

  exiftool:
    execution_preference: auto  # Auto-detect (default)
    enabled: true
    notes: ""
```

**Configuration via UI:**

1. Open **Settings** → **Plugin Preferences**
2. Select plugin from list
3. Choose execution preference:
   - **Auto**: Try system first, fallback to portable
   - **System Only**: Only use system-installed tool
   - **Portable Only**: Only use portable version
4. Click **Save**

### Version Validation Dialog

When a system tool doesn't meet version requirements, users see:

```
┌─────────────────────────────────────────┐
│ Version Mismatch Detected               │
├─────────────────────────────────────────┤
│ Plugin: Git                             │
│                                         │
│ System version: 2.35.1                  │
│ Required version: ≥2.40.0               │
│                                         │
│ The system-installed version does not   │
│ meet the minimum requirement.           │
│                                         │
│ Choose an action:                       │
│  ○ Use system version anyway            │
│  ● Download and use portable version    │
│  ○ Disable this plugin                  │
│                                         │
│           [ Cancel ]    [ OK ]          │
└─────────────────────────────────────────┘
```

### Migration from v1 to v2

The plugin migrator automatically upgrades v1 manifests:

**Using justfile:**
```bash
# Dry run (preview changes)
just migrate-plugins dry-run

# Apply migration
just migrate-plugins apply

# Rollback if needed
just migrate-plugins rollback
```

**Using Python:**
```python
from app.plugins.plugin_migrator import PluginMigrator
from pathlib import Path

migrator = PluginMigrator(
    plugins_dir=Path("plugins"),
    backup_dir=Path("backups/plugins")
)

# Preview migration
report = migrator.dry_run()
print(f"Will migrate {len(report['to_migrate'])} plugins")

# Apply migration with backup
results = migrator.migrate_all(
    backup=True,
    skip_on_error=False
)

# Rollback if something went wrong
migrator.rollback_all()
```

### Migration Example

**Before (v1):**
```yaml
name: Git
version: 2.47.1
description: Distributed version control system
homepage: https://git-scm.com
mandatory: false
enabled: true

source:
  type: github
  uri: git-for-windows/git
  asset_pattern: "PortableGit-.*-64-bit\\.7z\\.exe$"
  checksum_sha256: "f9a9d5c1..."

command:
  path: cmd
  executable: git.exe
  register_to_path: true

dependencies: []
```

**After (v2):**
```yaml
schema_version: 2

name: Git
version: 2.47.1
description: Distributed version control system
homepage: https://git-scm.com
mandatory: false
enabled: true

platforms:
  windows:
    source:
      type: github
      uri: git-for-windows/git
      asset_pattern: "PortableGit-.*-64-bit\\.7z\\.exe$"
      checksum_sha256: "f9a9d5c1..."

    command:
      path: cmd
      executable: git.exe
      register_to_path: true

    system_detection:
      executable_name: git
      version_command: ["git", "--version"]
      version_pattern: "git version (\\d+\\.\\d+\\.\\d+)"
      minimum_version: "2.40.0"

dependencies: []
```

### Backward Compatibility

v2 plugins are **backward compatible** with v1 behavior:

- If `schema_version: 2` is omitted, manifest is treated as v1
- v1 manifests continue to work without migration
- Migration is optional but recommended

### Testing v2 Plugins

```python
import pytest
from app.plugins.plugin_manager import PluginManager
from app.plugins.plugin_schema import PluginManifestV2

def test_v2_schema_validation():
    """Test v2 schema validation."""
    manifest_data = {
        "schema_version": 2,
        "name": "TestPlugin",
        "version": "1.0.0",
        "platforms": {
            "windows": {
                "system_detection": {
                    "executable_name": "test",
                    "version_command": ["test", "--version"],
                    "version_pattern": r"(\d+\.\d+\.\d+)",
                    "minimum_version": "1.0.0"
                }
            }
        }
    }

    manifest = PluginManifestV2.model_validate(manifest_data)
    assert manifest.schema_version == 2
    assert "windows" in manifest.platforms

def test_system_tool_detection():
    """Test system tool detection."""
    from app.plugins.system_tool_detector import SystemToolDetector

    detector = SystemToolDetector()
    result = detector.detect_tool(
        executable_name="python",
        version_command=["python", "--version"],
        version_pattern=r"Python (\d+\.\d+\.\d+)",
        minimum_version="3.12.0"
    )

    assert result is not None
    assert result.path.exists()
    assert result.version
```

---

## �📚 API Reference

### PluginManifest Dataclass

```python
@dataclass
class PluginManifest:
    """Plugin manifest configuration."""

    name: str
    version: str
    mandatory: bool
    enabled: bool
    source_type: str  # 'url' or 'github'
    source_uri: str
    asset_pattern: str | None = None
    command_path: str = ""
    command_executable: str = ""
    register_to_path: bool = False
    dependencies: list[str] = field(default_factory=list)
    checksum_sha256: str | None = None
    file_size: int | None = None
```

---

### PluginBase Abstract Class

```python
class PluginBase(ABC):
    """Abstract base class for plugins."""

    def __init__(self, manifest: PluginManifest, install_dir: Path):
        """
        Initialize plugin.

        Args:
            manifest: Plugin manifest configuration
            install_dir: Directory where plugin will be installed
        """

    @abstractmethod
    async def download(
        self,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """
        Download plugin binaries.

        Args:
            progress_callback: Optional callback for progress updates
                              (current_bytes, total_bytes) -> None

        Returns:
            True if download successful
        """

    @abstractmethod
    async def extract(self) -> bool:
        """
        Extract downloaded plugin archive.

        Returns:
            True if extraction successful
        """

    @abstractmethod
    def validate_installation(self) -> bool:
        """
        Validate that plugin is properly installed.

        Returns:
            True if plugin is installed and functional
        """

    @abstractmethod
    def get_version(self) -> str | None:
        """
        Get installed plugin version.

        Returns:
            Version string or None if not installed
        """

    def get_executable_path(self) -> Path | None:
        """
        Get path to plugin executable.

        Returns:
            Path to executable or None if not found
        """
```

---

### PluginManager Class

```python
class PluginManager:
    """Manager for application plugins."""

    def __init__(self, plugins_dir: Path, manifests_dir: Path):
        """
        Initialize plugin manager.

        Args:
            plugins_dir: Directory where plugins are installed
            manifests_dir: Directory containing plugin manifest YAML files
        """

    def discover_plugins(self) -> int:
        """
        Discover plugins from manifest files.

        Returns:
            Number of plugins discovered
        """

    async def install_plugin(
        self,
        plugin_name: str,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> bool:
        """
        Install plugin with progress tracking.

        Args:
            plugin_name: Name of plugin to install
            progress_callback: Optional progress callback

        Returns:
            True if installation succeeded
        """

    def get_installed_plugins(self) -> list[str]:
        """
        Get list of installed plugin names.

        Returns:
            List of plugin names
        """

    def get_plugin_status(self, plugin_name: str) -> dict[str, Any]:
        """
        Get detailed status for a plugin.

        Args:
            plugin_name: Name of plugin

        Returns:
            Dictionary with keys:
              - installed: bool
              - version: str | None
              - enabled: bool
              - path: str | None
        """
```

---

## 📖 Additional Resources

### Official Documentation

- [Architecture Documentation](architecture.md)
- [Installation](installation.md)
- [Getting Started](getting-started.md)
- [Contributing Guidelines](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md)

### External References

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Semantic Versioning](https://semver.org/)
- [YAML Specification](https://yaml.org/spec/1.2.2/)

### Example Plugins

Study official plugin manifests:

- [Git Plugin](../plugins/git/plugin.yaml)
- [FFmpeg Plugin](../plugins/ffmpeg/plugin.yaml)
- [ExifTool Plugin](../plugins/exiftool/plugin.yaml)

---

## 🤝 Community

### Getting Help

- **GitHub Issues**: https://github.com/mosh666/pyMM/issues
- **Email**: 24556349+mosh666@users.noreply.github.com

### Contributing

We welcome plugin contributions! See [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) for:

- Code of Conduct
- Development setup
- Testing requirements
- PR submission process

---

**Document Version:** 1.0.0
**Last Updated:** January 7, 2026
**Maintainer:** @mosh666
**Status:** ✅ Current
