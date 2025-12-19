# src/spelling/en/candidate_generator.py
from __future__ import annotations

from pathlib import Path
from typing import List

from symspellpy import SymSpell, Verbosity


class EnglishCandidateGenerator:
    def __init__(
        self,
        dictionary_path: Path,
        max_edit_distance: int = 2,
        prefix_length: int = 7,
    ):
        self.symspell = SymSpell(
            max_dictionary_edit_distance=max_edit_distance,
            prefix_length=prefix_length,
        )

        if not dictionary_path.exists():
            raise FileNotFoundError(dictionary_path)

        # term<TAB>frequency
        self.symspell.load_dictionary(
            str(dictionary_path),
            term_index=0,
            count_index=1,
        )

    def generate(self, word: str) -> List[str]:
        suggestions = self.symspell.lookup(
            word,
            Verbosity.CLOSEST,
            max_edit_distance=2,
        )
        return [s.term for s in suggestions]
