.. _configuration:

# Configuration & Troubleshooting

> **Last Updated:** 2026-01-17 21:41 UTC


<!-- markdownlint-disable MD013 MD033 MD036 MD051 -->

This guide covers configuration options, CLI usage, and troubleshooting.

.. seealso::
   Need help with features? See :ref:`features` for usage guides.
   First-time setup? See :ref:`getting-started` for the Quick Configuration Setup guide.

---

## 🚀 Quick Start: Configuration Templates

pyMediaManager provides configuration template files that you can copy and customize. These templates include comprehensive documentation for all available settings.

### Available Templates

| File                                    | Purpose                       | Required    |
|-----------------------------------------|-------------------------------|-------------|
| `config/user.yaml.example`              | User preferences and paths    | Recommended |
| `config/storage_groups.yaml.example`    | Master/Backup drive pairs     | Optional    |
| `config/app.yaml`                       | Default app settings          | Do NOT edit |

### Copy Configuration Templates

**Windows (PowerShell)**:

```powershell
# Navigate to pyMM directory
cd D:\pyMM  # Or your installation path

# Copy user configuration
Copy-Item config\user.yaml.example config\user.yaml

# Copy storage groups (if using Storage Groups feature)
Copy-Item config\storage_groups.yaml.example config\storage_groups.yaml
```

**Linux / macOS (Bash)**:

```bash
# Navigate to pyMM directory
cd ~/pyMM  # Or your installation path

# Copy user configuration
cp config/user.yaml.example config/user.yaml

# Copy storage groups (if using Storage Groups feature)
cp config/storage_groups.yaml.example config/storage_groups.yaml
```

> **Important**: `user.yaml` overrides settings in `app.yaml`. Never edit `app.yaml` directly—your changes will be lost on updates. Always use `user.yaml` for customization.

For complete first-time setup instructions, see the {ref}`quick-configuration-setup` guide.

---

## 🐚 Environment Variables

pyMediaManager supports several environment variables for advanced configuration and development:

### Core Environment Variables

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `PYMM_PORTABLE` | `bool` | `true` (portable mode) | Set to `false` for non-portable installation mode |
| `PYMM_CONFIG_DIR` | `str` | Platform-specific | Override configuration directory path |
| `PYMM_PROJECTS_DIR` | `str` | `pyMM.Projects` | Override default projects directory |
| `PYMM_PLUGINS_DIR` | `str` | `pyMM.Plugins` | Override plugins installation directory |
| `PYMM_LOG_LEVEL` | `str` | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `PYMM_DEBUG` | `bool` | `false` | Enable debug mode with verbose logging |

### Build System Variables

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `UV_CACHE_DIR` | `str` | Platform-specific | UV package cache location |
| `UV_PYTHON` | `str` | Auto-detected | Force specific Python version for UV |
| `HATCH_BUILD_CLEAN` | `bool` | `false` | Clean build artifacts before building |

### Development Variables

| Variable | Type | Default | Description |
| -------- | ---- | ------- | ----------- |
| `PYTEST_TIMEOUT` | `int` | `300` | Test timeout in seconds |
| `PYTEST_WORKERS` | `int` | Auto | Number of parallel test workers |
| `QT_QPA_PLATFORM` | `str` | Auto | Qt platform plugin (`offscreen` for headless tests) |

### Usage Examples

**Windows (PowerShell):**

```powershell
# Enable debug mode
$env:PYMM_DEBUG="true"
$env:PYMM_LOG_LEVEL="DEBUG"
python launcher.py

# Use non-portable mode
$env:PYMM_PORTABLE="false"
python launcher.py

# Override projects directory
$env:PYMM_PROJECTS_DIR="D:\MyProjects"
python launcher.py
```

**Linux/macOS (Bash):**

