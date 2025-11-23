"""Font management utilities."""

from pathlib import Path

from app.core.config import get_settings


class FontManager:
    """Manages font paths for video generation."""

    def __init__(self, font_path: str | None = None):
        """
        Initialize FontManager.

        Args:
            font_path: Optional custom font path. If not provided, uses settings default.
        """
        self.font_path: str | None = font_path
        if not self.font_path:
            settings = get_settings()
            self.font_path = settings.default_font_path

    def get_font_path(self) -> str | None:
        """
        Get the font path.

        Returns:
            Font path string or None if not available
        """
        if self.font_path and Path(self.font_path).exists():
            return self.font_path
        return None

    def validate_font(self) -> bool:
        """
        Validate that the font file exists.

        Returns:
            True if font exists, False otherwise
        """
        return self.font_path is not None and Path(self.font_path).exists()


def get_font_path() -> str | None:
    """
    Get default font path from settings.

    Returns:
        Font path string or None
    """
    manager = FontManager()
    return manager.get_font_path()

