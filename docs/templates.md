# Project Templates

> **Last Updated:** 2026-01-17 21:41 UTC


**Project template system** for pyMediaManager, providing pre-configured
directory structures, metadata, and plugin configurations for different media
management workflows.

---

## Overview

Templates provide standardized project structures optimized for specific
workflows (photography, video editing, mixed media, etc.). Each template
includes:

- **Directory Structure**: Pre-created folders for organized file management
- **README Template**: Project documentation with placeholder variables
- **Plugin Recommendations**: Suggested plugins for the workflow
- **Git Configuration**: Optional `.gitignore` and `.gitattributes`
- **Metadata Schema**: Template version and migration support

### Benefits

- **Consistency**: Standardized structures across projects
- **Efficiency**: Skip manual folder creation
- **Best Practices**: Industry-standard workflows built-in
- **Extensibility**: Create custom templates for your needs

---

## Available Templates

pyMediaManager ships with 5 built-in templates:

### 1. Base Template

**Purpose**: Minimal starting point for any project type

**Directory Structure**:

```text
project/
├── .pymm/             # pyMM metadata (hidden)
│   └── config.yaml
├── media/             # General media files
├── exports/           # Rendered outputs
├── cache/             # Temporary files
└── README.md          # Project documentation
```

**Use Cases**:

- Quick project setup
- Custom workflows not matching other templates
- Starting point for template customization

**Plugins**: None required

---

### 2. Default Template

**Purpose**: General-purpose media management

**Directory Structure**:

```text
project/
├── .pymm/
│   └── config.yaml
├── media/             # Source media files
├── exports/           # Rendered/exported outputs
├── cache/             # Temporary cache files
└── README.md
```

**Use Cases**:

- Mixed media projects
- General file organization
- No specific workflow requirements

**Plugins**: None required

**README Variables**:

- `{PROJECT_NAME}` - Project display name
- `{DATE}` - Creation date (YYYY-MM-DD)
- `{AUTHOR}` - Project creator
- `{DESCRIPTION}` - Project description
- `{GIT_ENABLED}` - Git initialization status
- `{DATETIME}` - Full timestamp

---

### 3. Photo Management Template

**Purpose**: Professional photography workflow

**Directory Structure**:

```text
project/
├── .pymm/
│   └── config.yaml
├── raw/               # Original RAW image files
├── processed/         # Edited/processed images
├── selections/        # Curated selections and favorites
├── metadata/          # EXIF data, catalogs, sidecar files
├── exports/           # Final exported images (web, print)
├── cache/             # Thumbnail and preview cache
└── README.md
```

**Use Cases**:

- Photography projects (weddings, portraits, events)
- RAW workflow management
- DigiKam catalog projects
- Photo archiving

**Required Plugins**:

- **ExifTool** - Metadata extraction and manipulation
- **ImageMagick** - Image processing and conversion
- **DigiKam** - Photo management and cataloging

**Workflow**:

1. Import RAW files to `raw/`
2. Process and edit images, save to `processed/`
3. Select best images and copy to `selections/`
4. Manage metadata in `metadata/` (DigiKam catalogs, XMP sidecar files)
5. Export final versions to `exports/` (different resolutions, formats)

**Git Recommendations**:

- Track metadata and selections
- Exclude large RAW and processed files
- Use Git LFS for final exports

---

### 4. Video Editing Template

**Purpose**: Video production and post-production workflow

**Directory Structure**:

```text
project/
├── .pymm/
│   └── config.yaml
├── source/            # Original source footage
├── proxies/           # Proxy/optimized media for editing
├── renders/           # Rendered output files
├── project-files/     # Editor project files (Premiere, DaVinci)
├── exports/           # Final exported deliverables
├── cache/             # Temporary cache and preview files
└── README.md
```

**Use Cases**:

- Video editing projects
- Multi-camera productions
- Documentary workflows
- YouTube content creation

**Required Plugins**:

- **FFmpeg** - Video processing and transcoding
- **MKVToolNix** - Matroska container manipulation

