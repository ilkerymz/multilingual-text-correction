# src/spelling/en/english_spell_corrector.py
from __future__ import annotations
from typing import Optional

from ..base import normalize_en, should_skip_token, tokenize_words
from .dictionary import EnglishDictionary
from .candidate_generator import EnglishCandidateGenerator
from .context_ranker import BertContextRanker
from .confusions import CONFUSIONS


class EnglishSpellCorrector:
    def __init__(
        self,
        dictionary: EnglishDictionary,
        candidate_generator: EnglishCandidateGenerator,
        context_ranker: Optional[BertContextRanker] = None,
    ):
        self.dictionary = dictionary
        self.dictionary.load()
        self.candidate_generator = candidate_generator
        self.context_ranker = context_ranker

    def correct(self, text: str) -> str:
        tokens = tokenize_words(text)
        norm_tokens = [normalize_en(t.text) for t in tokens]

        # 🔥 start from ORIGINAL surface forms
        corrected = [t.text for t in tokens]

        for i, tok in enumerate(tokens):
            raw = tok.text
            if should_skip_token(raw):
                continue

            w = norm_tokens[i]

            # Case 1: true spelling error
            if not self.dictionary.is_valid(w):
                candidates = self.candidate_generator.generate(w)
                if not candidates:
                    continue

                best = candidates[0]
                if self.context_ranker and len(candidates) > 1:
                    best = self.context_ranker.rank(norm_tokens, i, candidates)

                corrected[i] = best
                continue

            # Case 2: SAFE confusion set only
            if w in CONFUSIONS and self.context_ranker:
                candidates = CONFUSIONS[w]
                best = self.context_ranker.rank(norm_tokens, i, candidates)

                # 🔐 only replace if actually different
                if best != w:
                    corrected[i] = best

        # Safe reconstruction
        out = []
        last = 0
        for tok, word in zip(tokens, corrected):
            out.append(text[last:tok.start])
            out.append(word)
            last = tok.end
        out.append(text[last:])
        return "".join(out)
