"""Ollama local model backend."""

from __future__ import annotations

import json
from typing import TypeVar

from pydantic import BaseModel

from ..config import settings
from ..utils.logging_config import get_logger
from .base import BaseLLM

T = TypeVar("T", bound=BaseModel)
log = get_logger(__name__)


class OllamaLLM(BaseLLM):
    """Connects to a local Ollama instance via httpx."""

    def __init__(self) -> None:
        try:
            import httpx  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "httpx package required: pip install httpx"
            ) from exc

        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.ollama_model

    async def generate(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
    ) -> str:
        import httpx

        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self._base_url}/api/generate", json=payload
            )
            resp.raise_for_status()
            data = resp.json()

        text = data.get("response", "")
        log.debug("ollama_generate", model=self._model, length=len(text))
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
        raw = await self.generate(full_prompt, system=system, temperature=temperature)

        # Try to extract JSON from response
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if len(lines) > 2 else text

        return schema.model_validate_json(text)
