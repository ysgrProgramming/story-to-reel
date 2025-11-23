# Module Quick Reference

Quick reference for LLM-assisted development. See ARCHITECTURE.md for detailed descriptions.

## Module Map

```
app/
├── api/          → FastAPI HTTP endpoints (POST /generate, GET /video)
├── core/         → Config (Settings, FontManager) - environment vars, font detection
├── interfaces/   → Protocols (LLMProvider, AssetManager, VideoComposer) - extensibility points
├── models/       → Pydantic (Scene, VideoScript) - data structures
└── services/     → Implementations (LLM providers, AssetManager, VideoComposer, orchestrator)
```

## Key Files

### Entry Points
- `main.py` - CLI entry point (`python main.py "text" output.mp4`)
- `app/api/main.py` - FastAPI app (`uvicorn app.api.main:app`)
- `app/services/video_generator.py` - Main orchestration function

### Core Logic
- `app/services/script_generator.py` - Text → VideoScript conversion
- `app/services/asset_manager.py` - Audio/image generation
- `app/services/video_composer.py` - Video rendering (MoviePy)

### Configuration
- `app/core/config.py` - Settings from .env
- `pyproject.toml` - Project metadata, dependencies (uv/pip)

## Common Tasks

### Add New LLM Provider
1. Implement `LLMProvider` protocol in `app/services/`
2. Add to `ScriptGenerator` initialization options

### Add New Asset Source
1. Implement `AssetManager` protocol
2. Pass to `generate_video_from_text(asset_manager=...)`

### Change Video Rendering
1. Implement `VideoComposer` protocol
2. Pass to `generate_video_from_text(video_composer=...)`

### Add API Endpoint
1. Add route in `app/api/endpoints.py`
2. Import router in `app/api/main.py`

## Testing

- `tests/test_models.py` - Pydantic model validation
- `tests/test_llm_provider.py` - LLM provider implementations
- `tests/test_script_generator.py` - Script generation logic
- `tests/test_asset_manager.py` - Asset generation (mocked)
- `tests/test_video_generator.py` - Integration tests
- `tests/test_config.py` - Configuration management

Run: `pytest` or `pytest tests/test_models.py`

