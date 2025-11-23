"""Abstract interface for video composition."""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol

from app.models.video_script import VideoScript


class VideoComposer(Protocol):
    """Protocol defining the interface for video composition."""

    @abstractmethod
    def compose(
        self, script: VideoScript, output_path: Path, assets: dict[str, Path]
    ) -> Path:
        """
        Compose video from script and assets.

        Args:
            script: VideoScript object containing scene definitions
            output_path: Path where output video should be saved
            assets: Dictionary mapping scene numbers or keys to asset paths

        Returns:
            Path to generated video file

        Raises:
            Exception: If video composition fails
        """
        ...

