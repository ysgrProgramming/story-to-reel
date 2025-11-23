"""Tests for ScriptGenerator service."""

import json
from unittest.mock import Mock

import pytest

from app.services.script_generator import ScriptGenerator
from app.models.video_script import VideoScript


class TestScriptGenerator:
    """Tests for ScriptGenerator."""

    def test_generate_creates_video_script(self, mock_llm_provider_response, mock_llm_json_response):
        """Test that generate creates a valid VideoScript."""
        mock_provider = mock_llm_provider_response(mock_llm_json_response)
        generator = ScriptGenerator(mock_provider)

        script = generator.generate("Test input text")

        assert isinstance(script, VideoScript)
        assert script.title == "Test Story"
        assert len(script.scenes) == 2

    def test_generate_validates_scene_structure(self, mock_llm_provider_response, mock_llm_json_response):
        """Test that generated script has valid scene structure."""
        mock_provider = mock_llm_provider_response(mock_llm_json_response)
        generator = ScriptGenerator(mock_provider)

        script = generator.generate("Test input")

        assert all(scene.scene_number > 0 for scene in script.scenes)
        assert all(scene.dialogue for scene in script.scenes)
        assert all(scene.duration_seconds > 0 for scene in script.scenes)

    def test_generate_empty_input_raises_error(self):
        """Test that empty input raises ValueError."""
        mock_provider = Mock()
        generator = ScriptGenerator(mock_provider)

        with pytest.raises(ValueError, match="Input text cannot be empty"):
            generator.generate("")

        with pytest.raises(ValueError, match="Input text cannot be empty"):
            generator.generate("   ")

    def test_generate_invalid_json_raises_error(self):
        """Test that invalid JSON from provider raises ValueError."""
        mock_provider = Mock()
        mock_provider.generate_script_content.return_value = "invalid json"
        generator = ScriptGenerator(mock_provider)

        with pytest.raises(ValueError, match="Failed to parse LLM response"):
            generator.generate("Test input")

    def test_generate_missing_fields_raises_error(self):
        """Test that missing required fields raise ValueError."""
        mock_provider = Mock()
        mock_provider.generate_script_content.return_value = json.dumps({"title": "Test"})
        generator = ScriptGenerator(mock_provider)

        with pytest.raises(ValueError, match="missing 'scenes' field"):
            generator.generate("Test input")

    def test_generate_adjusts_duration_if_mismatch(self, mock_llm_provider_response):
        """Test that generator recalculates duration if mismatch."""
        # Create JSON with mismatched duration
        script_data = {
            "title": "Test",
            "scenes": [
                {
                    "scene_number": 1,
                    "dialogue": "Test",
                    "display_text": "Test",
                    "duration_seconds": 2.0,
                },
                {
                    "scene_number": 2,
                    "dialogue": "Test 2",
                    "display_text": "Test 2",
                    "duration_seconds": 3.0,
                },
            ],
            "total_duration_seconds": 100.0,  # Mismatched
        }
        mock_provider = mock_llm_provider_response(json.dumps(script_data))
        generator = ScriptGenerator(mock_provider)

        script = generator.generate("Test")

        # Duration should be recalculated
        expected_duration = 2.0 + 3.0
        assert script.total_duration_seconds == expected_duration

