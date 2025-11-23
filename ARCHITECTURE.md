# Architecture Documentation

This document provides an overview of the project structure for LLM-assisted development. Each module's purpose and key components are explained.

## Project Structure

```
story-to-reel/
├── app/                    # Main application package
│   ├── api/               # FastAPI endpoints and routing
│   ├── cli.py             # Click CLI interface
│   ├── core/              # Core configuration and utilities
│   ├── interfaces/        # Abstract interfaces (Protocols)
│   ├── models/            # Pydantic data models
│   └── services/          # Concrete implementations
├── tests/                 # Pytest test suite
├── main.py               # Legacy CLI entry point (for compatibility)
├── example.py            # Usage example
└── pyproject.toml        # Project configuration (uv/pip)

```

## Module Descriptions

### `/app/cli.py` - Command Line Interface

**Purpose**: Click-based CLI for video generation from command line.

- Provides `story-to-reel` command after installation
- `generate` subcommand: Generate video from text input
- Options: `--output`, `--use-openai`, `--width`, `--height`, `--mock-llm`

**Usage**: `story-to-reel generate "text" --output output.mp4`

---

### `/app/api/` - FastAPI HTTP API

**Purpose**: REST API endpoints for video generation service.

- `main.py`: FastAPI application instance and root route
- `endpoints.py`: Video generation endpoints (`/api/v1/generate`, `/api/v1/video/{filename}`)

**Key Exports**: FastAPI router, request/response models

---

### `/app/core/` - Core Configuration

**Purpose**: Application-wide settings and utilities.

- `config.py`: `Settings` class using `pydantic-settings` for environment variables
  - Loads `OPENAI_API_KEY`, font paths, output directories from `.env`
  - Auto-detects system fonts based on OS

- `font_manager.py`: `FontManager` class for font path management
  - Validates font availability
  - Provides default font path fallback

**Key Exports**: `Settings`, `get_settings()`, `FontManager`, `get_font_path()`

---

### `/app/interfaces/` - Abstract Interfaces

**Purpose**: Protocol definitions for loose coupling. Allows swapping implementations without changing dependent code.

- `llm_provider.py`: `LLMProvider` protocol
  - Method: `generate_script_content(input_text: str) -> str`
  - Returns JSON string for video script structure

- `asset_manager.py`: `AssetManager` protocol
  - Methods: `generate_audio()`, `get_background_image()`
  - Handles audio TTS and background image generation

- `video_composer.py`: `VideoComposer` protocol
  - Method: `compose(script, output_path, assets) -> Path`
  - Renders final video from script and assets

**Design Pattern**: Uses Python `Protocol` (structural typing) instead of ABC for flexibility.

---

### `/app/models/` - Data Models

**Purpose**: Pydantic models for type-safe data structures.

- `video_script.py`:
  - `Scene`: Single scene with dialogue, display text, duration, background
  - `VideoScript`: Complete script with title, scenes list, total duration

**Usage**: Input validation, serialization, type hints throughout the codebase.

---

### `/app/services/` - Service Implementations

**Purpose**: Concrete implementations of interfaces and orchestration logic.

- `llm_provider.py`:
  - `MockLLMProvider`: Simple mock that splits text into scenes (no API calls)
  - `OpenAILLMProvider`: Uses LangChain + OpenAI to generate structured JSON script

- `script_generator.py`:
  - `ScriptGenerator`: Orchestrates LLM provider to create `VideoScript` objects
  - Parses JSON, validates structure, creates Pydantic models

- `asset_manager.py`:
  - `SimpleAssetManager`: Generates audio via gTTS, creates background images with PIL
  - Outputs to temp directory, manages file paths

- `video_composer.py`:
  - `MoviePyVideoComposer`: Renders video using MoviePy
  - Composites background images, audio clips, and subtitle text clips
  - Concatenates scenes into final MP4

- `video_generator.py`:
  - `generate_video_from_text()`: Main orchestration function
  - Coordinates script generation → asset creation → video composition
  - Default implementations can be overridden via dependency injection

**Key Design**: All services accept protocol types (interfaces), enabling easy testing and swapping.

---

## Data Flow

1. **Input**: Text string (via CLI, Click CLI, or API)
2. **Script Generation**: `ScriptGenerator` uses `LLMProvider` → produces `VideoScript`
3. **Asset Generation**: `AssetManager` creates audio files and background images per scene
4. **Video Composition**: `VideoComposer` combines assets → outputs MP4 file

## Entry Points

- **Click CLI**: `story-to-reel generate "text"` (recommended, via `app/cli.py`)
- **Legacy CLI**: `python main.py "text" output.mp4` (for compatibility)
- **API**: `uvicorn app.api.main:app` (FastAPI server)
- **Programmatic**: `generate_video_from_text()` function in `app/services/video_generator.py`

## Extension Points

- **New LLM Provider**: Implement `LLMProvider` protocol in `/app/services/`
- **New Asset Source**: Implement `AssetManager` protocol (e.g., image/video inputs)
- **New Composer**: Implement `VideoComposer` protocol (e.g., different video library)
- **New Input Types**: Extend `ScriptGenerator` to accept images/videos, add parsing logic

## Configuration

All configuration via environment variables (see `.env.example`):
- `OPENAI_API_KEY`: For OpenAI LLM provider
- `DEFAULT_FONT_PATH`: Custom font (optional, auto-detected)
- Output directories configured in `Settings` class

## Testing Strategy

Tests in `/tests/` mirror `/app/` structure:
- Unit tests for each service with mocked dependencies
- Integration tests for end-to-end video generation
- Protocol conformance tests for implementations

