from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import os

class MbertLanguageClassifier:
    def __init__(self, model_path=None):

        # Proje kökünü bul (src/language_detection/ → src/ → project_root/)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Eğitilmiş model klasörü
        default_model_path = os.path.join(project_root, "models", "distilbert_langdet")

        # Eğer dışarıdan model_path verilmemişse default’u kullan
        if model_path is None:
            model_path = default_model_path

        print("🔍 Yüklenen Model Path:", model_path)

        # Model ve tokenizer yükle
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            num_labels=2
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def predict(self, text: str):
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            outputs = self.model(**tokens)
            logits = outputs.logits
            pred = torch.argmax(logits, dim=1).item()

        return "tr" if pred == 0 else "en"
