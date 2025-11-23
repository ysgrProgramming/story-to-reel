"""Asset manager implementation for audio and image generation."""

import colorsys
from pathlib import Path

from PIL import Image, ImageDraw
from gtts import gTTS

from app.core.config import get_settings


class SimpleAssetManager:
    """Simple asset manager using TTS and generated images."""

    def __init__(self, output_dir: Path | None = None):
        """
        Initialize SimpleAssetManager.

        Args:
            output_dir: Directory for storing generated assets (default: temp directory)
        """
        settings = get_settings()
        self.output_dir = output_dir or settings.temp_directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_audio(
        self, text: str, output_path: Path, language: str = "ja"
    ) -> Path:
        """
        Generate audio file from text using gTTS.

        Args:
            text: Text to convert to speech
            output_path: Path where audio file should be saved
            language: Language code (default: "ja" for Japanese)

        Returns:
            Path to generated audio file

        Raises:
            Exception: If audio generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for audio generation")

        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Generate TTS audio
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(str(output_path))

            if not output_path.exists():
                raise FileNotFoundError(f"Audio file was not created at {output_path}")

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to generate audio: {e}") from e

    def get_background_image(
        self, width: int, height: int, scene_number: int, color: str | None = None
    ) -> Path:
        """
        Generate or retrieve background image for a scene.

        Args:
            width: Image width in pixels
            height: Image height in pixels
            scene_number: Scene number for variation
            color: Optional background color (hex format)

        Returns:
            Path to background image file

        Raises:
            Exception: If image generation fails
        """
        try:
            # Determine background color
            if color:
                bg_color = self._hex_to_rgb(color)
            else:
                # Generate color based on scene number
                hue = (scene_number * 137.5) % 360 / 360.0  # Golden angle for variation
                saturation = 0.6
                lightness = 0.3
                rgb = colorsys.hls_to_rgb(hue, lightness, saturation)
                bg_color = tuple(int(c * 255) for c in rgb)

            # Create image
            image = Image.new("RGB", (width, height), bg_color)
            draw = ImageDraw.Draw(image)

            # Add subtle pattern for visual interest
            for i in range(0, width, 50):
                draw.line([(i, 0), (i, height)], fill=(*bg_color, 30), width=1)
            for i in range(0, height, 50):
                draw.line([(0, i), (width, i)], fill=(*bg_color, 30), width=1)

            # Save image
            image_path = self.output_dir / f"bg_scene_{scene_number}.png"
            image.save(image_path, "PNG")

            return image_path

        except Exception as e:
            raise RuntimeError(f"Failed to generate background image: {e}") from e

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        """
        Convert hex color string to RGB tuple.

        Args:
            hex_color: Hex color string (e.g., "#1a1a2e" or "1a1a2e")

        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")

        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

