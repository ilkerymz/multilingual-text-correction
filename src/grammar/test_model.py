
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# ---------------------------------------------------------
# 1. AYARLAR
# ---------------------------------------------------------
# Drive'daki checkpoint yolunu buraya yapıştır:
MODEL_PATH = "./models/grammar_model/Büyük_ama_Etkili_Model/"  

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"⚙️ Çalışma cihazı: {device}")

# ---------------------------------------------------------
# 2. MODELİ YÜKLE
# ---------------------------------------------------------
print(f"📂 Model yükleniyor: {MODEL_PATH}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_PATH).to(device)
    model.eval()
    print("✅ Model başarıyla yüklendi!")
except Exception as e:
    print(f"❌ Model yüklenirken hata oluştu: {e}")
    exit()

# ---------------------------------------------------------
# 3. TEST CÜMLELERİ (BURAYI İSTEDİĞİN GİBİ DOLDUR)
# ---------------------------------------------------------
test_cumleleri = [
    "Ben eve yada  uyuyabileceğim bir yere gitmek istiyorum.",
    "Bugün birazda onunla ilgilenmeliyim.",
    "Karşılıklı sayılarla devam eden maçta periyodun ilk 5 dakikasıda 15-16 Trabzonspor üstünlüğünde geçildi.",
    "Onlarıda yapacağız.",
    "Kimin ne dediğini bende biliyorum.",
    "Hiçbir şey benide yıldıramaz.",
]

# ---------------------------------------------------------
# 4. TOPLU DÜZELTME KODU
# ---------------------------------------------------------
def duzelt(text):
    inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=128,
            num_beams=5,          # Kalite için beam search
            repetition_penalty=1.2,
            early_stopping=True
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

print("\n" + "="*60)
print(f"{'GİRDİ (HATALI)':<30} | {'ÇIKTI (MODEL)':<30}")
print("="*60)

for cumle in test_cumleleri:
    sonuc = duzelt(cumle)
    print(f"{cumle:<30} | {sonuc:<30}")

print("="*60)