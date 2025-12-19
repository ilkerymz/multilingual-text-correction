import os
import sys
import subprocess
import jpype
import traceback

# --- JAVA AYARLARI ---
def setup_java():
    try:
        java_bin = subprocess.check_output(["which", "java"]).decode("utf-8").strip()
        real_path = os.path.realpath(java_bin)
        java_home = os.path.dirname(os.path.dirname(real_path))
        os.environ["JAVA_HOME"] = java_home
        
        jvm_path = jpype.getDefaultJVMPath()
        if not jpype.isJVMStarted():
            jpype.startJVM(
                jvm_path, "-Djava.class.path=.", "-ea",
                f"-Djava.home={java_home}", convertStrings=True
            )
    except:
        pass

setup_java()

# --- ZEMBEREK ---
print("⏳ Sistem Yükleniyor...")
try:
    from zemberek import TurkishSpellChecker, TurkishMorphology
except ImportError:
    print("❌ HATA: 'zemberek-python' yok.")
    sys.exit()

class SmartCorrector:
    def __init__(self):
        print("⚙️ Motor Başlatılıyor...")
        self.morphology = TurkishMorphology.create_with_defaults()
        self.spell = TurkishSpellChecker(self.morphology)
        
        # 1. MANUEL DÜZELTME SÖZLÜĞÜ (Sadece yazım hataları)
        self.manual_map = {
            # Kısaltmalar & Slang
            "bgn": "bugün", "bugn": "bugün", "bugun": "bugün",
            "hva": "hava", "hana": "hava",
            "cnm": "canım", "bisi": "bir şey", "bişey": "bir şey", "bisey": "bir şey",
            "hic": "hiç", "nbr": "naber", "slm": "selam", "tmm": "tamam", "ok": "tamam",
            "naptin": "ne yaptın", "naptın": "ne yaptın", "napıyosun": "ne yapıyorsun",
            "nerdeydn": "neredeydin", "gorunmedn": "görünmedin",
            
            # Yaygın Yazım Hataları (de/da AYIRIMI YOK - gramer modülü halleder)
            "yanlız": "yalnız", "herkez": "herkes",
            "dgl": "değil", "degil": "değil",
            
            # ASCII Sorunları
            "cok": "çok", "guzel": "güzel", "gusel": "güzel",
            "yagmur": "yağmur", "yagiyor": "yağıyor", "yagıyor": "yağıyor",
            "ogretmen": "öğretmen", "odev": "ödev", "semsiye": "şemsiye",
            "okla": "okula", "anlamadm": "anlamadım",
            "gun": "gün", "dun": "dün", "bugun": "bugün",
            
            # Fiil hataları
            "gittm": "gittim", "geldm": "geldim",
            "almayi": "almayı", "gelmeyi": "gelmeyi", "gitmeyi": "gitmeyi",
            "unuttum": "unuttum", "unuttm": "unuttum",
            "istiyom": "istiyorum", "gidiyom": "gidiyorum", "yapiyom": "yapıyorum",
            
            # Özel isim ekleri
            "ankaradır": "Ankara'dır", "ankarada": "Ankara'da", "ankaradan": "Ankara'dan",
            "istanbulda": "İstanbul'da", "istanbuldan": "İstanbul'dan",
            "izmirde": "İzmir'de", "izmirden": "İzmir'den",
            
            # Diğer
            "suan": "şuan", "kitab": "kitap",
        }
        
        # 2. SONEK DÜZELTME KURALLARI
        self.suffix_fixes = [
            # Konuşma dili fiil sonekleri (uzundan kısaya!)
            ("iyom", "iyorum"),    # gidiyom → gidiyorum, istiyom → istiyorum
            ("ıyom", "ıyorum"),    # yapıyom → yapıyorum
            ("uyom", "uyorum"),    # okuyom → okuyorum
            ("üyom", "üyorum"),    # yürüyom → yürüyorum
            
            ("iyon", "iyor"),      # gidiyon → gidiyor
            ("ıyon", "ıyor"),      # yapıyon → yapıyor
            ("uyon", "uyor"),      # uyuyon → uyuyor
            ("üyon", "üyor"),      # yürüyon → yürüyor
            
            ("iyosun", "iyorsun"), # gidiyosun → gidiyorsun
            ("ıyosun", "ıyorsun"), # yapıyosun → yapıyorsun
            
            # Gelecek zaman
            ("ycam", "yeceğim"),   # alıycam → alacağım
            ("ycaz", "yeceğiz"),   # alıycaz → alacağız
            ("cam", "cağım"),      # yapacam → yapacağım
            ("cem", "ceğim"),      # gelecem → geleceğim
            ("caz", "cağız"),      # yapcaz → yapacağız
            ("cez", "ceğiz"),      # gelcez → geleceğiz
            ("cak", "acak"),       # yapcak → yapacak
            ("cek", "ecek"),       # gelcek → gelecek
            
            # Geçmiş zaman
            ("tm", "tim"),         # gittm → gittim
            ("dm", "dim"),         # geldm → geldim
            ("tı", "tti"),         # gitti → geçerli
            ("dı", "ddi"),         # geldi → geçerli
        ]
        
        # 3. SABİT KELİMELER (Kesinlikle dokunma)
        self.safe_words = {
            "ben", "sen", "o", "biz", "siz", "onlar",
            "bu", "şu",
            "var", "yok", "ama", "ve", "ki", "ile",
            "bir", "iki", "üç", "dört", "beş",
            "ne", "neden", "nasıl", "nerede", "kim", "hangi",
            "mi", "mı", "mu", "mü",
            "de", "da", "te", "ta",  # Gramer modülü halleder
            "bende", "sende", "onda",  # Gramer modülü halleder
        }
        
        # 4. ŞEHİR VE ÖZEL İSİM KÖKLERI
        self.proper_nouns = {
            "ankara", "istanbul", "izmir", "bursa", "antalya", "adana",
            "ahmet", "mehmet", "ayşe", "fatma", "ali", "veli",
            "türkiye", "türkiyenin", "türkiyede",
        }
        
        print("✅ Sistem Hazır! (V12 Spelling Only)")

    def _is_valid(self, word):
        """Kelimenin Türkçe morfolojide geçerli olup olmadığını kontrol eder"""
        if not word or len(word) < 2:
            return False
        try:
            results = self.morphology.analyze(word)
            return results.analysisResults.size() > 0
        except:
            return False

    def _fix_ascii(self, word):
        """ASCII karakterleri Türkçe'ye çevir"""
        replacements = {
            'c': 'ç', 'g': 'ğ', 'i': 'ı', 
            'o': 'ö', 's': 'ş', 'u': 'ü'
        }
        
        # Tek harf değişimi
        for i, char in enumerate(word):
            if char in replacements:
                new_char = replacements[char]
                candidate = word[:i] + new_char + word[i+1:]
                if self._is_valid(candidate):
                    return candidate
        
        # İki harf değişimi (performans için max 2)
        changes = []
        for i, char in enumerate(word):
            if char in replacements:
                changes.append((i, replacements[char]))
        
        if len(changes) >= 2:
            # İlk 2 değişikliği uygula
            modified = list(word)
            for idx, new_char in changes[:2]:
                modified[idx] = new_char
            candidate = "".join(modified)
            if self._is_valid(candidate):
                return candidate
        
        return None

    def _fix_suffix(self, word):
        """Konuşma dili soneklerini düzelt"""
        for wrong, correct in self.suffix_fixes:
            if word.endswith(wrong):
                fixed = word[:-len(wrong)] + correct
                if self._is_valid(fixed):
                    return fixed
        return None

    def _handle_proper_noun_suffix(self, word):
        """Özel isimlere gelen ekleri ayır"""
        word_lower = word.lower()
        
        for noun in self.proper_nouns:
            if word_lower.startswith(noun) and len(word_lower) > len(noun):
                suffix = word_lower[len(noun):]
                # Sadece yaygın ekleri ayır
                if suffix in ["da", "de", "dır", "dir", "dan", "den", "ya", "ye", "nın", "nin", "nun", "nün"]:
                    return noun.capitalize() + "'" + suffix
        
        return None

    def _get_best_suggestion(self, word, suggestions):
        """En uygun öneriyi seç"""
        if not suggestions:
            return None
        
        word_len = len(word)
        best = suggestions[0]
        best_score = 0
        
        for sugg in suggestions[:5]:
            score = 0
            
            # Uzunluk benzerliği (çok önemli)
            len_diff = abs(len(sugg) - word_len)
            if len_diff == 0:
                score += 5
            elif len_diff == 1:
                score += 3
            elif len_diff == 2:
                score += 1
            
            # İlk harf aynı mı?
            if sugg and word and sugg[0] == word[0]:
                score += 3
            
            # Son harf aynı mı?
            if sugg and word and sugg[-1] == word[-1]:
                score += 2
            
            # İlk 3 harf benzerliği
            if len(sugg) >= 3 and len(word) >= 3 and sugg[:3] == word[:3]:
                score += 4
            
            if score > best_score:
                best_score = score
                best = sugg
        
        return best

    def correct(self, text):
        """Ana düzeltme fonksiyonu - SADECE YAZIM HATALARI"""
        if not text or not text.strip():
            return ""
        
        words = text.split()
        corrected_words = []
        
        for word in words:
            # Noktalama ayır
            punctuation = ""
            if word and word[-1] in ".,!?;:":
                punctuation = word[-1]
                word = word[:-1]
            
            if not word:
                continue
                
            word_lower = word.lower()
            original_case = word[0].isupper()
            
            try:
                # 1. MANUEL SÖZLÜK (En yüksek öncelik)
                if word_lower in self.manual_map:
                    corrected = self.manual_map[word_lower]
                    if original_case and corrected and not corrected[0].isupper():
                        corrected = corrected[0].upper() + corrected[1:]
                    corrected_words.append(corrected + punctuation)
                    continue
                
                # 2. SABİT KELİMELER (Dokunma!)
                if word_lower in self.safe_words:
                    corrected_words.append(word + punctuation)
                    continue
                
                # 3. ÖZEL İSİM + EK AYIRMA
                proper_fixed = self._handle_proper_noun_suffix(word)
                if proper_fixed:
                    corrected_words.append(proper_fixed + punctuation)
                    continue
                
                # 4. GEÇERLİLİK KONTROLÜ
                if self._is_valid(word_lower):
                    corrected_words.append(word + punctuation)
                    continue
                
                # 5. SONEK TAMIRI
                suffix_fixed = self._fix_suffix(word_lower)
                if suffix_fixed:
                    if original_case:
                        suffix_fixed = suffix_fixed[0].upper() + suffix_fixed[1:]
                    corrected_words.append(suffix_fixed + punctuation)
                    continue
                
                # 6. ASCII TAMIRI
                ascii_fixed = self._fix_ascii(word_lower)
                if ascii_fixed:
                    if original_case:
                        ascii_fixed = ascii_fixed[0].upper() + ascii_fixed[1:]
                    corrected_words.append(ascii_fixed + punctuation)
                    continue
                
                # 7. ZEMBEREK ÖNERİLERİ (Son çare)
                suggestions = self.spell.suggest_for_word(word_lower)
                if suggestions and len(suggestions) > 0:
                    best = self._get_best_suggestion(word_lower, suggestions)
                    if best:
                        if original_case:
                            best = best[0].upper() + best[1:]
                        corrected_words.append(best + punctuation)
                    else:
                        corrected_words.append(word + punctuation)
                else:
                    # Öneri yoksa olduğu gibi bırak
                    corrected_words.append(word + punctuation)
            
            except Exception as e:
                # Hata olursa kelimeyi koru
                corrected_words.append(word + punctuation)
        
        return " ".join(corrected_words)


if __name__ == "__main__":
    c = SmartCorrector()
    print("=" * 60)
    print("🇹🇷 V12 SPELLING ONLY (de/da ayrımı yok)")
    print("=" * 60)
    
    # Test örnekleri
    test_cases = [
        "bugn bende okula gelmek istiyom",
        "türkiye cumhuriyeti başkenti ankaradır ahmet ve ayşe okula gitti mi",
        "ben dun ormana gittm",
        "yagmur yagiyor semsiye almayi unuttum",
        "cok guzel bir gun bugun",
        "istanbulda hava cok guzel",
        "yapacam diyosun ama yapmıyosun",
        "bu kitab suan bende",
    ]
    
    print("\n📋 Otomatik Test Sonuçları:")
    print("-" * 60)
    for test in test_cases:
        result = c.correct(test)
        print(f"📝 Giriş : {test}")
        print(f"✅ Çıkış : {result}\n")
    
    print("=" * 60)
    print("Manuel test için metin girin (q = çıkış):")
    
    while True:
        try:
            t = input("\n📝 Yaz: ")
            if t.lower() == "q":
                break
            print(f"✅ Düzeltilmiş: {c.correct(t)}")
        except KeyboardInterrupt:
            break