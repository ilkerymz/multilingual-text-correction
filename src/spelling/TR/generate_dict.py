import os
try:
    from wordfreq import top_n_list, word_frequency
except ImportError:
    print("❌ HATA: 'wordfreq' kütüphanesi yok. 'pip install wordfreq' yapmalısın.")
    exit()

# Sözlüğün kaydedileceği yer
OUTPUT_FILE = "src/spelling/frequency_dictionary.txt"

def generate_dictionary():
    print("📚 Türkçe frekans sözlüğü oluşturuluyor...")
    
    # 1. Wordfreq kütüphanesinden en sık kullanılan 60.000 kelimeyi al
    # Bu sayı ne kadar artarsa sistem o kadar çok kelime bilir ama yavaşlayabilir.
    top_words = top_n_list('tr', 60000)
    
    # 2. Kelimeleri dosyaya yaz
    print(f"✅ {len(top_words)} kelime işleniyor...")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for word in top_words:
            # Kelime çok kısaysa (1 harf) ve 'o' değilse alma (Gürültüyü azaltır)
            if len(word) < 2 and word != "o":
                continue
                
            # Frekans skorunu tamsayıya çevir (SymSpell formatı: kelime frekans)
            freq_score = int(word_frequency(word, 'tr') * 1_000_000_000)
            f.write(f"{word} {freq_score}\n")
            
    print(f"💾 Sözlük başarıyla kaydedildi: {OUTPUT_FILE}")
    print("👉 Şimdi 'spell_checker.py' dosyasını çalıştırabilirsin.")

if __name__ == "__main__":
    generate_dictionary()