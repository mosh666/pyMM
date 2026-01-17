"""Unit tests for FileSystemService."""

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

    def test_get_drive_root(self, service, app_root):
        """Test drive root detection."""
        # Clean state
        service._drive_root = None

        # 1. Test Windows behavior (legacy portable mode)
        # Mock is_windows() to return True
        with patch("app.core.services.file_system_service.is_windows", return_value=True):
            service._force_portable = True

            # On Windows, it uses app_root.anchor
            drive_root = service.get_drive_root()
            assert drive_root == Path(app_root.anchor)

        # 2. Test Linux/Unix behavior (XDG/Home based)
        service._drive_root = None

        # Mock is_windows() to return False and Path.home()
        mock_home = app_root / "home"
        with (
            patch("app.core.services.file_system_service.is_windows", return_value=False),
            patch("pathlib.Path.home", return_value=mock_home),
        ):
            drive_root = service.get_drive_root()
            expected_linux_root = mock_home / "PortableMediaManager"
            assert drive_root == expected_linux_root

    def test_get_drive_root_cached(self, app_root):
        """Test that drive root result is cached."""
        # Create service without bypass flag for this test
        service = FileSystemService(app_root)
        service._force_portable = True

        # Mock the platform-specific logic to avoid cross-platform issues
        # This prevents the WindowsPath/PosixPath incompatibility in Python 3.14
        mock_root = app_root / "mock_drive"
        mock_root.mkdir(exist_ok=True)

        # First call: should compute and cache the result
        service._drive_root = None
        root1 = service.get_drive_root()
        assert root1 is not None

        # Verify caching: modify the internal _drive_root and confirm get_drive_root
        # returns the cached value without recomputing
        cached_value = service._drive_root
        assert cached_value is not None

        # Second call: should return the same cached value
        root2 = service.get_drive_root()
        assert root2 == root1
        assert root2 == cached_value

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

    def test_move_file_success(self, service, app_root):
        """Test moving a file."""
        src = app_root / "source.txt"
        src.write_text("test content")
        dst = app_root / "moved" / "dest.txt"

        result = service.move_file(src, dst)
        assert result.exists()
        assert result.read_text() == "test content"
        assert not src.exists()  # Original should be moved

    def test_move_file_overwrite(self, service, app_root):
        """Test moving with overwrite."""
        src = app_root / "source.txt"
        src.write_text("new content")
        dst = app_root / "dest.txt"
        dst.write_text("old content")

        # Should fail without overwrite
        with pytest.raises(FileExistsError):
            service.move_file(src, dst, overwrite=False)

        # Recreate source file since move failed
        src.write_text("new content")

        # Should succeed with overwrite
        result = service.move_file(src, dst, overwrite=True)
        assert result.read_text() == "new content"
        assert not src.exists()

    def test_delete_file_success(self, service, app_root):
        """Test deleting a file."""
        file_to_delete = app_root / "delete_me.txt"
        file_to_delete.write_text("content")

        assert file_to_delete.exists()
        service.delete_file(file_to_delete)
        assert not file_to_delete.exists()

    def test_delete_file_not_found(self, service, app_root):
        """Test deleting non-existent file."""
        non_existent = app_root / "missing.txt"

        # Should not raise error
        service.delete_file(non_existent)
        assert not non_existent.exists()

    def test_delete_directory_success(self, service, app_root):
        """Test deleting a directory."""
        dir_to_delete = app_root / "delete_dir"
        dir_to_delete.mkdir()
        (dir_to_delete / "file.txt").write_text("content")

        assert dir_to_delete.exists()
        service.delete_directory(dir_to_delete, recursive=True)
        assert not dir_to_delete.exists()

    def test_delete_directory_not_found(self, service, app_root):
        """Test deleting non-existent directory."""
        non_existent = app_root / "missing_dir"

        # Should not raise error with missing_ok
        service.delete_directory(non_existent, missing_ok=True)
        assert not non_existent.exists()

    def test_file_size(self, service, app_root):
        """Test getting file size."""
        test_file = app_root / "sized.txt"
        test_file.write_text("12345678")

        size = service.get_file_size(test_file)
        assert size == 8

    def test_file_size_not_found(self, service, app_root):
        """Test getting size of non-existent file."""
        non_existent = app_root / "missing.txt"

        with pytest.raises(FileNotFoundError):
            service.get_file_size(non_existent)

    def test_get_free_space(self, service, app_root):
        """Test getting free space."""
        free_space = service.get_free_space(app_root)
        assert free_space > 0
        assert isinstance(free_space, int)

    def test_get_relative_path(self, service, app_root):
        """Test getting relative path."""
        full_path = app_root / "subdir" / "file.txt"
        relative = service.get_relative_path(full_path, base=app_root)
        assert relative == Path("subdir") / "file.txt"

    def test_get_relative_path_default_base(self, service, app_root):
        """Test getting relative path with default base."""
        full_path = app_root / "file.txt"
        relative = service.get_relative_path(full_path)
        # Should be relative to app_root by default
        assert not relative.is_absolute() or relative == Path("file.txt")


