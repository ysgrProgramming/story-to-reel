"""Abstract interface for LLM providers."""

from abc import abstractmethod
from typing import Protocol


class LLMProvider(Protocol):
    """Protocol defining the interface for LLM providers."""

    @abstractmethod
    def generate_script_content(self, input_text: str) -> str:
        """
        Generate video script content from input text.

        Args:
            input_text: Raw input text to transform into script

        Returns:
            Generated script content as string

        Raises:
            Exception: If generation fails
        """
        ...

