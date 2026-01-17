"""
Test suite for Sphinx reference validation (Phase 2).

Tests cover:
- All :ref: labels exist in documentation
- Cross-references are reachable
- No broken internal links
- Proper Sphinx label format
"""

from pathlib import Path
import re

import pytest

# Constants
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"


def find_ref_labels(content: str) -> set[str]:
    """Extract all Sphinx reference labels from content."""
    # Pattern: .. _label-name:
    label_pattern = re.compile(r"^\.\.\s+_([a-zA-Z0-9_-]+):", re.MULTILINE)
    # Pattern: (label-name)=
    myst_pattern = re.compile(r"^\(([a-zA-Z0-9_-]+)\)=", re.MULTILINE)

    labels = set(label_pattern.findall(content))
    labels.update(myst_pattern.findall(content))
    return labels


def find_ref_references(content: str) -> set[str]:
    """Extract all :ref: references from content."""
    # Pattern: :ref:`label-name` or :ref:`text <label-name>`
    ref_pattern = re.compile(r":ref:`(?:[^<>`]+<)?([a-zA-Z0-9_-]+)(?:>)?`")
    return set(ref_pattern.findall(content))


def discover_doc_files() -> list[Path]:
    """Discover all markdown documentation files."""
    return list(DOCS_DIR.glob("*.md"))


@pytest.mark.docs
class TestSphinxReferences:
    """Test Sphinx reference labels and cross-references."""

    def test_all_ref_labels_defined(self):
        """All :ref: references must point to defined labels."""
        all_labels = set()
        all_refs = set()
        files_with_labels = {}
        files_with_refs = {}

        # Collect all labels and references
        for doc_file in discover_doc_files():
            content = doc_file.read_text(encoding="utf-8")

            labels = find_ref_labels(content)
            if labels:
                all_labels.update(labels)
                files_with_labels[doc_file.name] = labels

            refs = find_ref_references(content)
            if refs:
                all_refs.update(refs)
                files_with_refs[doc_file.name] = refs

        # Find undefined references
        undefined_refs = all_refs - all_labels

        if undefined_refs:
            # Build detailed error message
            error_lines = ["\n❌ Undefined Sphinx references found:"]
            for ref in sorted(undefined_refs):
                error_lines.append(f"\n  Reference: '{ref}'")
                # Find which files use this reference
                using_files = [f for f, refs in files_with_refs.items() if ref in refs]
                error_lines.append(f"  Used in: {', '.join(using_files)}")

            error_lines.append(f"\n\nAvailable labels: {sorted(all_labels)}")
            pytest.fail("".join(error_lines))

    def test_split_guides_have_labels(self):
        """New split guides must have proper Sphinx labels."""
        required_files = {
            "installation.md": "installation",
            "getting-started.md": "getting-started",
            "features.md": "features",
            "configuration.md": "configuration",
        }

        for filename, expected_label in required_files.items():
            file_path = DOCS_DIR / filename
            assert file_path.exists(), f"File {filename} not found"

            content = file_path.read_text(encoding="utf-8")
            labels = find_ref_labels(content)

            assert expected_label in labels, (
                f"{filename} missing required label '.. _{expected_label}:'"
            )

    def test_cross_references_between_guides(self):
        """Split guides should cross-reference each other."""
        expected_refs = {
            "installation.md": {"getting-started"},  # Should ref next guide
            "getting-started.md": {"installation", "features"},  # Should ref prev/next
            "features.md": {"getting-started", "configuration"},  # Should ref prev/next
            "configuration.md": {"features"},  # Should ref prev guide
        }

        for filename, expected in expected_refs.items():
            file_path = DOCS_DIR / filename
            content = file_path.read_text(encoding="utf-8")
            refs = find_ref_references(content)

            # Check if at least one expected reference exists
            found = refs & expected
            assert found, (
                f"{filename} should reference at least one of {expected}, but found: {refs}"
            )

    def test_no_orphaned_labels(self):
        """Warn about labels that are never referenced (may indicate cleanup needed)."""
        all_labels = set()
        all_refs = set()

        for doc_file in discover_doc_files():
            content = doc_file.read_text(encoding="utf-8")
            all_labels.update(find_ref_labels(content))
            all_refs.update(find_ref_references(content))

        orphaned = all_labels - all_refs

        # Don't fail, just warn - some labels may be referenced from outside docs
        if orphaned:
            print(f"\n⚠️  Orphaned labels (never referenced): {sorted(orphaned)}")  # noqa: T201

    def test_label_naming_convention(self):
        """Labels should follow kebab-case naming convention."""
        invalid_labels: list[tuple[str, str]] = []

        for doc_file in discover_doc_files():
            content = doc_file.read_text(encoding="utf-8")
            labels = find_ref_labels(content)

            # Check kebab-case: lowercase letters, numbers, hyphens only
            invalid_labels.extend(
                (doc_file.name, label)
                for label in labels
                if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", label)
            )

        assert not invalid_labels, (
            "Labels should use kebab-case (lowercase with hyphens):\n"
            + "\n".join(f"  {file}: {label}" for file, label in invalid_labels)
        )

    def test_user_guide_not_referenced(self):
        """Ensure old user-guide.md is not referenced after split."""
        user_guide_refs = []

        for doc_file in discover_doc_files():
            if doc_file.name == "user-guide.md":
                continue  # Skip the file itself if it still exists

            content = doc_file.read_text(encoding="utf-8")

            # Check for references to user-guide
            if "user-guide" in content.lower() or "user_guide" in content.lower():
                # Find specific lines
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    if "user-guide" in line.lower() or "user_guide" in line.lower():
                        user_guide_refs.append(f"{doc_file.name}:{i}: {line.strip()}")

        assert not user_guide_refs, (
            "Found references to old user-guide.md after split:\n"
            + "\n".join(f"  {ref}" for ref in user_guide_refs)
        )


@pytest.mark.docs
class TestDocumentationStructure:
    """Test documentation file structure."""

    def test_split_guides_exist(self):
        """All split guide files must exist."""
        required_files = [
            "installation.md",
            "getting-started.md",
            "features.md",
            "configuration.md",
        ]

        for filename in required_files:
            file_path = DOCS_DIR / filename
            assert file_path.exists(), f"Required file {filename} not found"
            assert file_path.stat().st_size > 0, f"{filename} is empty"

    def test_split_guides_have_content(self):
        """Split guides should have substantial content."""
        min_lines = {
            "installation.md": 500,  # Long installation guide
            "getting-started.md": 30,  # Shorter intro
            "features.md": 400,  # Comprehensive features
            "configuration.md": 500,  # Detailed configuration
        }

        for filename, expected_lines in min_lines.items():
            file_path = DOCS_DIR / filename
            content = file_path.read_text(encoding="utf-8")
            line_count = len(content.splitlines())

            assert line_count >= expected_lines, (
                f"{filename} has only {line_count} lines, expected at least {expected_lines}"
            )

    def test_index_references_split_guides(self):
        """Index.md should reference all split guides."""
        index_path = DOCS_DIR / "index.md"
        content = index_path.read_text(encoding="utf-8")

        required_refs = [
            "installation",
            "getting-started",
            "features",
            "configuration",
        ]

        for ref in required_refs:
            assert ref in content, f"index.md should reference {ref}.md in toctree"


# Pytest configuration
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "docs: marks tests as documentation-related (deselect with '-m \"not docs\"')"
    )
