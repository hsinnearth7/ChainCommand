"""OpenAI LLM backend."""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

from ..config import settings
from ..utils.logging_config import get_logger
from .base import BaseLLM

T = TypeVar("T", bound=BaseModel)
log = get_logger(__name__)


class OpenAILLM(BaseLLM):
    """Async OpenAI client with JSON mode support."""

    def __init__(self) -> None:
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:
            raise ImportError(
                "openai package required: pip install openai"
            ) from exc

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
        )
        text = resp.choices[0].message.content or ""
        log.debug("openai_generate", tokens=resp.usage.total_tokens if resp.usage else 0)
        return text

    async def generate_json(
        self,
        prompt: str,
        schema: type[T],
        system: str = "",
        temperature: float = 0.1,
    ) -> T:
        schema_json = json.dumps(schema.model_json_schema(), indent=2)
        full_prompt = (
            f"{prompt}\n\n"
            f"Respond ONLY with valid JSON matching this schema:\n{schema_json}"
        )
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": full_prompt})

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        text = resp.choices[0].message.content or "{}"
        log.debug("openai_generate_json", tokens=resp.usage.total_tokens if resp.usage else 0)
        return schema.model_validate_json(text)