**Workflow**:

1. Import source footage to `source/`
2. Generate proxies in `proxies/` for smooth editing (1080p → 720p, H.264 →
   ProRes Proxy)
3. Create edits and save projects to `project-files/`
4. Render intermediate files to `renders/` (VFX, color-graded clips)
5. Export final deliverables to `exports/` (master, web, social media
   versions)

**Git Recommendations**:

- Track project files and scripts
- Exclude source footage and renders
- Use Git LFS for project files if large

---

### 5. Test Template

**Purpose**: Internal testing and development

**Directory Structure**:

```text
project/
├── .pymm/
│   └── config.yaml
├── test-data/         # Test files
├── temp/              # Temporary test outputs
└── README.md
```

**Use Cases**:

- pyMM development and testing
- Plugin development
- CI/CD test scenarios

**Plugins**: None required

**Note**: Not recommended for production use

---

## Using Templates

### During Project Creation

#### Project Wizard

1. Click **"+ New Project"** or press `Ctrl+N`
2. **Project Wizard** opens:
   - **Step 1: Project Type** - Select template:

     ```text
     ○ Base Template            (Minimal structure)
     ○ Default Template         (General-purpose) [Selected]
     ● Photo Management         (RAW workflow)
     ○ Video Editing            (Video production)
     ```

3. **Step 2: Project Details** - Fill in name, location, description
4. **Step 3: Plugin Selection** - Recommended plugins pre-selected based on template
5. **Step 4: Review & Create**

#### Command Line

```bash
# Create project from template
pymm create-project "MyProject" \
  --template photo-management \
  --location "D:\pyMM.Projects" \
  --description "Wedding photography 2026"

# List available templates
pymm list-templates

# Get template details
pymm template-info photo-management
```

### API Usage

```python
from app.services.project_service import ProjectService
from pathlib import Path

# Initialize service
project_service = ProjectService(
    projects_dir=Path("D:/pyMM.Projects"),
    templates_dir=Path("D:/pyMM/templates")
)

# List available templates
templates = project_service.list_templates()
for template in templates:
    print(f"{template['name']}: {template['description']}")

# Create project from template
project = project_service.create_project(
    name="WeddingPhotos2026",
    template="photo-management",
    description="John & Jane wedding",
    author="Photographer Name"
)

print(f"Project created: {project.path}")
```

---

## Creating Custom Templates

### Template Directory Structure

```text
templates/
└── my-custom-template/         # Template name (kebab-case)
    ├── template.yaml           # Template metadata (required)
    ├── README.md.template      # README template with variables
    ├── .gitignore              # Git ignore patterns (optional)
    ├── .gitattributes          # Git LFS configuration (optional)
    └── dirs.txt                # Directory structure (optional)
```

### 1. Create Template Metadata (`template.yaml`)

```yaml
# template.yaml
name: my-custom-template
version: 1.0.0
display_name: "My Custom Template"
description: "Custom workflow for my specific needs"
author: "Your Name"
created: "2026-01-14"

# Recommended plugins (optional)
plugins:
  - exiftool
  - ffmpeg

# Required Python version (optional)
python_version: ">=3.12"

# Directory structure
directories:
  - source
  - work-in-progress
  - final
  - archive
  - metadata

# Files to create (optional)
files:
  - path: ".gitignore"
    content: |
      cache/
      temp/
      *.tmp
  - path: "WORKFLOW.md"
    content: |
      # Workflow Guide

      1. Import files to source/
      2. Work on files in work-in-progress/
      3. Move completed work to final/
```

### 2. Create README Template (`README.md.template`)

```markdown
# {PROJECT_NAME}

**Created:** {DATE}
**Template:** My Custom Template v1.0.0
**Author:** {AUTHOR}
**Path:** {PROJECT_PATH}

## Description

{DESCRIPTION}

## Directory Structure

- `source/` - Original files
- `work-in-progress/` - Active work
- `final/` - Completed work
- `archive/` - Historical versions
- `metadata/` - Tracking and documentation

## Workflow

1. Import to source/
2. Edit in work-in-progress/
3. Finalize to final/
4. Archive old versions

## Version Control

Git Enabled: {GIT_ENABLED}

---

*Managed by pyMediaManager - {DATETIME}*
```

