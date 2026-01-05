"""
Test Git integration functionality.

This test script verifies:
- GitService operations
- Git status, commit, and log operations

Note: Git integration with project management has been removed.
This test only verifies the GitService standalone functionality.
"""

import shutil
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.git_service import GitService


def test_git_service():
    """Test GitService functionality."""
    print("=" * 60)
    print("Testing Git Service")
    print("=" * 60)

    test_repo_path = Path("D:/pyMM/test_projects/git_test_repo")

    # Clean up if exists
    if test_repo_path.exists():
        shutil.rmtree(test_repo_path)

    test_repo_path.mkdir(parents=True)

    try:
        # Test init_repository
        print("\n✓ Creating test repository directory")
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        print("✓ Initialized Git repository with initial commit")

        # Test is_repository
        assert GitService.is_repository(test_repo_path)
        print("✓ Confirmed directory is a Git repository")

        # Test get_status
        status = GitService.get_status(test_repo_path)
        print(f"✓ Got repository status: {status['branch']}")
        print(f"  - Branch: {status['branch']}")
        print(f"  - Changes: {status['total_changes']}")

        # Create a test file
        test_file = test_repo_path / "test.txt"
        test_file.write_text("Hello, Git!")
        print("✓ Created test file: test.txt")

        # Check status with untracked file
        status = GitService.get_status(test_repo_path)
        assert len(status["untracked"]) == 1
        print(f"✓ Detected untracked file: {status['untracked']}")

        # Test commit
        success = GitService.commit(test_repo_path, "Add test file", add_all=True)
        assert success
        print("✓ Committed changes")

        # Check status after commit
        status = GitService.get_status(test_repo_path)
        assert status["total_changes"] == 0
        print("✓ Repository is clean after commit")

        # Test get_log
        log = GitService.get_log(test_repo_path, max_count=5)
        assert len(log) == 2  # Initial commit + test file commit
        print(f"✓ Retrieved commit log: {len(log)} commits")
        for commit in log:
            print(f"  - {commit['sha']}: {commit['message'][:50]}")

        # Close the repository to release file handles
        repo.close()

        print("\n✅ Git service tests passed!")

    except Exception as e:
        print(f"\n✗ Error during test: {e}")
        import traceback

        traceback.print_exc()
        raise
    finally:
        # Clean up
        if test_repo_path.exists():
            try:
                # On Windows, we need to handle file permissions
                import stat

                def remove_readonly(func, path, _):
                    """Clear the readonly bit and reattempt the removal"""
                    Path(path).chmod(stat.S_IWRITE)
                    func(path)

                shutil.rmtree(test_repo_path, onerror=remove_readonly)
            except Exception as e:
                print(f"Warning: Could not clean up test repo: {e}")
        print("✓ Cleaned up test repository")


if __name__ == "__main__":
    print("=" * 60)
    print("Git Service Test")
    print("=" * 60)
    print("\nNote: Git integration with project management has been removed.")
    print("This test only verifies the GitService standalone functionality.\n")

    try:
        test_git_service()

        print("\n" + "=" * 60)
        print("All tests complete!")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
