"""Service implementations for video generation.

This module contains concrete implementations of interfaces:
- LLM Providers: MockLLMProvider (test), OpenAILLMProvider (OpenAI API)
- ScriptGenerator: Converts text input to VideoScript objects
- SimpleAssetManager: Generates audio (gTTS) and background images (PIL)
- MoviePyVideoComposer: Renders video using MoviePy
- generate_video_from_text(): Main orchestration function

All services implement protocols defined in app.interfaces.
See ARCHITECTURE.md for detailed descriptions.
"""

from app.services.llm_provider import MockLLMProvider, OpenAILLMProvider
from app.services.script_generator import ScriptGenerator
from app.services.asset_manager import SimpleAssetManager
from app.services.video_generator import generate_video_from_text

# MoviePyVideoComposer may fail if moviepy is not installed - use lazy import
try:
    from app.services.video_composer import MoviePyVideoComposer
except ImportError:
    MoviePyVideoComposer = None  # type: ignore

__all__ = [
    "MockLLMProvider",
    "OpenAILLMProvider",
    "ScriptGenerator",
    "SimpleAssetManager",
    "MoviePyVideoComposer",
    "generate_video_from_text",
]

