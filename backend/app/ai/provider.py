from abc import ABC, abstractmethod
from typing import TypeVar, Type, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class AIProviderError(Exception):
    """Base exception for AI provider errors"""
    pass

class AIProviderNotConfiguredError(AIProviderError):
    """Raised when the AI provider credentials or settings are not configured"""
    pass

class AIProvider(ABC):
    """
    Abstract AI Provider interface for IncidentZero.
    Decouples agent reasoning from the underlying LLM infrastructure.
    """

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the provider has valid credentials configured."""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Returns the configured model identifier."""
        pass

    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_class: Type[T],
        temperature: float = 0.2
    ) -> T:
        """
        Submits prompt to LLM and returns structured validated Pydantic model.
        Raises AIProviderNotConfiguredError if unconfigured.
        """
        pass
