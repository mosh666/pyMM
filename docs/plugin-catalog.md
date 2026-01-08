# Plugin Catalog

> **Last Updated:** January 8, 2026

Complete catalog of official plugins available for pyMediaManager. All plugins use YAML manifests and SHA-256
verification for security.

## Table of Contents

- [Official Plugins](#official-plugins)
- [Plugin Installation](#plugin-installation)
- [Plugin Management](#plugin-management)
- [Creating Custom Plugins](#creating-custom-plugins)

---

## Official Plugins

### Version Control

#### Git

**Description:** Distributed version control system for tracking changes in projects

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Initialize repositories
- Commit changes
- Branch management
- Push/pull from remotes
- Conflict resolution

**System Requirements:**

- Git 2.40+

**Installation:**

- **Windows:** Download from <https://git-scm.com/download/win>
- **Linux:** `sudo apt install git` (Ubuntu/Debian) or equivalent
- **macOS:** `brew install git` or Xcode Command Line Tools

**Plugin File:** [plugins/git/plugin.yaml](../plugins/git/plugin.yaml)

---

#### Git LFS (Large File Storage)

**Description:** Git extension for versioning large files

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Track large media files (video, images, audio)
- Automatic LFS pointer management
- Bandwidth-efficient clones
- Integrates with Git workflow

**System Requirements:**

- Git 2.40+
- Git LFS 3.0+

**Installation:**

- **Windows:** Included with Git for Windows, or download from <https://git-lfs.github.com/>
- **Linux:** `sudo apt install git-lfs`
- **macOS:** `brew install git-lfs`

**Recommended For:** Video editing, photography projects with RAW files

**Plugin File:** [plugins/gitlfs/plugin.yaml](../plugins/gitlfs/plugin.yaml)

---

#### GitVersion

**Description:** Semantic versioning tool for Git repositories

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Automatic version calculation from Git history
- Semantic versioning (SemVer 2.0)
- Branch-based versioning strategies
- CI/CD integration

**System Requirements:**

- Git 2.40+
- .NET Runtime 6.0+ (for GitVersion)

**Installation:**

- **Windows:** `dotnet tool install --global GitVersion.Tool`
- **Linux:** `dotnet tool install --global GitVersion.Tool`
- **macOS:** `dotnet tool install --global GitVersion.Tool`

**Plugin File:** [plugins/gitversion/plugin.yaml](../plugins/gitversion/plugin.yaml)

---

### Media Processing

#### FFmpeg

**Description:** Complete multimedia framework for video/audio processing

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Video transcoding and conversion
- Audio extraction and processing
- Thumbnail generation
- Format support: MP4, MKV, AVI, MOV, WebM, etc.
- Codec support: H.264, H.265, VP9, AV1, etc.

**System Requirements:**

- FFmpeg 5.0+

**Installation:**

- **Windows:** Download from <https://ffmpeg.org/download.html#build-windows>
- **Linux:** `sudo apt install ffmpeg`
- **macOS:** `brew install ffmpeg`

**Recommended For:** Video editing, media conversion projects

**Plugin File:** [plugins/ffmpeg/plugin.yaml](../plugins/ffmpeg/plugin.yaml)

---

#### MKVToolNix

**Description:** Tools for creating, editing and inspecting Matroska (MKV) files

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- MKV file creation and editing
- Track manipulation (add, remove, reorder)
- Chapter management
- Metadata editing
- Splitting and merging MKV files

**System Requirements:**

- MKVToolNix 70.0+

**Installation:**

- **Windows:** Download from <https://mkvtoolnix.download/downloads.html#windows>
- **Linux:** `sudo apt install mkvtoolnix`
- **macOS:** `brew install mkvtoolnix`

**Recommended For:** Video editing projects using MKV format

**Plugin File:** [plugins/mkvtoolnix/plugin.yaml](../plugins/mkvtoolnix/plugin.yaml)

---

### Image Processing

#### ExifTool

**Description:** Read, write and edit metadata in image, video and audio files

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Read/write EXIF, IPTC, XMP metadata
- Support for 100+ file formats
- Batch processing
- GPS coordinate handling
- Date/time correction

**System Requirements:**

- Perl 5.8+ (often pre-installed on Linux/macOS)

**Installation:**

- **Windows:** Download from <https://exiftool.org/>
- **Linux:** `sudo apt install libimage-exiftool-perl`
- **macOS:** `brew install exiftool`

**Recommended For:** Photography projects, metadata management

**Plugin File:** [plugins/exiftool/plugin.yaml](../plugins/exiftool/plugin.yaml)

---

#### ImageMagick

**Description:** Create, edit, compose, and convert bitmap images

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Format conversion (JPEG, PNG, GIF, TIFF, etc.)
- Image resizing and scaling
- Color correction and enhancement
- Batch processing
- Composite image creation

**System Requirements:**

- ImageMagick 7.0+

**Installation:**

- **Windows:** Download from <https://imagemagick.org/script/download.php#windows>
- **Linux:** `sudo apt install imagemagick`
- **macOS:** `brew install imagemagick`

**Recommended For:** Photography projects, batch image processing

**Plugin File:** [plugins/imagemagick/plugin.yaml](../plugins/imagemagick/plugin.yaml)

---

#### DigiKam

**Description:** Professional photo management and editing application

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- Photo organization and tagging
- RAW file support
- Batch processing
- Face recognition
- Geo-location tagging
- Integrated editor

**System Requirements:**

- DigiKam 8.0+

**Installation:**

- **Windows:** Download from <https://www.digikam.org/download/>
- **Linux:** `sudo apt install digikam`
- **macOS:** Download DMG from <https://www.digikam.org/download/>

**Recommended For:** Photography projects, large photo collections

**Plugin File:** [plugins/digikam/plugin.yaml](../plugins/digikam/plugin.yaml)

---

### Database

#### MariaDB

**Description:** Open-source relational database (MySQL-compatible)

**Supported Platforms:** Windows, Linux, macOS

**Features:**

- SQL database for project metadata
- High performance and scalability
- ACID compliance
- Replication support

**System Requirements:**

- MariaDB 10.6+

**Installation:**

- **Windows:** Download from <https://mariadb.org/download/>
- **Linux:** `sudo apt install mariadb-server`
- **macOS:** `brew install mariadb`

**Recommended For:** Advanced users, large-scale projects with custom metadata

**Plugin File:** [plugins/mariadb/plugin.yaml](../plugins/mariadb/plugin.yaml)

---

## Plugin Installation

### Automatic Installation

pyMediaManager can automatically detect system-installed tools:

1. Open **Settings → Plugins**
2. Click **Refresh System Tools**
3. pyMM will scan common installation paths
4. Detected plugins appear with green checkmark

### Manual Installation

If auto-detection fails:

1. Install the tool using instructions above
2. Open **Settings → Plugins → [Plugin Name]**
3. Click **Locate Manually**
4. Browse to executable:
   - **Windows:** Usually in `C:\Program Files\`
   - **Linux:** Usually in `/usr/bin/` or `/usr/local/bin/`
   - **macOS:** Usually in `/usr/local/bin/` or `/opt/homebrew/bin/`

### Download-Based Plugins

Some plugins can download portable versions:

1. **Settings → Plugins → [Plugin Name]**
2. Click **Download Portable Version**
3. pyMM downloads, verifies SHA-256 checksum
4. Extracts to `pyMM.Plugins/[plugin-name]/`

**Security:** All downloads verified with SHA-256 checksums defined in plugin manifests.

---

## Plugin Management

### Enabling/Disabling Plugins

**Via UI:**

- Settings → Plugins
- Toggle switch next to plugin name

**Via Configuration:**

```yaml
# config/user.yaml
plugins:
  disabled:
    - legacy-plugin
    - experimental-tool
```

### Updating Plugins

**System-Installed Tools:**

- Update tools using your system package manager
- Windows: Download new installer
- Linux: `sudo apt update && sudo apt upgrade`
- macOS: `brew upgrade`

**Portable Plugins:**

- Settings → Plugins → [Plugin Name]
- Click **Check for Updates**
- If available, click **Update**

### Plugin Priorities

When multiple versions of a tool are installed:

1. **Manually specified path** (highest priority)
2. **System PATH** (e.g., `/usr/bin/git`)
3. **Portable plugin** (downloaded by pyMM)
4. **Bundled version** (lowest priority, rarely used)

Change priority in Settings → Plugins → [Plugin Name] → Preferences

---

## Plugin Feature Matrix

| Plugin | Version Control | Media Processing | Metadata | Batch Ops | Cross-Platform |
| -------- | ---------------- | ------------------ | ---------- | ----------- | ---------------- |
| Git | ✅ | ❌ | ❌ | ❌ | ✅ |
| Git LFS | ✅ | ❌ | ❌ | ❌ | ✅ |
| GitVersion | ✅ | ❌ | ❌ | ❌ | ✅ |
| FFmpeg | ❌ | ✅ | ✅ | ✅ | ✅ |
| MKVToolNix | ❌ | ✅ | ✅ | ✅ | ✅ |
| ExifTool | ❌ | ❌ | ✅ | ✅ | ✅ |
| ImageMagick | ❌ | ✅ | ❌ | ✅ | ✅ |
| DigiKam | ❌ | ✅ | ✅ | ✅ | ✅ |
| MariaDB | ❌ | ❌ | ✅ | ❌ | ✅ |

---

## Creating Custom Plugins

Want to add your own tools? See [Plugin Development Guide](plugin-development.md) for:

- YAML manifest format
- Plugin schema reference
- Security best practices
- Testing and validation

---

## Plugin Compatibility

### Minimum pyMM Version

All listed plugins require **pyMediaManager v1.0+**

### Python Version

Plugins work with **Python 3.12, 3.13, 3.14**

### Platform Support

All official plugins support **Windows 10+, Linux (Ubuntu 20.04+), macOS 11+**

---

## Troubleshooting Plugins

Common issues and solutions in [Troubleshooting Guide](troubleshooting.md#plugin-issues):

- Plugin not detected
- Download failures
- Version incompatibilities
- Permission issues

---

## Contributing Plugins

Want to contribute a plugin to the official catalog?

1. Create plugin manifest following [Plugin Development Guide](plugin-development.md)
2. Test on all supported platforms
3. Submit Pull Request to <https://github.com/mosh666/pyMM>
4. Include:
   - Plugin YAML manifest
   - README with installation instructions
   - SHA-256 checksums for downloadable binaries
   - Test coverage

---

**Document Version:** 1.0
**Last Updated:** January 8, 2026
**Total Official Plugins:** 9
**Compatible with:** pyMediaManager v1.0+