```bash
# Enable debug mode
export PYMM_DEBUG=true
export PYMM_LOG_LEVEL=DEBUG
python launcher.py

# Use non-portable mode
export PYMM_PORTABLE=false
python launcher.py

# Override configuration directory
export PYMM_CONFIG_DIR="$HOME/.config/pymm-custom"
python launcher.py
```

**Persistent Configuration:**

For permanent environment variables, add to your shell profile:

```bash
# ~/.bashrc or ~/.zshrc (Linux/macOS)
export PYMM_LOG_LEVEL=DEBUG
export PYMM_PORTABLE=false
```

```powershell
# PowerShell profile ($PROFILE)
$env:PYMM_LOG_LEVEL="DEBUG"
$env:PYMM_PORTABLE="false"
```

### Portable Mode Behavior

When `PYMM_PORTABLE=true` (default):

- All paths are relative to installation directory
- Data stored in `pyMM.Projects`, `pyMM.Logs`, etc.
- Ideal for USB drives and portable installations
- No system registry/config modifications

When `PYMM_PORTABLE=false`:

- Uses platform-specific standard directories (XDG, AppData, Library)
- Projects in `~/Documents/pyMM.Projects` or similar
- Logs in system log directories
- Follows OS conventions for installed applications

---

## ⚙️ Configuration

### Application Settings

Access via **⚙️ Settings** button or `Ctrl+,`:

#### General Settings

```text
General
┌─────────────────────────────────────────┐
│ Language: English                       │
│ Theme: Auto (follows system)            │
│ ○ Light  ○ Dark  ● Auto                 │
│                                         │
│ Startup:                                │
│ ☑ Launch on Windows startup             │
│ ☑ Restore last session                  │
│ ☐ Check for updates on startup          │
│                                         │
│ Default Locations:                      │
│ Projects: D:\pyMM.Projects              │
│ [Browse]                                │
│                                         │
│ Plugins: D:\pyMM.Plugins                │
│ [Browse]                                │
└─────────────────────────────────────────┘
```

#### Performance Settings

```text
Performance
┌─────────────────────────────────────────┐
│ Processing:                             │
│ Thread Pool Size: Auto (8 threads)      │
│ Max Memory Usage: 4096 MB               │
│                                         │
│ Cache:                                  │
│ Thumbnail Cache: 512 MB                 │
│ ☑ Preload thumbnails                    │
│ ☑ Cache metadata                        │
│                                         │
│ Network:                                │
│ Download Threads: 4                     │
│ Connection Timeout: 30 seconds          │
└─────────────────────────────────────────┘
```

#### Privacy Settings

```text
Privacy
┌─────────────────────────────────────────┐
│ Data Collection:                        │
│ ☐ Send anonymous usage statistics       │
│ ☐ Send crash reports                    │
│                                         │
│ Logging:                                │
│ Log Level: INFO                         │
│ ☑ Log to file                           │
│ ☐ Enable debug logging                  │
│                                         │
│ Auto-Save:                              │
│ ☑ Auto-save project changes             │
│ Save interval: 5 minutes                │
└─────────────────────────────────────────┘
```

### Configuration Files

pyMM stores configuration in platform-specific standard directories:

#### Platform-Specific Locations

**Windows:**

```text
Config:  %APPDATA%\pyMM\config\
Data:    %APPDATA%\pyMM\data\
Cache:   %LOCALAPPDATA%\pyMM\cache\
Logs:    %APPDATA%\pyMM\logs\

Example: C:\Users\YourName\AppData\Roaming\pyMM\
```

**Linux (XDG Base Directory):**

```text
Config:  $XDG_CONFIG_HOME/pyMM/  (default: ~/.config/pyMM/)
Data:    $XDG_DATA_HOME/pyMM/    (default: ~/.local/share/pyMM/)
Cache:   $XDG_CACHE_HOME/pyMM/   (default: ~/.cache/pyMM/)
Logs:    $XDG_STATE_HOME/pyMM/   (default: ~/.local/state/pyMM/)

Example: /home/username/.config/pyMM/
```

**macOS:**

