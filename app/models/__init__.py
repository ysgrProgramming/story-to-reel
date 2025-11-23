"""Pydantic models for video script and scene definitions.

Data models:
- Scene: Single video scene (dialogue, display_text, duration, background)
- VideoScript: Complete script (title, scenes list, total_duration)

These models provide type safety and validation throughout the application.
See video_script.py for field definitions and validation rules.
"""

from app.models.video_script import Scene, VideoScript

__all__ = ["Scene", "VideoScript"]

