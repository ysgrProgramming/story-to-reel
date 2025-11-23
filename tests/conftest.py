"""Pytest configuration and shared fixtures."""

import json
from pathlib import Path

import pytest

from app.models.video_script import Scene, VideoScript


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Create temporary directory for test outputs."""
    test_dir = tmp_path / "test_output"
    test_dir.mkdir(parents=True, exist_ok=True)
    return test_dir


@pytest.fixture
def sample_scene() -> Scene:
    """Create a sample Scene for testing."""
    return Scene(
        scene_number=1,
        dialogue="Hello world",
        display_text="Hello world",
        duration_seconds=3.0,
        background_color="#000000",
    )


@pytest.fixture
def sample_video_script(sample_scene: Scene) -> VideoScript:
    """Create a sample VideoScript for testing."""
    return VideoScript(
        title="Test Video",
        scenes=[sample_scene],
        total_duration_seconds=3.0,
    )


@pytest.fixture
def mock_llm_json_response() -> str:
    """Return a mock JSON response from LLM provider."""
    script_data = {
        "title": "Test Story",
        "scenes": [
            {
                "scene_number": 1,
                "dialogue": "First scene dialogue",
                "display_text": "First scene",
                "duration_seconds": 2.0,
                "background_color": "#1a1a2e",
            },
            {
                "scene_number": 2,
                "dialogue": "Second scene dialogue",
                "display_text": "Second scene",
                "duration_seconds": 2.5,
                "background_color": "#16213e",
            },
        ],
        "total_duration_seconds": 4.5,
    }
    return json.dumps(script_data, ensure_ascii=False)


@pytest.fixture
def mock_llm_provider_response():
    """Mock LLM provider that returns predefined JSON."""
    class MockLLMProviderResponse:
        def __init__(self, response_json: str):
            self.response_json = response_json

        def generate_script_content(self, input_text: str) -> str:
            return self.response_json

    return MockLLMProviderResponse

