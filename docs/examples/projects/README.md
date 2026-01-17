# Project Management Examples

> **Last Updated:** 2026-01-17 21:41 UTC
\nExamples for creating, managing, and migrating media projects in pyMediaManager.

## Overview

Projects in pyMM organize media files with version control integration. Each project
has a name, path, template, and associated plugins.

## Basic Examples

**`create_project.py`** - Create a new project
**`load_project.py`** - Load and inspect project data
**`list_projects.py`** - List all projects in storage

## Intermediate Examples

**`create_with_template.py`** - Create project from template
**`migrate_project.py`** - Update project to new template version
**`batch_operations.py`** - Perform operations on multiple projects

## Advanced Examples

**`custom_project_type.py`** - Define custom project structures
**`migration_rollback.py`** - Rollback failed migrations
**`conflict_resolution.py`** - Handle project conflicts and errors

## Key Concepts

- **Project**: Directory structure with `.pymm` metadata
- **Template**: Pre-defined directory and file structure
- **Migration**: Updating project to match new template version
- **Storage**: Drive or location where projects are stored

## See Also

- {ref}`getting-started` - Getting Started Guide
- {ref}`projectservice` - API Reference ProjectService
