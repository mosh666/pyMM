"""
First-run wizard for pyMediaManager initial setup.
Multi-step wizard for storage detection and plugin configuration.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.core.services.storage_group_service import StorageGroupService
    from app.core.services.storage_service import StorageService


class WizardPage(QWidget):
    """Base class for wizard pages."""

    def __init__(self, title: str, description: str) -> None:
        """Initialize wizard page base class.

        Args:
            title: Page title text.
            description: Page description text.

        Examples:
            >>> page = WizardPage('Welcome', 'Welcome to the app')
        """
        super().__init__()
        self.title = title
        self.description = description
        self._init_ui()

    def _init_ui(self) -> None:
        """Initialize base UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        # Title
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(self.description)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        # Content area (to be filled by subclasses)
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)

        layout.addStretch()

    def validate(self) -> bool:
        """
        Validate page before moving to next.

        Returns:
            True if page is valid and can proceed
        """
        return True

    def get_data(self) -> dict[str, Any]:
        """
        Get data collected on this page.

        Returns:
            Dictionary with page data
        """
        return {}


class WelcomePage(WizardPage):
    """Welcome page introducing the application."""

    def __init__(self) -> None:
        """Initialize welcome page with application introduction.

        Examples:
            >>> welcome_page = WelcomePage()
        """
        super().__init__(
            "Welcome to pyMediaManager",
            "Thank you for choosing pyMediaManager, your portable media management solution.<br>"
            "This wizard will help you set up the application for first use.",
        )

        # Add welcome content
        features = QLabel(
            "<b>Features:</b><br>"
            "• Portable - runs from removable drives<br>"
            "• Plugin-based - manage external tools easily<br>"
            "• Project-based - organize your media projects<br>"
            "• Version control ready - Git integration built-in"
        )
        features.setTextFormat(Qt.RichText)
        self.content_layout.addWidget(features)

        next_steps = QLabel(
            "<br><b>Next steps:</b><br>We'll help you configure storage and plugins."
        )
        next_steps.setTextFormat(Qt.RichText)
        self.content_layout.addWidget(next_steps)


class StoragePage(WizardPage):
    """Storage detection and selection page."""

    drive_selected = Signal(Path)

    def __init__(self, storage_service: StorageService) -> None:
        """Initialize storage selection page.

        Args:
            storage_service: Storage service for drive detection.

        Examples:
            >>> storage_page = StoragePage(storage_service)
        """
        self.storage_service = storage_service
        self.selected_drive: Path | None = None

        super().__init__(
            "Select Portable Drive",
            "Choose the removable drive where pyMediaManager projects and logs will be stored. "
            "The application will create 'pyMM.Projects' and 'pyMM.Logs' folders at the drive root.",
        )

        # Drive list
        self.drive_list = QListWidget()
        self.drive_list.setMinimumHeight(200)
        self.drive_list.itemSelectionChanged.connect(self._on_drive_selected)
        self.content_layout.addWidget(self.drive_list)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Drive List")
        refresh_btn.clicked.connect(self.refresh_drives)
        self.content_layout.addWidget(refresh_btn)

        # Auto-refresh on page show
        self.refresh_drives()

    def refresh_drives(self) -> None:
        """Refresh the list of available drives."""
        self.drive_list.clear()

        # Get all removable drives
        drives = self.storage_service.get_removable_drives()

        if not drives:
            item = QListWidgetItem("⚠️ No removable drives detected")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.drive_list.addItem(item)
            return

        # Add each drive
        for drive in drives:
            size_gb = drive.total_size / (1024**3)
            free_gb = drive.free_space / (1024**3)

            label = f"{drive.drive_letter}"
            if drive.label:
                label += f" ({drive.label})"

            label += f" - {free_gb:.1f} GB free / {size_gb:.1f} GB total"

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, drive.drive_letter)
            self.drive_list.addItem(item)

        # Auto-select first drive
        if self.drive_list.count() > 0:
            self.drive_list.setCurrentRow(0)

    def _on_drive_selected(self) -> None:
        """Handle drive selection and emit signal.

        Updates selected_drive attribute and emits drive_selected signal
        when user selects a drive from the list.

        Examples:
            >>> storage_page._on_drive_selected()
            # Emits drive_selected signal with Path object
        """
        items = self.drive_list.selectedItems()
        if items:
            drive_letter = items[0].data(Qt.UserRole)
            if drive_letter:
                self.selected_drive = Path(drive_letter)
                self.drive_selected.emit(self.selected_drive)

    def validate(self) -> bool:
        """Validate that a drive is selected."""
        return self.selected_drive is not None

    def get_data(self) -> dict[str, Path | None]:
        """Return selected drive."""
        return {"portable_drive": self.selected_drive}


