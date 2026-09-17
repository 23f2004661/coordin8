"""Security utilities for Coordin8.

Addresses Section 23 of ProjectDetails.md:
- Treating retrieved content as untrusted data
- Prompt injection protection
- Safe sanitization of system prompt boundaries
"""

import html
import re

# Known patterns often used in indirect prompt injection attacks
SUSPICIOUS_PROMPT_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?prior\s+context", re.IGNORECASE),
    re.compile(r"system\s*:\s*you\s+are\s+now", re.IGNORECASE),
    re.compile(r"reveal\s+(the\s+)?secret(s)?", re.IGNORECASE),
    re.compile(r"<\|im_start\|>", re.IGNORECASE),
    re.compile(r"<\|im_end\|>", re.IGNORECASE),
]


def sanitize_untrusted_text(text: str) -> str:
    """Sanitize retrieved text to prevent prompt injection or escape sequences.

    Retrieved document text is untrusted data. We escape control tags and
    delimit context boundaries clearly.
    """
    if not text:
        return ""
    # Strip null bytes and non-printable control characters (except newline, tab, carriage return)
    cleaned = "".join(ch for ch in text if ch in "\n\r\t" or (ord(ch) >= 32 and ord(ch) != 127))
    # Replace dangerous model delimiter tokens
    cleaned = cleaned.replace("<|im_start|>", "[TAG_START]").replace("<|im_end|>", "[TAG_END]")
    cleaned = cleaned.replace("```system", "```escaped_system")
    return cleaned


def detect_suspicious_injection(text: str) -> list[str]:
    """Scan text for high-risk prompt injection phrases.

    Returns a list of detected pattern descriptions for audit logging.
    """
    matches = []
    for pattern in SUSPICIOUS_PROMPT_PATTERNS:
        if pattern.search(text):
            matches.append(pattern.pattern)
    return matches
