from __future__ import annotations

from pathlib import Path
from typing import Optional

from src.spelling.en.dictionary import EnglishDictionary
from src.spelling.en.candidate_generator import EnglishCandidateGenerator
from src.spelling.en.context_ranker import BertContextRanker
from src.spelling.en.english_spell_corrector import EnglishSpellCorrector
from src.grammar.en.t5_corrector import T5GrammarCorrector, T5GrammarCorrectorConfig


class EnglishCorrectionPipeline:
    """
    Two-stage pipeline: SymSpell-based spelling fix followed by T5 grammar correction.
    """

    def __init__(
        self,
        dictionary_path: Path = Path("src/data/en_words.txt"),
        symspell_path: Path = Path("src/data/en_symspell.txt"),
        grammar_config: Optional[T5GrammarCorrectorConfig] = None,
    ):
        dictionary = EnglishDictionary(words_path=dictionary_path)
        candidate_generator = EnglishCandidateGenerator(dictionary_path=symspell_path)
        ranker = BertContextRanker()

        self.spelling_corrector = EnglishSpellCorrector(
            dictionary=dictionary,
            candidate_generator=candidate_generator,
            context_ranker=ranker,
        )
        self.grammar_corrector = T5GrammarCorrector(grammar_config)

    def correct(self, text: str) -> str:
        spelling_fixed = self.spelling_corrector.correct(text)
        grammar_fixed = self.grammar_corrector.correct(spelling_fixed)
        return grammar_fixed
