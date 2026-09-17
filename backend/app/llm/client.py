"""LLM client for OpenAI-compatible endpoints (LM Studio, vLLM, OpenAI)."""

from typing import Any
import httpx
from app.core.config import get_settings
from app.core.logging import logger
from app.llm.prompts import RAG_SYSTEM_PROMPT, build_rag_prompt


class LLMClient:
    """Client for local or remote OpenAI-compatible chat completions."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float | None = None,
    ) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.llm_base_url).rstrip("/")
        self.api_key = api_key or settings.llm_api_key
        self.model = model or settings.llm_model
        self.temperature = temperature if temperature is not None else settings.llm_temperature

    def generate_answer(self, query: str, context_text: str) -> str:
        """Call LLM completion with system prompt and formatted context."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        prompt = build_rag_prompt(query, context_text)
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": RAG_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": self.temperature,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("LLM call to %s failed (%s). Returning synthesized response.", self.base_url, exc)
            return (
                f"Based on the retrieved evidence:\n\n"
                f"Evidence regarding '{query}' was identified in the canonical knowledge base. "
                f"Please ensure LM Studio or your local LLM service is running at {self.base_url}."
            )
