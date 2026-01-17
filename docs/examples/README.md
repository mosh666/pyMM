# pyMediaManager Examples

> **Last Updated:** 2026-01-17 21:41 UTC


This directory contains working Python examples demonstrating pyMediaManager's API and features.

## Structure

Examples are organized by **feature area** and **complexity level**:

```text
examples/
├── plugins/        # Plugin system examples
├── projects/       # Project management examples
├── storage/        # Storage and drive detection examples
├── ui/             # User interface component examples
├── config/         # Configuration management examples
└── platform/       # Platform abstraction examples
```

Each feature directory contains three complexity levels:

- **basic/** - Simple, single-concept examples for getting started
- **intermediate/** - Multi-step workflows combining several features
- **advanced/** - Complex scenarios with error handling and edge cases

## Running Examples

All examples are standalone Python scripts that can be run directly:

```bash
# Basic plugin example
python docs/examples/plugins/basic/list_plugins.py

# Intermediate project example
python docs/examples/projects/intermediate/create_with_template.py
```

### Prerequisites

Examples require pyMediaManager to be installed:

```bash
uv sync --all-extras
```

Some UI examples require a display environment (not suitable for headless servers).

## Example Categories

### Plugins

Learn how to work with pyMM's plugin system:

- **Basic**: List plugins, check plugin status, get plugin metadata
- **Intermediate**: Install plugins, validate manifests, handle dependencies
- **Advanced**: Create custom plugins, verify SHA-256, handle platform-specific code

### Projects

Project creation, management, and migration:

- **Basic**: Create project, load project, list projects
- **Intermediate**: Project templates, project migration, batch operations
- **Advanced**: Custom project types, migration rollback, conflict resolution

### Storage

Storage detection and drive management:

- **Basic**: List drives, check drive status, get drive information
- **Intermediate**: Monitor drive changes, portable mode detection, drive validation
- **Advanced**: Cross-platform storage handling, network drives, custom storage backends

### UI

Build custom interfaces with pyMM's UI components:

- **Basic**: Create simple dialogs, show notifications, use widgets
- **Intermediate**: Custom wizard pages, themed components, signal handling
- **Advanced**: Custom views, complex layouts, integration with main window

### Config

Configuration management and validation:

- **Basic**: Read config, update config, save config
- **Intermediate**: Config layering, environment variables, portable mode
- **Advanced**: Custom validators, config migration, schema evolution

### Platform

Cross-platform code and platform abstraction:

- **Basic**: Detect platform, use platform paths, check platform features
- **Intermediate**: Platform-specific config, conditional imports, platform testing
- **Advanced**: Platform compatibility checks, custom platform handlers, AST validation

## Documentation

For detailed API documentation, see:

- [API Reference](../api-reference.md)
- [Installation](../installation.md)
- [Getting Started](../getting-started.md)
- [Features](../features.md)
- [Configuration](../configuration.md)
- [Plugin Development](../plugin-development.md)

## Contributing Examples

We welcome contributions! See [CONTRIBUTING.md](https://github.com/mosh666/pyMM/blob/main/CONTRIBUTING.md) for guidelines.

Good examples are:

- **Self-contained**: Can run independently without external files
- **Well-commented**: Explain what the code does and why
- **Realistic**: Show actual use cases, not contrived scenarios
- **Educational**: Teach one clear concept per example

---

**Note**: Examples use development APIs marked with `.. versionadded:: dev` that may change before release.
