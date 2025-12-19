from pathlib import Path
from src.spelling.en.dictionary import EnglishDictionary
from src.spelling.en.candidate_generator import EnglishCandidateGenerator
from src.spelling.en.context_ranker import BertContextRanker
from src.spelling.en.english_spell_corrector import EnglishSpellCorrector

dict_ = EnglishDictionary(words_path=Path("src/data/en_words.txt"))
cand_gen = EnglishCandidateGenerator(dictionary_path=Path("src/data/en_symspell.txt"))
ranker = BertContextRanker()

sc = EnglishSpellCorrector(dict_, cand_gen, ranker)

print(sc.correct("I went to the see yesterday."))
print(sc.correct("They left their bags over there."))
print(sc.correct("I want to go too."))