class StorageGroupPage(WizardPage):
    """Storage group configuration page for setting up Master/Backup drive pairs."""

    def __init__(
        self,
        storage_service: StorageService,
        storage_group_service: StorageGroupService | None = None,
    ) -> None:
        """Initialize storage group configuration page.

        Args:
            storage_service: Storage service for drive detection.
            storage_group_service: Storage group service for managing drive pairs.

        Examples:
            >>> storage_group_page = StorageGroupPage(storage_service, storage_group_service)
        """
        self.storage_service = storage_service
        self.storage_group_service = storage_group_service
        self.master_drive = None
        self.backup_drive = None

        super().__init__(
            "Configure Storage Groups (Optional)",
            "Set up Master/Backup drive pairs for data redundancy. "
            "This allows you to maintain synchronized copies of your projects on two drives. "
            "You can skip this step and configure it later.",
        )

        # Skip message
        skip_label = QLabel(
            "💡 <b>Tip:</b> You can skip this step and configure storage groups later "
            "from the Storage Management view."
        )
        skip_label.setWordWrap(True)
        skip_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0;")
        self.content_layout.addWidget(skip_label)

        # Master drive selection
        master_group = QLabel("<b>Master Drive:</b> (Primary storage)")
        self.content_layout.addWidget(master_group)

        self.master_combo = QComboBox()
        self.master_combo.currentIndexChanged.connect(self._on_master_changed)
        self.content_layout.addWidget(self.master_combo)

        # Backup drive selection
        backup_group = QLabel("<b>Backup Drive:</b> (Redundant copy)")
        self.content_layout.addWidget(backup_group)

        self.backup_combo = QComboBox()
        self.backup_combo.currentIndexChanged.connect(self._on_backup_changed)
        self.content_layout.addWidget(self.backup_combo)

        # Group name
        name_label = QLabel("<b>Group Name:</b>")
        self.content_layout.addWidget(name_label)

        self.name_edit = QTextEdit()
        self.name_edit.setMaximumHeight(60)
        self.name_edit.setPlaceholderText(
            "Enter a name for this storage group (e.g., 'Photo Archive 2026')"
        )
        self.content_layout.addWidget(self.name_edit)

        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Drive List")
        refresh_btn.clicked.connect(self.refresh_drives)
        self.content_layout.addWidget(refresh_btn)

        # Status label
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        self.content_layout.addWidget(self.status_label)

        # Auto-refresh on page show
        self.refresh_drives()

    def refresh_drives(self) -> None:
        """Refresh the list of available drives."""
        self.master_combo.clear()
        self.backup_combo.clear()

        # Add "None" / "Skip" option
        self.master_combo.addItem("-- Skip (configure later) --", None)
        self.backup_combo.addItem("-- Select backup drive --", None)

        # Get all removable drives
        drives = self.storage_service.get_removable_drives()

        if not drives:
            self.status_label.setText("⚠️ No removable drives detected")
            self.status_label.setStyleSheet("color: orange;")
            return

        # Add each drive to both combos
        for drive in drives:
            size_gb = drive.total_size / (1024**3)
            label = f"{drive.drive_letter}"
            if drive.label:
                label += f" ({drive.label})"
            label += f" - {size_gb:.1f} GB"

            self.master_combo.addItem(label, drive)
            self.backup_combo.addItem(label, drive)

        self.status_label.setText(f"✓ Found {len(drives)} removable drive(s)")
        self.status_label.setStyleSheet("color: green;")

    def _on_master_changed(self, index: int) -> None:
        """Handle master drive selection."""
        self.master_drive = self.master_combo.itemData(index)
        self._validate_selection()

    def _on_backup_changed(self, index: int) -> None:
        """Handle backup drive selection."""
        self.backup_drive = self.backup_combo.itemData(index)
        self._validate_selection()

    def _validate_selection(self) -> None:
        """Validate that master and backup drives are different."""
        if self.master_drive and self.backup_drive:
            if self.master_drive.drive_letter == self.backup_drive.drive_letter:
                self.status_label.setText("⚠️ Master and Backup drives must be different!")
                self.status_label.setStyleSheet("color: red;")
            else:
                self.status_label.setText("✓ Valid drive pair selected")
                self.status_label.setStyleSheet("color: green;")

    def validate(self) -> bool:
        """Validate page - always valid since storage groups are optional."""
        # If user selects drives, ensure they're different
        return not (
            self.master_drive
            and self.backup_drive
            and self.master_drive.drive_letter == self.backup_drive.drive_letter
        )

    def get_data(self) -> dict[str, Any]:
        """Return storage group configuration data."""
        # Only return data if both drives are selected
        if self.master_drive and self.backup_drive:
            group_name = self.name_edit.toPlainText().strip()
            if not group_name:
                group_name = f"Storage Group {self.master_drive.drive_letter} ↔ {self.backup_drive.drive_letter}"

            return {
                "storage_group": {
                    "master_drive": self.master_drive,
                    "backup_drive": self.backup_drive,
                    "name": group_name,
                }
            }
        return {"storage_group": None}


