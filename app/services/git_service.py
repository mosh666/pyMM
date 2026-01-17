"""
Git service for managing Git operations.

This module provides a GitService class that wraps GitPython
to provide Git functionality for projects.
"""

from pathlib import Path
from typing import Any

import git
from git import GitCommandError, Repo


class GitService:
    """
    Service for Git repository operations.

    Provides methods for:
    - Repository initialization
    - Status checking
    - Committing changes
    - Pushing to remotes
    """

    @staticmethod
    def init_repository(path: Path, initial_commit: bool = True) -> Repo:
        """
        Initialize a Git repository.

        Args:
            path: Path to the directory to initialize
            initial_commit: Whether to create an initial commit

        Returns:
            Git Repo object

        Raises:
            GitCommandError: If Git initialization fails
        """
        repo = Repo.init(path)

        if initial_commit:
            # Create .gitignore
            gitignore_path = path / ".gitignore"
            if not gitignore_path.exists():
                gitignore_content = """# pyMM project files
cache/
*.tmp
*.log
*.pyc
__pycache__/

# OS files
.DS_Store
Thumbs.db
desktop.ini

# IDE files
.vscode/
.idea/
*.swp
"""
                gitignore_path.write_text(gitignore_content, encoding="utf-8")

            # Add .gitignore to repo
            repo.index.add([".gitignore"])

            # Create initial commit
            repo.index.commit("Initial commit")

        return repo

    @staticmethod
    def get_repository(path: Path) -> Repo | None:
        """
        Get a Git repository at the specified path.

        Args:
            path: Path to the repository

        Returns:
            Repo object or None if not a Git repository
        """
        try:
            return Repo(path)
        except (git.InvalidGitRepositoryError, git.NoSuchPathError):
            return None

    @staticmethod
    def is_repository(path: Path) -> bool:
        """
        Check if a directory is a Git repository.

        Args:
            path: Path to check

        Returns:
            True if it's a Git repository
        """
        return (path / ".git").exists()

    @staticmethod
    def get_status(path: Path) -> dict[str, Any] | None:
        """
        Get the status of a Git repository.

        Args:
            path: Path to the repository

        Returns:
            Dictionary with status information or None if not a repo
        """
        repo = GitService.get_repository(path)
        if not repo:
            return None

        # Get staged files
        staged = [item.a_path for item in repo.index.diff("HEAD")]

        # Get unstaged files
        unstaged = [item.a_path for item in repo.index.diff(None)]

        # Get untracked files
        untracked = repo.untracked_files

        # Get current branch
        try:
            branch = repo.active_branch.name
        except TypeError:
            # Detached HEAD
            branch = "HEAD (detached)"

        # Check if repo is dirty
        is_dirty = repo.is_dirty(untracked_files=True)

        return {
            "branch": branch,
            "staged": staged,
            "unstaged": unstaged,
            "untracked": untracked,
            "is_dirty": is_dirty,
            "total_changes": len(staged) + len(unstaged) + len(untracked),
        }

    @staticmethod
    def commit(
        path: Path,
        message: str,
        add_all: bool = False,
        files: list[str] | None = None,
    ) -> bool:
        """
        Commit changes to the repository.

        Args:
            path: Path to the repository
            message: Commit message
            add_all: Whether to stage all changes before committing
            files: Specific files to stage (if add_all is False)

        Returns:
            True if commit was successful

        Raises:
            GitCommandError: If commit fails
        """
        repo = GitService.get_repository(path)
        if not repo:
            raise ValueError(f"Not a Git repository: {path}")

        # Stage changes
        if add_all:
            repo.git.add(A=True)
        elif files:
            repo.index.add(files)

        # Check if there are changes to commit
        if not repo.index.diff("HEAD") and not repo.untracked_files:
            return False

        # Commit
        repo.index.commit(message)
        return True

    @staticmethod
    def push(path: Path, remote: str = "origin", branch: str | None = None) -> tuple[bool, str]:
        """
        Push commits to a remote repository.

        Args:
            path: Path to the repository
            remote: Name of the remote (default: "origin")
            branch: Branch to push (default: current branch)

        Returns:
            Tuple of (success, message)
        """
        repo = GitService.get_repository(path)
        if not repo:
            return False, f"Not a Git repository: {path}"

        # Check if remote exists
        if remote not in [r.name for r in repo.remotes]:
            return False, f"Remote '{remote}' not found"

        try:
            # Get the remote
            remote_obj = repo.remote(remote)

            # Get branch to push
            if branch is None:
                branch = repo.active_branch.name

            # Push
            push_info = remote_obj.push(branch)

            # Check if push was successful
            if push_info and push_info[0].flags & push_info[0].ERROR:
                return False, f"Push failed: {push_info[0].summary}"

            return True, f"Successfully pushed to {remote}/{branch}"

        except GitCommandError as e:
            return False, f"Push failed: {e!s}"

    @staticmethod
    def add_remote(path: Path, name: str, url: str) -> bool:
        """
        Add a remote to the repository.

        Args:
            path: Path to the repository
            name: Name of the remote
            url: URL of the remote

        Returns:
            True if remote was added successfully
        """
        repo = GitService.get_repository(path)
        if not repo:
            return False

        try:
            repo.create_remote(name, url)
            return True
        except GitCommandError:
            return False

    @staticmethod
    def get_remotes(path: Path) -> list[dict[str, Any]]:
        """
        Get list of remotes for the repository.

        Args:
            path: Path to the repository

        Returns:
            List of dictionaries with remote information
        """
        repo = GitService.get_repository(path)
        if not repo:
            return []

        remotes = []
        for remote in repo.remotes:
            remotes.append(
                {
                    "name": remote.name,
                    "urls": list(remote.urls),
                }
            )

        return remotes

    @staticmethod
    def get_log(path: Path, max_count: int = 10) -> list[dict[str, Any]]:
        """
        Get commit log for the repository.

        Args:
            path: Path to the repository
            max_count: Maximum number of commits to retrieve

        Returns:
            List of commit dictionaries
        """
        repo = GitService.get_repository(path)
        if not repo:
            return []

        commits = []
        for commit in repo.iter_commits(max_count=max_count):
            commits.append(
                {
                    "sha": commit.hexsha[:7],
                    "message": commit.message.strip(),
                    "author": f"{commit.author.name} <{commit.author.email}>",
                    "date": commit.committed_datetime.isoformat(),
                }
            )

        return commits
