import os
try:
    from wordfreq import top_n_list, word_frequency
except ImportError:
    print("❌ HATA: 'wordfreq' kütüphanesi bulunamadı.")
    print("Lütfen terminalden şu komutu çalıştırın: pip install wordfreq")
    exit()

# Kayıt Yeri
OUTPUT_FILE = "src/spelling/frequency_dictionary.txt"

def generate_dictionary():
    print("📚 Türkçe kelime hazinesi oluşturuluyor (Kaynak: wordfreq)...")
    
    # Türkçe'de en sık kullanılan 50.000 kelimeyi al
    # Bu liste Wikipedia, altyazılar ve sosyal medya verilerinden derlenmiştir.
    top_words = top_n_list('tr', 50000)
    
    print(f"✅ {len(top_words)} kelime bulundu. Dosyaya yazılıyor...")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for word in top_words:
            # SymSpell için format: "kelime [boşluk] frekans_sayısı"
            # Kütüphane 0.001 gibi oran verir, biz bunu tamsayıya (1.000.000) çeviriyoruz
            freq_score = int(word_frequency(word, 'tr') * 1_000_000_000)
            f.write(f"{word} {freq_score}\n")
            
    print(f"💾 Profesyonel sözlük hazır: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_dictionary()