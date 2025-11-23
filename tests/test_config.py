"""Tests for configuration management."""

from pathlib import Path
from unittest.mock import patch


from app.core.config import Settings
from app.core.font_manager import FontManager


class TestSettings:
    """Tests for Settings class."""

    def test_settings_loads_from_env(self, monkeypatch):
        """Test that settings load from environment variables."""
        monkeypatch.setenv("OPENAI_API_KEY", "test_key_123")
        monkeypatch.setenv("OUTPUT_DIRECTORY", "/test/output")

        settings = Settings()

        assert settings.openai_api_key == "test_key_123"

    def test_settings_has_defaults(self):
        """Test that settings have sensible defaults."""
        settings = Settings()

        assert settings.output_directory == Path("output")
        assert settings.temp_directory == Path("temp")

    @patch("platform.system")
    def test_font_detection_macos(self, mock_system, monkeypatch):
        """Test font detection on macOS."""
        mock_system.return_value = "Darwin"

        # Clear cache to force re-creation of Settings
        Settings.model_config = Settings.model_config

        settings = Settings()

        # Should attempt to find macOS fonts
        assert settings.default_font_path is not None or settings.default_font_path == ""

    @patch("platform.system")
    def test_font_detection_linux(self, mock_system):
        """Test font detection on Linux."""
        mock_system.return_value = "Linux"

        settings = Settings()

        # Should attempt to find Linux fonts
        assert settings.default_font_path is not None or settings.default_font_path == ""


class TestFontManager:
    """Tests for FontManager class."""

    def test_font_manager_with_custom_path(self, temp_dir: Path):
        """Test FontManager with custom font path."""
        font_path = temp_dir / "custom_font.ttf"
        font_path.touch()

        manager = FontManager(font_path=str(font_path))
        assert manager.get_font_path() == str(font_path)

    def test_font_manager_validation(self, temp_dir: Path):
        """Test font validation."""
        font_path = temp_dir / "test_font.ttf"
        font_path.touch()

        manager = FontManager(font_path=str(font_path))
        assert manager.validate_font() is True

    def test_font_manager_invalid_path(self):
        """Test FontManager with invalid font path."""
        manager = FontManager(font_path="/nonexistent/font.ttf")
        assert manager.validate_font() is False
        assert manager.get_font_path() is None