```text
Config:  ~/Library/Application Support/pyMM/config/
Data:    ~/Library/Application Support/pyMM/data/
Cache:   ~/Library/Caches/pyMM/
Logs:    ~/Library/Logs/pyMM/

Example: /Users/YourName/Library/Application Support/pyMM/
```

#### Application Config (`app.yaml`)

**Location:** `{config_dir}/app.yaml`

```yaml
# Application-wide configuration
version: "1.0.0"

general:
  language: "en"
  theme: "auto"
  startup:
    launch_on_boot: true
    restore_session: true
    check_updates: false

paths:
  projects: "D:\\pyMM.Projects"
  plugins: "D:\\pyMM.Plugins"
  logs: "D:\\pyMM.Logs"
  config: "D:\\pyMM.Config"

performance:
  max_threads: 8
  max_memory_mb: 4096
  cache_size_mb: 512
  preload_thumbnails: true

network:
  download_threads: 4
  timeout_seconds: 30
  retry_attempts: 3
```

#### User Config (`D:\pyMM.Config\user.yaml`)

```yaml
# User-specific preferences
user:
  name: "User"
  email: "user@example.com"

ui:
  window:
    width: 1280
    height: 720
    maximized: false
  recent_projects:
    - "D:\\pyMM.Projects\\Client_Wedding_2026"
    - "D:\\pyMM.Projects\\Video_Project_Jan2026"
  sidebar_width: 250

privacy:
  telemetry_enabled: false
  crash_reports_enabled: false
  log_level: "INFO"
```

---

(command-line-interface)=

## 💻 Command Line Interface

pyMM provides a powerful CLI for automation and scripting:

### Basic Commands

```powershell
# Show version
pymm --version

# Show help
pymm --help

# Launch GUI
pymm

# Run in console mode (no GUI)
pymm --console
```

### Project Commands

```powershell
# Create new project
pymm create-project "MyProject" --type photo --location "D:\pyMM.Projects"

# Open project
pymm open-project "D:\pyMM.Projects\MyProject"

# List all projects
pymm list-projects

# Archive project
pymm archive-project "MyProject" --output "D:\Archives" --format 7z

# Delete project
pymm delete-project "MyProject" --confirm
```

### Plugin Commands

```powershell
# List available plugins
pymm list-plugins

# Install plugin
pymm install-plugin digikam

# Update plugin
pymm update-plugin digikam

# Remove plugin
pymm remove-plugin digikam --purge

# Show plugin info
pymm plugin-info digikam
```

### Storage Commands

```powershell
# Show storage usage
pymm storage-info

# Clean up temporary files
pymm cleanup --temp --logs --cache

# Move project to different drive
pymm move-project "MyProject" --destination "E:\pyMM.Projects"
```

### Advanced Commands

```powershell
# Export project metadata
pymm export-metadata "MyProject" --output "metadata.json"

# Import project from archive
pymm import-project "archive.7z" --destination "D:\pyMM.Projects"

# Run maintenance tasks
pymm maintenance --verify-integrity --optimize-db --rebuild-cache

# Generate project report
pymm generate-report "MyProject" --format pdf --output "report.pdf"
```

---

(troubleshooting)=

## 🔧 Troubleshooting

### Common Issues

#### Application Won't Start

**Symptoms**: Double-clicking launcher does nothing or shows error.

**Solutions**:

1. **Verify Python installation**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         python --version
         # Should show Python 3.12+ or 3.13+

   .. tab:: Linux

      .. code-block:: bash

         python3 --version
         # Should show Python 3.12+ or 3.13+

   .. tab:: macOS

      .. code-block:: bash

         python3 --version
         # Should show Python 3.12+ or 3.13+
   ```

2. **Check dependencies**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         uv pip list | Select-String PySide6
         # Should show PySide6 6.6.0 or higher

   .. tab:: Linux

      .. code-block:: bash

         uv pip list | grep PySide6
         # Should show PySide6 6.6.0 or higher

   .. tab:: macOS

      .. code-block:: bash

         uv pip list | grep PySide6
         # Should show PySide6 6.6.0 or higher
   ```

