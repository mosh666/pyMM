#!/usr/bin/env python3
"""
Fetch GitHub release tags for sphinx-multiversion filtering.

This script queries the GitHub API to get all release tags (including pre-releases)
and writes them to release_tags.txt. It requires a GITHUB_TOKEN environment variable
for authentication.

Usage:
    python get_release_tags.py

Environment Variables:
    GITHUB_TOKEN: GitHub personal access token or workflow token (required)
    GITHUB_REPOSITORY: Repository in format 'owner/repo' (defaults to mosh666/pyMM)

Exit Codes:
    0: Success
    1: Missing GITHUB_TOKEN or API error
"""

import getpass
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""


def get_release_tags(repo: str, token: str) -> list[str]:  # noqa: C901
    """
    Query GitHub API for all release tags.

    Args:
        repo: Repository in format 'owner/repo'
        token: GitHub authentication token

    Returns:
        List of release tag names

    Raises:
        GitHubAPIError: If API request fails
    """
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "pyMM-sphinx-multiversion",
    }

    tags = []
    page = 1
    per_page = 100

    # Paginate through all releases
    while True:
        paginated_url = f"{url}?page={page}&per_page={per_page}"

        try:
            req = urllib.request.Request(paginated_url, headers=headers)  # noqa: S310
            with urllib.request.urlopen(req, timeout=30) as response:  # noqa: S310
                if response.status != 200:
                    raise GitHubAPIError(f"GitHub API returned status {response.status}")  # noqa: TRY301

                data = json.loads(response.read().decode())

                # No more releases
                if not data:
                    break

                # Extract tag names from all releases (including pre-releases)
                for release in data:
                    tag_name = release.get("tag_name")
                    if tag_name:
                        tags.append(tag_name)

                # Check if there are more pages
                if len(data) < per_page:
                    break

                page += 1

        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise GitHubAPIError(f"GitHub API HTTP error {e.code}: {error_body}") from e
        except urllib.error.URLError as e:
            raise GitHubAPIError(f"GitHub API network error: {e.reason}") from e
        except json.JSONDecodeError as e:
            raise GitHubAPIError(f"Failed to parse GitHub API response: {e}") from e
        except GitHubAPIError:
            raise
        except Exception as e:
            raise GitHubAPIError(f"Unexpected error querying GitHub API: {e}") from e

    return tags


