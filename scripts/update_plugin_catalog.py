#!/usr/bin/env python3
"""Update plugin catalog documentation from YAML manifests.

Auto-generates the plugin catalog in docs/plugin-catalog.md by parsing all
plugin.yaml manifests in the plugins/ directory. Replaces content between
<!-- AUTO-GENERATED:PLUGIN_CATALOG:START/END --> markers.

Usage:
    python scripts/update_plugin_catalog.py
    python scripts/update_plugin_catalog.py --dry-run
    python scripts/update_plugin_catalog.py --verbose
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path
import re
import sys
import time
import traceback
from typing import Any

import yaml

# Ensure UTF-8 encoding for stdout/stderr on Windows
if sys.platform == "win32":
    import io

    if sys.stdout.encoding != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if sys.stderr.encoding != "utf-8":
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).parent.parent
PLUGINS_DIR = PROJECT_ROOT / "plugins"
CATALOG_FILE = PROJECT_ROOT / "docs" / "plugin-catalog.md"


class TimingMetrics:
    """Track operation timing for performance monitoring."""

    def __init__(self) -> None:
        self.timings: dict[str, float] = {}
        self._start_times: dict[str, float] = {}

    def start(self, label: str) -> None:
        """Start timing an operation."""
        self._start_times[label] = time.perf_counter()

    def stop(self, label: str) -> float:
        """Stop timing an operation and return duration."""
        if label not in self._start_times:
            return 0.0
        duration = time.perf_counter() - self._start_times[label]
        self.timings[label] = duration
        return duration

    def get_duration(self, label: str) -> float:
        """Get duration of a completed operation."""
        return self.timings.get(label, 0.0)

    def report(self, verbose: bool = False) -> None:
        """Print timing report."""
        if not self.timings:
            return

        total = sum(self.timings.values())
        if verbose:
            print("\n⏱️  Performance Report:")
            for label, duration in self.timings.items():
                print(f"  {label}: {duration:.2f}s")
            print(f"  Total: {total:.2f}s")
        else:
            print(f"⏱️  Total execution time: {total:.2f}s")


def discover_plugins(verbose: bool = False) -> list[dict[str, Any]]:  # noqa: C901
    """Discover all plugins in plugins/ directory.

    Args:
        verbose: Print detailed progress

    Returns:
        List of plugin data dicts with manifest and metadata
    """
    if verbose:
        print(f"🔍 Discovering plugins in {PLUGINS_DIR}...")

    plugins: list[dict[str, Any]] = []

    if not PLUGINS_DIR.exists():
        if verbose:
            print(f"⚠️  Plugins directory not found: {PLUGINS_DIR}")
        return plugins

    for plugin_dir in sorted(PLUGINS_DIR.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith(("_", ".")):
            continue

        manifest_file = plugin_dir / "plugin.yaml"
        if not manifest_file.exists():
            if verbose:
                print(f"  ⚠️  Skipping {plugin_dir.name}: No plugin.yaml found")
            continue

        try:
            with manifest_file.open(encoding="utf-8") as f:
                manifest_data = yaml.safe_load(f)

            plugins.append(
                {
                    "folder": plugin_dir.name,
                    "manifest": manifest_data,
                    "path": manifest_file.relative_to(PROJECT_ROOT),
                }
            )

            if verbose:
                print(f"  ✓ {plugin_dir.name}")

        except Exception as e:
            if verbose:
                print(f"  ❌ Error loading {plugin_dir.name}: {e}")
            continue

    if verbose:
        print(f"✓ Found {len(plugins)} plugins")

    return plugins


def validate_with_schema(
    plugins: list[dict[str, Any]], verbose: bool = False
) -> list[dict[str, Any]]:
    """Validate plugins against Pydantic schema.

    Args:
        plugins: List of plugin dicts
        verbose: Print detailed progress

    Returns:
        List of validated plugins
    """
    if verbose:
        print("\n🔍 Validating plugins against schema...")

    try:
        sys.path.insert(0, str(PROJECT_ROOT))
        from app.plugins.plugin_schema import PluginManifestSchema  # noqa: PLC0415
    except ImportError as e:
        if verbose:
            print(f"⚠️  Could not import schema: {e}")
        return plugins

    validated = []
    for plugin_data in plugins:
        try:
            manifest = PluginManifestSchema(**plugin_data["manifest"])
            plugin_data["validated_manifest"] = manifest
            validated.append(plugin_data)

            if verbose:
                print(f"  ✓ {plugin_data['folder']}")

        except Exception as e:
            if verbose:
                print(f"  ❌ Validation failed for {plugin_data['folder']}: {e}")

    if verbose:
        print(f"✓ Validated {len(validated)}/{len(plugins)} plugins")

    return validated


def categorize_plugins(plugins: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Categorize plugins by type.

    Args:
        plugins: List of plugin dicts

    Returns:
        Dict mapping category names to plugin lists
    """
    # Hardcoded fallback mapping for plugins without category field
    fallback_categories = {
        "git": "Version Control",
        "gitlfs": "Version Control",
        "git-lfs": "Version Control",
        "gitversion": "Version Control",
        "ffmpeg": "Media Processing",
        "mkvtoolnix": "Media Processing",
        "exiftool": "Image Processing",
        "imagemagick": "Image Processing",
        "digikam": "Image Processing",
        "mariadb": "Database",
    }

    categorized: dict[str, list[dict[str, Any]]] = {}

    for plugin in plugins:
        manifest = plugin["manifest"]

        # Try to get category from manifest
        category = manifest.get("category")

        # Fall back to hardcoded mapping if no category field
        if not category:
            category = fallback_categories.get(plugin["folder"].lower(), "Other")

        if category not in categorized:
            categorized[category] = []

        categorized[category].append(plugin)

    return categorized