3. **Reinstall dependencies**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         uv sync --all-extras --reinstall

   .. tab:: Linux

      .. code-block:: bash

         uv sync --all-extras --reinstall

   .. tab:: macOS

      .. code-block:: bash

         uv sync --all-extras --reinstall
   ```

4. **Check logs**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         # View latest log file
         Get-Content "D:\pyMM.Logs\pymm_*.log" -Tail 50

         # Or view in Notepad
         notepad "D:\pyMM.Logs\pymm_$(Get-Date -Format 'yyyy-MM-dd').log"

   .. tab:: Linux

      .. code-block:: bash

         # View latest log file
         tail -n 50 ~/pyMM.Logs/pymm_*.log

         # Or follow live
         tail -f ~/pyMM.Logs/pymm_$(date +%Y-%m-%d).log

   .. tab:: macOS

      .. code-block:: bash

         # View latest log file
         tail -n 50 ~/Library/Logs/pyMM/pymm_*.log

         # Or follow live
         tail -f ~/Library/Logs/pyMM/pymm_$(date +%Y-%m-%d).log
   ```

#### Projects Not Loading

**Symptoms**: Projects appear in list but won't open.

**Solutions**:

1. **Verify project integrity**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm verify-project "D:\pyMM.Projects\MyProject"

   .. tab:: Linux

      .. code-block:: bash

         pymm verify-project "~/pyMM.Projects/MyProject"

   .. tab:: macOS

      .. code-block:: bash

         pymm verify-project "~/Documents/pyMM.Projects/MyProject"
   ```

2. **Check permissions**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         # Ensure you have read/write access
         Test-Path -Path "D:\pyMM.Projects\MyProject" -PathType Container

         # Check file permissions
         icacls "D:\pyMM.Projects\MyProject"

   .. tab:: Linux

      .. code-block:: bash

         # Check if directory exists and is writable
         test -w ~/pyMM.Projects/MyProject && echo "Writable" || echo "Not writable"

         # Check permissions
         ls -ld ~/pyMM.Projects/MyProject

   .. tab:: macOS

      .. code-block:: bash

         # Check if directory exists and is writable
         test -w ~/Documents/pyMM.Projects/MyProject && echo "Writable" || echo "Not writable"

         # Check permissions
         ls -ld ~/Documents/pyMM.Projects/MyProject
   ```

3. **Repair project**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm repair-project "MyProject"

   .. tab:: Linux

      .. code-block:: bash

         pymm repair-project "MyProject"

   .. tab:: macOS

      .. code-block:: bash

         pymm repair-project "MyProject"
   ```

#### Plugin Download Fails

**Symptoms**: Plugin download stalls or shows error.

**Solutions**:

1. **Check internet connection**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         Test-Connection -ComputerName github.com -Count 4

         # Alternative with curl
         curl -I https://github.com

   .. tab:: Linux

      .. code-block:: bash

         # Ping GitHub
         ping -c 4 github.com

         # Check HTTP connectivity
         curl -I https://github.com

   .. tab:: macOS

      .. code-block:: bash

         # Ping GitHub
         ping -c 4 github.com

         # Check HTTP connectivity
         curl -I https://github.com
   ```

2. **Try manual download**:

   - Visit plugin's GitHub releases page
   - Download manually
   - Extract to platform-specific location:

     - Windows: ``D:\pyMM.Plugins\<plugin_name>``
     - Linux: ``~/pyMM.Plugins/<plugin_name>``
     - macOS: ``~/Library/Application Support/pyMM/Plugins/<plugin_name>``

