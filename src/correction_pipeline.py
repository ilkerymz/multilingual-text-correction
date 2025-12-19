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

class TextCorrectionPipeline:
    def __init__(self):
        print("🚀 Tüm modeller yükleniyor, lütfen bekleyin...")
        
        # 1. Dil Tespiti
        self.detector = HybridDetector(model_path="models/distilbert_langdet")
        
        # 2. Yazım Denetimi (Zemberek)
        self.speller = SmartCorrector()
        
        # 3. Gramer Modeli
        self.grammar = GrammarCorrector()
        
        # 4. Noktalama Modeli (Zemberek nesnesini paylaşıyoruz)
        self.punc_restorer = PunctuationRestorer(morphology=self.speller.morphology)
        
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
        
        if lang != "tr":
            return None, lang, "Şu an sadece Türkçe desteklenmektedir."

        # B. TÜRKÇE DÜZELTME ZİNCİRİ
        # 1. Yazım Denetimi
        steps["spelling"] = self.speller.correct(text)
        
        # 2. Gramer Düzeltme
        steps["grammar"] = self.grammar.correct(steps["spelling"])
        
        # 3. Noktalama ve Büyük Harf
        steps["final"] = self.punc_restorer.restore(steps["grammar"])
        
        return steps, "tr", None