def prompt_for_token() -> str | None:  # noqa: C901, PLR0912, PLR0915
    """
    Interactively prompt user for GitHub token and storage preference.

    Returns:
        Token string if provided, None if user cancels
    """
    # Only prompt if running in an interactive terminal (not CI/CD)
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return None

    print(
        "\n" + "=" * 70,
        file=sys.stderr,
    )
    print(
        "  GitHub Token Required for Documentation Build",
        file=sys.stderr,
    )
    print(
        "=" * 70,
        file=sys.stderr,
    )
    print(
        "\nTo build documentation with release filtering, you need a GitHub",
        file=sys.stderr,
    )
    print(
        "personal access token with 'repo' scope.",
        file=sys.stderr,
    )
    print(
        "\n📖 Create token at:",
        file=sys.stderr,
    )
    print(
        "   https://github.com/settings/tokens/new?scopes=repo&description=pyMM-docs",
        file=sys.stderr,
    )
    print(file=sys.stderr)

    # Prompt for token (hidden input)
    try:
        token = getpass.getpass("Enter your GitHub token (or press Enter to cancel): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled by user.", file=sys.stderr)
        return None

    if not token:
        print("\nNo token provided. Exiting.", file=sys.stderr)
        return None

    # Ask about persistence
    print(file=sys.stderr)
    print("How should the token be saved?", file=sys.stderr)
    print("  1) Temporary (current session only)", file=sys.stderr)
    print("  2) Persistent (current user - saved in environment)", file=sys.stderr)
    print(file=sys.stderr)

    try:
        choice = input("Enter choice [1/2] (default: 1): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\nCancelled by user.", file=sys.stderr)
        return None

    # Default to temporary if no choice
    if not choice:
        choice = "1"

    # Set token based on choice
    if choice == "2":
        # Persistent storage
        is_windows = sys.platform == "win32"

        if is_windows:
            # Windows: Use setx command
            try:
                result = subprocess.run(
                    ["setx", "GITHUB_TOKEN", token],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode == 0:
                    print(
                        "\n✓ Token saved persistently for current user (Windows)",
                        file=sys.stderr,
                    )
                    print(
                        "  Restart your terminal for the change to take effect.",
                        file=sys.stderr,
                    )
                    print(
                        "  For this session, using temporary token.",
                        file=sys.stderr,
                    )
                else:
                    print(
                        f"\n⚠ Warning: Failed to save token persistently: {result.stderr}",
                        file=sys.stderr,
                    )
                    print(
                        "  Using temporary token for this session only.",
                        file=sys.stderr,
                    )
            except subprocess.SubprocessError as e:
                print(
                    f"\n⚠ Warning: Failed to save token persistently: {e}",
                    file=sys.stderr,
                )
                print(
                    "  Using temporary token for this session only.",
                    file=sys.stderr,
                )
        else:
            # Unix-like: Provide instructions
            shell = os.environ.get("SHELL", "")
            if "zsh" in shell:
                config_file = "~/.zshrc"
            elif "bash" in shell:
                config_file = "~/.bashrc"
            else:
                config_file = "~/.profile"

            print(
                f"\n✓ To save persistently, add this line to your {config_file}:",
                file=sys.stderr,
            )
            print(
                f'  export GITHUB_TOKEN="{token}"',
                file=sys.stderr,
            )
            print(
                f"\nThen run: source {config_file}",
                file=sys.stderr,
            )
            print(
                "For this session, using temporary token.",
                file=sys.stderr,
            )
    else:
        # Temporary storage
        print(
            "\n✓ Using token for current session only.",
            file=sys.stderr,
        )

    print(file=sys.stderr)
    # Set for current process
    os.environ["GITHUB_TOKEN"] = token
    return token


def main() -> int:
    """
    Main entry point.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Check for required GITHUB_TOKEN
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        # Try to prompt interactively (only works in terminal)
        token = prompt_for_token()

        if not token:
            # Still no token - show error and exit
            print(
                "ERROR: GITHUB_TOKEN environment variable is required",
                file=sys.stderr,
            )
            print(
                "\nFor local builds, create a GitHub personal access token with 'repo' scope:",
                file=sys.stderr,
            )
            print(
                "  https://github.com/settings/tokens/new?scopes=repo&description=pyMM-docs",
                file=sys.stderr,
            )
            print(
                "\nThen set it as an environment variable:",
                file=sys.stderr,
            )
            print(
                "  PowerShell: $env:GITHUB_TOKEN = 'your_token_here'",
                file=sys.stderr,
            )
            print(
                "  Bash/Zsh:   export GITHUB_TOKEN='your_token_here'",
                file=sys.stderr,
            )
            print(
                "\nSee docs/getting-started-dev.md for more details.",
                file=sys.stderr,
            )
            return 1

    # Get repository (from environment or default)
    repo = os.environ.get("GITHUB_REPOSITORY", "mosh666/pyMM")

    try:
        # Fetch release tags
        tags = get_release_tags(repo, token)

        if not tags:
            print(
                f"WARNING: No GitHub releases found for {repo}",
                file=sys.stderr,
            )
            print(
                "Documentation will only be built for branches (main/dev).",
                file=sys.stderr,
            )

        # Write tags to file
        output_file = Path("release_tags.txt")
        try:
            with output_file.open("w", encoding="utf-8") as f:
                for tag in tags:
                    f.write(f"{tag}\n")
            print(
                f"✓ Successfully wrote {len(tags)} release tag(s) to {output_file}",
                file=sys.stderr,
            )
        except OSError as e:
            print(
                f"ERROR: Failed to write {output_file}: {e}",
                file=sys.stderr,
            )
            return 1

        return 0

    except GitHubAPIError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print(
            "\nFailed to fetch GitHub releases. Documentation build cannot continue.",
            file=sys.stderr,
        )
        print(
            "Please check your GITHUB_TOKEN is valid and has 'repo' scope.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
