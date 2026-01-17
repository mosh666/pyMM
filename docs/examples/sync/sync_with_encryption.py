"""Perform sync with encryption and compression enabled.

This example demonstrates secure backup with encryption support.
"""

from pathlib import Path
import sys

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parents[3]))

from app.core.services.storage_group_service import StorageGroupService
from app.core.sync.crypto_compression import CryptoCompression
from app.core.sync.file_synchronizer import FileSynchronizer


def main() -> None:
    """Perform encrypted sync for a storage group."""
    if len(sys.argv) < 2:
        print("Usage: python sync_with_encryption.py <storage_group_id>")
        sys.exit(1)

    group_id = sys.argv[1]
    service = StorageGroupService()
    group = service.get_group(group_id)

    if not group:
        print(f"Storage group not found: {group_id}")
        sys.exit(1)

    print(f"Starting encrypted sync for: {group.name}")
    print("Encryption: Enabled")
    print("Compression: Enabled\n")

    # Initialize with encryption
    crypto = CryptoCompression(
        enable_encryption=True,
        enable_compression=True,
        encryption_key="your-secure-key-here",  # Use secure key management!
    )

    synchronizer = FileSynchronizer(
        group=group,
        crypto=crypto,
    )

    # Perform encrypted sync
    result = synchronizer.sync()

    print("\nEncrypted sync completed:")
    print(f"  Files encrypted: {result.get('files_encrypted', 0)}")
    print(f"  Space saved: {result.get('compression_ratio', 0):.1%}")
    print(f"  Total size: {result.get('total_size_bytes', 0) / (1024**2):.2f} MB")


if __name__ == "__main__":
    main()
