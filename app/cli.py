"""CLI interface for video generation using Click."""

from pathlib import Path

import click

from app.core.config import get_settings
from app.services.video_generator import generate_video_from_text


@click.command()
@click.argument("input_text", type=str, required=True)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output video file path (default: output_video.mp4)",
)
@click.option(
    "--use-openai",
    is_flag=True,
    default=False,
    help="Use OpenAI API instead of mock LLM",
)
@click.option(
    "--width",
    type=int,
    default=1920,
    help="Video width in pixels (default: 1920)",
)
@click.option(
    "--height",
    type=int,
    default=1080,
    help="Video height in pixels (default: 1080)",
)
@click.option(
    "--mock-llm",
    "use_mock_llm",
    is_flag=True,
    default=None,
    help="Force use of mock LLM (overrides --use-openai)",
)
def generate(
    input_text: str,
    output: Path | None,
    use_openai: bool,
    width: int,
    height: int,
    use_mock_llm: bool | None,
) -> None:
    """
    Generate a video from input text.

    INPUT_TEXT: Text content to convert to video
    """
    # Determine output path
    if output is None:
        output = Path("output_video.mp4")

    # Determine LLM provider
    if use_mock_llm is not None:
        # Explicit flag takes precedence
        use_mock = use_mock_llm
    elif use_openai:
        use_mock = False
    else:
        # Check if OpenAI API key is available
        settings = get_settings()
        if settings.openai_api_key:
            use_mock = click.confirm("\nUse OpenAI API?", default=False)
        else:
            click.echo("No OpenAI API key found. Using mock LLM.")
            use_mock = True

    try:
        click.echo(f"Generating video from text: {input_text[:50]}...")
        click.echo(f"Output path: {output.absolute()}")
        click.echo(f"Video size: {width}x{height}")
        click.echo(f"LLM provider: {'Mock' if use_mock else 'OpenAI'}\n")

        video_path = generate_video_from_text(
            input_text=input_text,
            output_path=output,
            use_mock_llm=use_mock,
            width=width,
            height=height,
        )

        click.echo(f"\n✓ Success! Video saved to: {video_path.absolute()}")

    except Exception as e:
        click.echo(f"\n✗ Error: {e}", err=True)
        raise click.Abort() from e


@click.group()
def cli() -> None:
    """Story to Reel - Automated video generation engine."""
    pass


# Register commands
cli.add_command(generate)


if __name__ == "__main__":
    cli()

