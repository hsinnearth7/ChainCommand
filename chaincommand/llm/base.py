"""Abstract base class for LLM backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLM(ABC):
    """All LLM backends implement this interface."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
    ) -> str:
        """Generate a free-form text completion."""

    @abstractmethod
    async def generate_json(
        self,
        prompt: str,
        schema: type[T],
        system: str = "",
        temperature: float = 0.1,
    ) -> T:
        """Generate a response and parse it into a Pydantic model."""
