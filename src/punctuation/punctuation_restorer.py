import re
from transformers import pipeline

class PunctuationRestorer:
    def __init__(self, morphology):
        # Kaynak tasarrufu için Zemberek nesnesini dışarıdan alıyoruz
        self.morphology = morphology
        print("YTU Cosmos BERT modeli yükleniyor...")
        self.model_id = "ytu-ce-cosmos/turkish-base-bert-punctuation-correction"
        self.nlp = pipeline("token-classification", model=self.model_id)

    def _apply_smart_capitalization(self, text):
        words = text.split()
        fixed_words = []
        org_suffixes = ["cumhuriyeti", "üniversitesi", "fakültesi", "başkanlığı", "müdürlüğü", "mahallesi", "vakfı"]

        for i, word in enumerate(words):
            clean_word = word.strip(".,!?\"' ")
            if not clean_word:
                fixed_words.append(word)
                continue
                
            results = self.morphology.analyze(clean_word)
            
            is_proper = False
            stem = clean_word
            for res in results:
                res_str = str(res)
                if "ProperNoun" in res_str or "Prop" in res_str:
                    is_proper = True
                    stem = res.get_stem()
                    break
            
            # --- TÜRKİYE HATASI İÇİN ÖZEL KONTROL ---
            if stem.lower() == "türki" and clean_word.lower() == "türkiye":
                stem = "türkiye"

            if is_proper:
                if len(clean_word) > len(stem):
                    suffix = clean_word[len(stem):]
                    fixed_word = stem.capitalize() + "'" + suffix
                else:
                    fixed_word = clean_word.capitalize()
                
                punc_at_end = word[len(clean_word):]
                fixed_words.append(fixed_word + punc_at_end)
                
            elif i > 0 and fixed_words[i-1][0].isupper() and clean_word.lower() in org_suffixes:
                fixed_word = word[0].upper() + word[1:]
                fixed_words.append(fixed_word)
            else:
                fixed_words.append(word)
                
        return " ".join(fixed_words)

    def restore(self, text):
        # 1. BERT Tahmini
        model_output = self.nlp(text)
        
        # 2. BERT Token Birleştirme
        restored_text = ""
        for res in model_output:
            word = res['word']
            label = res['entity']
            if word.startswith("##"):
                restored_text += word.replace("##", "")
            else:
                if restored_text != "": restored_text += " "
                restored_text += word
            if label != "non": restored_text += label
        
        # 3. Temel Temizlik
        restored_text = restored_text.replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")
        
        # 4. Akıllı Harf Büyütme ve Kesme İşareti
        restored_text = self._apply_smart_capitalization(restored_text)
        
        # 5. Cümle Başı ve Noktalama Sonrası Büyütme
        if len(restored_text) > 0:
            restored_text = restored_text[0].upper() + restored_text[1:]
        restored_text = re.sub(r'([.!?]\s+)([a-zçğıöşü])', lambda m: m.group(1) + m.group(2).upper(), restored_text)
        
        return restored_text