"""Convert plugin YAML files from flat v2 to nested v2 structure."""

from pathlib import Path
import traceback

import yaml


def convert_plugin_yaml(plugin_file: Path) -> None:
    """Convert a plugin.yaml file to use nested source and command objects."""
    print(f"Converting {plugin_file}...")

    with plugin_file.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Check if platforms exist
    if "platforms" not in data:
        print(f"  Skipping {plugin_file} - no platforms section")
        return

    # Convert each platform
    for platform_name, platform_data in data["platforms"].items():
        # Check if already converted
        if isinstance(platform_data.get("source"), dict) and isinstance(
            platform_data.get("command"), dict
        ):
            print(f"  {platform_name} already converted")
            continue

        # Extract flat fields
        source_type = platform_data.pop("source", None)
        download_url = platform_data.pop("download_url", None)
        checksum = platform_data.pop("checksum_sha256", None)
        file_size = platform_data.pop("file_size", None)
        command_path = platform_data.pop("command_path", None)
        command_executable = platform_data.pop("command_executable", None)

        # Create nested source object (only if source type exists and is not empty)
        if source_type and download_url:
            platform_data["source"] = {
                "type": source_type,
                "base_uri": download_url,
            }
            # Add optional fields
            if checksum:
                platform_data["source"]["checksum_sha256"] = checksum
            if file_size:
                platform_data["source"]["file_size"] = file_size

        # Create nested command object (required)
        if command_path is not None and command_executable is not None:
            platform_data["command"] = {
                "path": command_path or "",
                "executable": command_executable,
            }
        elif command_executable is not None:
            platform_data["command"] = {
                "path": "",
                "executable": command_executable,
            }

        print(f"  Converted {platform_name}")

    # Write back to file
    with plugin_file.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

    print(f"  Saved {plugin_file}")


def main():
    """Convert all plugin.yaml files in the plugins directory."""
    plugins_dir = Path(__file__).parent.parent / "plugins"

    for plugin_yaml in plugins_dir.glob("*/plugin.yaml"):
        try:
            convert_plugin_yaml(plugin_yaml)
        except Exception as e:
            print(f"ERROR converting {plugin_yaml}: {e}")
            traceback.print_exc()


if __name__ == "__main__":
    main()
