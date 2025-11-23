"""Main entry point for video generation from text input."""

import sys
from pathlib import Path

from app.core.config import get_settings
from app.services.video_generator import generate_video_from_text


def main():
    """Main function for command-line execution."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_text> [output_path]")
        print("\nExample:")
        print('  python main.py "これはテストです。動画が生成されます。" output.mp4')
        sys.exit(1)

    input_text = sys.argv[1]
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("output_video.mp4")

    # Check if OpenAI API key is available
    use_mock_llm = True
    settings = get_settings()
    if settings.openai_api_key:
        response = input("\nUse OpenAI API? (y/N): ").strip().lower()
        use_mock_llm = response != "y"

    try:
        video_path = generate_video_from_text(
            input_text=input_text,
            output_path=output_path,
            use_mock_llm=use_mock_llm,
        )
        print(f"\n✓ Success! Video saved to: {video_path.absolute()}")
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