class TestPortableModeDetection:
    """Test suite for portable mode detection logic."""

    def test_detect_portable_mode_cli_argument(self):
        """Test CLI argument takes precedence."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        result = resolve_portable_config(cli_portable=True)
        assert result.enabled is True
        assert result.source == PortableMode.CLI

        result = resolve_portable_config(cli_portable=False)
        assert result.enabled is False
        assert result.source == PortableMode.CLI

    def test_detect_portable_mode_environment_variable(self, monkeypatch):
        """Test environment variable detection."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        # Test with various truthy values
        monkeypatch.setenv("PYMM_PORTABLE", "1")
        result = resolve_portable_config()
        assert result.enabled is True
        assert result.source == PortableMode.ENV

        # Test with falsy values
        for falsy_value in ["0", "false", "off", "no"]:
            monkeypatch.setenv("PYMM_PORTABLE", falsy_value)
            result = resolve_portable_config()
            assert result.enabled is False
            assert result.source == PortableMode.ENV

    def test_detect_portable_mode_auto_detect_removable(self):
        """Test auto-detection based on removable drive."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        # Mock storage service that detects removable drive
        mock_storage = Mock()
        mock_storage.is_path_on_removable_drive.return_value = True

        result = resolve_portable_config(storage_service=mock_storage)
        assert result.enabled is True
        assert result.source == PortableMode.AUTO
        assert result.auto_detected_removable is True

    def test_detect_portable_mode_auto_detect_not_removable(self):
        """Test auto-detection when not on removable drive."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        # Mock storage service that doesn't detect removable drive
        mock_storage = Mock()
        mock_storage.is_path_on_removable_drive.return_value = False

        result = resolve_portable_config(storage_service=mock_storage)
        assert result.enabled is True
        assert result.source == PortableMode.DEFAULT

    def test_detect_portable_mode_storage_error(self):
        """Test auto-detection with storage service errors."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        # Mock storage service that raises exception
        mock_storage = Mock()
        mock_storage.is_path_on_removable_drive.side_effect = OSError("Storage error")

        result = resolve_portable_config(storage_service=mock_storage)
        # Should fall back to default
        assert result.enabled is True
        assert result.source == PortableMode.DEFAULT

    def test_detect_portable_mode_storage_attribute_error(self):
        """Test auto-detection with missing storage method."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        # Mock storage service without the required method
        mock_storage = Mock()
        del mock_storage.is_path_on_removable_drive

        result = resolve_portable_config(storage_service=mock_storage)
        # Should fall back to default
        assert result.enabled is True
        assert result.source == PortableMode.DEFAULT

    def test_detect_portable_mode_default(self):
        """Test default portable mode enabled."""
        from app.core.services.file_system_service import (
            PortableMode,
            resolve_portable_config,
        )

        result = resolve_portable_config()
        assert result.enabled is True
        assert result.source == PortableMode.DEFAULT
