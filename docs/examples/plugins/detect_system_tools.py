"""Detect installed system tools automatically.

This example demonstrates the system tool detector for plugins.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.plugins.system_tool_detector import SystemToolDetector


def main() -> None:
    """Detect system tools and display results."""
    detector = SystemToolDetector()

    tools_to_check = [
        "git",
        "ffmpeg",
        "exiftool",
        "convert",  # ImageMagick
        "mkvmerge",  # MKVToolNix
        "digikam",
    ]

    print("Detecting system tools...\n")

    for tool in tools_to_check:
        result = detector.detect_tool(tool)
        if result:
            print(f"\u2705 {tool}")
            print(f"   Path: {result['path']}")
            print(f"   Version: {result.get('version', 'Unknown')}")
        else:
            print(f"\u274c {tool} - Not found")
        print()


if __name__ == "__main__":
    main()
