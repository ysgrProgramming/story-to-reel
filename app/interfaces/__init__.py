"""Abstract interfaces for video generation components.

Protocol-based interfaces using Python's typing.Protocol:
- LLMProvider: Generates script JSON from input text
- AssetManager: Creates audio files and background images
- VideoComposer: Renders final video from script + assets

These protocols enable loose coupling and easy swapping of implementations.
See ARCHITECTURE.md for extension guidance.
"""

from app.interfaces.llm_provider import LLMProvider
from app.interfaces.asset_manager import AssetManager
from app.interfaces.video_composer import VideoComposer

__all__ = ["LLMProvider", "AssetManager", "VideoComposer"]

