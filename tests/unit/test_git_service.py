"""
Tests for GitService.
"""

import pytest

from app.services.git_service import GitService

# Skip all tests if Git is not available
pytest.importorskip("git")


@pytest.fixture
def test_repo_path(tmp_path):
    """Create a temporary repository path."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    return repo_path


class TestGitService:
    """Tests for GitService."""

    def test_init_repository(self, test_repo_path):
        """Test initializing a Git repository."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)

        assert repo is not None
        assert (test_repo_path / ".git").exists()
        assert (test_repo_path / ".gitignore").exists()

        # Check initial commit exists
        commits = list(repo.iter_commits())
        assert len(commits) == 1
        assert commits[0].message.strip() == "Initial commit"

        repo.close()

    def test_init_repository_without_commit(self, test_repo_path):
        """Test initializing repository without initial commit."""
        repo = GitService.init_repository(test_repo_path, initial_commit=False)

        assert (test_repo_path / ".git").exists()

        # No commits yet - cannot iterate on empty repo
        assert repo.head.is_valid() is False

        repo.close()

    def test_is_repository(self, test_repo_path):
        """Test checking if directory is a repository."""
        assert not GitService.is_repository(test_repo_path)

        GitService.init_repository(test_repo_path)

        assert GitService.is_repository(test_repo_path)

    def test_get_repository(self, test_repo_path):
        """Test getting a repository object."""
        # Non-existent repo
        repo = GitService.get_repository(test_repo_path)
        assert repo is None

        # Create repo
        GitService.init_repository(test_repo_path)

        repo = GitService.get_repository(test_repo_path)
        assert repo is not None
        repo.close()

    def test_get_status(self, test_repo_path):
        """Test getting repository status."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        status = GitService.get_status(test_repo_path)

        assert status is not None
        assert "branch" in status
        assert status["branch"] in ["main", "master"]
        assert status["is_dirty"] is False
        assert status["total_changes"] == 0
        assert isinstance(status["staged"], list)
        assert isinstance(status["unstaged"], list)
        assert isinstance(status["untracked"], list)

    def test_get_status_with_changes(self, test_repo_path):
        """Test status with untracked files."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Create untracked file
        test_file = test_repo_path / "test.txt"
        test_file.write_text("Hello")

        status = GitService.get_status(test_repo_path)

        assert status["is_dirty"] is True
        assert len(status["untracked"]) == 1
        assert "test.txt" in status["untracked"]
        assert status["total_changes"] == 1

    def test_commit(self, test_repo_path):
        """Test committing changes."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Create and commit file
        test_file = test_repo_path / "test.txt"
        test_file.write_text("Hello")

        success = GitService.commit(
            test_repo_path,
            "Add test file",
            add_all=True,
        )

        assert success is True

        # Verify commit
        status = GitService.get_status(test_repo_path)
        assert status["is_dirty"] is False

        log = GitService.get_log(test_repo_path, max_count=5)
        assert len(log) == 2
        assert log[0]["message"] == "Add test file"

    def test_commit_no_changes(self, test_repo_path):
        """Test committing with no changes."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        success = GitService.commit(
            test_repo_path,
            "No changes",
            add_all=True,
        )

        assert success is False

    def test_commit_specific_files(self, test_repo_path):
        """Test committing specific files."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Create multiple files
        (test_repo_path / "file1.txt").write_text("File 1")
        (test_repo_path / "file2.txt").write_text("File 2")

        # Commit only file1
        success = GitService.commit(
            test_repo_path,
            "Add file1",
            files=["file1.txt"],
        )

        assert success is True

        status = GitService.get_status(test_repo_path)
        assert len(status["untracked"]) == 1
        assert "file2.txt" in status["untracked"]

    def test_get_log(self, test_repo_path):
        """Test getting commit log."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Create commits
        for i in range(3):
            test_file = test_repo_path / f"file{i}.txt"
            test_file.write_text(f"Content {i}")
            GitService.commit(test_repo_path, f"Add file {i}", add_all=True)

        log = GitService.get_log(test_repo_path, max_count=5)

        assert len(log) == 4  # 3 + initial commit
        assert all("sha" in commit for commit in log)
        assert all("message" in commit for commit in log)
        assert all("author" in commit for commit in log)
        assert all("date" in commit for commit in log)

        # Most recent first
        assert log[0]["message"] == "Add file 2"

    def test_add_remote(self, test_repo_path):
        """Test adding a remote."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        success = GitService.add_remote(
            test_repo_path,
            "origin",
            "https://github.com/user/repo.git",
        )

        assert success is True

        remotes = GitService.get_remotes(test_repo_path)
        assert len(remotes) == 1
        assert remotes[0]["name"] == "origin"
        assert "https://github.com/user/repo.git" in remotes[0]["urls"]

    def test_get_remotes_empty(self, test_repo_path):
        """Test getting remotes when none exist."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        remotes = GitService.get_remotes(test_repo_path)
        assert remotes == []

    def test_get_log_non_repo(self, test_repo_path):
        """Test getting log for non-repository."""
        log = GitService.get_log(test_repo_path)
        assert log == []

    def test_get_status_non_repo(self, test_repo_path):
        """Test getting status for non-repository."""
        status = GitService.get_status(test_repo_path)
        assert status is None

    def test_get_status_detached_head(self, test_repo_path):
        """Test getting status with detached HEAD."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)

        # Create a second commit
        test_file = test_repo_path / "test.txt"
        test_file.write_text("content")
        GitService.commit(test_repo_path, "Add test file", add_all=True)

        # Checkout first commit to create detached HEAD
        first_commit = list(repo.iter_commits())[-1]
        repo.git.checkout(first_commit.hexsha)
        repo.close()

        status = GitService.get_status(test_repo_path)

        assert status is not None
        assert "detached" in status["branch"].lower()

    def test_commit_no_repository(self, test_repo_path):
        """Test committing to non-repository raises error."""
        with pytest.raises(ValueError, match="Not a Git repository"):
            GitService.commit(test_repo_path, "Test commit")

    def test_push_non_repository(self, test_repo_path):
        """Test pushing from non-repository."""
        success, message = GitService.push(test_repo_path)

        assert success is False
        assert "Not a Git repository" in message

    def test_push_remote_not_found(self, test_repo_path):
        """Test pushing to non-existent remote."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        success, message = GitService.push(test_repo_path, remote="nonexistent")

        assert success is False
        assert "not found" in message.lower()

    def test_add_remote_duplicate(self, test_repo_path):
        """Test adding duplicate remote fails."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Add first remote
        success1 = GitService.add_remote(
            test_repo_path, "origin", "https://github.com/user/repo1.git"
        )
        assert success1 is True

        # Try to add duplicate
        success2 = GitService.add_remote(
            test_repo_path, "origin", "https://github.com/user/repo2.git"
        )
        assert success2 is False

    def test_add_remote_non_repository(self, test_repo_path):
        """Test adding remote to non-repository."""
        success = GitService.add_remote(
            test_repo_path, "origin", "https://github.com/user/repo.git"
        )
        assert success is False

    def test_get_log_with_limit(self, test_repo_path):
        """Test getting log with custom limit."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Create multiple commits
        for i in range(5):
            test_file = test_repo_path / f"file{i}.txt"
            test_file.write_text(f"Content {i}")
            GitService.commit(test_repo_path, f"Commit {i}", add_all=True)

        # Get only 3 commits
        log = GitService.get_log(test_repo_path, max_count=3)

        assert len(log) == 3
        # Most recent commit first
        assert log[0]["message"] == "Commit 4"

    def test_commit_with_no_changes_staged(self, test_repo_path):
        """Test commit returns False when no changes to commit."""
        repo = GitService.init_repository(test_repo_path, initial_commit=True)
        repo.close()

        # Try to commit with no changes at all
        result = GitService.commit(test_repo_path, "Test commit", add_all=False, files=None)

        # Should return False since there are no staged changes and no files specified
        assert result is False
