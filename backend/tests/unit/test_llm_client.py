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


@pytest.mark.parametrize("message", [
    {"content": '{"name":"explain","parameters":{"topic":"project manager"}}', "tool_calls": []},
    {"content": None, "tool_calls": [{"type": "function", "function": {"name": "explain"}}]},
    {"content": None, "function_call": {"name": "explain", "arguments": "{}"}},
])
def test_function_calls_are_not_presented_as_answers(monkeypatch, message):
    original_client = httpx.Client
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"choices": [{"message": message}]})
    )
    monkeypatch.setattr(
        "app.llm.client.httpx.Client",
        lambda **kwargs: original_client(transport=transport, **kwargs),
    )

    with pytest.raises(RuntimeError, match="function call.*prompt template"):
        LLMClient().generate_answer("question", "project evidence")


@pytest.mark.parametrize("content", [
    "The delivery date is 2026-10-16. [Doc doc_123]",
    '{"summary":"Reviewed milestones","decisions":[],"action_items":[]}',
])
def test_no_tools_payload_preserves_text_and_mom_json(monkeypatch, content):
    import json

    original_client = httpx.Client

    def respond(request):
        payload = json.loads(request.content)
        assert str(request.url).endswith("/v1/chat/completions")
        assert payload == {
            "model": "test-model",
            "messages": [
                {"role": "system", "content": "system instructions"},
                {"role": "user", "content": "source content"},
            ],
            "temperature": 0.1,
        }
        return httpx.Response(200, json={"choices": [{"message": {"content": content}}]})

    monkeypatch.setattr(
        "app.llm.client.httpx.Client",
        lambda **kwargs: original_client(transport=httpx.MockTransport(respond), **kwargs),
    )
    client = LLMClient(base_url="http://127.0.0.1:1234/v1", model="test-model", temperature=0.1)
    assert client.generate_completion("system instructions", "source content") == content