def get_supported_platforms(manifest: dict[str, Any]) -> list[str]:
    """Extract supported platforms from manifest.

    Args:
        manifest: Plugin manifest data

    Returns:
        List of platform names (e.g., ["Windows", "Linux", "macOS"])
    """
    platforms: list[str] = []
    platform_map = {
        "windows": "Windows",
        "linux": "Linux",
        "macos": "macOS",
    }

    manifest_platforms = manifest.get("platforms", {})
    if not manifest_platforms:
        return platforms

    for key, config in manifest_platforms.items():
        # Check if platform has meaningful configuration
        # Platform is supported if it has command executable
        if isinstance(config, dict) and (
            config.get("command_executable") or config.get("command", {}).get("executable")
        ):
            platforms.append(platform_map.get(key, key.title()))

    return platforms


def generate_plugin_entry(plugin_data: dict[str, Any]) -> str:
    """Generate markdown for single plugin entry.

    Args:
        plugin_data: Dict with folder, manifest, path

    Returns:
        Markdown string for plugin table row
    """
    manifest = plugin_data["manifest"]
    folder = plugin_data["folder"]
    path = plugin_data["path"]

    name = manifest.get("name", folder)
    version = manifest.get("version", "N/A")
    platforms = get_supported_platforms(manifest)
    platform_str = ", ".join(platforms) if platforms else "N/A"

    # Dependencies
    dependencies = manifest.get("dependencies", [])
    deps_str = ", ".join(dependencies) if dependencies else "None"

    # Status
    mandatory = manifest.get("mandatory", False)
    enabled = manifest.get("enabled", False)
    status_parts = []
    if mandatory:
        status_parts.append("Mandatory")
    if enabled:
        status_parts.append("Enabled")
    if not status_parts:
        status_parts.append("Optional")
    status_str = ", ".join(status_parts)

    # Description
    description = manifest.get("description", "No description available")

    # Plugin file link (use forward slashes for cross-platform compatibility)
    file_link = str(path).replace("\\", "/")

    return f"| [{name}](../{file_link}) | {version} | {platform_str} | {deps_str} | {status_str} | {description} |"


def generate_category_section(category: str, plugins: list[dict[str, Any]]) -> str:
    """Generate markdown for a plugin category section.

    Args:
        category: Category name
        plugins: List of plugin dicts in this category

    Returns:
        Markdown string for category section
    """
    lines = [
        f"### {category}",
        "",
        "| Plugin | Version | Platforms | Dependencies | Status | Description |",
        "|--------|---------|-----------|--------------|--------|-------------|",
    ]

    lines.extend(
        generate_plugin_entry(plugin_data)
        for plugin_data in sorted(plugins, key=lambda p: p["manifest"].get("name", ""))
    )

    lines.append("")
    return "\n".join(lines)


