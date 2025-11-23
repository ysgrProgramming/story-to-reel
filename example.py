"""Example usage of the video generation engine."""

from pathlib import Path

from app.services.video_generator import generate_video_from_text


def main():
    """Example: Generate a video from text."""
    # Example text input
    input_text = """
    今日は美しい一日です。
    空は青く、雲が浮かんでいます。
    鳥たちが歌い、風が優しく吹いています。
    自然の美しさを感じることができます。
    """

    # Output path
    output_path = Path("output") / "example_video.mp4"
    output_path.parent.mkdir(exist_ok=True)

    print("Starting video generation...")
    print(f"Input text: {input_text.strip()}\n")

    try:
        # Generate video with mock LLM (no API key required)
        video_path = generate_video_from_text(
            input_text=input_text.strip(),
            output_path=output_path,
            use_mock_llm=True,  # Set to False and set OPENAI_API_KEY to use OpenAI
            width=1920,
            height=1080,
        )

        print(f"\n✓ Success! Video saved to: {video_path.absolute()}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise


if __name__ == "__main__":
    main()

