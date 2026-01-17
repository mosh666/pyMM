"""Validate a plugin YAML manifest.

This example demonstrates Pydantic validation of plugin manifests.
"""

from pathlib import Path
import sys

import yaml

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from pydantic import ValidationError

from app.plugins.plugin_schema import PluginManifestSchema


def main() -> None:
    """Validate a plugin manifest file."""
    if len(sys.argv) < 2:
        print("Usage: python validate_plugin_manifest.py <path_to_plugin.yaml>")
        sys.exit(1)

    manifest_path = Path(sys.argv[1])
    if not manifest_path.exists():
        print(f"File not found: {manifest_path}")
        sys.exit(1)

    print(f"Validating: {manifest_path.name}\n")

    try:
        with manifest_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Validate against schema
        manifest = PluginManifestSchema(**data)

        print("\u2705 Validation passed!")
        print(f"\nPlugin: {manifest.name} v{manifest.version}")
        print(f"Schema version: {manifest.schema_version}")
        print(f"Category: {manifest.category}")
        print(f"Platforms: {', '.join(manifest.platforms)}")

        if manifest.dependencies:
            print(f"Dependencies: {', '.join(manifest.dependencies)}")

    except ValidationError as e:
        print("\u274c Validation failed!\n")
        print("Errors:")
        for error in e.errors():
            field = " -> ".join(str(x) for x in error["loc"])
            print(f"  {field}: {error['msg']}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"\u274c Invalid YAML: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
