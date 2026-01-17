"""
Sync Schedule Configuration Dialog.

Provides UI for configuring automatic scheduled syncs for projects.
"""

from __future__ import annotations

import logging

from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

logger = logging.getLogger(__name__)


class SyncScheduleDialog(QDialog):
    """Dialog for configuring sync schedules."""

    def __init__(
        self,
        current_schedule: dict[str, object] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        """
        Initialize sync schedule dialog.

        Args:
            current_schedule: Existing schedule configuration or None
            parent: Parent widget
        """
        super().__init__(parent)
        self.current_schedule = current_schedule or {}

        self.setWindowTitle("Configure Sync Schedule")
        self.setMinimumWidth(500)
        self._init_ui()
        self._load_schedule()

    def _init_ui(self) -> None:
        """Initialize the user interface."""
        layout = QVBoxLayout(self)

        # Enable/Disable checkbox
        self.enabled_checkbox = QCheckBox("Enable Scheduled Sync")
        self.enabled_checkbox.setStyleSheet("font-weight: bold; font-size: 13px;")
        self.enabled_checkbox.toggled.connect(self._on_enabled_toggled)
        layout.addWidget(self.enabled_checkbox)

        # Schedule type group
        schedule_group = QGroupBox("Schedule Type")
        schedule_layout = QVBoxLayout(schedule_group)

        self.schedule_type_buttons = QButtonGroup()

        # Interval-based radio
        self.interval_radio = QRadioButton("Interval-based (every X minutes)")
        self.schedule_type_buttons.addButton(self.interval_radio, 0)
        schedule_layout.addWidget(self.interval_radio)

        # Interval configuration
        interval_config = QWidget()
        interval_layout = QHBoxLayout(interval_config)
        interval_layout.setContentsMargins(30, 0, 0, 0)

        interval_layout.addWidget(QLabel("Sync every"))

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setMinimum(5)
        self.interval_spinbox.setMaximum(1440)  # 24 hours
        self.interval_spinbox.setValue(60)
        self.interval_spinbox.setSuffix(" minutes")
        interval_layout.addWidget(self.interval_spinbox)

        interval_layout.addStretch()
        schedule_layout.addWidget(interval_config)

        # Preset radio
        self.preset_radio = QRadioButton("Preset schedule")
        self.schedule_type_buttons.addButton(self.preset_radio, 1)
        schedule_layout.addWidget(self.preset_radio)

        # Preset configuration
        preset_config = QWidget()
        preset_layout = QHBoxLayout(preset_config)
        preset_layout.setContentsMargins(30, 0, 0, 0)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Hourly", "0 * * * *")
        self.preset_combo.addItem("Daily at 2 AM", "0 2 * * *")
        self.preset_combo.addItem("Daily at Midnight", "0 0 * * *")
        self.preset_combo.addItem("Weekly on Monday at 3 PM", "0 15 * * 1")
        self.preset_combo.addItem("Weekly on Sunday at Midnight", "0 0 * * 0")
        preset_layout.addWidget(self.preset_combo)

        preset_layout.addStretch()
        schedule_layout.addWidget(preset_config)

        # Custom cron radio
        self.custom_radio = QRadioButton("Custom cron expression")
        self.schedule_type_buttons.addButton(self.custom_radio, 2)
        schedule_layout.addWidget(self.custom_radio)

        # Custom cron configuration
        custom_config = QWidget()
        custom_layout = QFormLayout(custom_config)
        custom_layout.setContentsMargins(30, 0, 0, 0)

        self.cron_edit = QLineEdit()
        self.cron_edit.setPlaceholderText("0 2 * * *")
        custom_layout.addRow("Cron:", self.cron_edit)

        cron_help = QLabel(
            "Format: minute hour day month day_of_week\nExample: '0 2 * * *' = Every day at 2 AM"
        )
        cron_help.setStyleSheet("color: gray; font-size: 11px;")
        cron_help.setWordWrap(True)
        custom_layout.addRow("", cron_help)

        schedule_layout.addWidget(custom_config)

        # Connect radio buttons to enable/disable widgets
        self.interval_radio.toggled.connect(lambda checked: interval_config.setEnabled(checked))
        self.preset_radio.toggled.connect(lambda checked: preset_config.setEnabled(checked))
        self.custom_radio.toggled.connect(lambda checked: custom_config.setEnabled(checked))

        # Default to interval
        self.interval_radio.setChecked(True)

        layout.addWidget(schedule_group)

        # Information label
        info_label = QLabel(
            "ℹ Scheduled syncs run in the background. You will receive notifications "
            "upon completion or failure."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 10px; background-color: #E3F2FD;")
        layout.addWidget(info_label)

        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self._on_ok_clicked)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def _load_schedule(self) -> None:
        """Load current schedule into UI."""
        if not self.current_schedule:
            return

        enabled: bool = bool(self.current_schedule.get("enabled", False))
        self.enabled_checkbox.setChecked(enabled)

        schedule_type_val = self.current_schedule.get("type", "interval")
        schedule_type: str = str(schedule_type_val) if schedule_type_val else "interval"

        if schedule_type == "interval":
            self.interval_radio.setChecked(True)
            interval_val = self.current_schedule.get("interval_minutes", 60)
            interval: int = int(interval_val) if isinstance(interval_val, (int, str)) else 60
            self.interval_spinbox.setValue(interval)

        elif schedule_type == "cron":
            cron_expr_val = self.current_schedule.get("cron_expression", "0 2 * * *")
            cron_expr: str = str(cron_expr_val) if cron_expr_val else "0 2 * * *"

            # Try to match with presets
            matched = False
            for i in range(self.preset_combo.count()):
                if self.preset_combo.itemData(i) == cron_expr:
                    self.preset_radio.setChecked(True)
                    self.preset_combo.setCurrentIndex(i)
                    matched = True
                    break

            if not matched:
                self.custom_radio.setChecked(True)
                self.cron_edit.setText(cron_expr)

    def _on_enabled_toggled(self, checked: bool) -> None:
        """Handle enabled checkbox toggle."""
        # Enable/disable all schedule configuration widgets
        for widget in self.findChildren(QGroupBox):
            widget.setEnabled(checked)

    def _on_ok_clicked(self) -> None:
        """Validate and accept dialog."""
        if not self.enabled_checkbox.isChecked():
            # Schedule disabled - just close
            self.accept()
            return

        # Validate configuration
        if self.interval_radio.isChecked():
            # Interval schedule - always valid
            pass

        elif self.preset_radio.isChecked():
            # Preset - always valid
            pass

        elif self.custom_radio.isChecked():
            # Custom cron - validate
            cron_expr = self.cron_edit.text().strip()
            if not cron_expr:
                QMessageBox.warning(self, "Invalid Input", "Please enter a cron expression.")
                return

            parts = cron_expr.split()
            if len(parts) != 5:
                QMessageBox.warning(
                    self,
                    "Invalid Cron Expression",
                    "Cron expression must have 5 parts:\nminute hour day month day_of_week",
                )
                return

        self.accept()

    def get_schedule_config(self) -> dict[str, bool | str | int] | None:
        """
        Get the configured schedule.

        Returns:
            Schedule configuration dict or None if disabled
        """
        if not self.enabled_checkbox.isChecked():
            return None

        config: dict[str, bool | str | int] = {"enabled": True}

        if self.interval_radio.isChecked():
            config["type"] = "interval"
            config["interval_minutes"] = self.interval_spinbox.value()

        elif self.preset_radio.isChecked():
            config["type"] = "cron"
            config["cron_expression"] = self.preset_combo.currentData()

        elif self.custom_radio.isChecked():
            config["type"] = "cron"
            config["cron_expression"] = self.cron_edit.text().strip()

        return config
