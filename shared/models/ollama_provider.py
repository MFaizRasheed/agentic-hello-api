import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.config import get_settings

from functools import lru_cache

from openai import AsyncOpenAI
from agents import OpenAIChatCompletionsModel, set_tracing_disabled


settings = get_settings()
set_tracing_disabled(True)

@lru_cache
def get_client() -> AsyncOpenAI:
    client = AsyncOpenAI(base_url=settings.ollama_base_url, api_key="ollama")
    return client


def get_model(model_name: str | None = None) -> OpenAIChatCompletionsModel:
    """Get an Ollama-backed model for the OpenAI Agents SDK."""
    local_model = OpenAIChatCompletionsModel(
        model=model_name or settings.ollama_model,
        openai_client=get_client(),
    )
    return local_model
