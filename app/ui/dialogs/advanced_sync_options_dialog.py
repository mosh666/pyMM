"""
Advanced Sync Options Dialog.

UI for configuring bandwidth throttling, encryption, compression,
and parallel copying options.
"""

from __future__ import annotations

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.core.sync.advanced_sync_options import (
    AdvancedSyncOptions,
    CompressionType,
    EncryptionType,
)

logger = logging.getLogger(__name__)


class AdvancedSyncOptionsDialog(QDialog):
    """Dialog for configuring advanced sync options."""

    def __init__(
        self, options: AdvancedSyncOptions | None = None, parent: object | None = None
    ) -> None:
        """
        Initialize dialog.

        Args:
            options: Existing options to edit (creates new if None)
            parent: Parent widget
        """
        from PySide6.QtWidgets import QWidget

        parent_widget: QWidget | None = None
        if isinstance(parent, QWidget):
            parent_widget = parent

        super().__init__(parent_widget)
        self.options = options or AdvancedSyncOptions()

        self.setWindowTitle("Advanced Sync Options")
        self.resize(550, 600)

        self._create_ui()
        self._load_options()

    def _create_ui(self) -> None:
        """Create the dialog UI."""
        layout = QVBoxLayout(self)

        # Bandwidth throttling
        bandwidth_group = QGroupBox("Bandwidth Throttling")
        bandwidth_layout = QFormLayout(bandwidth_group)

        self.bandwidth_enabled = QCheckBox("Enable bandwidth limiting")
        bandwidth_layout.addRow(self.bandwidth_enabled)

        self.bandwidth_limit = QDoubleSpinBox()
        self.bandwidth_limit.setRange(0.1, 1000.0)
        self.bandwidth_limit.setValue(10.0)
        self.bandwidth_limit.setSuffix(" MB/s")
        self.bandwidth_limit.setDecimals(1)
        self.bandwidth_limit.setEnabled(False)
        bandwidth_layout.addRow("Transfer rate limit:", self.bandwidth_limit)

        self.bandwidth_enabled.toggled.connect(self.bandwidth_limit.setEnabled)

        layout.addWidget(bandwidth_group)

        # Encryption
        encryption_group = QGroupBox("Encryption")
        encryption_layout = QFormLayout(encryption_group)

        self.encryption_enabled = QCheckBox("Enable encryption for backup files")
        encryption_layout.addRow(self.encryption_enabled)

        self.encryption_type = QComboBox()
        self.encryption_type.addItem("AES-256-GCM", EncryptionType.AES_256_GCM)
        self.encryption_type.setEnabled(False)
        encryption_layout.addRow("Algorithm:", self.encryption_type)

        self.encryption_password = QLineEdit()
        self.encryption_password.setEchoMode(QLineEdit.Password)
        self.encryption_password.setPlaceholderText("Enter encryption password")
        self.encryption_password.setEnabled(False)
        encryption_layout.addRow("Password:", self.encryption_password)

        # Key file
        key_file_layout = QHBoxLayout()
        self.encryption_key_file = QLineEdit()
        self.encryption_key_file.setPlaceholderText("Optional: Use key file instead of password")
        self.encryption_key_file.setEnabled(False)
        key_file_layout.addWidget(self.encryption_key_file)

        self.browse_key_button = QPushButton("Browse...")
        self.browse_key_button.clicked.connect(self._browse_key_file)
        self.browse_key_button.setEnabled(False)
        key_file_layout.addWidget(self.browse_key_button)

        encryption_layout.addRow("Key file:", key_file_layout)

        # Warning label
        warning_label = QLabel(
            "⚠️ Warning: Encrypted backups cannot be restored without the password/key. "
            "Store credentials securely!"
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet("color: #D32F2F; font-weight: bold;")
        encryption_layout.addRow(warning_label)

        self.encryption_enabled.toggled.connect(self._on_encryption_toggled)

        layout.addWidget(encryption_group)

        # Compression
        compression_group = QGroupBox("Compression")
        compression_layout = QFormLayout(compression_group)

        self.compression_enabled = QCheckBox("Enable compression")
        compression_layout.addRow(self.compression_enabled)

        self.compression_type = QComboBox()
        self.compression_type.addItem("GZIP (Standard)", CompressionType.GZIP)
        self.compression_type.addItem("LZ4 (Fast)", CompressionType.LZ4)
        self.compression_type.setEnabled(False)
        compression_layout.addRow("Algorithm:", self.compression_type)

        self.compression_level = QSpinBox()
        self.compression_level.setRange(1, 9)
        self.compression_level.setValue(6)
        self.compression_level.setEnabled(False)
        compression_layout.addRow("Level (1=fast, 9=best):", self.compression_level)

        # Info label
        info_label = QLabel(
            "Higher levels provide better compression but are slower. "
            "Level 6 is recommended for general use."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        compression_layout.addRow(info_label)

        self.compression_enabled.toggled.connect(self._on_compression_toggled)

        layout.addWidget(compression_group)

        # Parallel copying
        parallel_group = QGroupBox("Parallel Copying")
        parallel_layout = QFormLayout(parallel_group)

        self.parallel_enabled = QCheckBox("Enable parallel file transfers")
        parallel_layout.addRow(self.parallel_enabled)

        self.parallel_max_files = QSpinBox()
        self.parallel_max_files.setRange(2, 16)
        self.parallel_max_files.setValue(4)
        self.parallel_max_files.setEnabled(False)
        parallel_layout.addRow("Max concurrent files:", self.parallel_max_files)

        # Info label
        parallel_info = QLabel(
            "Process multiple files simultaneously. "
            "Best for small files on SSDs. May reduce performance on HDDs."
        )
        parallel_info.setWordWrap(True)
        parallel_info.setStyleSheet("color: gray; font-size: 9pt;")
        parallel_layout.addRow(parallel_info)

        self.parallel_enabled.toggled.connect(self.parallel_max_files.setEnabled)

        layout.addWidget(parallel_group)

        # Reporting
        reporting_group = QGroupBox("Reporting")
        reporting_layout = QFormLayout(reporting_group)

        self.space_savings_enabled = QCheckBox("Calculate and report space savings")
        self.space_savings_enabled.setChecked(True)
        reporting_layout.addRow(self.space_savings_enabled)

        layout.addWidget(reporting_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _on_encryption_toggled(self, enabled: bool) -> None:
        """Handle encryption checkbox toggle."""
        self.encryption_type.setEnabled(enabled)
        self.encryption_password.setEnabled(enabled)
        self.encryption_key_file.setEnabled(enabled)
        self.browse_key_button.setEnabled(enabled)

    def _on_compression_toggled(self, enabled: bool) -> None:
        """Handle compression checkbox toggle."""
        self.compression_type.setEnabled(enabled)
        self.compression_level.setEnabled(enabled)

    def _browse_key_file(self) -> None:
        """Browse for encryption key file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Encryption Key File",
            "",
            "All Files (*.*)",
        )

        if file_path:
            self.encryption_key_file.setText(file_path)

    def _load_options(self) -> None:
        """Load options into UI."""
        # Bandwidth
        self.bandwidth_enabled.setChecked(self.options.enable_bandwidth_limit)
        self.bandwidth_limit.setValue(self.options.bandwidth_limit_mbps)

        # Encryption
        self.encryption_enabled.setChecked(self.options.enable_encryption)
        idx = self.encryption_type.findData(self.options.encryption_type)
        if idx >= 0:
            self.encryption_type.setCurrentIndex(idx)
        if self.options.encryption_password:
            self.encryption_password.setText(self.options.encryption_password)
        if self.options.encryption_key_file:
            self.encryption_key_file.setText(str(self.options.encryption_key_file))

        # Compression
        self.compression_enabled.setChecked(self.options.enable_compression)
        idx = self.compression_type.findData(self.options.compression_type)
        if idx >= 0:
            self.compression_type.setCurrentIndex(idx)
        self.compression_level.setValue(self.options.compression_level)

        # Parallel
        self.parallel_enabled.setChecked(self.options.enable_parallel_copy)
        self.parallel_max_files.setValue(self.options.max_parallel_files)

        # Reporting
        self.space_savings_enabled.setChecked(self.options.calculate_space_savings)

    def _accept(self) -> None:
        """Validate and accept dialog."""
        # Validate encryption settings
        if self.encryption_enabled.isChecked():
            has_password = bool(self.encryption_password.text().strip())
            has_key_file = bool(self.encryption_key_file.text().strip())

            if not has_password and not has_key_file:
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    "Encryption is enabled but no password or key file is specified.\n\n"
                    "Please provide either a password or key file.",
                )
                return

        # Save options
        self.options.enable_bandwidth_limit = self.bandwidth_enabled.isChecked()
        self.options.bandwidth_limit_mbps = self.bandwidth_limit.value()

        self.options.enable_encryption = self.encryption_enabled.isChecked()
        self.options.encryption_type = self.encryption_type.currentData()
        self.options.encryption_password = self.encryption_password.text().strip() or None
        key_file_text = self.encryption_key_file.text().strip()
        self.options.encryption_key_file = Path(key_file_text) if key_file_text else None

        self.options.enable_compression = self.compression_enabled.isChecked()
        self.options.compression_type = self.compression_type.currentData()
        self.options.compression_level = self.compression_level.value()

        self.options.enable_parallel_copy = self.parallel_enabled.isChecked()
        self.options.max_parallel_files = self.parallel_max_files.value()

        self.options.calculate_space_savings = self.space_savings_enabled.isChecked()

        self.accept()

    def get_options(self) -> AdvancedSyncOptions:
        """Get the configured options."""
        return self.options
