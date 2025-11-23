"""Tests for LLM provider implementations."""

import json


from app.services.llm_provider import MockLLMProvider


class TestMockLLMProvider:
    """Tests for MockLLMProvider."""

    def test_generate_script_content_returns_json(self):
        """Test that generate_script_content returns valid JSON."""
        provider = MockLLMProvider()
        input_text = "This is a test. It has multiple sentences."
        result = provider.generate_script_content(input_text)

        # Should be valid JSON
        data = json.loads(result)
        assert isinstance(data, dict)
        assert "title" in data
        assert "scenes" in data
        assert "total_duration_seconds" in data

    def test_generate_script_content_creates_scenes(self):
        """Test that mock provider creates scenes from sentences."""
        provider = MockLLMProvider()
        input_text = "First sentence. Second sentence. Third sentence."
        result = provider.generate_script_content(input_text)
        data = json.loads(result)

        assert len(data["scenes"]) > 0
        assert all("scene_number" in scene for scene in data["scenes"])
        assert all("dialogue" in scene for scene in data["scenes"])
        assert all("duration_seconds" in scene for scene in data["scenes"])

    def test_generate_script_content_with_japanese(self):
        """Test mock provider with Japanese text."""
        provider = MockLLMProvider()
        input_text = "これは最初の文です。これは二番目の文です。"
        result = provider.generate_script_content(input_text)
        data = json.loads(result)

        assert len(data["scenes"]) > 0
        assert "title" in data

    def test_generate_script_content_limits_scenes(self):
        """Test that mock provider limits to 5 scenes."""
        provider = MockLLMProvider()
        # Create text with many sentences
        input_text = ". ".join([f"Sentence {i}" for i in range(10)])
        result = provider.generate_script_content(input_text)
        data = json.loads(result)

        assert len(data["scenes"]) <= 5

    def test_generate_script_content_empty_input(self):
        """Test mock provider with empty input."""
        provider = MockLLMProvider()
        result = provider.generate_script_content("")
        data = json.loads(result)

        assert "title" in data
        assert isinstance(data["scenes"], list)

