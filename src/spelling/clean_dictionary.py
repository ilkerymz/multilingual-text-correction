import os

# Dosya Yolları
INPUT_DICT = "src/spelling/frequency_dictionary.txt"
OUTPUT_DICT = "src/spelling/frequency_dictionary_clean.txt"

# Yasaklı Kelimeler Listesi (Sözlükten atılacaklar)
# Buraya modelin "doğru sanmaması" gereken sık yapılan yanlışları ekliyoruz
BLACKLIST = {
    "herkez", "yanlız", "yalnış", "yeryüzü", "şöför", "eşşek", 
    "egsoz", "eksoz", "orjinal", "dinazor", "çünki", "kiprik",
    "ahcı", "aşcı", "bir çok", "hic", "cok", "guzel", "ozel", 
    "turkce", "turkiye", "gelcem", "gidiyom", "yapcam", "etcez",
    "kitab", "gelyorum", "gidicem", "yapıcam", "edecem"
}

def clean_dict():
    print("🧹 Sözlük temizliği başlıyor...")
    
    if not os.path.exists(INPUT_DICT):
        print(f"❌ HATA: {INPUT_DICT} bulunamadı.")
        return

    cleaned_lines = []
    removed_count = 0
    
    with open(INPUT_DICT, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if not parts: continue
            
            word = parts[0].lower()
            
            # 1. Kara listede var mı?
            if word in BLACKLIST:
                removed_count += 1
                continue
                
            # 2. İçinde q, w, x var mı? (Türkçe'de olmaz, genelde çöp veridir)
            if any(char in word for char in "qwx"):
                removed_count += 1
                continue

            cleaned_lines.append(line)

    # Temizlenmiş sözlüğü kaydet (Eskisinin üzerine yazıyoruz)
    with open(INPUT_DICT, "w", encoding="utf-8") as f:
        f.writelines(cleaned_lines)
        
    print(f"✅ Temizlik Tamamlandı!")
    print(f"🗑️ Toplam {removed_count} adet 'kirli/hatalı' kelime sözlükten atıldı.")
    print(f"💾 Yeni sözlük hazır: {INPUT_DICT}")

if __name__ == "__main__":
    clean_dict()