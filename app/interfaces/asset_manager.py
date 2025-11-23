"""Abstract interface for asset management (audio, images, etc.)."""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol


class AssetManager(Protocol):
    """Protocol defining the interface for asset management."""

    @abstractmethod
    def generate_audio(
        self, text: str, output_path: Path, language: str = "ja"
    ) -> Path:
        """
        Generate audio file from text using TTS.

        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved
            language: Language code (default: "ja" for Japanese)

        Returns:
            Path to generated audio file

        Raises:
            Exception: If audio generation fails
        """
        ...

    @abstractmethod
    def get_background_image(
        self, width: int, height: int, scene_number: int, color: str | None = None
    ) -> Path:
        """
        Get or generate background image for a scene.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            scene_number: Scene number for variation
            color: Optional background color (hex format)

        Returns:
            Path to background image file

        Raises:
            Exception: If image generation/retrieval fails
        """
        ...

