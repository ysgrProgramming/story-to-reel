"""Video script models for defining scenes and video structure."""

from pydantic import BaseModel, ConfigDict, Field


class Scene(BaseModel):
    """Represents a single scene in the video script."""

    scene_number: int = Field(..., description="Sequential scene number")
    dialogue: str = Field(..., description="Text to be spoken/displayed in this scene")
    display_text: str = Field(..., description="Text to display as subtitle")
    duration_seconds: float = Field(
        ..., ge=0.1, description="Duration of this scene in seconds"
    )
    background_color: str | None = Field(
        default="#000000", description="Background color (hex format)"
    )
    background_image_url: str | None = Field(
        default=None, description="Optional background image URL"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scene_number": 1,
                "dialogue": "Welcome to our story",
                "display_text": "Welcome to our story",
                "duration_seconds": 3.0,
                "background_color": "#1a1a2e",
                "background_image_url": None,
            }
        }
    )


class VideoScript(BaseModel):
    """Complete video script containing all scenes."""

    title: str = Field(..., description="Title of the video")
    scenes: list[Scene] = Field(..., min_length=1, description="List of scenes")
    total_duration_seconds: float = Field(
        ..., ge=0.1, description="Total duration of the video"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "My Story",
                "scenes": [
                    {
                        "scene_number": 1,
                        "dialogue": "This is the first scene",
                        "display_text": "This is the first scene",
                        "duration_seconds": 3.0,
                        "background_color": "#1a1a2e",
                    }
                ],
                "total_duration_seconds": 3.0,
            }
        }
    )

    def validate_duration(self) -> bool:
        """Validate that total duration matches sum of scene durations."""
        calculated_duration = sum(scene.duration_seconds for scene in self.scenes)
        return abs(self.total_duration_seconds - calculated_duration) < 0.1

