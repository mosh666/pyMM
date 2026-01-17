"""
Synchronization module for Storage Groups.

Handles file synchronization between Master and Backup drives with
incremental backup support, scheduled syncs, real-time watching, encryption,
compression, and bandwidth throttling.
"""

from app.core.sync.advanced_sync_options import (
    AdvancedSyncOptions,
    CompressionType,
    EncryptionType,
    SpaceSavingsReport,
)
from app.core.sync.backup_tracking import BackupTrackingDatabase
from app.core.sync.bandwidth_throttler import BandwidthThrottler
from app.core.sync.crypto_compression import CompressionHelper, CryptoHelper
from app.core.sync.file_synchronizer import (
    FileConflict,
    FileSynchronizer,
    SyncStatistics,
)
from app.core.sync.notifications import NotificationManager, get_notification_manager
from app.core.sync.realtime_sync import RealtimeSyncHandler, RealtimeSyncManager
from app.core.sync.scheduled_sync import ScheduledSyncManager, SyncSchedule

__all__ = [
    "AdvancedSyncOptions",
    "BackupTrackingDatabase",
    "BandwidthThrottler",
    "CompressionHelper",
    "CompressionType",
    "CryptoHelper",
    "EncryptionType",
    "FileConflict",
    "FileSynchronizer",
    "NotificationManager",
    "RealtimeSyncHandler",
    "RealtimeSyncManager",
    "ScheduledSyncManager",
    "SpaceSavingsReport",
    "SyncSchedule",
    "SyncStatistics",
    "get_notification_manager",
]