def generate_plugin_catalog(plugins: list[dict[str, Any]], verbose: bool = False) -> str:
    """Generate complete plugin catalog markdown.

    Args:
        plugins: List of plugin dicts
        verbose: Print detailed progress

    Returns:
        Markdown string for plugin catalog section
    """
    if verbose:
        print("\n📝 Generating plugin catalog...")

    if not plugins:
        return "*No plugins found.*"

    categorized = categorize_plugins(plugins)

    lines = [
        "## Official Plugins",
        "",
        f"**Total Plugins:** {len(plugins)}  ",
        f"**Last Auto-Generated:** {datetime.now(UTC).strftime('%B %d, %Y at %H:%M UTC')}  ",
        "**Generated by:** `scripts/update_plugin_catalog.py`",
        "",
    ]

    # Define category order
    category_order = [
        "Version Control",
        "Media Processing",
        "Image Processing",
        "Database",
        "Development Tools",
        "Other",
    ]

    # Generate sections in order
    for category in category_order:
        if categorized.get(category):
            if verbose:
                print(f"  ✓ {category}: {len(categorized[category])} plugins")
            lines.append(generate_category_section(category, categorized[category]))

    # Handle any categories not in the predefined order
    for category, plugin_list in sorted(categorized.items()):
        if category not in category_order:
            if verbose:
                print(f"  ✓ {category}: {len(plugin_list)} plugins")
            lines.append(generate_category_section(category, plugin_list))

    return "\n".join(lines)


def update_catalog_section(content: str, new_content: str) -> str:
    """Update section in plugin catalog between markers.

    Args:
        content: Full catalog file content
        new_content: New content to insert

    Returns:
        Updated catalog content
    """
    start_marker = "<!-- AUTO-GENERATED:PLUGIN_CATALOG:START -->"
    end_marker = "<!-- AUTO-GENERATED:PLUGIN_CATALOG:END -->"

    pattern = re.compile(
        rf"({re.escape(start_marker)}).*?({re.escape(end_marker)})",
        re.DOTALL,
    )

    replacement = f"{start_marker}\n{new_content}\n{end_marker}"

    if pattern.search(content):
        return pattern.sub(replacement, content)

    # If markers don't exist, warn but don't modify
    print("⚠️  Warning: Markers not found in catalog file")
    return content


def main() -> int:  # noqa: C901, PLR0911, PLR0912, PLR0915
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update plugin catalog from YAML manifests")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show changes without writing",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print detailed progress",
    )
    parser.add_argument(
        "--catalog-file",
        type=Path,
        default=CATALOG_FILE,
        help=f"Catalog file path (default: {CATALOG_FILE.relative_to(PROJECT_ROOT)})",
    )
    parser.add_argument(
        "--check-timing",
        action="store_true",
        help="Check timing against thresholds and warn if exceeded",
    )
    args = parser.parse_args()

    timing = TimingMetrics()

    try:
        # Check if catalog file exists
        if not args.catalog_file.exists():
            print(f"❌ Catalog file not found: {args.catalog_file}", file=sys.stderr)
            return 1

        # Discover plugins
        timing.start("discovery")
        plugins = discover_plugins(verbose=args.verbose)
        timing.stop("discovery")

        if not plugins:
            print("⚠️  No plugins found to process")
            return 0

        # Validate plugins
        timing.start("validation")
        plugins = validate_with_schema(plugins, verbose=args.verbose)
        timing.stop("validation")

        # Generate catalog
        timing.start("generation")
        new_catalog = generate_plugin_catalog(plugins, verbose=args.verbose)
        timing.stop("generation")

        # Read current content
        original_content = args.catalog_file.read_text(encoding="utf-8")

        # Update content
        updated_content = update_catalog_section(original_content, new_catalog)

        # Check if anything changed
        if original_content == updated_content:
            print("✅ Plugin catalog is already up to date")
            timing.report(verbose=args.verbose)
            return 0

        if args.dry_run:
            print("\n🔍 Dry run - changes that would be made:")
            print("=" * 80)
            print(new_catalog)
            print("=" * 80)
            timing.report(verbose=args.verbose)
            return 0

        # Write changes
        args.catalog_file.write_text(updated_content, encoding="utf-8")
        print("✅ Plugin catalog updated successfully")

        if args.verbose:
            print(f"   Updated: {args.catalog_file.relative_to(PROJECT_ROOT)}")
            print(f"   Plugins: {len(plugins)}")

        timing.report(verbose=args.verbose)

        # Check timing thresholds
        if args.check_timing:
            thresholds = {
                "discovery": 1.0,
                "validation": 2.0,
                "generation": 3.0,
            }
            total_threshold = 10.0

            warnings = []
            for operation, threshold in thresholds.items():
                duration = timing.get_duration(operation)
                if duration > threshold:
                    warnings.append(f"{operation}: {duration:.2f}s (threshold: {threshold}s)")

            total = sum(timing.timings.values())
            if total > total_threshold:
                warnings.append(f"total: {total:.2f}s (threshold: {total_threshold}s)")

            if warnings:
                print("\n⚠️  Performance warnings:")
                for warning in warnings:
                    print(f"  {warning}")

        return 0

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
