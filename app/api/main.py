"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.endpoints import router

app = FastAPI(
    title="Story to Reel API",
    description="Automated video generation engine API",
    version="0.1.0",
)

app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Story to Reel API",
        "docs": "/docs",
        "health": "/api/v1/health",
    }

