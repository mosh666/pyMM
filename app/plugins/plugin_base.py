"""
Plugin base class and plugin management system.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
import asyncio


@dataclass
class PluginManifest:
    """Plugin manifest configuration."""

    name: str
    version: str
    mandatory: bool
    enabled: bool
    source_type: str  # 'url' or 'github'
    source_uri: str
    asset_pattern: Optional[str] = None
    command_path: str = ""
    command_executable: str = ""
    register_to_path: bool = False
    dependencies: list[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class PluginBase(ABC):
    """Abstract base class for plugins."""

    def __init__(self, manifest: PluginManifest, install_dir: Path):
        """
        Initialize plugin.

        Args:
            manifest: Plugin manifest configuration
            install_dir: Directory where plugin will be installed
        """
        self.manifest = manifest
        self.install_dir = install_dir
        self.plugin_dir = install_dir / manifest.name.lower()

    @abstractmethod
    async def download(self, progress_callback=None) -> bool:
        """
        Download plugin binaries.

        Args:
            progress_callback: Optional callback for progress updates (current, total)

        Returns:
            True if download successful
        """
        pass

    @abstractmethod
    async def extract(self) -> bool:
        """
        Extract downloaded plugin archive.

        Returns:
            True if extraction successful
        """
        pass

    @abstractmethod
    def validate_installation(self) -> bool:
        """
        Validate that plugin is properly installed.

        Returns:
            True if plugin is installed and functional
        """
        pass

    @abstractmethod
    def get_version(self) -> Optional[str]:
        """
        Get installed plugin version.

        Returns:
            Version string or None if not installed
        """
        pass

    def get_executable_path(self) -> Optional[Path]:
        """
        Get path to plugin executable.

        Returns:
            Path to executable or None if not found
        """
        if not self.plugin_dir.exists():
            return None

        exe_path = self.plugin_dir / self.manifest.command_path / self.manifest.command_executable
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
        self, url: str, destination: Path, progress_callback=None
    ) -> bool:
        """
        Download a file from URL.

        Args:
            url: URL to download from
            destination: Destination file path
            progress_callback: Optional callback for progress updates

        Returns:
            True if download successful
        """
        try:
            print(f"  Downloading from: {url}")
            print(f"  Destination: {destination}")
            destination.parent.mkdir(parents=True, exist_ok=True)

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    print(f"  HTTP Status: {response.status}")
                    if response.status != 200:
                        print(f"  Error: HTTP {response.status} - {response.reason}")
                        return False

                    total_size = int(response.headers.get("content-length", 0))
                    print(f"  Download size: {total_size / (1024*1024):.2f} MB")
                    downloaded = 0

                    with open(destination, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                            downloaded += len(chunk)

                            if progress_callback and total_size > 0:
                                progress_callback(downloaded, total_size)

            print(f"  Download complete: {destination.exists()}")
            return True
        except Exception as e:
            print(f"  Download exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            if destination.exists():
                destination.unlink()
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
        self.archive_path = install_dir / f"{manifest.name.lower()}.zip"

    async def download(self, progress_callback=None) -> bool:
        """Download plugin archive."""
        return await self._download_file(self.download_url, self.archive_path, progress_callback)

    async def extract(self) -> bool:
        """Extract plugin archive."""
        if not self.archive_path.exists():
            return False

        try:
            import zipfile

            with zipfile.ZipFile(self.archive_path, "r") as zip_ref:
                zip_ref.extractall(self.plugin_dir)

            # Clean up archive after extraction
            self.archive_path.unlink()
            return True
        except Exception:
            return False

    def validate_installation(self) -> bool:
        """Validate plugin installation by checking executable."""
        exe_path = self.get_executable_path()
        return exe_path is not None and exe_path.exists()

    def get_version(self) -> Optional[str]:
        """Get plugin version from manifest."""
        return self.manifest.version if self.is_installed() else None
