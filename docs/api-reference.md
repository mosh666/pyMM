# API Reference

> **Last Updated:** January 8, 2026
>
> **Auto-generated from source code docstrings**

Complete API reference for pyMediaManager. This documentation is automatically generated using Sphinx autodoc.

## Core Modules

### Application Core

```{eval-rst}
.. automodule:: app.core
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Logging Service

```{eval-rst}
.. automodule:: app.core.logging_service
   :members:
   :undoc-members:
   :show-inheritance:
```

#### Platform Abstraction

```{eval-rst}
.. automodule:: app.core.platform
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Services

### Config Service

```{eval-rst}
.. automodule:: app.core.services.config_service
   :members:
   :undoc-members:
   :show-inheritance:
```

### File System Service

```{eval-rst}
.. automodule:: app.core.services.file_system_service
   :members:
   :undoc-members:
   :show-inheritance:
```

### Storage Service

```{eval-rst}
.. automodule:: app.core.services.storage_service
   :members:
   :undoc-members:
   :show-inheritance:
```

### Git Service

```{eval-rst}
.. automodule:: app.services.git_service
   :members:
   :undoc-members:
   :show-inheritance:
```

### Project Service

```{eval-rst}
.. automodule:: app.services.project_service
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Plugin System

### Plugin Manager

```{eval-rst}
.. automodule:: app.plugins.plugin_manager
   :members:
   :undoc-members:
   :show-inheritance:
```

### Plugin Base

```{eval-rst}
.. automodule:: app.plugins.plugin_base
   :members:
   :undoc-members:
   :show-inheritance:
```

### Plugin Schema

```{eval-rst}
.. automodule:: app.plugins.plugin_schema
   :members:
   :undoc-members:
   :show-inheritance:
```

### Plugin Migrator

```{eval-rst}
.. automodule:: app.plugins.plugin_migrator
   :members:
   :undoc-members:
   :show-inheritance:
```

### System Tool Detector

```{eval-rst}
.. automodule:: app.plugins.system_tool_detector
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Models

### Project Model

```{eval-rst}
.. automodule:: app.models.project
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Platform-Specific

### Windows Platform

```{eval-rst}
.. automodule:: app.platform.windows
   :members:
   :undoc-members:
   :show-inheritance:
```

### Linux Platform

```{eval-rst}
.. automodule:: app.platform.linux
   :members:
   :undoc-members:
   :show-inheritance:
```

### macOS Platform

```{eval-rst}
.. automodule:: app.platform.macos
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## User Interface

### Main Window

```{eval-rst}
.. automodule:: app.ui.main_window
   :members:
   :undoc-members:
   :show-inheritance:
```

### Components

```{eval-rst}
.. automodule:: app.ui.components
   :members:
   :undoc-members:
   :show-inheritance:
```

### Dialogs

```{eval-rst}
.. automodule:: app.ui.dialogs
   :members:
   :undoc-members:
   :show-inheritance:
```

### Views

```{eval-rst}
.. automodule:: app.ui.views
   :members:
   :undoc-members:
   :show-inheritance:
```

---

## Building API Documentation

To generate the API reference documentation locally:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Generate HTML documentation
cd docs
sphinx-build -b html . _build/html

# Open in browser
# Windows: start _build/html/index.html
# Linux: xdg-open _build/html/index.html
# macOS: open _build/html/index.html
```

Or using the justfile:

```bash
just docs
```

---

## Development Guidelines

### Docstring Format

pyMediaManager uses **Google-style docstrings**:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of the function.

    Longer description with more details about what the function does,
    its behavior, and any important notes.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When input is invalid.
        FileNotFoundError: When file doesn't exist.

    Examples:
        >>> example_function("test", 42)
        True
    """
    ...
```

### Type Hints

All public APIs must have complete type hints:

```python
from collections.abc import Sequence
from pathlib import Path

def process_files(
    paths: Sequence[Path],
    *,
    recursive: bool = False,
    pattern: str | None = None,
) -> list[Path]:
    """Process a sequence of file paths."""
    ...
```

### Module Documentation

Every module should have a module-level docstring:

```python
"""Module for handling project configuration.

This module provides utilities for loading, validating, and saving
project configuration files using Pydantic models.
"""

from pathlib import Path
...
```

---

## Index and Search

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`

---

**Document Version:** 1.0
**Last Updated:** January 8, 2026
**Built with:** Sphinx 7.2+ with autodoc extension
