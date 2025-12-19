# src/spelling/base.py
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")  # don't, I'm, you're
_SHORT_WORDS = {
    "am",
    "an",
    "as",
    "at",
    "be",
    "by",
    "do",
    "go",
    "he",
    "if",
    "in",
    "is",
    "it",
    "me",
    "my",
    "no",
    "of",
    "on",
    "or",
    "so",
    "to",
    "up",
    "us",
    "we",
}


@dataclass(frozen=True)
class Token:
    text: str
    start: int
    end: int


def tokenize_words(text: str) -> List[Token]:
    """Extract word tokens with offsets. Keeps punctuation outside."""
    return [Token(m.group(0), m.start(), m.end()) for m in _WORD_RE.finditer(text)]


def should_skip_token(token: str) -> bool:
    """Skip tokens we should not spell-check."""
    if not token:
        return True

    # all caps acronyms (NASA, USA)
    if token.isupper() and len(token) >= 2:
        return True

    # very short tokens tend to be noisy (a, I) unless explicitly allowed
    if len(token) <= 2 and token.lower() not in _SHORT_WORDS:
        return True

    return False


def normalize_en(token: str) -> str:
    """Normalize English token for dictionary lookup."""
    return token.lower()
