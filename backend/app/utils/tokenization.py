"""Tokenization utilities for Coordin8.

Provides fast token estimation and context length bounds.
"""


def estimate_token_count(text: str) -> int:
    """Estimate token count based on average word-to-token ratio (~4 chars per token)."""
    if not text:
        return 0
    # Standard rule of thumb: ~4 characters per token in English text
    return max(1, len(text) // 4)


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    """Truncate text to approximate token limit."""
    max_chars = max_tokens * 4
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."
