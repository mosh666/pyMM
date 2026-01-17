# {PROJECT_NAME}

> **Last Updated:** 2026-01-17 21:41 UTC
\n**Created:** {DATE}
**Template:** Photo Management Template v1.0.0
**Author:** {AUTHOR}
**Project Path:** {PROJECT_PATH}

## Project Structure

- `media/` - General media assets
- `raw/` - Original RAW image files
- `processed/` - Edited/processed images
- `selections/` - Curated selections and favorites
- `metadata/` - EXIF data, catalogs, and sidecar files
- `exports/` - Final exported images (web, print, etc.)
- `cache/` - Thumbnail and preview cache

## Description

{DESCRIPTION}

## Required Plugins

- ExifTool - Metadata extraction and manipulation
- ImageMagick - Image processing and conversion
- digiKam - Photo management and cataloging

## Workflow

1. Import RAW files to `raw/`
2. Process and edit images, save to `processed/`
3. Select best images and copy to `selections/`
4. Manage metadata in `metadata/`
5. Export final versions to `exports/`

## Version Control

Git Enabled: {GIT_ENABLED}

---

<!-- markdownlint-disable MD036 -->
*Managed by pyMediaManager - {DATETIME}*
<!-- markdownlint-enable MD036 -->
