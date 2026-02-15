"""Factory function to create the configured LLM backend."""

from __future__ import annotations

from ..config import LLMMode, settings
from .base import BaseLLM


def create_llm() -> BaseLLM:
    """Instantiate the LLM backend based on ``settings.llm_mode``."""
    if settings.llm_mode == LLMMode.OPENAI:
        from .openai_llm import OpenAILLM
        return OpenAILLM()

    if settings.llm_mode == LLMMode.OLLAMA:
        from .ollama_llm import OllamaLLM
        return OllamaLLM()

    # Default: mock
    from .mock_llm import MockLLM
    return MockLLM()
