"""Core configuration and utilities.

This module provides:
- Settings: Application configuration loaded from environment variables (.env)
- FontManager: Font path detection and validation (OS-specific)
- get_settings(): Cached settings instance
- get_font_path(): Default font path helper

See ARCHITECTURE.md for detailed module descriptions.
"""

from app.core.config import Settings, get_settings
from app.core.font_manager import FontManager, get_font_path

__all__ = ["Settings", "get_settings", "FontManager", "get_font_path"]

