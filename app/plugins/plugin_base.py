"""
Plugin base class and plugin management system.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
import shutil
import subprocess
from typing import TYPE_CHECKING

import aiohttp

from app.core.platform import Platform, current_platform

if TYPE_CHECKING:
    from collections.abc import Callable

if TYPE_CHECKING:
    from app.ui.dialogs.tool_version_dialog import VersionChoice


class ExecutableSource(str, Enum):
    """Source of plugin executable."""

    SYSTEM = "system"  # System-installed tool via PATH
    PORTABLE = "portable"  # Portable binary managed by pyMM
    NONE = "none"  # Not found/available


@dataclass
class PlatformManifest:
    """Platform-specific plugin configuration."""

    source_type: str | None = None
    source_uri: str | None = None
    asset_pattern: str | None = None
    checksum_sha256: str | None = None
    file_size: int | None = None
    command_path: str = ""
    command_executable: str = ""
    system_package: str | None = None
    version_constraint: str | None = None


@dataclass
class PluginManifest:
    """Plugin manifest configuration (v2 schema)."""

    name: str
    version: str
    mandatory: bool
    enabled: bool
    prefer_system: bool = True
    register_to_path: bool = False
    dependencies: list[str] = field(default_factory=list)

    # Platform-specific configurations
    windows_config: PlatformManifest | None = None
    linux_config: PlatformManifest | None = None
    macos_config: PlatformManifest | None = None

    def get_current_platform_config(self) -> PlatformManifest | None:
        """Get configuration for current platform."""
        match current_platform():
            case Platform.WINDOWS:
                return self.windows_config
            case Platform.LINUX:
                return self.linux_config
            case Platform.MACOS:
                return self.macos_config


class PluginBase(ABC):
    """Abstract base class for plugins."""

    def __init__(self, manifest: PluginManifest, install_dir: Path):
        """
        Initialize plugin.

        Args:
            manifest: Plugin manifest configuration
            install_dir: Directory where plugin will be installed
        """
        self.logger = logging.getLogger(__name__)
        self.manifest = manifest
        self.install_dir = install_dir
        self.plugin_dir = install_dir / manifest.name.lower()

    @abstractmethod
    async def download(self, progress_callback: Callable[[int, int], None] | None = None) -> bool:
        """
        Download plugin binaries.

        Args:
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            True if download successful
        """

    @abstractmethod
    async def extract(self) -> bool:
        """
        Extract downloaded plugin archive.

        Returns:
            True if extraction successful
        """

    @abstractmethod
    def validate_installation(self) -> bool:
        """
        Validate that plugin is properly installed.

        Returns:
            True if plugin is installed and functional
        """

    @abstractmethod
    def get_version(self) -> str | None:
        """
        Get installed plugin version.

        Returns:
            Version string or None if not installed
        """

    def get_executable_path(self) -> Path | None:
        """
        Get path to plugin executable (backwards compatible wrapper).

        Returns:
            Path to executable or None if not found
        """
        exe_info = self.get_executable_info()
        return exe_info[0] if exe_info else None

    def get_executable_info(self) -> tuple[Path | None, ExecutableSource, str | None]:
        """
        Get plugin executable with hybrid system/portable resolution.

        Returns:
            Tuple of (path, source, version) or (None, ExecutableSource.NONE, None)
        """

        platform_config = self.manifest.get_current_platform_config()

        # Return None if no platform configuration exists
        if not platform_config:
            return (None, ExecutableSource.NONE, None)

        prefer_system = self.manifest.prefer_system

        # Try system tool first if preferred
        if prefer_system and platform_config.system_package:
            system_info = self._try_system_tool(platform_config)
            if system_info:
                return system_info

        # Try portable executable
        portable_path = self._get_portable_executable_path(platform_config)
        if portable_path and portable_path.exists():
            # TODO: Get version from portable binary
            return (portable_path, ExecutableSource.PORTABLE, None)

        # Fallback to system tool even if not preferred
        if not prefer_system and platform_config.system_package:
            system_info = self._try_system_tool(platform_config)
            if system_info:
                return system_info

        return (None, ExecutableSource.NONE, None)

    def _try_system_tool(
        self, platform_config: PlatformManifest
    ) -> tuple[Path, ExecutableSource, str] | None:
        """
        Try to find and validate system-installed tool.

        Args:
            platform_config: Platform-specific configuration

        Returns:
            Tuple of (path, source, version) or None if not found/invalid
        """
        from .system_tool_detector import SystemToolDetector, ToolDetectionStatus

        detector = SystemToolDetector()
        tool_info = detector.find_system_tool(
            platform_config.system_package or self.manifest.name, platform_config.version_constraint
        )

        if not tool_info:
            return None

        if tool_info.status == ToolDetectionStatus.FOUND_VALID and tool_info.path:
            return (tool_info.path, ExecutableSource.SYSTEM, tool_info.version or "")

        if tool_info.status == ToolDetectionStatus.FOUND_INVALID:
            # Handle version mismatch - ask user
            choice = self._handle_version_mismatch(
                str(tool_info.path),
                tool_info.version or "unknown",
                platform_config.version_constraint or "any",
            )

            from app.ui.dialogs.tool_version_dialog import VersionChoice

            if choice == VersionChoice.USE_ANYWAY and tool_info.path:
                return (tool_info.path, ExecutableSource.SYSTEM, tool_info.version or "")
            # INSTALL_PORTABLE or CANCEL - return None to try portable

        return None

    def _handle_version_mismatch(
        self, _tool_path: str, found_version: str, required_version: str
    ) -> VersionChoice:
        """
        Handle system tool version mismatch by showing dialog.

        Args:
            tool_path: Path to found tool
            found_version: Version that was found
            required_version: Version constraint required

        Returns:
            User's choice
        """
        from app.ui.dialogs.tool_version_dialog import ToolVersionDialog

        return ToolVersionDialog.ask(
            self.manifest.name,
            found_version,
            required_version,
            None,  # parent widget
        )

    def _get_portable_executable_path(self, platform_config: PlatformManifest) -> Path | None:
        """
        Get path to portable executable.

        Args:
            platform_config: Platform-specific configuration

        Returns:
            Path to portable executable or None
        """
        if not self.plugin_dir.exists():
            return None

        command_path = platform_config.command_path
        command_executable = platform_config.command_executable

        exe_path = self.plugin_dir / command_path / command_executable
        return exe_path if exe_path.exists() else None

    def is_installed(self) -> bool:
        """
        Check if plugin is installed.

        Returns:
            True if plugin directory exists and validates
        """
        return self.plugin_dir.exists() and self.validate_installation()

    async def uninstall(self) -> bool:
        """
        Uninstall plugin by removing its directory.

        Returns:
            True if uninstallation successful
        """
        if not self.plugin_dir.exists():
            return True

        try:
            import shutil

            shutil.rmtree(self.plugin_dir)
            return True
        except Exception:
            return False

    async def _download_file(
        self,
        url: str,
        destination: Path,
        progress_callback: Callable[[int, int], None] | None = None,
        max_retries: int = 3,
    ) -> bool:
        """
        Download a file from URL with retry logic.

        Args:
            url: URL to download from
            destination: Destination file path
            progress_callback: Optional callback for progress updates
            max_retries: Maximum number of retry attempts (default 3)

        Returns:
            True if download successful
        """
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2**attempt  # Exponential backoff: 2, 4, 8 seconds
                    self.logger.info(
                        f"  Retry attempt {attempt + 1}/{max_retries} after {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)

                self.logger.debug(f"  Downloading from: {url}")
                self.logger.debug(f"  Destination: {destination}")
                destination.parent.mkdir(parents=True, exist_ok=True)

                async with (
                    aiohttp.ClientSession() as session,
                    session.get(url, timeout=aiohttp.ClientTimeout(total=300)) as response,
                ):
                    self.logger.info(f"  HTTP Status: {response.status}")
                    if response.status != 200:
                        self.logger.error(f"  Error: HTTP {response.status} - {response.reason}")
                        if attempt < max_retries - 1:
                            continue
                        return False

                    total_size = int(response.headers.get("content-length", 0))
                    self.logger.info(f"  Download size: {total_size / (1024 * 1024):.2f} MB")
                    downloaded = 0

                    with open(destination, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:
                                progress_callback(downloaded, total_size)

                self.logger.info(f"  Download complete: {destination.exists()}")

                return True
            except (TimeoutError, aiohttp.ClientError) as e:
                self.logger.warning(
                    f"  Download error (attempt {attempt + 1}/{max_retries}): {type(e).__name__}: {e}"
                )
                if destination.exists():
                    destination.unlink()
                if attempt < max_retries - 1:
                    continue
                return False
            except Exception:
                self.logger.exception("  Download exception")
                import traceback

                traceback.print_exc()
                if destination.exists():
                    destination.unlink()
                return False

        return False

    async def _verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
        """Verify file SHA256 checksum.

        Args:
            file_path: Path to file to verify
            expected_sha256: Expected SHA256 hash (case-insensitive)

        Returns:
            True if checksum matches
        """
        try:
            import hashlib

            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256_hash.update(chunk)

            calculated = sha256_hash.hexdigest().upper()
            expected = expected_sha256.upper()

            if calculated == expected:
                return True
            self.logger.error(f"  Expected: {expected}")
            self.logger.error(f"  Got:      {calculated}")
            return False
        except Exception:
            self.logger.exception("  Checksum verification error")
            return False


class SimplePluginImplementation(PluginBase):
    """
    Simple plugin implementation for downloading and extracting archives.
    """

    def __init__(self, manifest: PluginManifest, install_dir: Path, download_url: str):
        """
        Initialize simple plugin.

        Args:
            manifest: Plugin manifest
            install_dir: Installation directory
            download_url: Direct download URL for plugin archive
        """
        super().__init__(manifest, install_dir)
        self.download_url = download_url

        # Determine archive extension from URL
        url_lower = download_url.lower()
        if ".7z.exe" in url_lower:
            ext = "7z.exe"
        elif url_lower.endswith(".7z"):
            ext = "7z"
        elif url_lower.endswith(".zip"):
            ext = "zip"
        else:
            ext = "zip"  # Default to zip

        self.archive_path = install_dir / f"{manifest.name.lower()}.{ext}"

    async def download(self, progress_callback: Callable[[int, int], None] | None = None) -> bool:
        """Download plugin archive."""
        # Get platform-specific config for checksum and size
        platform_config = self.manifest.get_current_platform_config()
        expected_sha256 = platform_config.checksum_sha256 if platform_config else None

        success = await self._download_file(self.download_url, self.archive_path, progress_callback)

        # Verify checksum if available
        if (
            success
            and expected_sha256
            and not await self._verify_checksum(self.archive_path, expected_sha256)
        ):
            self.logger.error("Checksum verification failed")
            return False

        return success

    async def extract(self) -> bool:
        """Extract plugin archive with support for ZIP, 7z, and self-extracting exe."""
        if not self.archive_path.exists():
            return False

        try:
            # Create temporary extraction directory
            temp_extract_dir = self.plugin_dir.parent / f"{self.plugin_dir.name}_temp"
            temp_extract_dir.mkdir(parents=True, exist_ok=True)

            # Extract based on archive type
            if self.archive_path.suffix == ".zip":
                success = await self._extract_zip(temp_extract_dir)
            elif str(self.archive_path).endswith(".7z.exe"):
                success = await self._extract_7z_exe(temp_extract_dir)
            elif self.archive_path.suffix == ".7z":
                success = await self._extract_7z(temp_extract_dir)
            else:
                return False

            if not success:
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                return False

            # Flatten nested structure if needed
            self._flatten_extraction(temp_extract_dir)

            # Handle special file renames (e.g., ExifTool)
            self._handle_special_cases(temp_extract_dir)

            # Move to final location
            if self.plugin_dir.exists():
                shutil.rmtree(self.plugin_dir)
            temp_extract_dir.rename(self.plugin_dir)

            # Clean up archive
            self.archive_path.unlink()
            return True
        except Exception:
            self.logger.exception("  Extraction error")
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
            return False

    async def _extract_zip(self, extract_dir: Path) -> bool:
        """Extract ZIP archive."""
        try:
            import zipfile

            with zipfile.ZipFile(self.archive_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)
            return True
        except Exception:
            return False

    async def _extract_7z(self, extract_dir: Path) -> bool:
        """Extract 7z archive using py7zr."""
        try:
            import py7zr

            with py7zr.SevenZipFile(self.archive_path, mode="r") as archive:
                archive.extractall(path=extract_dir)
            return True
        except ImportError:
            self.logger.debug("  py7zr not installed, attempting 7z command-line")
            return await self._extract_7z_cli(extract_dir)
        except Exception:
            return False

    async def _extract_7z_cli(self, extract_dir: Path) -> bool:
        """Extract 7z archive using 7z command-line tool."""
        try:
            result = subprocess.run(
                ["7z", "x", str(self.archive_path), f"-o{extract_dir}", "-y"],
                check=False,
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    async def _extract_7z_exe(self, extract_dir: Path) -> bool:
        """Extract self-extracting 7z .exe archive."""
        try:
            # Self-extracting 7z archives can be extracted with -o flag
            result = subprocess.run(
                [str(self.archive_path), "-o" + str(extract_dir), "-y"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.archive_path.parent),
            )
            return result.returncode == 0
        except Exception:
            # If that fails, try with py7zr (7z.exe files are often just 7z archives)
            return await self._extract_7z(extract_dir)

    def _flatten_extraction(self, extract_dir: Path) -> None:
        """Flatten nested extraction structure if archive contains a single top-level directory."""
        try:
            items = list(extract_dir.iterdir())

            # If extraction resulted in a single directory, flatten it
            if len(items) == 1 and items[0].is_dir():
                nested_dir = items[0]

                # Move all contents up one level
                for item in nested_dir.iterdir():
                    dest = extract_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))

                # Remove the now-empty nested directory
                nested_dir.rmdir()
        except Exception as e:
            self.logger.warning(f"  Could not flatten structure: {e}")

    def _handle_special_cases(self, extract_dir: Path) -> None:
        """Handle plugin-specific post-extraction tasks."""
        try:
            # ExifTool: Rename exiftool(-k).exe to exiftool.exe
            if self.manifest.name == "ExifTool":
                old_name = extract_dir / "exiftool(-k).exe"
                new_name = extract_dir / "exiftool.exe"
                if old_name.exists() and not new_name.exists():
                    old_name.rename(new_name)
        except Exception as e:
            self.logger.warning(f"  Special case handling failed: {e}")

    def validate_installation(self) -> bool:
        """Validate plugin installation by checking executable."""
        exe_path = self.get_executable_path()
        return exe_path is not None and exe_path.exists()

    def get_version(self) -> str | None:
        """Get plugin version from manifest."""
        return self.manifest.version if self.is_installed() else None
