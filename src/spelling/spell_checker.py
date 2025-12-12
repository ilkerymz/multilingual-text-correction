import os
from symspellpy import SymSpell, Verbosity

class SpellingCorrector:
    def __init__(self):
        # --- AYAR 1: Düzeltme Kapasitesini Artırıyoruz ---
        # max_dictionary_edit_distance=3 yaptık (Daha agresif düzeltir)
        self.sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)
        
        dictionary_path = os.path.join("src", "spelling", "frequency_dictionary.txt")
        
        if not os.path.exists(dictionary_path):
            print("⚠️ HATA: Sözlük dosyası yok! Önce generate_dict.py çalıştırın.")
        else:
            # Sözlüğü yükle
            self.sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
            print("✅ Spelling modeli yüklendi.")

    def correct_text(self, text):
        words = text.split()
        corrected_words = []

        for word in words:
            # Noktalama işaretlerini temizlemeden işlem yapalım
            # (Basit split yaptık, gelişmişi için regex gerekebilir ama şimdilik yeterli)
            
            # Kelimeyi küçük harfe çevirip kontrol et
            word_lower = word.lower()

            # --- AYAR 2: En İyi Öneriyi Bul ---
            # transfer_casing=True: "Gelyorum" -> "Geliyorum" (Büyük harfi korur)
            suggestions = self.sym_spell.lookup(
                word_lower, 
                Verbosity.CLOSEST, 
                max_edit_distance=2, # Kelime başı tolerans
                transfer_casing=True 
            )

            if suggestions:
                # En iyi öneriyi al
                best_suggestion = suggestions[0].term
                
                # Orijinal kelimenin ilk harfi büyükse, öneriyi de büyüt
                if word[0].isupper():
                    best_suggestion = best_suggestion.capitalize()
                
                corrected_words.append(best_suggestion)
            else:
                # Öneri yoksa olduğu gibi bırak
                corrected_words.append(word)

        return " ".join(corrected_words)

if __name__ == "__main__":
    corrector = SpellingCorrector()
    
    test_sentences = [
        "Bugn hva cok guzel",     
        "Eve gelyorum",            
        "Yanlız kaldım",         
        "Herkez burda mı",         
        "Kitab okumayı sevyorum"   
    ]
    
    print("\n--- 🧪 GELİŞMİŞ SPELLING TESTİ ---")
    for sent in test_sentences:
        corrected = corrector.correct_text(sent)
        print(f"🔴 {sent}")
        print(f"🟢 {corrected}")
        print("-" * 30)