#!/usr/bin/env python3
"""Update dynamic sections in README.md with current project statistics.

This script updates auto-generated sections in README.md marked with
HTML comment tags. It's designed to be run manually or via GitHub Actions.

Usage:
    python scripts/update_readme_stats.py
    python scripts/update_readme_stats.py --dry-run
    python scripts/update_readme_stats.py --verbose
"""

from __future__ import annotations

import argparse
from contextlib import suppress
from pathlib import Path
import re
import sys
from typing import Any

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def get_python_versions() -> list[str]:
    """Extract supported Python versions from pyproject.toml."""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    content = pyproject.read_text(encoding="utf-8")

    # Find classifiers section
    versions = [
        match.group(1)
        for line in content.splitlines()
        if (match := re.search(r'"Programming Language :: Python :: (3\.\d+)"', line))
    ]

    return sorted(versions)


def get_plugin_count() -> int:
    """Count number of plugins in the plugins/ directory."""
    plugins_dir = PROJECT_ROOT / "plugins"
    if not plugins_dir.exists():
        return 0

    # Count directories (exclude __pycache__ and hidden dirs)
    return len(
        [d for d in plugins_dir.iterdir() if d.is_dir() and not d.name.startswith(("_", "."))]
    )


def get_plugin_list() -> list[dict[str, Any]]:
    """Get list of plugins with their metadata."""
    plugins_dir = PROJECT_ROOT / "plugins"
    if not plugins_dir.exists():
        return []

    plugins = []
    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith(("_", ".")):
            continue

        # Look for plugin.yaml or manifest.yaml
        manifest_file = None
        for name in ["plugin.yaml", "manifest.yaml", "plugin.yml", "manifest.yml"]:
            candidate = plugin_dir / name
            if candidate.exists():
                manifest_file = candidate
                break

        plugin_info = {
            "name": plugin_dir.name,
            "title": plugin_dir.name.replace("-", " ").title(),
            "has_manifest": manifest_file is not None,
        }

        plugins.append(plugin_info)

    return plugins


def get_test_stats() -> dict[str, Any]:
    """Get test count and coverage statistics."""
    stats = {"test_count": 0, "coverage": "N/A"}

    # Try to get test count
    tests_dir = PROJECT_ROOT / "tests"
    if tests_dir.exists():
        test_files = list(tests_dir.rglob("test_*.py"))
        stats["test_count"] = len(test_files)

    # Try to get coverage from coverage report
    htmlcov_index = PROJECT_ROOT / "htmlcov" / "index.html"
    if htmlcov_index.exists():
        content = htmlcov_index.read_text(encoding="utf-8")
        if match := re.search(r'<span class="pc_cov">(\d+)%</span>', content):
            stats["coverage"] = f"{match.group(1)}%"

    return stats


def get_line_count() -> dict[str, int]:
    """Count lines of code in the project."""
    counts = {"python": 0, "yaml": 0, "markdown": 0}

    # Count Python files
    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(
            p in py_file.parts for p in [".venv", "venv", "__pycache__", "htmlcov", ".pytest_cache"]
        ):
            continue
        with suppress(Exception):
            counts["python"] += len(py_file.read_text(encoding="utf-8").splitlines())

    # Count YAML files
    for yaml_file in list(PROJECT_ROOT.rglob("*.yaml")) + list(PROJECT_ROOT.rglob("*.yml")):
        if ".github" not in yaml_file.parts and ".venv" not in yaml_file.parts:
            with suppress(Exception):
                counts["yaml"] += len(yaml_file.read_text(encoding="utf-8").splitlines())

    # Count Markdown files
    for md_file in PROJECT_ROOT.rglob("*.md"):
        if ".venv" not in md_file.parts and "htmlcov" not in md_file.parts:
            with suppress(Exception):
                counts["markdown"] += len(md_file.read_text(encoding="utf-8").splitlines())

    return counts


def generate_plugin_table() -> str:
    """Generate markdown table of plugins."""
    plugins = get_plugin_list()
    if not plugins:
        return "*No plugins found.*"

    lines = ["| Plugin | Status |", "|--------|--------|"]

    for plugin in plugins:
        status = "✅ Configured" if plugin["has_manifest"] else "⚠️ Not configured"
        lines.append(f"| **{plugin['title']}** | {status} |")

    return "\n".join(lines)


def generate_stats_section() -> str:
    """Generate project statistics section."""
    python_versions = get_python_versions()
    plugin_count = get_plugin_count()
    test_stats = get_test_stats()
    line_counts = get_line_count()

    lines = [
        "### 📊 Project Statistics",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| **Python Versions** | {', '.join(python_versions)} |",
        f"| **Plugins Available** | {plugin_count} |",
        f"| **Test Cases** | {test_stats['test_count']}+ |",
        f"| **Test Coverage** | {test_stats['coverage']} |",
        f"| **Lines of Code** | ~{line_counts['python']:,} Python |",
        f"| **Documentation** | ~{line_counts['markdown']:,} lines |",
    ]

    return "\n".join(lines)


def update_readme_section(content: str, marker: str, new_content: str) -> str:
    """Update a section in README.md between HTML comment markers.

    Args:
        content: Full README.md content
        marker: Marker name (e.g., 'PLUGIN_LIST')
        new_content: New content to insert

    Returns:
        Updated README content
    """
    start_marker = f"<!-- AUTO-GENERATED:{marker}:START -->"
    end_marker = f"<!-- AUTO-GENERATED:{marker}:END -->"

    pattern = re.compile(
        rf"({re.escape(start_marker)}).*?({re.escape(end_marker)})",
        re.DOTALL,
    )

    replacement = f"{start_marker}\n{new_content}\n{end_marker}"

    if pattern.search(content):
        return pattern.sub(replacement, content)

    # If markers don't exist, don't modify
    return content


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update README.md with current statistics")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    readme_path = PROJECT_ROOT / "README.md"
    if not readme_path.exists():
        print(f"❌ README.md not found at {readme_path}", file=sys.stderr)
        return 1

    # Read current content
    original_content = readme_path.read_text(encoding="utf-8")
    updated_content = original_content

    # Update sections
    updates = {
        "STATS": generate_stats_section(),
        "PLUGIN_LIST": generate_plugin_table(),
    }

    for marker, new_content in updates.items():
        if args.verbose:
            print(f"Updating section: {marker}")
        updated_content = update_readme_section(updated_content, marker, new_content)

    # Check if anything changed
    if original_content == updated_content:
        print("✅ README.md is already up to date - no changes needed")
        return 0

    if args.dry_run:
        print("🔍 Dry run - changes that would be made:")
        print("=" * 80)
        # Show diff-like output
        for i, (orig_line, new_line) in enumerate(
            zip(original_content.splitlines(), updated_content.splitlines(), strict=False), 1
        ):
            if orig_line != new_line:
                print(f"Line {i}:")
                print(f"  - {orig_line}")
                print(f"  + {new_line}")
        print("=" * 80)
        return 0

    # Write changes
    readme_path.write_text(updated_content, encoding="utf-8")
    print("✅ README.md updated successfully")

    if args.verbose:
        print("\nUpdated sections:")
        for marker in updates:
            print(f"  - {marker}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
