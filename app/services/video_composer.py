"""Video composer implementation using MoviePy."""

from pathlib import Path

# MoviePy 2.x uses different import paths - try direct imports first
try:
    # MoviePy 2.x - direct imports
    from moviepy import (
        AudioFileClip,
        CompositeVideoClip,
        ImageClip,
        TextClip,
        concatenate_videoclips,
    )
except ImportError:
    # Fallback for MoviePy 1.x - editor module
    try:
        from moviepy.editor import (
            AudioFileClip,
            CompositeVideoClip,
            ImageClip,
            TextClip,
            concatenate_videoclips,
        )
    except ImportError:
        # Last resort
        raise ImportError(
            "MoviePy is not properly installed. Please install with: pip install moviepy"
        )

from app.models.video_script import Scene, VideoScript
from app.core.font_manager import FontManager


class MoviePyVideoComposer:
    """Video composer using MoviePy for rendering."""

    def __init__(
        self,
        width: int = 1920,
        height: int = 1080,
        font_path: str | None = None,
    ):
        """
        Initialize MoviePyVideoComposer.

        Args:
            width: Video width in pixels (default: 1920)
            height: Video height in pixels (default: 1080)
            font_path: Optional font path for subtitles
        """
        self.width = width
        self.height = height

        # Get font path
        if font_path:
            self.font_path = font_path
        else:
            font_manager = FontManager()
            self.font_path = font_manager.get_font_path()

    def compose(
        self, script: VideoScript, output_path: Path, assets: dict[str, Path]
    ) -> Path:
        """
        Compose video from script and assets.

        Args:
            script: VideoScript object containing scene definitions
            output_path: Path where output video should be saved
            assets: Dictionary mapping scene numbers (as strings) to asset paths
                   Expected keys: "audio_{scene_number}", "bg_{scene_number}"

        Returns:
            Path to generated video file

        Raises:
            Exception: If video composition fails
        """
        try:
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Build video clips for each scene
            video_clips: list[CompositeVideoClip] = []

            for scene in script.scenes:
                scene_clip = self._create_scene_clip(scene, assets)
                video_clips.append(scene_clip)

            # Concatenate all scenes
            if not video_clips:
                raise ValueError("No video clips generated from script")

            final_video = concatenate_videoclips(video_clips, method="compose")

            # Write video file
            final_video.write_videofile(
                str(output_path),
                fps=24,
                codec="libx264",
                audio_codec="aac",
                temp_audiofile=str(output_path.parent / f"temp_audio_{output_path.stem}.m4a"),
                remove_temp=True,
                # MoviePy 2.x: verbose and logger parameters removed
            )

            # Cleanup
            final_video.close()
            for clip in video_clips:
                clip.close()

            return output_path

        except Exception as e:
            raise RuntimeError(f"Failed to compose video: {e}") from e

    def _create_scene_clip(
        self, scene: Scene, assets: dict[str, Path]
    ) -> CompositeVideoClip:
        """
        Create a video clip for a single scene.

        Args:
            scene: Scene object
            assets: Dictionary of asset paths

        Returns:
            CompositeVideoClip for the scene
        """
        # Get background image
        bg_key = f"bg_{scene.scene_number}"
        if bg_key not in assets:
            raise ValueError(f"Background asset not found for scene {scene.scene_number}")

        bg_path = assets[bg_key]

        # Create background clip with duration (MoviePy 2.x API)
        bg_clip = ImageClip(str(bg_path), duration=scene.duration_seconds)
        bg_clip = bg_clip.resized((self.width, self.height))

        # Create subtitle clip
        subtitle_clip = self._create_subtitle_clip(scene, scene.duration_seconds)

        # Get audio clip if available
        audio_key = f"audio_{scene.scene_number}"
        audio_clip = None
        if audio_key in assets and assets[audio_key].exists():
            try:
                audio_clip = AudioFileClip(str(assets[audio_key]))
                # Adjust audio duration to match scene
                if audio_clip.duration > scene.duration_seconds:
                    audio_clip = audio_clip.subclipped(0, scene.duration_seconds)  # MoviePy 2.x: subclip -> subclipped
                elif audio_clip.duration < scene.duration_seconds:
                    # Loop audio if shorter than scene duration
                    loops = int(scene.duration_seconds / audio_clip.duration) + 1
                    audio_clip = concatenate_videoclips(
                        [audio_clip] * loops
                    ).subclipped(0, scene.duration_seconds)  # MoviePy 2.x: subclip -> subclipped

                bg_clip = bg_clip.with_audio(audio_clip)
            except Exception as e:
                # If audio loading fails, continue without audio
                print(f"Warning: Failed to load audio for scene {scene.scene_number}: {e}")

        # Composite background and subtitle
        composite = CompositeVideoClip([bg_clip, subtitle_clip])

        return composite

    def _create_subtitle_clip(
        self, scene: Scene, duration: float
    ) -> TextClip:
        """
        Create subtitle text clip for a scene.

        Args:
            scene: Scene object
            duration: Clip duration in seconds

        Returns:
            TextClip for subtitles
        """
        try:
            # Create text clip with font if available
            text_params = {
                "text": scene.display_text,  # MoviePy 2.x: txt -> text
                "font_size": 70,  # MoviePy 2.x: fontsize -> font_size
                "color": "white",
                "method": "caption",
                "size": (int(self.width * 0.8), None),  # MoviePy 2.x: width must be int
                # MoviePy 2.x: align parameter removed, use with_position instead
            }

            # Only add font if it's a valid path
            if self.font_path and Path(self.font_path).exists():
                text_params["font"] = self.font_path

            # Add duration to text_params for MoviePy 2.x API
            text_params["duration"] = duration
            subtitle_clip = TextClip(**text_params)
            # MoviePy 2.x: with_margin() removed, use position with offset instead
            subtitle_clip = subtitle_clip.with_position(
                ("center", self.height - int(self.height * 0.1))
            )

            return subtitle_clip

        except Exception as e:
            # Fallback: create simple text clip without font
            print(f"Warning: Failed to create subtitle with font: {e}")
            subtitle_clip = TextClip(
                scene.display_text,
                font_size=50,  # MoviePy 2.x: fontsize -> font_size
                color="white",
                size=(int(self.width * 0.8), None),  # MoviePy 2.x: width must be int
                method="caption",
                # MoviePy 2.x: align parameter removed, use with_position instead
                duration=duration,  # MoviePy 2.x API
            )
            # MoviePy 2.x: with_margin() removed, use position with offset instead
            subtitle_clip = subtitle_clip.with_position(
                ("center", self.height - int(self.height * 0.1))
            )

            return subtitle_clip

