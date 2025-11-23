"""FastAPI endpoints for video generation API."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.services.video_generator import generate_video_from_text

router = APIRouter(prefix="/api/v1", tags=["video"])


class VideoGenerationRequest(BaseModel):
    """Request model for video generation."""

    input_text: str = Field(..., description="Input text to convert to video")
    use_mock_llm: bool = Field(default=True, description="Use mock LLM provider")
    width: int = Field(default=1920, ge=640, le=3840, description="Video width")
    height: int = Field(default=1080, ge=360, le=2160, description="Video height")


class VideoGenerationResponse(BaseModel):
    """Response model for video generation."""

    message: str
    video_path: str | None = None
    status: str = Field(..., description="Status: 'processing' or 'completed'")


@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    background_tasks: BackgroundTasks,
) -> VideoGenerationResponse:
    """
    Generate video from input text.

    Note: Video generation is CPU-intensive and may take time.
    Consider implementing async task queue (e.g., Celery) for production.
    """
    settings = get_settings()
    output_path = settings.output_directory / f"video_{id(request)}.mp4"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        video_path = generate_video_from_text(
            input_text=request.input_text,
            output_path=output_path,
            use_mock_llm=request.use_mock_llm,
            width=request.width,
            height=request.height,
        )

        return VideoGenerationResponse(
            message="Video generated successfully",
            video_path=str(video_path),
            status="completed",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")


@router.get("/video/{video_filename}")
async def get_video(video_filename: str) -> FileResponse:
    """
    Retrieve generated video file.

    Args:
        video_filename: Name of the video file

    Returns:
        Video file response
    """
    settings = get_settings()
    video_path = settings.output_directory / video_filename

    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    return FileResponse(
        path=video_path,
        media_type="video/mp4",
        filename=video_filename,
    )


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "story-to-reel"}

