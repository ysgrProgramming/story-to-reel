"""Tests for AssetManager service."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.services.asset_manager import SimpleAssetManager


class TestSimpleAssetManager:
    """Tests for SimpleAssetManager."""

    def test_get_background_image_creates_file(self, temp_dir: Path):
        """Test that get_background_image creates an image file."""
        manager = SimpleAssetManager(output_dir=temp_dir)
        image_path = manager.get_background_image(
            width=1920, height=1080, scene_number=1, color="#FF0000"
        )

        assert image_path.exists()
        assert image_path.suffix == ".png"

    def test_get_background_image_uses_scene_number_in_path(self, temp_dir: Path):
        """Test that background image path includes scene number."""
        manager = SimpleAssetManager(output_dir=temp_dir)
        image_path = manager.get_background_image(
            width=1920, height=1080, scene_number=5
        )

        assert "scene_5" in str(image_path)

    def test_get_background_image_with_custom_color(self, temp_dir: Path):
        """Test background image generation with custom color."""
        manager = SimpleAssetManager(output_dir=temp_dir)
        image_path = manager.get_background_image(
            width=100, height=100, scene_number=1, color="#00FF00"
        )

        assert image_path.exists()
        # Verify image can be loaded (basic validation)
        from PIL import Image
        img = Image.open(image_path)
        assert img.size == (100, 100)

    def test_get_background_image_generates_variation_by_scene(self, temp_dir: Path):
        """Test that different scene numbers generate different images."""
        manager = SimpleAssetManager(output_dir=temp_dir)
        path1 = manager.get_background_image(100, 100, scene_number=1)
        path2 = manager.get_background_image(100, 100, scene_number=2)

        assert path1 != path2

    @patch("app.services.asset_manager.gTTS")
    def test_generate_audio_creates_file(self, mock_gtts, temp_dir: Path):
        """Test that generate_audio creates an audio file."""
        # Mock gTTS
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance

        manager = SimpleAssetManager(output_dir=temp_dir)
        audio_path = temp_dir / "test_audio.mp3"

        # Create a temporary file to simulate gTTS save
        audio_path.touch()

        # Mock the save method to create the file
        def mock_save(path):
            Path(path).touch()

        mock_tts_instance.save = mock_save

        result_path = manager.generate_audio("Test text", audio_path, language="ja")

        assert result_path.exists()
        mock_gtts.assert_called_once_with(text="Test text", lang="ja", slow=False)

    def test_generate_audio_empty_text_raises_error(self, temp_dir: Path):
        """Test that empty text raises ValueError."""
        manager = SimpleAssetManager(output_dir=temp_dir)
        audio_path = temp_dir / "test.mp3"

        with pytest.raises(ValueError, match="Text cannot be empty"):
            manager.generate_audio("", audio_path)

    def test_hex_to_rgb_conversion(self):
        """Test hex color to RGB conversion."""
        from app.services.asset_manager import SimpleAssetManager

        # Test standard hex color
        rgb = SimpleAssetManager._hex_to_rgb("#FF0000")
        assert rgb == (255, 0, 0)

        # Test hex without #
        rgb = SimpleAssetManager._hex_to_rgb("00FF00")
        assert rgb == (0, 255, 0)

    def test_hex_to_rgb_invalid_format(self):
        """Test that invalid hex format raises error."""
        from app.services.asset_manager import SimpleAssetManager

        with pytest.raises(ValueError):
            SimpleAssetManager._hex_to_rgb("invalid")

        with pytest.raises(ValueError):
            SimpleAssetManager._hex_to_rgb("#FF")

