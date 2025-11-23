"""FastAPI endpoints for video generation.

REST API module providing:
- POST /api/v1/generate: Generate video from text
- GET /api/v1/video/{filename}: Download generated video
- GET /api/v1/health: Health check

See endpoints.py for request/response models and implementation.
FastAPI app instance is in main.py.
"""

from app.api.endpoints import router

__all__ = ["router"]

