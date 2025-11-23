"""Script generator service that creates VideoScript from input text."""

import json

from app.interfaces.llm_provider import LLMProvider
from app.models.video_script import Scene, VideoScript


class ScriptGenerator:
    """Generates VideoScript objects from input text using LLM providers."""

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize ScriptGenerator.

        Args:
            llm_provider: LLM provider implementation
        """
        self.llm_provider = llm_provider

    def generate(self, input_text: str) -> VideoScript:
        """
        Generate VideoScript from input text.

        Args:
            input_text: Raw input text to transform into video script

        Returns:
            VideoScript object containing scene definitions

        Raises:
            ValueError: If script generation or parsing fails
        """
        if not input_text or not input_text.strip():
            raise ValueError("Input text cannot be empty")

        try:
            # Get JSON content from LLM provider
            json_content = self.llm_provider.generate_script_content(input_text)

            # Parse JSON
            script_data = json.loads(json_content)

            # Validate required fields
            if "scenes" not in script_data:
                raise ValueError("Generated script missing 'scenes' field")
            if "title" not in script_data:
                raise ValueError("Generated script missing 'title' field")

            # Build VideoScript object
            scenes = [
                Scene(
                    scene_number=scene_data.get("scene_number", idx + 1),
                    dialogue=scene_data.get("dialogue", ""),
                    display_text=scene_data.get("display_text", scene_data.get("dialogue", "")),
                    duration_seconds=float(scene_data.get("duration_seconds", 3.0)),
                    background_color=scene_data.get("background_color", "#000000"),
                    background_image_url=scene_data.get("background_image_url"),
                )
                for idx, scene_data in enumerate(script_data["scenes"])
            ]

            total_duration = script_data.get(
                "total_duration_seconds",
                sum(scene.duration_seconds for scene in scenes),
            )

            video_script = VideoScript(
                title=script_data["title"],
                scenes=scenes,
                total_duration_seconds=float(total_duration),
            )

            # Validate duration consistency
            if not video_script.validate_duration():
                # Recalculate total duration from scenes
                video_script.total_duration_seconds = sum(
                    scene.duration_seconds for scene in scenes
                )

            return video_script

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}") from e
        except KeyError as e:
            raise ValueError(f"Missing required field in generated script: {e}") from e
        except Exception as e:
            raise ValueError(f"Script generation failed: {e}") from e

