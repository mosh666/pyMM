"""
Bandwidth Throttler.

Implements token bucket algorithm for bandwidth limiting during file transfers.
"""

from __future__ import annotations

import logging
from threading import Lock
import time

logger = logging.getLogger(__name__)


class BandwidthThrottler:
    """Token bucket bandwidth throttler."""

    def __init__(self, rate_limit_mbps: float):
        """
        Initialize bandwidth throttler.

        Args:
            rate_limit_mbps: Maximum transfer rate in megabytes per second
        """
        self.rate_limit_bytes_per_sec: float = (
            rate_limit_mbps * 1024 * 1024
        )  # Convert MB/s to bytes/s
        self.bucket_capacity: float = (
            self.rate_limit_bytes_per_sec
        )  # Burst capacity = 1 second of data
        self.tokens: float = self.bucket_capacity  # Start with full bucket
        self.last_refill_time = time.time()
        self.lock = Lock()

    def _refill_tokens(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill_time

        # Add tokens based on elapsed time
        tokens_to_add = elapsed * self.rate_limit_bytes_per_sec
        self.tokens = min(self.bucket_capacity, self.tokens + tokens_to_add)
        self.last_refill_time = now

    def consume(self, bytes_count: int) -> None:
        """
        Consume tokens for bytes transferred, blocking if necessary.

        Args:
            bytes_count: Number of bytes to consume
        """
        with self.lock:
            bytes_count_float: float = float(bytes_count)
            while bytes_count_float > 0:
                self._refill_tokens()

                if self.tokens >= bytes_count_float:
                    # Enough tokens available
                    self.tokens -= bytes_count_float
                    bytes_count_float = 0.0
                else:
                    # Not enough tokens - consume what we have and wait
                    bytes_count_float -= self.tokens
                    self.tokens = 0.0

                    # Calculate wait time for next refill
                    wait_time: float = float(bytes_count_float) / self.rate_limit_bytes_per_sec
                    time.sleep(min(wait_time, 0.1))  # Sleep in small chunks

    def get_current_rate(self) -> float:
        """
        Get current available bandwidth rate in MB/s.

        Returns:
            Current rate in megabytes per second
        """
        with self.lock:
            self._refill_tokens()
            return (self.tokens / self.bucket_capacity) * (
                self.rate_limit_bytes_per_sec / 1024 / 1024
            )
