import re
from transformers import pipeline

class PunctuationRestorer:
    def __init__(self, morphology):
        self.morphology = morphology
        print("YTU Cosmos BERT modeli yükleniyor...")
        self.model_id = "ytu-ce-cosmos/turkish-base-bert-punctuation-correction"
        self.nlp = pipeline("token-classification", model=self.model_id)
        
        # GERÇEK ÖZEL İSİMLER - Elle kontrol edilmiş liste
        self.known_proper_nouns = {
            # Şehirler
            "ankara", "istanbul", "izmir", "bursa", "antalya", "adana", "konya",
            "gaziantep", "kayseri", "diyarbakır", "mersin", "eskişehir",
            
            # Ülkeler
            "türkiye", "almanya", "fransa", "ingiltere", "amerika", "rusya",
            "çin", "japonya", "hindistan", "brezilya", "mısır",
            
            # Kişi adları (çok yaygın olanlar)
            "ahmet", "mehmet", "mustafa", "ali", "hasan", "hüseyin",
            "ayşe", "fatma", "emine", "hatice", "zeynep",
            
            # Kurumlar
            "microsoft", "google", "apple", "amazon", "facebook",
        }
        
        # ASLA ÖZEL İSİM OLMAYAN KELİMELER
        self.never_proper_nouns = {
            "nlp", "doğal", "dil", "işleme", "bilgisayar", "bilgisayarlar",
            "bilgisayarların", "insan", "insanın", "teknoloji", "günümüz",
            "günümüzde", "yapay", "zeka", "model", "modeli", "modeller",
            "modelleri", "metin", "metinler", "metinleri", "analiz",
            "bazı", "zorluk", "zorluklar", "özellikle", "türkçe",
            "gibi", "sondan", "eklemeli", "dil", "diller", "dillerde",
            "kelime", "kelimeleri", "yapı", "yapısı", "karmaşık",
            "için", "daha", "zor", "bu", "yüzden", "veri", "set",
            "setler", "setleri", "setlerinin", "düzgün", "ve", "eğitim",
            "eğitiminin", "doğru", "ayrıca", "makine", "öğrenme",
            "öğrenmesi", "algoritma", "algoritmalar", "algoritmaları",
            "her", "zaman", "bağlam", "bağlamı", "tam", "olarak",
            "ama", "fakat", "ancak", "çünkü", "eğer", "ise", "ile",
            "veya", "ya", "hem", "de", "da", "ki",
        }
        
        # KURUM SONEK KELİMELERİ
        self.org_suffixes = {
            "cumhuriyeti", "üniversitesi", "fakültesi", "başkanlığı",
            "müdürlüğü", "mahallesi", "vakfı", "derneği", "kulübü",
        }
        
        # KESME İŞARETİ GEREKTİREN GERÇEK EKLER
        self.apostrophe_suffixes = {
            "da", "de", "dan", "den", "ta", "te", "tan", "ten",
            "ya", "ye", "a", "e",
            "nın", "nin", "nun", "nün", "ın", "in", "un", "ün",
            "dır", "dir", "dur", "dür", "tır", "tir", "tur", "tür",
        }

    def _is_really_proper_noun(self, word):
        """Kelimenin gerçekten özel isim olup olmadığını akıllıca kontrol et"""
        word_lower = word.lower()
        clean_word = word.strip(".,!?\"'")
        
        # 1. Kesinlikle özel isim DEĞİL
        if word_lower in self.never_proper_nouns:
            return False, None
        
        # 2. Bilinen özel isimler listesinde mi?
        if word_lower in self.known_proper_nouns:
            return True, word_lower.capitalize()
        
        # 3. Kurum soneki var mı? (örn: "Ankara Üniversitesi")
        if word_lower in self.org_suffixes:
            return False, None
        
        # 4. Zemberek'e sor (ama dikkatli!)
        try:
            results = self.morphology.analyze(clean_word.lower())
            
            for res in results:
                res_str = str(res)
                
                # Özel isim işareti var mı?
                if "ProperNoun" in res_str or "Prop" in res_str:
                    stem = res.get_stem()
                    
                    # Zemberek'in hatalı tespitlerini filtrele
                    stem_lower = stem.lower()
                    
                    # Yaygın kelimeler özel isim değildir
                    if stem_lower in self.never_proper_nouns:
                        return False, None
                    
                    # Kök kelime çok kısaysa (1-2 harf) şüpheli
                    if len(stem_lower) <= 2:
                        return False, None
                    
                    # Kabul et
                    return True, stem.capitalize()
            
            return False, None
            
        except Exception as e:
            return False, None

    def _needs_apostrophe(self, stem, full_word):
        """Kesme işareti gerekip gerekmediğini kontrol et"""
        if len(full_word) <= len(stem):
            return False
        
        suffix = full_word[len(stem):].lower()
        
        # Ek, kesme işareti gerektiren listede mi?
        return suffix in self.apostrophe_suffixes

    def _apply_smart_capitalization(self, text):
        """Akıllı büyük harf ve kesme işareti uygula"""
        words = text.split()
        fixed_words = []
        prev_was_proper = False

        for i, word in enumerate(words):
            # Noktalama işaretlerini ayır
            clean_word = word.strip(".,!?\"' ")
            trailing_punct = word[len(clean_word):] if len(word) > len(clean_word) else ""
            
            if not clean_word:
                fixed_words.append(word)
                continue
            
            # Cümle başı mı?
            is_sentence_start = (i == 0 or 
                                (i > 0 and any(p in fixed_words[i-1] for p in ['.', '!', '?'])))
            
            # Özel isim kontrolü
            is_proper, stem = self._is_really_proper_noun(clean_word)
            
            if is_proper and stem:
                # Kesme işareti gerekiyor mu?
                if self._needs_apostrophe(stem, clean_word):
                    suffix = clean_word[len(stem):]
                    fixed_word = stem + "'" + suffix.lower()
                else:
                    # Ek varsa olduğu gibi ekle (kesme işareti yok)
                    if len(clean_word) > len(stem):
                        suffix = clean_word[len(stem):]
                        fixed_word = stem + suffix.lower()
                    else:
                        fixed_word = stem
                
                fixed_words.append(fixed_word + trailing_punct)
                prev_was_proper = True
                
            elif prev_was_proper and clean_word.lower() in self.org_suffixes:
                # Önceki kelime özel isimse ve bu kurum sonekiyse büyüt
                fixed_word = clean_word.capitalize()
                fixed_words.append(fixed_word + trailing_punct)
                prev_was_proper = False
                
            elif is_sentence_start:
                # Cümle başıysa büyüt
                fixed_word = clean_word[0].upper() + clean_word[1:] if len(clean_word) > 1 else clean_word.upper()
                fixed_words.append(fixed_word + trailing_punct)
                prev_was_proper = False
                
            else:
                # Normal kelime - küçük harf
                fixed_words.append(clean_word.lower() + trailing_punct)
                prev_was_proper = False
                
        return " ".join(fixed_words)

    def restore(self, text):
        """Ana düzeltme fonksiyonu"""
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
                if restored_text != "":
                    restored_text += " "
                restored_text += word
            
            if label != "non":
                restored_text += label
        
        # 3. Temel Temizlik
        restored_text = restored_text.replace(" ,", ",")
        restored_text = restored_text.replace(" .", ".")
        restored_text = restored_text.replace(" ?", "?")
        restored_text = restored_text.replace(" !", "!")
        restored_text = restored_text.replace(" :", ":")
        restored_text = restored_text.replace(" ;", ";")
        
        # Parantez düzeltmeleri
        restored_text = restored_text.replace("( ", "(")
        restored_text = restored_text.replace(" )", ")")
        
        # 4. Akıllı Büyük Harf ve Kesme İşareti
        restored_text = self._apply_smart_capitalization(restored_text)
        
        # 5. Cümle Başı Büyük Harf Garantisi
        if len(restored_text) > 0:
            restored_text = restored_text[0].upper() + restored_text[1:]
        
        # Noktalama sonrası büyük harf
        restored_text = re.sub(
            r'([.!?]\s+)([a-zçğıöşü])',
            lambda m: m.group(1) + m.group(2).upper(),
            restored_text
        )
        
        return restored_text


# TEST KODU
if __name__ == "__main__":
    # Zemberek'i başlat (örnek)
    print("Test için mock Zemberek nesnesi kullanılıyor...")
    
    class MockMorphology:
        def analyze(self, word):
            return []
    
    morphology = MockMorphology()
    restorer = PunctuationRestorer(morphology)
    
    test_text = """doğal dil işleme (NLP) bilgisayarların insan dilini anlamasını sağlayan bir teknolojidir günümüzde yapay zeka modeli metinleri analiz ederken bazı zorluklar yaşayabiliyor özellikle türkçe gibi sondan eklemeli dillerde kelime yapısı karmaşık olduğu için analiz yapmak daha da zor olmaktadır bu yüzden veri setlerinin düzgün olması ve model eğitiminin doğru yapılması gerekiyor ayrıca makine öğrenmesi algoritmaları her zaman bağlamı tam olarak anlayamaz"""
    
    print("\n" + "="*60)
    print("NOKTALAMA DÜZELTME TESTİ")
    print("="*60)
    print(f"\nGiriş:\n{test_text}\n")
    
    result = restorer.restore(test_text)
    print(f"Çıkış:\n{result}\n")
    print("="*60)