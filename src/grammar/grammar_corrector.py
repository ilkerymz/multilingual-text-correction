import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class GrammarCorrector:
    def __init__(self, model_path="./models/grammar_model/Büyük_ama_Etkili_Model", device=None):
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"📂 Gramer modeli yükleniyor ({self.device})...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(self.device)
        self.model.eval()

    def correct(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", max_length=128, truncation=True).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=128,
                num_beams=5,
                repetition_penalty=1.2,
                early_stopping=True
            )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
