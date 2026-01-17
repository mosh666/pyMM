"""Tests for ToolVersionDialog."""

from unittest.mock import patch

from PySide6.QtWidgets import QWidget
import pytest

from app.ui.dialogs.tool_version_dialog import ToolVersionDialog, VersionChoice


class TestToolVersionDialog:
    """Test suite for ToolVersionDialog."""

    @pytest.fixture
    def parent(self, qtbot):
        """Create parent widget."""
        parent = QWidget()
        parent.resize(800, 600)
        qtbot.addWidget(parent)
        return parent

    @pytest.fixture
    def dialog(self, qtbot, parent):
        """Create dialog instance."""
        dlg = ToolVersionDialog("Git", "2.30.0", ">=2.40.0", parent=parent)
        qtbot.addWidget(dlg)
        return dlg

    def test_init(self, dialog):
        """Test dialog initialization."""
        assert dialog.tool_name == "Git"
        assert dialog.detected_version == "2.30.0"
        assert dialog.required_constraint == ">=2.40.0"
        assert dialog.choice == VersionChoice.CANCEL

        # Check UI elements
        assert "Git Version Incompatible" in dialog.titleLabel.text()
        assert "2.30.0" in dialog.versionLabel.text()
        assert ">=2.40.0" in dialog.versionLabel.text()
        assert dialog.useAnywayButton is not None

    def test_install_portable_choice(self, dialog):
        """Test choosing install portable."""
        dialog._on_install_portable()
        assert dialog.choice == VersionChoice.INSTALL_PORTABLE

    def test_use_anyway_choice(self, dialog):
        """Test choosing use anyway."""
        dialog._on_use_anyway()
        assert dialog.choice == VersionChoice.USE_ANYWAY

    def test_cancel_choice(self, dialog):
        """Test choosing cancel."""
        dialog._on_cancel()
        assert dialog.choice == VersionChoice.CANCEL

    def test_ask_method(self):
        """Test static ask method using mocks."""
        with patch("app.ui.dialogs.tool_version_dialog.ToolVersionDialog") as mock_dialog:
            mock_instance = mock_dialog.return_value
            mock_instance.choice = VersionChoice.INSTALL_PORTABLE

            result = ToolVersionDialog.ask("Git", "1.0", "2.0")

            mock_dialog.assert_called_once_with("Git", "1.0", "2.0", None)
            mock_instance.exec.assert_called_once()
            assert result == VersionChoice.INSTALL_PORTABLE
