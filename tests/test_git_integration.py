"""
Test Git integration functionality.

This test script verifies:
- GitService operations
- Git status, commit, and log operations

Note: Git integration with project management has been removed.
This test only verifies the GitService standalone functionality.
"""

from pathlib import Path
import sys

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.git_service import GitService


def test_git_service(tmp_path):
    """Test GitService functionality."""

    test_repo_path = tmp_path / "git_test_repo"
    test_repo_path.mkdir(parents=True)

    try:
        # Test init_repository
        repo = GitService.init_repository(test_repo_path, initial_commit=True)

        # Test is_repository
        assert GitService.is_repository(test_repo_path)

        # Test get_status
        status = GitService.get_status(test_repo_path)

        # Create a test file
        test_file = test_repo_path / "test.txt"
        test_file.write_text("Hello, Git!")

        # Check status with untracked file
        status = GitService.get_status(test_repo_path)
        assert len(status["untracked"]) == 1

        # Test commit
        success = GitService.commit(test_repo_path, "Add test file", add_all=True)
        assert success

        # Check status after commit
        status = GitService.get_status(test_repo_path)
        assert status["total_changes"] == 0

        # Test get_log
        log = GitService.get_log(test_repo_path, max_count=5)
        assert len(log) == 2  # Initial commit + test file commit
        for _commit in log:
            pass

        # Close the repository to release file handles
        repo.close()

    except Exception:
        import traceback

        traceback.print_exc()
        raise


if __name__ == "__main__":
    import tempfile

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_git_service(Path(tmpdir))

    except Exception:
        sys.exit(1)
