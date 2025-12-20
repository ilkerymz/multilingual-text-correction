import os
import sys

# Proje kök dizinini yola ekle
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.language_detection.hybrid_detector import HybridDetector
from src.spelling.TR.spell_checker import SmartCorrector
from src.grammar.grammar_corrector import GrammarCorrector
from src.punctuation.punctuation_restorer import PunctuationRestorer
from src.english_correction_pipeline import EnglishCorrectionPipeline

class TextCorrectionPipeline:
    def __init__(self):
        print("🚀 Tüm modeller yükleniyor, lütfen bekleyin...")
        
        # 1. Dil Tespiti
        self.detector = HybridDetector(model_path="models/distilbert_langdet")
        
        # 2. Türkçe yazım ve sonrası için bileşenler
        self.speller = SmartCorrector()
        self.grammar = GrammarCorrector(device="cpu")
        self.punc_restorer = PunctuationRestorer(morphology=self.speller.morphology)

        # 3. İngilizce pipeline (SymSpell + T5)
        self.english_pipeline = EnglishCorrectionPipeline()
        
        print("✅ Sistem başarıyla hazırlandı!")

    def process(self, text):
        if not text.strip():
            return None, "unknown", "Metin boş olamaz."

        # Ara sonuçları tutacak sözlük
        steps = {
            "raw": text,
            "spelling": None,
            "grammar": None,
            "final": None
        }

        # A. DİL TESPİTİ
        lang = self.detector.detect(text)
        
        if lang == "tr":
            # B. TÜRKÇE DÜZELTME ZİNCİRİ
            steps["spelling"] = self.speller.correct(text)
            steps["grammar"] = self.grammar.correct(steps["spelling"])
            steps["final"] = self.punc_restorer.restore(steps["grammar"])
            return steps, "tr", None

        if lang == "en":
            # C. İNGİLİZCE DÜZELTME ZİNCİRİ
            steps["spelling"] = self.english_pipeline.spelling_corrector.correct(text)
            steps["grammar"] = self.english_pipeline.grammar_corrector.correct(steps["spelling"])
            steps["final"] = steps["grammar"]  # Şimdilik noktalama/restorasyon yok
            return steps, "en", None

        return None, lang, "Bu dil şu anda desteklenmiyor."
