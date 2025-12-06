from .langdetect_wrapper import detect_lang_simple
from .mbert_classifier import MbertLanguageClassifier

class HybridDetector:
    def __init__(self, model_path=None):
        self.mbert = MbertLanguageClassifier(model_path=model_path)

    def detect(self, text: str):
        # 1) Kısa cümlelerde langdetect
        if len(text.split()) <= 2:
            return detect_lang_simple(text)

        # 2) Model tahmini
        pred = self.mbert.predict(text)

        # 3) Model kararsızsa fallback
        if pred == "unknown":
            return detect_lang_simple(text)

        return pred
