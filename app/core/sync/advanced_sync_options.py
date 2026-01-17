"""
Advanced Sync Options.

Configuration classes for bandwidth throttling, encryption, compression,
and parallel copying features.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class CompressionType(str, Enum):
    """Compression algorithm types."""

    NONE = "none"
    GZIP = "gzip"
    LZ4 = "lz4"


class EncryptionType(str, Enum):
    """Encryption algorithm types."""

    NONE = "none"
    AES_256_GCM = "aes-256-gcm"


@dataclass
class AdvancedSyncOptions:
    """Advanced synchronization options."""

    # Bandwidth throttling
    enable_bandwidth_limit: bool = False
    bandwidth_limit_mbps: float = 10.0  # Megabytes per second

    # Encryption
    enable_encryption: bool = False
    encryption_type: EncryptionType = EncryptionType.AES_256_GCM
    encryption_password: str | None = None
    encryption_key_file: Path | None = None

    # Compression
    enable_compression: bool = False
    compression_type: CompressionType = CompressionType.GZIP
    compression_level: int = 6  # 1-9 for gzip, 1-12 for lz4

    # Parallel copying
    enable_parallel_copy: bool = False
    max_parallel_files: int = 4

    # Reporting
    calculate_space_savings: bool = True

    def to_dict(self) -> dict[str, object]:
        """Convert to dictionary."""
        return {
            "enable_bandwidth_limit": self.enable_bandwidth_limit,
            "bandwidth_limit_mbps": self.bandwidth_limit_mbps,
            "enable_encryption": self.enable_encryption,
            "encryption_type": self.encryption_type.value,
            "encryption_password": self.encryption_password,
            "encryption_key_file": str(self.encryption_key_file)
            if self.encryption_key_file
            else None,
            "enable_compression": self.enable_compression,
            "compression_type": self.compression_type.value,
            "compression_level": self.compression_level,
            "enable_parallel_copy": self.enable_parallel_copy,
            "max_parallel_files": self.max_parallel_files,
            "calculate_space_savings": self.calculate_space_savings,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AdvancedSyncOptions:
        """Create from dictionary."""
        return cls(
            enable_bandwidth_limit=bool(data.get("enable_bandwidth_limit", False)),
            bandwidth_limit_mbps=float(str(data.get("bandwidth_limit_mbps", 10.0))),
            enable_encryption=bool(data.get("enable_encryption", False)),
            encryption_type=EncryptionType(str(data.get("encryption_type", "none"))),
            encryption_password=str(data.get("encryption_password"))
            if data.get("encryption_password")
            else None,
            encryption_key_file=Path(str(data["encryption_key_file"]))
            if data.get("encryption_key_file")
            else None,
            enable_compression=bool(data.get("enable_compression", False)),
            compression_type=CompressionType(str(data.get("compression_type", "none"))),
            compression_level=int(str(data.get("compression_level", 6))),
            enable_parallel_copy=bool(data.get("enable_parallel_copy", False)),
            max_parallel_files=int(str(data.get("max_parallel_files", 4))),
            calculate_space_savings=bool(data.get("calculate_space_savings", True)),
        )


@dataclass
class SpaceSavingsReport:
    """Report on space savings from compression/deduplication."""

    original_size: int  # Total bytes before compression
    compressed_size: int  # Total bytes after compression
    files_processed: int
    compression_ratio: float  # compressed_size / original_size
    space_saved: int  # original_size - compressed_size
    space_saved_percent: float  # (space_saved / original_size) * 100

    @classmethod
    def calculate(
        cls, original_size: int, compressed_size: int, files_processed: int
    ) -> SpaceSavingsReport:
        """Calculate space savings report."""
        space_saved = original_size - compressed_size
        compression_ratio = compressed_size / original_size if original_size > 0 else 0.0
        space_saved_percent = (space_saved / original_size * 100) if original_size > 0 else 0.0

        return cls(
            original_size=original_size,
            compressed_size=compressed_size,
            files_processed=files_processed,
            compression_ratio=compression_ratio,
            space_saved=space_saved,
            space_saved_percent=space_saved_percent,
        )
