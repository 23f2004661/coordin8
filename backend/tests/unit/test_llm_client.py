"""LLM client failure behavior tests."""

import httpx
import pytest

from app.llm.client import LLMClient


def test_unreachable_llm_does_not_return_a_fallback_answer(monkeypatch):
    class UnreachableClient:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def post(self, *_args, **_kwargs):
            raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.llm.client.httpx.Client", lambda **_kwargs: UnreachableClient())
    client = LLMClient(base_url="http://127.0.0.1:1234/v1", model="test-model")

    with pytest.raises(RuntimeError, match="AI service is currently unavailable"):
        client.generate_answer("question", "project evidence")