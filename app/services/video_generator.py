"""Video generator service that orchestrates the entire video generation process."""

from pathlib import Path

from app.core.config import get_settings
from app.interfaces.llm_provider import LLMProvider
from app.interfaces.asset_manager import AssetManager
from app.interfaces.video_composer import VideoComposer
from app.services.llm_provider import MockLLMProvider, OpenAILLMProvider
from app.services.script_generator import ScriptGenerator
from app.services.asset_manager import SimpleAssetManager
from app.services.video_composer import MoviePyVideoComposer


def generate_video_from_text(
    input_text: str,
    output_path: Path,
    llm_provider: LLMProvider | None = None,
    asset_manager: AssetManager | None = None,
    video_composer: VideoComposer | None = None,
    use_mock_llm: bool = True,
    width: int = 1920,
    height: int = 1080,
) -> Path:
    """
    Generate video from input text.

    Args:
        input_text: Text to convert to video
        output_path: Path where output video will be saved
        llm_provider: Optional LLM provider (default: MockLLMProvider or OpenAILLMProvider)
        asset_manager: Optional asset manager (default: SimpleAssetManager)
        video_composer: Optional video composer (default: MoviePyVideoComposer)
        use_mock_llm: Whether to use mock LLM if provider not specified (default: True)
        width: Video width in pixels (default: 1920)
        height: Video height in pixels (default: 1080)

    Returns:
        Path to generated video file

    Raises:
        Exception: If video generation fails
    """
    settings = get_settings()

    # Initialize components if not provided
    if llm_provider is None:
        if use_mock_llm:
            llm_provider = MockLLMProvider()
        else:
            try:
                llm_provider = OpenAILLMProvider()
            except ValueError as e:
                print(f"Warning: Failed to initialize OpenAI LLM: {e}")
                print("Falling back to Mock LLM provider")
                llm_provider = MockLLMProvider()

    if asset_manager is None:
        asset_manager = SimpleAssetManager(output_dir=settings.temp_directory)

    if video_composer is None:
        video_composer = MoviePyVideoComposer(width=width, height=height)

    # Step 1: Generate script
    print("Generating video script...")
    script_generator = ScriptGenerator(llm_provider)
    try:
        video_script = script_generator.generate(input_text)
        print(f"✓ Generated script: {video_script.title}")
        print(f"  Total scenes: {len(video_script.scenes)}")
        print(f"  Total duration: {video_script.total_duration_seconds:.1f}s")
    except Exception as e:
        raise RuntimeError(f"Script generation failed: {e}") from e

    # Step 2: Generate assets
    print("\nGenerating assets...")
    assets: dict[str, Path] = {}

    for scene in video_script.scenes:
        scene_num = scene.scene_number
        print(f"  Processing scene {scene_num}...")

        # Generate background image
        try:
            bg_path = asset_manager.get_background_image(
                width=width,
                height=height,
                scene_number=scene_num,
                color=scene.background_color,
            )
            assets[f"bg_{scene_num}"] = bg_path
            print(f"    ✓ Background image: {bg_path.name}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate background for scene {scene_num}: {e}"
            ) from e

        # Generate audio
        try:
            audio_path = settings.temp_directory / f"audio_scene_{scene_num}.mp3"
            asset_manager.generate_audio(
                text=scene.dialogue,
                output_path=audio_path,
                language="ja",
            )
            assets[f"audio_{scene_num}"] = audio_path
            print(f"    ✓ Audio: {audio_path.name}")
        except Exception as e:
            print(f"    ⚠ Failed to generate audio for scene {scene_num}: {e}")
            # Continue without audio for this scene

    # Step 3: Compose video
    print("\nComposing video...")
    try:
        video_path = video_composer.compose(
            script=video_script,
            output_path=output_path,
            assets=assets,
        )
        print(f"✓ Video generated: {video_path}")
    except Exception as e:
        raise RuntimeError(f"Video composition failed: {e}") from e

    return video_path

