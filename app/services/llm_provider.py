"""LLM provider implementations."""

import json
import os

from app.core.config import get_settings

# Lazy import for langchain (only needed when OpenAILLMProvider is used)
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Fallback for older langchain versions
    try:
        from langchain.prompts import ChatPromptTemplate  # type: ignore
        from langchain_openai import ChatOpenAI  # type: ignore
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        LANGCHAIN_AVAILABLE = False
        ChatPromptTemplate = None  # type: ignore
        ChatOpenAI = None  # type: ignore


class MockLLMProvider:
    """Mock LLM provider for testing without API calls."""

    def generate_script_content(self, input_text: str) -> str:
        """
        Generate mock script content from input text.

        Args:
            input_text: Raw input text

        Returns:
            JSON string containing mock video script structure
        """
        # Simple mock implementation: split input into scenes
        sentences = [
            s.strip()
            for s in input_text.replace(".", ".\n")
            .replace("。", "。\n")
            .split("\n")
            if s.strip()
        ]

        scenes = []
        for idx, sentence in enumerate(sentences[:5], 1):  # Limit to 5 scenes
            if not sentence:
                continue
            scene = {
                "scene_number": idx,
                "dialogue": sentence,
                "display_text": sentence,
                "duration_seconds": max(2.0, len(sentence) * 0.1),
                "background_color": f"#{idx * 30 % 255:02x}{idx * 50 % 255:02x}{idx * 70 % 255:02x}",
            }
            scenes.append(scene)

        script_data = {
            "title": sentences[0][:30] if sentences else "Generated Video",
            "scenes": scenes,
            "total_duration_seconds": sum(s["duration_seconds"] for s in scenes),
        }

        return json.dumps(script_data, ensure_ascii=False, indent=2)


class OpenAILLMProvider:
    """OpenAI-based LLM provider using LangChain."""

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.7):
        """
        Initialize OpenAI LLM provider.

        Args:
            model_name: OpenAI model name (default: "gpt-4")
            temperature: Sampling temperature (default: 0.7)

        Raises:
            ImportError: If langchain packages are not installed
            ValueError: If API key is not found
        """
        if not LANGCHAIN_AVAILABLE or ChatOpenAI is None or ChatPromptTemplate is None:
            raise ImportError(
                "langchain packages are required for OpenAILLMProvider. "
                "Install with: pip install langchain langchain-openai"
            )

        settings = get_settings()
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables or settings"
            )

        self.llm = ChatOpenAI(model=model_name, temperature=temperature, api_key=api_key)
        self.prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a video script generator. Generate a JSON structure for a video script based on the input text.

The output must be valid JSON with this structure:
{{
  "title": "Video title",
  "scenes": [
    {{
      "scene_number": 1,
      "dialogue": "Text to speak",
      "display_text": "Text to display",
      "duration_seconds": 3.0,
      "background_color": "#1a1a2e"
    }}
  ],
  "total_duration_seconds": 10.0
}}

Split the input text into 3-5 scenes. Each scene should have appropriate duration based on text length.""",
                ),
                ("user", "{input_text}"),
            ]
        )

    def generate_script_content(self, input_text: str) -> str:
        """
        Generate script content using OpenAI API.

        Args:
            input_text: Raw input text

        Returns:
            JSON string containing video script structure

        Raises:
            Exception: If API call fails
        """
        chain = self.prompt_template | self.llm
        response = chain.invoke({"input_text": input_text})

        content = response.content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]

        return content.strip()

