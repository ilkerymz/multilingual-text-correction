from .langdetect_wrapper import detect_lang_simple
from .mbert_classifier import MbertLanguageClassifier

class HybridDetector:
    def __init__(self, model_path=None):
        self.mbert = MbertLanguageClassifier(model_path=model_path)

    def detect(self, text: str):
        # Kelime sayısını al
        words = text.split()
        word_count = len(words)
        
        # 1) Her iki yöntemi de çalıştır
        simple_pred = detect_lang_simple(text)  # İstatistiksel
        model_pred = self.mbert.predict(text)   # Yapay Zeka (AI)

        # Debug için konsola bilgi basalım (Test bitince silebilirsin)
        # print(f"   [Analiz] Uzunluk: {word_count} | Basit: {simple_pred} | Model: {model_pred}")

        # 2) Karar Mantığı (Decision Logic)
        
        # Durum A: Model "unknown" dediyse veya basit yöntemle aynıysa
        if model_pred == "unknown" or model_pred == simple_pred:
            # Basit yöntem 'unknown' değilse onu döndür, yoksa modeli döndür
            return simple_pred if simple_pred not in ["unknown", None] else model_pred

        # Durum B: İkisi FARKLI sonuç verdiyse (Conflict Resolution)
        else:
            # Eğer metin KISA ise (15 kelimeden az) -> Yapay Zekaya (Model) güven.
            # (Örnek: "Selam", "Hi", "Bugün meeting var")
            if word_count < 15:
                # Ancak basit yöntem "unknown" ise zaten mecburen modele güveneceğiz
                return model_pred
            
            # Eğer metin UZUN ise (15 kelimeden fazla) -> İstatistiğe (Basit) güven.
            # (Örnek: Senin İngilizce Abstract içine gizlenmiş 'nasılsın' örneği)
            else:
                # İstatistik hata vermediyse ona güven, verdiyse modele dön
                if simple_pred not in ["unknown", None]:
                    return simple_pred
                else:
                    return model_pred