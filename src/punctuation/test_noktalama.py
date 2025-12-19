import re
from transformers import pipeline
from zemberek import TurkishMorphology

# 1. Zemberek Analizcisini Başlat
print("Zemberek başlatılıyor...")
morphology = TurkishMorphology.create_with_defaults()

# 2. BERT Modelini Yükle
print("YTU Cosmos BERT modeli yükleniyor...")
model_id = "ytu-ce-cosmos/turkish-base-bert-punctuation-correction"
nlp = pipeline("token-classification", model=model_id)

def apply_smart_capitalization(text):
    words = text.split()
    fixed_words = []
    
    org_suffixes = ["cumhuriyeti", "üniversitesi", "fakültesi", "başkanlığı", "müdürlüğü", "mahallesi", "vakfı"]

    for i, word in enumerate(words):
        clean_word = word.strip(".,!?\"' ")
        if not clean_word:
            fixed_words.append(word)
            continue
            
        results = morphology.analyze(clean_word)
        
        is_proper = False
        stem = clean_word
        for res in results:
            res_str = str(res)
            if "ProperNoun" in res_str or "Prop" in res_str:
                is_proper = True
                stem = res.get_stem()
                break
        
        # --- TÜRKİYE HATASI İÇİN ÖZEL KONTROL ---
        # Zemberek "türkiye"nin kökünü "türki" bulabiliyor. Bunu engellemek için:
        if stem.lower() == "türki" and clean_word.lower() == "türkiye":
            stem = "türkiye"

        if is_proper:
            # Eğer kelime kökten uzunsa ve kök "türkiye" değilse kesme işareti koy
            if len(clean_word) > len(stem):
                suffix = clean_word[len(stem):]
                # Kökü büyüt + ' + eki ekle
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

def finalize_text(model_output):
    # 1. BERT Token Birleştirme
    text = ""
    for res in model_output:
        word = res['word']
        label = res['entity']
        if word.startswith("##"):
            text += word.replace("##", "")
        else:
            if text != "": text += " "
            text += word
        if label != "non": text += label
    
    # 2. Temel Temizlik
    text = text.replace(" ,", ",").replace(" .", ".").replace(" ?", "?").replace(" !", "!")
    
    # 3. Akıllı Harf Büyütme ve Kesme İşareti
    text = apply_smart_capitalization(text)
    
    # 4. Cümle Başı ve Noktalama Sonrası Büyütme
    if len(text) > 0:
        text = text[0].upper() + text[1:]
    text = re.sub(r'([.!?]\s+)([a-zçğıöşü])', lambda m: m.group(1) + m.group(2).upper(), text)
    
    return text

# --- TEST ---
print("\n" + "="*50)
test_input = "türkiye cumhuriyeti başkenti ankaradır ahmet ve ayşe okula gitti mi"

ham_cikti = nlp(test_input)
sonuc = finalize_text(ham_cikti)

print(f"Girdi : {test_input}")
print(f"Çıktı : {sonuc}")
print("="*50)