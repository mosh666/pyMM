"""Tests for FileSystemService."""
import pytest
from pathlib import Path
from app.core.services.file_system_service import FileSystemService


class TestFileSystemService:
    """Test suite for FileSystemService."""

    @pytest.fixture
    def service(self, app_root):
        """Create FileSystemService instance."""
        return FileSystemService(app_root)

    def test_init_with_explicit_root(self, app_root):
        """Test initialization with explicit root path."""
        service = FileSystemService(app_root)
        assert service.get_app_root() == app_root

    def test_init_auto_detect_root(self):
        """Test initialization with auto-detected root."""
        service = FileSystemService()
        # Should auto-detect from module location
        assert service.get_app_root().exists()

    def test_resolve_relative_path(self, service, app_root):
        """Test resolving relative paths."""
        rel_path = Path("test/file.txt")
        resolved = service.resolve_path(rel_path)
        assert resolved == app_root / "test" / "file.txt"
        assert resolved.is_absolute()

    def test_resolve_absolute_path(self, service, temp_dir):
        """Test resolving absolute paths."""
        abs_path = temp_dir / "absolute" / "file.txt"
        resolved = service.resolve_path(abs_path)
        assert resolved == abs_path.resolve()

    def test_ensure_directory_creates_new(self, service, app_root):
        """Test creating a new directory."""
        new_dir = "test_dir/nested"
        result = service.ensure_directory(new_dir)
        assert result.exists()
        assert result.is_dir()
        assert result == app_root / "test_dir" / "nested"

    def test_ensure_directory_existing(self, service, app_root):
        """Test ensuring existing directory."""
        existing = app_root / "existing"
        existing.mkdir()
        result = service.ensure_directory(existing)
        assert result.exists()
        assert result == existing

    def test_list_directory_empty(self, service, app_root):
        """Test listing empty directory."""
        empty_dir = app_root / "empty"
        empty_dir.mkdir()
        files = service.list_directory(empty_dir)
        assert files == []

    def test_list_directory_with_files(self, service, app_root):
        """Test listing directory with files."""
        test_dir = app_root / "files"
        test_dir.mkdir()
        (test_dir / "file1.txt").touch()
        (test_dir / "file2.txt").touch()
        (test_dir / "file3.log").touch()

        # List all files
        all_files = service.list_directory(test_dir)
        assert len(all_files) == 3

        # List with pattern
        txt_files = service.list_directory(test_dir, pattern="*.txt")
        assert len(txt_files) == 2

    def test_list_directory_recursive(self, service, app_root):
        """Test recursive directory listing."""
        base = app_root / "recursive"
        base.mkdir()
        (base / "level1").mkdir()
        (base / "level1" / "level2").mkdir()
        (base / "file1.txt").touch()
        (base / "level1" / "file2.txt").touch()
        (base / "level1" / "level2" / "file3.txt").touch()

        files = service.list_directory(base, pattern="*.txt", recursive=True)
        assert len(files) == 3

    def test_copy_file_success(self, service, app_root):
        """Test copying a file."""
        src = app_root / "source.txt"
        src.write_text("test content")
        dst = app_root / "copy" / "dest.txt"

        result = service.copy_file(src, dst)
        assert result.exists()
        assert result.read_text() == "test content"
        assert src.exists()  # Original still exists

    def test_copy_file_overwrite(self, service, app_root):
        """Test copying with overwrite."""
        src = app_root / "source.txt"
        src.write_text("new content")
        dst = app_root / "dest.txt"
        dst.write_text("old content")

        # Should fail without overwrite
        with pytest.raises(FileExistsError):
            service.copy_file(src, dst, overwrite=False)

        # Should succeed with overwrite
        result = service.copy_file(src, dst, overwrite=True)
        assert result.read_text() == "new content"

    def test_copy_file_not_found(self, service, app_root):
        """Test copying non-existent file."""
        src = app_root / "missing.txt"
        dst = app_root / "dest.txt"

        with pytest.raises(FileNotFoundError):
            service.copy_file(src, dst)

    def test_move_file_success(self, service, app_root):
        """Test moving a file."""
        src = app_root / "source.txt"
        src.write_text("test content")
        dst = app_root / "moved" / "dest.txt"

        result = service.move_file(src, dst)
        assert result.exists()
        assert result.read_text() == "test content"
        assert not src.exists()  # Original moved

    def test_delete_file_exists(self, service, app_root):
        """Test deleting existing file."""
        file = app_root / "delete_me.txt"
        file.touch()

        result = service.delete_file(file)
        assert result is True
        assert not file.exists()

    def test_delete_file_missing(self, service, app_root):
        """Test deleting non-existent file."""
        file = app_root / "missing.txt"

        # Should not raise with missing_ok=True
        result = service.delete_file(file, missing_ok=True)
        assert result is False

        # Should raise with missing_ok=False
        with pytest.raises(FileNotFoundError):
            service.delete_file(file, missing_ok=False)

    def test_delete_directory_empty(self, service, app_root):
        """Test deleting empty directory."""
        dir_path = app_root / "empty_dir"
        dir_path.mkdir()

        result = service.delete_directory(dir_path)
        assert result is True
        assert not dir_path.exists()

    def test_delete_directory_recursive(self, service, app_root):
        """Test deleting directory recursively."""
        dir_path = app_root / "full_dir"
        dir_path.mkdir()
        (dir_path / "file.txt").touch()
        (dir_path / "subdir").mkdir()

        # Should fail without recursive
        with pytest.raises(OSError):
            service.delete_directory(dir_path, recursive=False)

        # Should succeed with recursive
        result = service.delete_directory(dir_path, recursive=True)
        assert result is True
        assert not dir_path.exists()

    def test_get_file_size(self, service, app_root):
        """Test getting file size."""
        file = app_root / "sized.txt"
        content = "A" * 1000
        file.write_text(content)

        size = service.get_file_size(file)
        assert size == len(content.encode("utf-8"))

    def test_get_file_size_missing(self, service, app_root):
        """Test getting size of non-existent file."""
        file = app_root / "missing.txt"

        with pytest.raises(FileNotFoundError):
            service.get_file_size(file)

    def test_get_free_space(self, service, app_root):
        """Test getting free disk space."""
        free_space = service.get_free_space(app_root)
        assert free_space > 0
        assert isinstance(free_space, int)

    def test_get_relative_path(self, service, app_root):
        """Test getting relative path."""
        abs_path = app_root / "sub" / "file.txt"
        rel_path = service.get_relative_path(abs_path, app_root)
        assert rel_path == Path("sub") / "file.txt"

    def test_get_relative_path_outside_base(self, service, app_root, temp_dir):
        """Test relative path for path outside base."""
        outside_path = temp_dir / "outside" / "file.txt"
        rel_path = service.get_relative_path(outside_path, app_root)
        # Should return original path if not relative to base
        assert rel_path == outside_path
