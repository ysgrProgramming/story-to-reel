"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from app.models.video_script import Scene, VideoScript


class TestScene:
    """Tests for Scene model."""

    def test_create_valid_scene(self):
        """Test creating a valid scene."""
        scene = Scene(
            scene_number=1,
            dialogue="Test dialogue",
            display_text="Test display",
            duration_seconds=3.0,
            background_color="#000000",
        )
        assert scene.scene_number == 1
        assert scene.dialogue == "Test dialogue"
        assert scene.duration_seconds == 3.0

    def test_scene_default_background_color(self):
        """Test that background color defaults to black."""
        scene = Scene(
            scene_number=1,
            dialogue="Test",
            display_text="Test",
            duration_seconds=2.0,
        )
        assert scene.background_color == "#000000"

    def test_scene_duration_validation(self):
        """Test that duration must be >= 0.1."""
        with pytest.raises(ValidationError):
            Scene(
                scene_number=1,
                dialogue="Test",
                display_text="Test",
                duration_seconds=0.0,
            )

    def test_scene_optional_background_image_url(self):
        """Test optional background_image_url field."""
        scene = Scene(
            scene_number=1,
            dialogue="Test",
            display_text="Test",
            duration_seconds=2.0,
            background_image_url="https://example.com/image.jpg",
        )
        assert scene.background_image_url == "https://example.com/image.jpg"


class TestVideoScript:
    """Tests for VideoScript model."""

    def test_create_valid_video_script(self, sample_scene: Scene):
        """Test creating a valid video script."""
        script = VideoScript(
            title="Test Video",
            scenes=[sample_scene],
            total_duration_seconds=3.0,
        )
        assert script.title == "Test Video"
        assert len(script.scenes) == 1
        assert script.total_duration_seconds == 3.0

    def test_video_script_requires_at_least_one_scene(self):
        """Test that video script must have at least one scene."""
        with pytest.raises(ValidationError):
            VideoScript(
                title="Test",
                scenes=[],
                total_duration_seconds=0.0,
            )

    def test_validate_duration_matches(self, sample_scene: Scene):
        """Test duration validation when durations match."""
        script = VideoScript(
            title="Test",
            scenes=[sample_scene],
            total_duration_seconds=3.0,
        )
        assert script.validate_duration() is True

    def test_validate_duration_mismatch(self, sample_scene: Scene):
        """Test duration validation when durations don't match."""
        script = VideoScript(
            title="Test",
            scenes=[sample_scene],
            total_duration_seconds=10.0,  # Different from scene duration
        )
        assert script.validate_duration() is False

    def test_validate_duration_with_multiple_scenes(self):
        """Test duration validation with multiple scenes."""
        scenes = [
            Scene(
                scene_number=i,
                dialogue=f"Scene {i}",
                display_text=f"Scene {i}",
                duration_seconds=float(i),
            )
            for i in range(1, 4)
        ]
        total = sum(s.duration_seconds for s in scenes)
        script = VideoScript(
            title="Multi-scene",
            scenes=scenes,
            total_duration_seconds=total,
        )
        assert script.validate_duration() is True