**Available Variables**:

| Variable | Description | Example |
| ---------- | ------------- | --------- |
| `{PROJECT_NAME}` | Project display name | "My Project" |
| `{PROJECT_PATH}` | Absolute project path | "D:\pyMM.Projects\MyProject" |
| `{AUTHOR}` | Project creator | "John Doe" |
| `{DATE}` | Creation date (ISO) | "2026-01-14" |
| `{DATETIME}` | Full timestamp | "2026-01-14 10:30:45" |
| `{DESCRIPTION}` | Project description | "Custom project" |
| `{GIT_ENABLED}` | Git status | "Yes" or "No" |
| `{TEMPLATE_NAME}` | Template identifier | "my-custom-template" |
| `{TEMPLATE_VERSION}` | Template version | "1.0.0" |

### 3. Place in Templates Directory

```bash
# Copy template to templates directory
cp -r my-custom-template D:\pyMM\templates\

# Verify placement
ls D:\pyMM\templates\
# Should show: base, default, photo-management, video-editing, my-custom-template
```

### 4. Test Template

```bash
# Create test project
pymm create-project "TestCustom" --template my-custom-template

# Verify structure
ls D:\pyMM.Projects\TestCustom\
# Should match template structure
```

---

## Template Versioning & Migration

### Version Schema

Templates use semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Incompatible structure changes (requires migration)
- **MINOR**: Backward-compatible additions (optional migration)
- **PATCH**: Bug fixes and documentation (no migration)

### Template Metadata in Projects

When a project is created, template metadata is stored in `.pymm/config.yaml`:

```yaml
# .pymm/config.yaml
project:
  name: "MyPhotoProject"
  created: "2026-01-14T10:00:00"

template:
  name: "photo-management"
  version: "1.0.0"

  # Migration tracking
  last_migrated: "2026-01-14T10:00:00"
  migration_history:
    - from_version: "1.0.0"
      to_version: "1.0.0"
      migrated_at: "2026-01-14T10:00:00"
```

### Detecting Template Updates

```python
from app.services.project_service import ProjectService

# Check for template updates
service = ProjectService()
project = service.load_project(Path("D:/pyMM.Projects/MyProject"))

# Get template version diff
diff = service.get_template_diff(project)

if diff.has_updates:
    print(f"Template update available: {diff.current_version} → {diff.target_version}")
    print(f"Changes: {diff.change_type}")  # MAJOR, MINOR, PATCH

    # Migration required?
    if diff.requires_migration:
        print("⚠️ Migration required for this update")
```

### Migration Process

```python
# Migrate project to latest template version
result = service.migrate_project_template(
    project_path=Path("D:/pyMM.Projects/MyProject"),
    target_version="1.1.0",
    backup=True  # Create backup before migration
)

if result.success:
    print(f"✓ Migration complete: {result.changes_applied}")
else:
    print(f"✗ Migration failed: {result.error}")
```

---

## Template Development

### Best Practices

1. **Naming Convention**: Use kebab-case for template directories (`my-template`, not `MyTemplate` or `my_template`)

2. **Directory Structure**: Keep structures shallow (max 3-4 levels deep) for usability

3. **Required vs Optional**: Mark plugins as required only if absolutely necessary

4. **Documentation**: Include comprehensive README.md.template explaining the workflow

5. **Git Integration**: Provide sensible `.gitignore` for large media files

6. **Version Control**: Use semantic versioning and document breaking changes

7. **Testing**: Create test projects before publishing

### Directory Naming Guidelines

