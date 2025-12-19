# src/spelling/en/dictionary.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set


@dataclass
class EnglishDictionary:
    words_path: Path

    _words: Optional[Set[str]] = None

    def load(self) -> None:
        if not self.words_path.exists():
            raise FileNotFoundError(f"Word list not found: {self.words_path}")

        words: Set[str] = set()
        for line in self.words_path.read_text(encoding="utf-8").splitlines():
            w = line.strip().lower()
            if w and w.isalpha():
                words.add(w)

        self._words = words

    def is_valid(self, word: str) -> bool:
        if self._words is None:
            raise RuntimeError("Dictionary not loaded. Call load() first.")
        return word.lower() in self._words
