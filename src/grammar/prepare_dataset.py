import pandas as pd
import os

# Dosyaların bulunduğu klasör (Bu dosyanın olduğu yerin altındaki 'data' klasörü)
BASE_DIR = os.path.join(os.path.dirname(__file__), "../data")

def create_verified_csv(source_name, target_name, output_name):
    source_file = os.path.join(BASE_DIR, source_name)
    target_file = os.path.join(BASE_DIR, target_name)
    output_csv = os.path.join(BASE_DIR, output_name)

    print(f"🔄 İşleniyor: {source_name} + {target_name} -> {output_name}")
    
    if not os.path.exists(source_file) or not os.path.exists(target_file):
        print(f"❌ HATA: Dosyalar bulunamadı!\n   Aranan yer: {source_file}")
        return

    # 1. Kaynak (Hatalı) Dosyayı Oku
    with open(source_file, "r", encoding="utf-8") as f:
        # "S " ile başlayan satırları al ve başındaki "S "yi sil
        sources = [line.strip()[2:] for line in f if line.startswith("S ")]
    
    # 2. Hedef (Doğru) Dosyayı Oku
    with open(target_file, "r", encoding="utf-8") as f:
        targets = [line.strip() for line in f if line.strip()]

    # Satır sayısı kontrolü ve eşitleme
    min_len = min(len(sources), len(targets))
    sources = sources[:min_len]
    targets = targets[:min_len]

    # 3. DataFrame Oluştur
    df = pd.DataFrame({"input_text": sources, "target_text": targets})
    
    # 4. KONTROL AŞAMASI
    diff_count = len(df[df["input_text"] != df["target_text"]])
    
    print(f"   📊 Toplam Satır: {len(df)}")
    print(f"   ✅ Düzeltme İçeren Satır Sayısı: {diff_count}")
    
    if diff_count == 0:
        print("   ⚠️ UYARI: Bu dosya tamamen kopya! Bir sorun var.")
    else:
        df.to_csv(output_csv, index=False)
        print(f"   💾 {output_name} başarıyla oluşturuldu.")

if __name__ == "__main__":
    # Klasör yoksa oluştur
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"⚠️ '{BASE_DIR}' klasörü oluşturuldu. Lütfen .txt dosyalarını içine atın.")
    else:
        create_verified_csv("boun_source_train.txt", "boun_target_train.txt", "train.csv")
        create_verified_csv("boun_source_dev.txt", "boun_target_dev.txt", "val.csv")
        create_verified_csv("boun_source_test.txt", "boun_target_test.txt", "test.csv")