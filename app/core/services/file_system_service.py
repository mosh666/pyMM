"""
File system service for pyMediaManager.
Provides abstraction layer for file operations with portable path handling.
"""

import logging
from pathlib import Path
import shutil


class FileSystemService:
    """Service for file system operations with portable path handling."""

    def __init__(self, app_root: Path | None = None):
        """
        Initialize file system service.

        Args:
            app_root: Application root directory. If None, auto-detects from module path.
        """
        self.logger = logging.getLogger(__name__)
        if app_root is None:
            # Auto-detect: go up from app/core/services/ to root
            self.app_root = Path(__file__).parent.parent.parent.parent.resolve()
        else:
            self.app_root = Path(app_root).resolve()

        self._drive_root: Path | None = None

    def get_app_root(self) -> Path:
        """Get the application root directory."""
        return self.app_root

    def get_drive_root(self) -> Path:
        """
        Get the root of the drive containing the app.

        Returns the drive root (e.g., D:\\ if app is at D:\\pyMM).
        Caches the result after first call.

        Returns:
            Path to drive root directory
        """
        if self._drive_root is None:
            # Get the drive root by taking the anchor of the absolute path
            # For D:\pyMM\app, this returns D:\
            self._drive_root = Path(self.app_root.anchor)

        return self._drive_root

    def get_portable_folder(self, folder_name: str) -> Path:
        """
        Get path to a portable folder at the drive root.

        For portable operation, certain folders (Projects, Logs) should be
        at the drive root rather than within the app directory.

        Args:
            folder_name: Name of the folder (e.g., "pyMM.Projects", "pyMM.Logs")

        Returns:
            Path to the portable folder at drive root
        """
        return self.get_drive_root() / folder_name

    def ensure_portable_folders(self) -> dict[str, Path]:
        """
        Ensure all portable folders exist at the drive root.

        Creates pyMM.Projects and pyMM.Logs folders at the root of the
        drive containing the application.

        Returns:
            Dictionary mapping folder names to their resolved paths
        """
        folders = {
            "projects": self.get_portable_folder("pyMM.Projects"),
            "logs": self.get_portable_folder("pyMM.Logs"),
        }

        for name, path in folders.items():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                # Log error but continue - folders may already exist or have permission issues
                self.logger.warning(f"Could not create {name} folder at {path}: {e}")

        return folders

    def get_relative_path(self, path: Path, base: Path | None = None) -> Path:
        """
        Get path relative to base directory.

        Args:
            path: Absolute path to convert
            base: Base directory (defaults to app_root)

        Returns:
            Relative path from base to path
        """
        if base is None:
            base = self.app_root
        try:
            return path.relative_to(base)
        except ValueError:
            # Path is not relative to base, return as-is
            return path

    def resolve_path(self, path: Path | str, relative_to: Path | None = None) -> Path:
        """
        Resolve a path that may be relative or absolute.

        Args:
            path: Path to resolve (string or Path object)
            relative_to: Base directory for relative paths (defaults to app_root)

        Returns:
            Resolved absolute path
        """
        path = Path(path)
        if path.is_absolute():
            return path.resolve()

        if relative_to is None:
            relative_to = self.app_root

        return (relative_to / path).resolve()

    def ensure_directory(self, path: Path | str) -> Path:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            path: Directory path to create

        Returns:
            Resolved path to the directory

        Raises:
            OSError: If directory creation fails
        """
        dir_path = self.resolve_path(path)
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path

    def list_directory(
        self, path: Path | str, pattern: str = "*", recursive: bool = False
    ) -> list[Path]:
        """
        List files in a directory matching a pattern.

        Args:
            path: Directory to list
            pattern: Glob pattern to match (default: "*")
            recursive: If True, search recursively with rglob

        Returns:
            List of matching paths
        """
        dir_path = self.resolve_path(path)
        if not dir_path.exists() or not dir_path.is_dir():
            return []

        if recursive:
            return sorted(dir_path.rglob(pattern))
        return sorted(dir_path.glob(pattern))

    def copy_file(self, src: Path | str, dst: Path | str, overwrite: bool = False) -> Path:
        """
        Copy a file from source to destination.

        Args:
            src: Source file path
            dst: Destination file path
            overwrite: If True, overwrite existing destination

        Returns:
            Path to the copied file

        Raises:
            FileNotFoundError: If source doesn't exist
            FileExistsError: If destination exists and overwrite=False
        """
        src_path = self.resolve_path(src)
        dst_path = self.resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")

        if dst_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {dst_path}")

        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(src_path, dst_path)
        return dst_path

    def move_file(self, src: Path | str, dst: Path | str, overwrite: bool = False) -> Path:
        """
        Move a file from source to destination.

        Args:
            src: Source file path
            dst: Destination file path
            overwrite: If True, overwrite existing destination

        Returns:
            Path to the moved file

        Raises:
            FileNotFoundError: If source doesn't exist
            FileExistsError: If destination exists and overwrite=False
        """
        src_path = self.resolve_path(src)
        dst_path = self.resolve_path(dst)

        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")

        if dst_path.exists() and not overwrite:
            raise FileExistsError(f"Destination already exists: {dst_path}")

        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(src_path), str(dst_path))
        return dst_path

    def delete_file(self, path: Path | str, missing_ok: bool = True) -> bool:
        """
        Delete a file.

        Args:
            path: File path to delete
            missing_ok: If True, don't raise error if file doesn't exist

        Returns:
            True if file was deleted, False if it didn't exist

        Raises:
            FileNotFoundError: If file doesn't exist and missing_ok=False
        """
        file_path = self.resolve_path(path)

        if not file_path.exists():
            if missing_ok:
                return False
            raise FileNotFoundError(f"File not found: {file_path}")

        file_path.unlink()
        return True

    def delete_directory(
        self, path: Path | str, missing_ok: bool = True, recursive: bool = False
    ) -> bool:
        """
        Delete a directory.

        Args:
            path: Directory path to delete
            missing_ok: If True, don't raise error if directory doesn't exist
            recursive: If True, delete recursively (rmtree)

        Returns:
            True if directory was deleted, False if it didn't exist

        Raises:
            FileNotFoundError: If directory doesn't exist and missing_ok=False
            OSError: If directory is not empty and recursive=False
        """
        dir_path = self.resolve_path(path)

        if not dir_path.exists():
            if missing_ok:
                return False
            raise FileNotFoundError(f"Directory not found: {dir_path}")

        if recursive:
            shutil.rmtree(dir_path)
        else:
            dir_path.rmdir()  # Fails if not empty

        return True

    def get_file_size(self, path: Path | str) -> int:
        """
        Get file size in bytes.

        Args:
            path: File path

        Returns:
            File size in bytes

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.resolve_path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path.stat().st_size

    def get_free_space(self, path: Path | str) -> int:
        """
        Get free disk space for the drive containing the path.

        Args:
            path: Any path on the drive

        Returns:
            Free space in bytes
        """
        resolved_path = self.resolve_path(path)
        stat = shutil.disk_usage(resolved_path)
        return stat.free