3. **Clear download cache**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         pymm cleanup --download-cache

   .. tab:: Linux

      .. code-block:: bash

         pymm cleanup --download-cache

   .. tab:: macOS

      .. code-block:: bash

         pymm cleanup --download-cache
   ```

#### Performance Issues

**Symptoms**: Application is slow or unresponsive.

**Solutions**:

1. **Increase memory limit**:
   - Settings → Performance → Max Memory: 8192 MB

2. **Disable thumbnail preloading**:
   - Settings → Performance → ☐ Preload thumbnails

3. **Reduce thread count**:
   - Settings → Performance → Thread Pool: 4 threads

4. **Move to faster storage**:
   - Use SSD instead of HDD for application and projects

#### Git Integration Issues

**Symptoms**: Git operations fail or show errors.

**Solutions**:

1. **Verify Git installation**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         where.exe git

   .. tab:: Linux

      .. code-block:: bash

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         which git

   .. tab:: macOS

      .. code-block:: bash

         git --version
         # Should show Git 2.40+ or higher

         # Check Git path
         which git
   ```

2. **Initialize repository manually**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         cd "D:\pyMM.Projects\MyProject"
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"

   .. tab:: Linux

      .. code-block:: bash

         cd ~/pyMM.Projects/MyProject
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"

   .. tab:: macOS

      .. code-block:: bash

         cd ~/Documents/pyMM.Projects/MyProject
         git init
         git config user.name "Your Name"
         git config user.email "your@email.com"
   ```

3. **Check Git status**:

   ```{tabs}
   .. tab:: Windows

      .. code-block:: powershell

         cd "D:\pyMM.Projects\MyProject"
         git status

   .. tab:: Linux

      .. code-block:: bash

         cd ~/pyMM.Projects/MyProject
         git status

   .. tab:: macOS

      .. code-block:: bash

         cd ~/Documents/pyMM.Projects/MyProject
         git status
   ```

### Error Messages

| Error | Cause | Solution |
| ----- | ----- | -------- |
| `PermissionError: [Errno 13]` | Insufficient permissions | Run as administrator or check folder permissions |
| `ModuleNotFoundError: 'PySide6'` | Dependencies not installed | Run `uv sync` |
| `FileNotFoundError: config.yaml` | Missing configuration | Run first-time setup wizard |
| `OSError: [WinError 145]` | File in use | Close all applications using the file |
| `ConnectionError: github.com` | No internet connection | Check network connection and firewall |

### Debug Mode

Enable detailed logging for troubleshooting:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # Launch with debug logging
      pymm --debug

      # Or set in config (D:\pyMM.Config\app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      $env:PYMM_LOG_LEVEL="DEBUG"; pymm

.. tab:: Linux

   .. code-block:: bash

      # Launch with debug logging
      pymm --debug

      # Or set in config (~/.config/pyMM/app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      PYMM_LOG_LEVEL=DEBUG pymm

.. tab:: macOS

   .. code-block:: bash

      # Launch with debug logging
      pymm --debug

      # Or set in config (~/Library/Application Support/pyMM/app.yaml)
      # privacy:
      #   log_level: "DEBUG"

      # Launch with specific log level
      PYMM_LOG_LEVEL=DEBUG pymm
```

### Collecting Diagnostic Information

When reporting issues, collect this information:

```{tabs}
.. tab:: Windows

   .. code-block:: powershell

      # System information
      python --version
      uv pip list | Select-String "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      Get-Content "D:\pyMM.Logs\pymm_*.log" -Tail 100 | Out-File "diagnostic.txt"

      # System details
      systeminfo | Select-String "OS Name|OS Version|System Type"

.. tab:: Linux

   .. code-block:: bash

      # System information
      python3 --version
      pip3 list | grep -E "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      tail -n 100 ~/.local/share/pyMM/Logs/pymm_*.log > diagnostic.txt

      # System details
      uname -a
      lsb_release -a

.. tab:: macOS

   .. code-block:: bash

      # System information
      python3 --version
      pip3 list | grep -E "PySide6|pydantic|GitPython"

      # Application information
      pymm --version
      pymm storage-info

      # Recent logs
      tail -n 100 ~/Library/Logs/pyMM/pymm_*.log > diagnostic.txt

      # System details
      uname -a
      sw_vers
```