| Good | Bad | Reason |
| ------ | ----- | -------- |
| `raw/` | `RAW/` | Lowercase for consistency |
| `processed/` | `ProcessedImages/` | Simple, concise names |
| `exports/` | `final_exports_2026/` | Avoid dates in template structure |
| `metadata/` | `meta/` | Clear, descriptive names |

### Plugin Recommendations

Only recommend plugins that are:

- Actively maintained
- Available on all platforms
- Essential to the workflow
- Part of pyMM's plugin catalog

### Template Testing Checklist

- [ ] `template.yaml` valid YAML syntax
- [ ] All required fields present (name, version, display_name)
- [ ] README.md.template uses correct variable syntax
- [ ] Directory structure created correctly
- [ ] `.gitignore` patterns work as expected
- [ ] Test project creation succeeds
- [ ] Template appears in UI template selector
- [ ] Migration from v1.0 to v1.1 works

---

## Template Registry

### Listing Templates

```python
# List all available templates
templates = project_service.list_templates()

for template in templates:
    print(f"Name: {template['name']}")
    print(f"Version: {template['version']}")
    print(f"Description: {template['description']}")
    print(f"Plugins: {', '.join(template.get('plugins', []))}")
    print()
```

### Template Caching

Templates are loaded once on service initialization and cached in memory:

```python
class ProjectService:
    def __init__(self, ...):
        self._template_cache = {}  # name -> TemplateMetadata
        self._load_templates()  # Load all templates from templates_dir
```

### Reloading Templates

If you modify templates while the application is running:

```python
# Reload template cache
project_service.reload_templates()

# Or restart the application
```

---

## File System Watching

pyMediaManager watches `template.yaml` files for changes (development mode):

```python
# Auto-reload on template.yaml changes
class TemplateFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith("template.yaml"):
            # Reload this template
            template_name = Path(event.src_path).parent.name
            self.service.reload_template(template_name)
```

Disable watching for production:

```python
# Disable template watching
project_service = ProjectService(
    projects_dir=projects_path,
    disable_watch=True  # No filesystem watching
)

# Or via environment variable
export PYMM_DISABLE_TEMPLATE_WATCH=1
```

---

## Troubleshooting

### Issue: Template not appearing in UI

**Cause**: Invalid `template.yaml` or missing required fields

**Solution**:

1. Validate YAML syntax:

   ```bash
   python -c "import yaml; yaml.safe_load(open('templates/my-template/template.yaml'))"
   ```

2. Check required fields:

   ```yaml
   name: my-template         # Required
   version: 1.0.0            # Required
   display_name: "My Tmpl"   # Required
   description: "..."        # Required
   ```

3. Restart pyMediaManager or reload templates

### Issue: Directories not created

**Cause**: `directories` field empty or missing in `template.yaml`

**Solution**:

```yaml
# template.yaml
directories:
  - source
  - work
  - final
```

### Issue: Variables not replaced in README

**Cause**: Typo in variable name or missing `.template` extension

**Solution**:

- File must be named `README.md.template` (not `README.md`)
- Use exact variable names: `{PROJECT_NAME}`, not `{project_name}` or `{ProjectName}`

### Issue: Migration failed

**Cause**: Breaking changes without migration handler

**Solution**:

Implement custom migration in template:

```python
# templates/my-template/migrate.py
def migrate_v1_to_v2(project_path: Path):
    """Migrate from v1.0 to v2.0."""
    # Rename old directories
    (project_path / "old-dir").rename(project_path / "new-dir")

    # Update config
    config = yaml.safe_load((project_path / ".pymm" / "config.yaml").read_text())
    config["template"]["version"] = "2.0.0"
    (project_path / ".pymm" / "config.yaml").write_text(yaml.dump(config))
```

---

## Related Documentation

- [Features](features.md) - Project management features overview
- [Getting Started](getting-started.md) - First-time project setup
- [API Reference](api-reference.md) - ProjectService API documentation
- [Architecture](architecture.md) - Template system architecture
- [Plugin Development](plugin-development.md) - Creating plugins for templates

---

**Version**: 1.0
