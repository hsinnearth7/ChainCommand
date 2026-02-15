"""Abstract base class for agent tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
    """Every tool an agent can call implements this interface."""

    name: str = ""
    description: str = ""

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Run the tool and return a result dict."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