---

(faq)=

## ❓ FAQ

### General

**Q: Is pyMM free?**
A: Yes! pyMM is open-source software licensed under MIT. Free to use, modify, and distribute.

**Q: Does pyMM require internet connection?**
A: Only for initial plugin downloads and updates. Once installed, pyMM works completely offline.

**Q: Can I run pyMM on macOS or Linux?**
A: Yes! pyMM runs on Windows 10+, Windows 11, Ubuntu 20.04+, Debian 11+, and macOS 11+. Configuration directories follow platform standards (XDG Base Directory on Linux, ~/Library on macOS, %APPDATA% on Windows).

**Q: How much storage does pyMM need?**
A: ~200 MB for application. Plugins vary (12 MB - 450 MB each). Projects depend on your media.

### Projects

**Q: Can I share projects with others?**
A: Yes! Archive projects and share the archive file. Recipients extract and open in their pyMM.

**Q: What happens if I move pyMM to another drive?**
A: pyMM is fully portable. Move the entire `D:\pyMM` folder to any drive and run.

**Q: Can I have projects on multiple drives?**
A: Yes! Configure project location per-project. Mix local, external, and network drives.

**Q: How do I backup projects?**
A: Use built-in archive feature or copy project folders manually. Git integration provides version history.

### Plugins

**Q: Are plugins safe?**
A: All official plugins are verified and downloaded from trusted sources (GitHub, official websites).

**Q: Can I use my existing DigiKam database?**
A: Yes! Configure DigiKam plugin to point to your existing database location.

**Q: Why are some plugins so large?**
A: Plugins include full applications (DigiKam, FFmpeg) for portability. No system installation needed.

**Q: Can I create custom plugins?**
A: Yes! See [Plugin Development Guide](plugin-development.md) for instructions.

### Performance

**Q: Why is pyMM slow on my USB drive?**
A: USB 2.0 drives are slow. Use USB 3.0+ or move application to faster storage.

**Q: Can I use SSD for application and HDD for media?**
A: Yes! Install pyMM on SSD (`C:\pyMM`), configure project location on HDD (`D:\pyMM.Projects`).

**Q: How much RAM does pyMM use?**
A: Typically 200-500 MB idle, up to 2-4 GB when processing large projects.

---

(getting-help)=

## 🆘 Getting Help

### Documentation

- **README**: [README.md](https://github.com/mosh666/pyMM/blob/main/README.md) - Quick start and overview
- **Contributing**: [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) - Development guide
- **Architecture**: [docs/architecture.md](architecture.md) - Technical details
- **Plugin Development**: [docs/plugin-development.md](plugin-development.md) - Create plugins
- **Changelog**: [CHANGELOG.md](https://github.com/mosh666/pyMM/blob/main/CHANGELOG.md) - Version history

### Community & Support

- **GitHub Issues**: <https://github.com/mosh666/pyMM/issues>
  - Report bugs
  - Request features
  - Ask technical questions

- **Email Support**: <24556349+mosh666@users.noreply.github.com>
  - Security issues (private)
  - Commercial inquiries
  - Partnership opportunities

### Contributing

Want to help improve pyMM? We welcome contributions!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

See [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) for detailed guidelines.

### Security

Found a security vulnerability?

**Do not create a public issue.** Report privately to:
<24556349+mosh666@users.noreply.github.com>

See [SECURITY.md](https://github.com/mosh666/pyMM/blob/main/.github/SECURITY.md) for our security policy.

---

<div align="center">

**pyMediaManager** | **Version**: 0.0.0-dev | **Python**: 3.12+ (3.13 recommended) | **License**: MIT

[GitHub](https://github.com/mosh666/pyMM) · [Issues](https://github.com/mosh666/pyMM/issues)

**Made with ❤️ for media professionals**

</div>
