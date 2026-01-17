"""
Encryption and Compression Utilities.

Provides file encryption/decryption and compression/decompression for secure backups.
"""

from __future__ import annotations

import gzip
import hashlib
import logging
import os
from typing import TYPE_CHECKING

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


class CryptoHelper:
    """Helper class for encryption and decryption operations."""

    NONCE_SIZE = 12  # 96-bit nonce for AES-GCM
    KEY_SIZE = 32  # 256-bit key

    @staticmethod
    def derive_key(password: str, salt: bytes | None = None) -> tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.

        Args:
            password: User password
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)

        # Use PBKDF2 with SHA-256, 100k iterations
        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), salt, 100000, dklen=CryptoHelper.KEY_SIZE
        )
        return key, salt

    @staticmethod
    def encrypt_file(
        source_path: Path,
        dest_path: Path,
        password: str | None = None,
        key: bytes | None = None,
    ) -> tuple[bytes, bytes]:
        """
        Encrypt a file using AES-256-GCM.

        Args:
            source_path: Source file to encrypt
            dest_path: Destination for encrypted file
            password: Password for key derivation (if key not provided)
            key: Pre-derived encryption key (if password not provided)

        Returns:
            Tuple of (encryption_key, salt) for decryption

        Raises:
            ValueError: If neither password nor key provided
        """
        if key is None:
            if password is None:
                raise ValueError("Either password or key must be provided")
            key, salt = CryptoHelper.derive_key(password)
        else:
            salt = b""  # No salt needed if key is provided directly

        # Read source file
        with source_path.open("rb") as f:
            plaintext = f.read()

        # Generate nonce
        nonce = os.urandom(CryptoHelper.NONCE_SIZE)

        # Encrypt
        aesgcm = AESGCM(key)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Write encrypted file: salt (16 bytes) + nonce (12 bytes) + ciphertext
        with dest_path.open("wb") as f:
            if salt:
                f.write(salt)
            f.write(nonce)
            f.write(ciphertext)

        logger.debug(f"Encrypted {source_path} to {dest_path}")
        return key, salt

    @staticmethod
    def decrypt_file(
        source_path: Path,
        dest_path: Path,
        password: str | None = None,
        key: bytes | None = None,
    ) -> None:
        """
        Decrypt a file using AES-256-GCM.

        Args:
            source_path: Encrypted source file
            dest_path: Destination for decrypted file
            password: Password for key derivation (if key not provided)
            key: Pre-derived encryption key (if password not provided)

        Raises:
            ValueError: If neither password nor key provided
            Exception: If decryption fails (wrong password/corrupted file)
        """
        # Read encrypted file
        with source_path.open("rb") as f:
            data = f.read()

        # Extract components
        if key is None:
            if password is None:
                raise ValueError("Either password or key must be provided")
            # File has salt prefix
            salt = data[:16]
            nonce = data[16:28]
            ciphertext = data[28:]
            key, _ = CryptoHelper.derive_key(password, salt)
        else:
            # No salt, just nonce + ciphertext
            nonce = data[: CryptoHelper.NONCE_SIZE]
            ciphertext = data[CryptoHelper.NONCE_SIZE :]

        # Decrypt
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        # Write decrypted file
        with dest_path.open("wb") as f:
            f.write(plaintext)

        logger.debug(f"Decrypted {source_path} to {dest_path}")


class CompressionHelper:
    """Helper class for compression and decompression operations."""

    @staticmethod
    def compress_gzip(
        source_path: Path, dest_path: Path, compression_level: int = 6
    ) -> tuple[int, int]:
        """
        Compress file using gzip.

        Args:
            source_path: Source file to compress
            dest_path: Destination for compressed file
            compression_level: Compression level (1-9, default 6)

        Returns:
            Tuple of (original_size, compressed_size)
        """
        original_size = source_path.stat().st_size

        with (
            source_path.open("rb") as f_in,
            gzip.open(dest_path, "wb", compresslevel=compression_level) as f_out,
        ):
            f_out.write(f_in.read())

        compressed_size = dest_path.stat().st_size
        logger.debug(
            f"Compressed {source_path} from {original_size} to {compressed_size} bytes "
            f"({compressed_size / original_size * 100:.1f}%)"
        )

        return original_size, compressed_size

    @staticmethod
    def decompress_gzip(source_path: Path, dest_path: Path) -> tuple[int, int]:
        """
        Decompress gzip file.

        Args:
            source_path: Compressed source file
            dest_path: Destination for decompressed file

        Returns:
            Tuple of (compressed_size, decompressed_size)
        """
        compressed_size = source_path.stat().st_size

        with gzip.open(source_path, "rb") as f_in, dest_path.open("wb") as f_out:
            f_out.write(f_in.read())

        decompressed_size = dest_path.stat().st_size
        logger.debug(
            f"Decompressed {source_path} from {compressed_size} to {decompressed_size} bytes"
        )

        return compressed_size, decompressed_size

    @staticmethod
    def compress_lz4(
        source_path: Path, dest_path: Path, compression_level: int = 6
    ) -> tuple[int, int]:
        """
        Compress file using LZ4.

        Note: Requires lz4 library. Falls back to gzip if not available.

        Args:
            source_path: Source file to compress
            dest_path: Destination for compressed file
            compression_level: Compression level (1-12, default 6)

        Returns:
            Tuple of (original_size, compressed_size)
        """
        try:
            import lz4.frame

            original_size = source_path.stat().st_size

            with (
                source_path.open("rb") as f_in,
                lz4.frame.open(dest_path, mode="wb", compression_level=compression_level) as f_out,
            ):
                f_out.write(f_in.read())

            compressed_size = dest_path.stat().st_size
            logger.debug(
                f"LZ4 compressed {source_path} from {original_size} to {compressed_size} bytes"
            )

            return original_size, compressed_size

        except ImportError:
            logger.warning("LZ4 library not available, falling back to gzip")
            return CompressionHelper.compress_gzip(source_path, dest_path, compression_level)

    @staticmethod
    def decompress_lz4(source_path: Path, dest_path: Path) -> tuple[int, int]:
        """
        Decompress LZ4 file.

        Args:
            source_path: Compressed source file
            dest_path: Destination for decompressed file

        Returns:
            Tuple of (compressed_size, decompressed_size)
        """
        try:
            import lz4.frame

            compressed_size = source_path.stat().st_size

            with lz4.frame.open(source_path, mode="rb") as f_in, dest_path.open("wb") as f_out:
                f_out.write(f_in.read())

            decompressed_size = dest_path.stat().st_size
            logger.debug(
                f"LZ4 decompressed {source_path} from {compressed_size} to {decompressed_size} bytes"
            )

            return compressed_size, decompressed_size

        except ImportError:
            logger.warning("LZ4 library not available, falling back to gzip")
            return CompressionHelper.decompress_gzip(source_path, dest_path)
