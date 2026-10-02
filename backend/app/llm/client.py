"""LLM client for OpenAI-compatible endpoints (LM Studio, vLLM, OpenAI)."""

import json
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
                message = response.json()["choices"][0]["message"]
        except Exception as exc:
            logger.warning("LLM completion to %s failed: %s", self.base_url, exc)
            raise RuntimeError("AI service is currently unavailable. Please try again.") from exc

        content = message.get("content")
        if message.get("tool_calls") or message.get("function_call"):
            raise RuntimeError("AI service returned a function call. Check LM Studio's prompt template.")
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("AI service returned no text content.")
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, dict) and "name" in parsed and "parameters" in parsed:
            raise RuntimeError("AI service returned a function call. Check LM Studio's prompt template.")
        return content

    def generate_answer(self, query: str, context_text: str) -> str:
        """Call LLM completion with system prompt and formatted context."""
        prompt = build_rag_prompt(query, context_text)
        return self.generate_completion(RAG_SYSTEM_PROMPT, prompt)
