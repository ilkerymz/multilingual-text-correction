import sys
import os

# Yolları ekle (Modüllerin bulunması için)
sys.path.append(os.path.join(os.path.dirname(__file__), 'spelling'))

from transformers import MBart50TokenizerFast, MBartForConditionalGeneration
from spelling.spell_checker import SpellingCorrector
import torch

class TextCorrectionPipeline:
    def __init__(self, model_path):
        print("🚀 Düzeltme Motoru Başlatılıyor...")
        
        # 1. Spelling Modülünü Yükle
        print("📦 Spelling (Yazım) Modülü yükleniyor...")
        self.spelling_corrector = SpellingCorrector()
        
        # 2. Grammar Modelini Yükle
        print(f"🧠 Grammar (Dilbilgisi) Modeli yükleniyor: {model_path}...")
        try:
            # GPU varsa kullan, yoksa CPU
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"🔥 Çalışma Modu: {self.device.upper()}")

            self.tokenizer = MBart50TokenizerFast.from_pretrained(model_path, src_lang="tr_TR", tgt_lang="tr_TR")
            self.model = MBartForConditionalGeneration.from_pretrained(model_path).to(self.device)
            print("✅ Grammar Modeli hazır!")
        except Exception as e:
            print(f"❌ HATA: Model yüklenemedi. {e}")
            exit()

    def correct(self, text):
        """
        Metni alır, önce Spelling'den geçirir, sonra Grammar modeline sokar.
        """
        # Adım 1: Spelling Düzeltmesi (Ön Temizlik)
        spelling_fixed = self.spelling_corrector.correct_text(text)
        
        # Adım 2: Grammar Düzeltmesi (Derin Temizlik)
        inputs = self.tokenizer(spelling_fixed, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                forced_bos_token_id=self.tokenizer.lang_code_to_id["tr_TR"],
                max_length=128,
                num_beams=5, # Akıllı arama
                early_stopping=True
            )
            
        grammar_fixed = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return grammar_fixed

if __name__ == "__main__":
    # Modelin yolunu buraya yaz (Drive'dan indirdiğin klasör)
    # Eğer klasör adı farklıysa burayı düzelt
    MODEL_DIR = "models/grammar_model/Büyük_ama_Etkili_Model" 
    
    if not os.path.exists(MODEL_DIR):
        print(f"⚠️ UYARI: '{MODEL_DIR}' klasörü bulunamadı. Lütfen model yolunu kontrol edin.")
    else:
        pipeline = TextCorrectionPipeline(MODEL_DIR)
        
        # Test Cümleleri
        test_inputs = [
            "Bugn hva cok guzel",           # Spelling + Grammar hatası
            "Herkez burda mı",              # Klasik yazım yanlışı
            "Bende gelmek istyorum",        # -de/-da ve harf hatası
            "Kitab okumayi sevyorum",       # Yumuşama ve harf hatası
            "Bende sizinle gelmk istiyorm", 
            "Mrhb, nerey gittin"
        ]
        
        print("\n" + "="*50)
        print("   TÜRKÇE METİN DÜZELTME TESTİ (FINAL)   ")
        print("="*50 + "\n")

        for text in test_inputs:
            result = pipeline.correct(text)
            print(f"🔴 Girdi:  {text}")
            print(f"🟢 Sonuç:  {result}")
            print("-" * 30)