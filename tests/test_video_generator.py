"""Integration tests for video generation workflow."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.services.video_generator import generate_video_from_text
from app.services.llm_provider import MockLLMProvider


class TestVideoGeneratorIntegration:
    """Integration tests for the full video generation pipeline."""

    @patch("app.services.video_composer.MoviePyVideoComposer.compose")
    @patch("app.services.asset_manager.SimpleAssetManager.generate_audio")
    @patch("app.services.asset_manager.SimpleAssetManager.get_background_image")
    def test_generate_video_from_text_full_workflow(
        self,
        mock_get_bg,
        mock_generate_audio,
        mock_compose,
        temp_dir: Path,
    ):
        """Test the complete video generation workflow."""
        # Setup mocks
        mock_bg_path = temp_dir / "bg_1.png"
        mock_bg_path.touch()
        mock_get_bg.return_value = mock_bg_path

        mock_audio_path = temp_dir / "audio_1.mp3"
        mock_audio_path.touch()
        mock_generate_audio.return_value = mock_audio_path

        output_path = temp_dir / "output.mp4"
        mock_compose.return_value = output_path

        # Generate video
        result_path = generate_video_from_text(
            input_text="This is a test. It has two sentences.",
            output_path=output_path,
            use_mock_llm=True,
            width=640,
            height=360,
        )

        # Verify workflow
        assert result_path == output_path
        mock_get_bg.assert_called()
        mock_generate_audio.assert_called()
        mock_compose.assert_called_once()

    def test_generate_video_from_text_with_custom_providers(self, temp_dir: Path):
        """Test video generation with custom provider instances."""
        mock_llm = Mock()
        mock_llm.generate_script_content.return_value = '{"title": "Test", "scenes": [{"scene_number": 1, "dialogue": "Test", "display_text": "Test", "duration_seconds": 2.0, "background_color": "#000000"}], "total_duration_seconds": 2.0}'

        mock_asset = Mock()
        mock_asset.get_background_image.return_value = temp_dir / "bg.png"
        mock_asset.generate_audio.return_value = temp_dir / "audio.mp3"
        temp_dir.joinpath("bg.png").touch()
        temp_dir.joinpath("audio.mp3").touch()

        mock_composer = Mock()
        output_path = temp_dir / "output.mp4"
        mock_composer.compose.return_value = output_path

        result = generate_video_from_text(
            input_text="Test",
            output_path=output_path,
            llm_provider=mock_llm,
            asset_manager=mock_asset,
            video_composer=mock_composer,
        )

        assert result == output_path
        mock_llm.generate_script_content.assert_called_once()
        mock_asset.get_background_image.assert_called()
        mock_composer.compose.assert_called_once()

    def test_generate_video_from_text_fallback_to_mock_llm(self, temp_dir: Path):
        """Test that invalid OpenAI config falls back to MockLLM."""
        with patch("app.services.video_generator.OpenAILLMProvider") as mock_openai:
            mock_openai.side_effect = ValueError("No API key")

            with patch("app.services.video_generator.SimpleAssetManager") as mock_asset:
                with patch("app.services.video_generator.MoviePyVideoComposer") as mock_composer:
                    mock_bg_path = temp_dir / "bg.png"
                    mock_bg_path.touch()
                    mock_audio_path = temp_dir / "audio.mp3"
                    mock_audio_path.touch()

                    mock_asset_instance = Mock()
                    mock_asset_instance.get_background_image.return_value = mock_bg_path
                    mock_asset_instance.generate_audio.return_value = mock_audio_path
                    mock_asset.return_value = mock_asset_instance

                    mock_composer_instance = Mock()
                    output_path = temp_dir / "output.mp4"
                    mock_composer_instance.compose.return_value = output_path
                    mock_composer.return_value = mock_composer_instance

                    result = generate_video_from_text(
                        input_text="Test",
                        output_path=output_path,
                        use_mock_llm=False,  # Tries OpenAI, should fallback
                    )

                    # Should succeed with fallback
                    assert result == output_path


class TestVideoGeneratorErrorHandling:
    """Tests for error handling in video generation."""

    def test_generate_video_empty_input_raises_error(self, temp_dir: Path):
        """Test that empty input raises error."""
        output_path = temp_dir / "output.mp4"

        with pytest.raises(RuntimeError, match="Script generation failed"):
            generate_video_from_text(
                input_text="",
                output_path=output_path,
                use_mock_llm=True,
            )

    def test_generate_video_asset_generation_failure(self, temp_dir: Path):
        """Test handling of asset generation failures."""
        mock_llm = MockLLMProvider()
        mock_asset = Mock()
        mock_asset.get_background_image.side_effect = RuntimeError("Asset generation failed")

        output_path = temp_dir / "output.mp4"

        with pytest.raises(RuntimeError, match="Failed to generate background"):
            generate_video_from_text(
                input_text="Test text",
                output_path=output_path,
                llm_provider=mock_llm,
                asset_manager=mock_asset,
            )

