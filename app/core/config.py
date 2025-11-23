"""Application configuration management."""

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Configuration
    openai_api_key: str | None = None

    # Font Configuration
    default_font_path: str | None = None

    # Output Configuration
    output_directory: Path = Path("output")
    temp_directory: Path = Path("temp")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def __init__(self, **kwargs):
        """Initialize settings with default font path detection."""
        super().__init__(**kwargs)
        if not self.default_font_path:
            self.default_font_path = self._detect_default_font()

    @staticmethod
    def _detect_default_font() -> str:
        """Detect default font path based on OS."""
        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            fonts = [
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            ]
        elif system == "Linux":
            fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            ]
        elif system == "Windows":
            fonts = [
                "C:/Windows/Fonts/msgothic.ttc",
                "C:/Windows/Fonts/meiryo.ttc",
            ]
        else:
            fonts = []

        for font_path in fonts:
            if os.path.exists(font_path):
                return font_path

        # Fallback: return first font path (may not exist)
        return fonts[0] if fonts else ""


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

