import pandas as pd
import torch
import os
from transformers import MBart50TokenizerFast, MBartForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments, DataCollatorForSeq2Seq
from torch.utils.data import Dataset

# --- AYARLAR ---
MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt"
# Çıktı klasörü (Proje ana dizininde models klasörü oluşturur)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../../models", "grammar_model")
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def filter_dataset(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"❌ HATA: {file_name} bulunamadı! Önce prepare_data.py çalıştırın.")
        return pd.DataFrame() # Boş döndür
        
    df = pd.read_csv(file_path).dropna().astype(str)
    # Input ve Target eşit DEĞİLSE al
    df_filtered = df[df["input_text"] != df["target_text"]]
    return df_filtered

def main():
    # GPU Kontrolü
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🔥 Çalışma Modu: {device.upper()}")
    if device == "cuda":
        print(f"   Ekran Kartı: {torch.cuda.get_device_name(0)}")

    print("🧹 Veri filtreleniyor (Sadece hatalı cümleler alınıyor)...")
    train_df = filter_dataset("train.csv")
    val_df = filter_dataset("val.csv")

    if train_df.empty:
        print("❌ Eğitim verisi boş. İşlem durduruluyor.")
        return

    print(f"🔥 Eğitim için seçilen 'Hatalı' cümle sayısı: {len(train_df)}")

    # Tokenizer ve Model
    print("📦 Model indiriliyor/yükleniyor...")
    tokenizer = MBart50TokenizerFast.from_pretrained(MODEL_NAME, src_lang="tr_TR", tgt_lang="tr_TR")
    model = MBartForConditionalGeneration.from_pretrained(MODEL_NAME)
    
    # Yerel PC optimizasyonu (VRAM Tasarrufu için)
    if device == "cuda":
        model.gradient_checkpointing_enable() 

    class GecDataset(Dataset):
        def __init__(self, df, tokenizer):
            self.data = df
            self.tokenizer = tokenizer
        def __len__(self): return len(self.data)
        def __getitem__(self, idx):
            row = self.data.iloc[idx]
            inputs = self.tokenizer(row["input_text"], max_length=64, truncation=True, padding="max_length", return_tensors="pt")
            with self.tokenizer.as_target_tokenizer():
                labels = self.tokenizer(row["target_text"], max_length=64, truncation=True, padding="max_length", return_tensors="pt")
            
            input_ids = inputs.input_ids.squeeze()
            labels = labels.input_ids.squeeze()
            labels[labels == tokenizer.pad_token_id] = -100 
            return {"input_ids": input_ids, "attention_mask": inputs.attention_mask.squeeze(), "labels": labels}

    train_ds = GecDataset(train_df, tokenizer)
    val_ds = GecDataset(val_df, tokenizer)

    # 3. Eğitimi Başlat
    training_args = Seq2SeqTrainingArguments(
        output_dir=OUTPUT_DIR,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=4e-5,
        
        # --- YEREL PC İÇİN OPTİMİZE EDİLMİŞ AYARLAR ---
        # Batch size 8 yaparsan bilgisayarın donabilir (OOM Hatası). 
        # Bunu 2 yaptık ama gradient_accumulation ile 16 gibi davranacak.
        per_device_train_batch_size=2,   
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,
        gradient_checkpointing=True, # VRAM kullanımını yarıya düşürür
        # ---------------------------------------------
        
        num_train_epochs=5,
        weight_decay=0.01,
        save_total_limit=1,
        predict_with_generate=True,
        fp16=True if device == "cuda" else False, # GPU varsa hızlandır
        load_best_model_at_end=True,
        report_to="none" # Wandb vs kapat
    )

    trainer = Seq2SeqTrainer(
        model=model, args=training_args, train_dataset=train_ds, eval_dataset=val_ds,
        tokenizer=tokenizer, data_collator=DataCollatorForSeq2Seq(tokenizer, model=model)
    )

    print("🏋️‍♂️ Gerçek Eğitim Başlıyor...")
    trainer.train()

    print(f"💾 Model Kaydediliyor: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("✅ Model Hazır!")

if __name__ == "__main__":
    main()