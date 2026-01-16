#!/usr/bin/env python3
"""
Validate proper use of [skip ci] and related skip directives in commit messages.

This pre-commit hook ensures developers don't accidentally skip CI on important changes.

Exit codes:
    0: Valid usage or no skip directive
    1: Invalid usage - blocks commit
    2: Warning - allows commit but shows warning
"""

from pathlib import Path
import re
import subprocess
import sys


def get_staged_files() -> list[str]:
    """Get list of files staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError:
        return []


def get_commit_message() -> str:
    """Get the commit message from command line or git."""
    # Check if commit message is being edited
    if len(sys.argv) > 1:
        msg_file = Path(sys.argv[1])
        if msg_file.exists():
            return msg_file.read_text().strip()

    # Fallback: get from stdin or environment
    if not sys.stdin.isatty():
        return sys.stdin.read().strip()

    return ""


def check_skip_directive(commit_msg: str) -> tuple[str | None, str]:
    """
    Check for skip directives in commit message.

    Returns:
        Tuple of (directive, reason) or (None, "") if no directive found
    """
    directives = [
        (r"\[skip ci\]", "skip ci"),
        (r"\[skip tests\]", "skip tests"),
        (r"\[skip lint\]", "skip lint"),
        (r"\[skip build\]", "skip build"),
    ]

    for pattern, name in directives:
        if re.search(pattern, commit_msg, re.IGNORECASE):
            return name, pattern

    return None, ""


def categorize_files(files: list[str]) -> dict[str, list[str]]:
    """Categorize staged files by type."""
    categories = {
        "code": [],
        "tests": [],
        "config": [],
        "docs": [],
        "workflows": [],
        "other": [],
    }

    for file in files:
        path = Path(file)

        if path.match("app/**/*.py"):
            categories["code"].append(file)
        elif path.match("tests/**/*.py"):
            categories["tests"].append(file)
        elif (
            path.match("pyproject.toml")
            or path.match("config/**")
            or path.match("Dockerfile")
            or path.match("justfile")
        ):
            categories["config"].append(file)
        elif path.match("docs/**") or path.suffix == ".md":
            categories["docs"].append(file)
        elif path.match(".github/workflows/**"):
            categories["workflows"].append(file)
        else:
            categories["other"].append(file)

    return categories


def _check_skip_ci_violations(categories: dict[str, list[str]]) -> tuple[int, str]:
    """Check [skip ci] violations. Returns (exit_code, message)."""
    if categories["code"]:
        return 1, (
            "❌ ERROR: [skip ci] cannot be used with code changes in app/\n"
            f"   Changed files: {', '.join(categories['code'][:3])}"
            + ("..." if len(categories["code"]) > 3 else "")
        )

    if categories["tests"]:
        return 1, (
            "❌ ERROR: [skip ci] cannot be used with test changes\n"
            f"   Changed files: {', '.join(categories['tests'][:3])}"
            + ("..." if len(categories["tests"]) > 3 else "")
        )

    if categories["workflows"]:
        return 1, (
            "❌ ERROR: [skip ci] cannot be used with workflow changes\n"
            f"   Changed files: {', '.join(categories['workflows'][:3])}"
            + ("..." if len(categories["workflows"]) > 3 else "")
            + "\n   Workflow changes must be validated by CI."
        )

    if categories["config"]:
        return 2, (
            "⚠️  WARNING: [skip ci] used with configuration changes\n"
            f"   Changed files: {', '.join(categories['config'][:3])}"
            + ("..." if len(categories["config"]) > 3 else "")
            + "\n   Consider running CI to validate config changes."
        )

    return 0, ""


def _check_skip_tests_violations(categories: dict[str, list[str]]) -> tuple[int, str]:
    """Check [skip tests] violations. Returns (exit_code, message)."""
    if categories["tests"]:
        return 1, (
            "❌ ERROR: [skip tests] cannot be used when tests are modified\n"
            f"   Changed files: {', '.join(categories['tests'][:3])}"
            + ("..." if len(categories["tests"]) > 3 else "")
        )

    if categories["code"]:
        return 2, (
            "⚠️  WARNING: [skip tests] used with code changes\n"
            f"   Changed files: {', '.join(categories['code'][:3])}"
            + ("..." if len(categories["code"]) > 3 else "")
            + "\n   Consider running tests to validate code changes."
        )

    return 0, ""


def validate_skip_usage(directive: str, categories: dict[str, list[str]]) -> tuple[int, str]:
    """
    Validate if skip directive is appropriate for the staged files.

    Returns:
        Tuple of (exit_code, message)
        0 = OK, 1 = Error (block), 2 = Warning (allow)
    """
    if directive == "skip ci":
        return _check_skip_ci_violations(categories)

    if directive == "skip tests":
        return _check_skip_tests_violations(categories)

    if directive == "skip lint" and (categories["code"] or categories["tests"]):
        return 2, (
            "⚠️  WARNING: [skip lint] used with code changes\n"
            "   Consider running linting to catch style issues early."
        )

    if directive == "skip build" and (categories["code"] or categories["config"]):
        return 2, (
            "⚠️  WARNING: [skip build] used with code/config changes\n"
            "   Build artifacts may need regeneration."
        )

    return 0, ""


def main() -> int:
    """Main validation logic."""
    # Get commit message
    commit_msg = get_commit_message()
    if not commit_msg:
        # No message yet (pre-commit hook), skip validation
        return 0

    # Check for skip directive
    directive, _ = check_skip_directive(commit_msg)
    if not directive:
        # No skip directive, nothing to validate
        return 0

    # Get staged files
    staged_files = get_staged_files()
    if not staged_files:
        print("⚠️  No staged files found, skipping validation")
        return 0

    # Categorize files
    categories = categorize_files(staged_files)

    # Validate skip usage
    exit_code, message = validate_skip_usage(directive, categories)

    if exit_code == 1:
        print("\n" + "=" * 70)
        print(message)
        print("\nTo fix this:")
        print("  1. Remove the skip directive from your commit message, OR")
        print("  2. Unstage the code/test files if they shouldn't be committed")
        print("\nProper [skip ci] usage:")
        print("  ✅ Documentation-only changes")
        print("  ✅ Trivial fixes (typos, comments)")
        print("  ❌ Code changes in app/ or tests/")
        print("  ❌ Configuration or workflow changes")
        print("=" * 70 + "\n")
        return 1

    if exit_code == 2:
        print("\n" + "=" * 70)
        print(message)
        print("\nThis is a warning - your commit will proceed.")
        print("Consider if CI validation would be helpful for these changes.")
        print("=" * 70 + "\n")
        return 0  # Allow commit with warning

    # Valid usage
    print(f"✅ [{directive}] usage validated - appropriate for changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
