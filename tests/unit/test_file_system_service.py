"""Unit tests for FileSystemService."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.core.services.file_system_service import FileSystemService


class TestFileSystemService:
    """Test suite for FileSystemService."""

    @pytest.fixture
    def service(self, app_root):
        """Create FileSystemService instance."""
        svc = FileSystemService(app_root)
        svc._bypass_drive_mock = True  # Enable real method for these tests
        return svc

    def test_init_with_explicit_root(self, app_root):
        """Test initialization with explicit root path."""
        service = FileSystemService(app_root)
        assert service.get_app_root().resolve() == app_root.resolve()

        # Test cache initialization
        assert hasattr(service, "_drive_root")
        assert service._drive_root is None

    def test_init_auto_detect_root(self):
        """Test initialization with auto-detected root."""
        service = FileSystemService()
        # Should auto-detect from module location
        assert service.get_app_root().exists()

    def test_get_drive_root(self, service, app_root, monkeypatch):
        """Test drive root detection."""
        # Clean state
        service._drive_root = None

        # 1. Test Windows behavior (legacy portable mode)
        # Mock os.name to be nt (Windows)
        monkeypatch.setattr(os, "name", "nt")
        service._force_portable = True

        # On Windows, it uses app_root.anchor
        drive_root = service.get_drive_root()
        assert drive_root == Path(app_root.anchor)

        # 2. Test Linux/Unix behavior (XDG/Home based)
        service._drive_root = None
        monkeypatch.setattr(os, "name", "posix")

        # Mock pathlib.Path.home()
        mock_home = app_root / "home"
        with patch("pathlib.Path.home", return_value=mock_home):
            drive_root = service.get_drive_root()
            expected_linux_root = mock_home / "PortableMediaManager"
            assert drive_root == expected_linux_root

    def test_get_drive_root_cached(self, service, app_root, monkeypatch):
        """Test that drive root result is cached."""
        service._drive_root = None
        service._force_portable = True
        monkeypatch.setattr(os, "name", "nt")

        # First call caches
        root1 = service.get_drive_root()
        assert root1 == Path(app_root.anchor)

        # Modify the detection logic (e.g. switch OS) to prove cache is used
        monkeypatch.setattr(os, "name", "posix")

        # Second call returns cached Windows value
        root2 = service.get_drive_root()
        assert root2 == root1

    def test_force_portable(self, service):
        """Test forcing portable mode."""
        # Manually set protected member since no public setter exists
        service._force_portable = True
        assert service._force_portable is True

    def test_get_portable_folder(self, service):
        """Test getting portable folder paths."""
        service._drive_root = None

        # Mock drive root
        mock_root = Path("/mock/root")
        with patch.object(service, "get_drive_root", return_value=mock_root):
            # Test generic folder - Implementation does NOT modify info
            folder = service.get_portable_folder("Test")
            assert folder == mock_root / "Test"

            # Test with prefix
            folder2 = service.get_portable_folder("pyMM.Config")
            assert folder2 == mock_root / "pyMM.Config"

    def test_ensure_portable_folders(self, service):
        """Test creation of portable directory structure."""
        with patch.object(service, "get_drive_root") as mock_get_root:
            mock_root = Mock()
            mock_get_root.return_value = mock_root

            # Mock get_portable_folder to return mocks that can be mkdir'd
            mock_folder = Mock()
            with patch.object(service, "get_portable_folder", return_value=mock_folder):
                service.ensure_portable_folders()

                # Should create basic folders
                assert service.get_portable_folder.call_count >= 2  # Projects and Logs
                mock_folder.mkdir.assert_called()

    def test_resolve_relative_path(self, service, app_root):
        """Test resolving relative paths."""
        rel_path = Path("test/file.txt")
        resolved = service.resolve_path(rel_path)
        assert resolved.resolve() == (app_root / "test" / "file.txt").resolve()
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
        assert result.resolve() == (app_root / "test_dir" / "nested").resolve()

    def test_ensure_directory_existing(self, service, app_root):
        """Test ensuring existing directory."""
        existing = app_root / "existing"
        existing.mkdir()
        result = service.ensure_directory(existing)
        assert result.exists()
        assert result.resolve() == existing.resolve()

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
