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

    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text with caller-provided instructions using the configured chat model."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": self.temperature,
        }
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.warning("LLM completion to %s failed: %s", self.base_url, exc)
            raise RuntimeError("AI service is currently unavailable. Please try again.") from exc

    def generate_answer(self, query: str, context_text: str) -> str:
        """Call LLM completion with system prompt and formatted context."""
        prompt = build_rag_prompt(query, context_text)
        try:
            return self.generate_completion(RAG_SYSTEM_PROMPT, prompt)
        except RuntimeError as exc:
            raise RuntimeError("AI service is currently unavailable. Please try again.") from exc
