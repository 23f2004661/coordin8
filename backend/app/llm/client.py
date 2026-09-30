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

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = 2048,
        json_mode: bool = False,
    ) -> str:
        """Execute a direct chat completion with OpenAI-compatible endpoint."""
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        try:
            with httpx.Client(timeout=90.0) as client:
                res = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            logger.error("LLM chat completion call failed: %s", exc)
            raise exc