class PluginPage(WizardPage):
    """Plugin selection page."""

    def __init__(self, plugin_names: list[str]) -> None:
        """Initialize plugin selection page.

        Args:
            plugin_names: List of available plugin names.

        Examples:
            >>> plugin_page = PluginPage(['git', 'digikam'])
        """
        self.plugin_names = plugin_names
        self.selected_plugins: list[str] = []

        super().__init__(
            "Select Optional Plugins",
            "Choose which optional plugins you'd like to install. "
            "Mandatory plugins will be installed automatically.",
        )

        # Plugin checkboxes
        self.checkboxes = {}
        for plugin_name in plugin_names:
            checkbox = QCheckBox(plugin_name)
            checkbox.setChecked(False)
            checkbox.stateChanged.connect(self._update_selection)
            self.checkboxes[plugin_name] = checkbox
            self.content_layout.addWidget(checkbox)

        # Info label
        self.info_label = QLabel(
            "Mandatory plugins (Git, GitVersion, digiKam, etc.) will be installed automatically."
        )
        self.info_label.setWordWrap(True)
        self.content_layout.addWidget(self.info_label)

    def _update_selection(self) -> None:
        """Update selected plugins list."""
        self.selected_plugins = [
            name for name, checkbox in self.checkboxes.items() if checkbox.isChecked()
        ]

    def get_data(self) -> dict[str, list[str]]:
        """Return selected plugins."""
        return {"optional_plugins": self.selected_plugins}


class CompletePage(WizardPage):
    """Completion page with summary and settings."""

    def __init__(self) -> None:
        """Initialize completion page with summary.

        Examples:
            >>> complete_page = CompletePage()
        """
        super().__init__(
            "Setup Complete!",
            "pyMediaManager is ready to use. You can now start managing your media projects.",
        )

        # Don't show again checkbox
        self.dont_show_checkbox = QCheckBox("Don't show this wizard again")
        self.dont_show_checkbox.setChecked(False)
        self.content_layout.addWidget(self.dont_show_checkbox)

        # Summary
        summary = QLabel(
            "<br><b>What's next?</b><br>"
            "• Create your first media project<br>"
            "• Install plugins from the Plugin Manager<br>"
            "• Configure application settings<br>"
            "• Explore the documentation"
        )
        summary.setTextFormat(Qt.RichText)
        self.content_layout.addWidget(summary)

    def get_data(self) -> dict[str, bool]:
        """Return wizard settings."""
        return {"dont_show_again": self.dont_show_checkbox.isChecked()}


class FirstRunWizard(QWidget):
    """Multi-step first-run wizard."""

    finished = Signal(dict)  # Emits collected data when wizard completes
    cancelled = Signal()

    def __init__(
        self,
        storage_service: StorageService,
        optional_plugin_names: list[str],
        parent: QWidget | None = None,
        storage_group_service: StorageGroupService | None = None,
    ) -> None:
        """Initialize first-run wizard.

        Args:
            storage_service: Storage service for drive detection.
            optional_plugin_names: List of optional plugin names.
            parent: Parent widget (optional).
            storage_group_service: Storage group service for managing drive pairs (optional).

        Examples:
            >>> wizard = FirstRunWizard(storage_service, ['git', 'digikam'])
        """
        super().__init__(parent)
        self.storage_service = storage_service
        self.optional_plugin_names = optional_plugin_names
        self.storage_group_service = storage_group_service
        self.collected_data: dict[str, Any] = {}

        self._init_ui()
        self._create_pages()

    def _init_ui(self) -> None:
        """Initialize wizard UI."""
        self.setWindowTitle("pyMediaManager Setup Wizard")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Stacked widget for pages
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Button bar
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.setSpacing(10)

        button_layout.addStretch()

        self.back_btn = QPushButton("← Back")
        self.back_btn.clicked.connect(self._go_back)
        self.back_btn.setEnabled(False)
        button_layout.addWidget(self.back_btn)

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._go_next)
        button_layout.addWidget(self.next_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)

        layout.addLayout(button_layout)

    def _create_pages(self) -> None:
        """Create wizard pages."""
        self.pages = [
            WelcomePage(),
            StoragePage(self.storage_service),
            StorageGroupPage(self.storage_service, self.storage_group_service),
            PluginPage(self.optional_plugin_names),
            CompletePage(),
        ]

        for page in self.pages:
            self.stack.addWidget(page)

        self._update_buttons()

    def _go_next(self) -> None:
        """Move to next page or finish."""
        current_page = self.stack.currentWidget()

        # Validate current page
        if not current_page.validate():
            return

        # Collect data from current page
        self.collected_data.update(current_page.get_data())

        # Move to next page or finish
        if self.stack.currentIndex() < len(self.pages) - 1:
            self.stack.setCurrentIndex(self.stack.currentIndex() + 1)
            self._update_buttons()
        else:
            # Finish wizard
            self.finished.emit(self.collected_data)
            self.close()

    def _go_back(self) -> None:
        """Move to previous page."""
        if self.stack.currentIndex() > 0:
            self.stack.setCurrentIndex(self.stack.currentIndex() - 1)
            self._update_buttons()

    def _on_cancel(self) -> None:
        """Handle wizard cancellation."""
        self.cancelled.emit()
        self.close()

    def _update_buttons(self) -> None:
        """Update button states based on current page."""
        current_index = self.stack.currentIndex()

        # Back button
        self.back_btn.setEnabled(current_index > 0)

        # Next/Finish button
        if current_index == len(self.pages) - 1:
            self.next_btn.setText("Finish")
        else:
            self.next_btn.setText("Next →")
