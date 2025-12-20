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
        
        # 1. MANUEL DÜZELTME SÖZLÜĞÜ
        self.manual_map = {
            # Kısaltmalar & Slang
            "bgn": "bugün", "bugn": "bugün", "bugun": "bugün",
            "hva": "hava", "hana": "hava",
            "cnm": "canım", "bisi": "bir şey", "bişey": "bir şey", "bisey": "bir şey",
            "hic": "hiç", "nbr": "naber", "slm": "selam", "tmm": "tamam", "ok": "tamam",
            "naptin": "ne yaptın", "naptın": "ne yaptın", "napıyosun": "ne yapıyorsun",
            "nerdeydn": "neredeydin", "gorunmedn": "görünmedin",
            
            # Kesin yazım hataları
            "yanlız": "yalnız", "herkez": "herkes",
            "dgl": "değil", "degil": "değil",
            "olmaktadır": "olmaktadır", "olmaktadir": "olmaktadır",
            
            # ASCII Sorunları
            "cok": "çok", "guzel": "güzel", "gusel": "güzel",
            "yagmur": "yağmur", "yagiyor": "yağıyor", "yagıyor": "yağıyor",
            "ogretmen": "öğretmen", "odev": "ödev", "semsiye": "şemsiye",
            "okla": "okula", "anlamadm": "anlamadım",
            "gun": "gün", "dun": "dün",
            "analiz": "analiz", "turce": "türkçe", "turkce": "türkçe",
            "ozellikle": "özellikle", "oldugu": "olduğu", "olduğu": "olduğu",
            "icin": "için", "yuzden": "yüzden", "yüzden": "yüzden",
            "duzgun": "düzgün", "dogru": "doğru", "gerekiyo": "gerekiyor",
            
            # Fiil hataları
            "gittm": "gittim", "geldm": "geldim",
            "almayi": "almayı", "gelmeyi": "gelmeyi", "gitmeyi": "gitmeyi",
            "unuttum": "unuttum", "unuttm": "unuttum",
            "istiyom": "istiyorum", "gidiyom": "gidiyorum", "yapiyom": "yapıyorum",
            "yaşayabilyor": "yaşayabiliyor",
            
            # Özel isim ekleri
            "ankaradır": "Ankara'dır", "ankarada": "Ankara'da", "ankaradan": "Ankara'dan",
            "istanbulda": "İstanbul'da", "istanbuldan": "İstanbul'dan",
            "izmirde": "İzmir'de", "izmirden": "İzmir'den",
            
            # Diğer
            "suan": "şuan", "kitab": "kitap",
            "br": "bir",
            "anlıyamaz": "anlayamaz",
        }
        
        # 2. SONEK DÜZELTME KURALLARI
        self.suffix_fixes = [
            ("iyom", "iyorum"), ("ıyom", "ıyorum"),
            ("uyom", "uyorum"), ("üyom", "üyorum"),
            ("iyon", "iyor"), ("ıyon", "ıyor"),
            ("uyon", "uyor"), ("üyon", "üyor"),
            ("iyosun", "iyorsun"), ("ıyosun", "ıyorsun"),
            ("ycam", "yeceğim"), ("ycaz", "yeceğiz"),
            ("cam", "cağım"), ("cem", "ceğim"),
            ("caz", "cağız"), ("cez", "ceğiz"),
            ("cak", "acak"), ("cek", "ecek"),
            ("tm", "tim"), ("dm", "dim"),
        ]
        
        # 3. YAKIN BENZER KELİMELER (Zemberek bunları karıştırıyor)
        self.confusables = {
            "sağlayan": ["sağlanan", "sağlayın"],
            "anlamasını": ["anlamayı", "anlamaya"],
            "yapılması": ["yapması", "yapılmaya"],
            "olması": ["olmaya", "olmasına"],
            "zorluklar": ["zorlukları", "zorluk"],
            "yaşayabiliyor": ["yaşıyor", "yaşayabilir"],
            "karmaşık": ["karmaşa", "karışık"],
            "algoritmalar": ["algoritma", "algoritmayı"],
            "bağlamı": ["bağlam", "bağlamın"],
            "anlayamaz": ["anlamaz", "anlıyor"],
        }
        
        # 4. SABİT KELİMELER - ASLA DOKUNMA
        self.safe_words = {
            # Zamirler
            "ben", "sen", "o", "biz", "siz", "onlar",
            "bu", "şu", "o",
            
            # Bağlaçlar ve edatlar
            "var", "yok", "ama", "ve", "ki", "ile", "veya", "ya",
            "de", "da", "te", "ta",
            "mi", "mı", "mu", "mü",
            
            # Sayılar
            "bir", "iki", "üç", "dört", "beş", "altı", "yedi", "sekiz", "dokuz", "on",
            
            # Soru kelimeleri
            "ne", "neden", "nasıl", "nerede", "kim", "hangi", "niye",
            
            # Yaygın fiiller
            "gitmek", "gelmek", "yapmak", "olmak", "almak", "vermek",
            "görmek", "bilmek", "söylemek", "istemek",
            
            # Yaygın sıfatlar
            "büyük", "küçük", "iyi", "kötü", "güzel", "çirkin",
            
            # Yaygın isimler
            "adam", "kadın", "çocuk", "insan", "ev", "iş", "gün", "zaman",
            "şey", "yer", "kişi",
            
            # Teknik terimler
            "doğal", "dil", "işleme", "bilgisayar", "bilgisayarlar",
            "bilgisayarların", "insan", "anlama", "anlamak",
            "teknoloji", "günümüz", "günümüzde", "yapay", "zeka",
            "model", "modeller", "modelleri", "metin", "metinler",
            "metinleri", "analiz", "etmek", "ederken", "bazı",
            "zorluk", "zorluklar", "yaşamak", "yaşayabiliyor",
            "özellikle", "türkçe", "gibi", "sondan", "eklemeli",
            "dil", "diller", "dillerde", "kelime", "yapı", "yapısı",
            "karmaşık", "olduğu", "için", "yapmak", "daha", "zor",
            "olmak", "olmaktadır", "bu", "yüzden", "veri", "set",
            "setler", "setleri", "setlerinin", "düzgün", "olması",
            "gerekir", "gerekiyor", "ayrıca", "makine", "öğrenme",
            "öğrenmesi", "algoritma", "algoritmalar", "algoritmaları",
            "her", "zaman", "bağlam", "bağlamı", "tam", "olarak",
            "anlayamaz", "anlamak",
            
            # Ek halindeki kelimeler
            "bende", "sende", "onda",
        }
        
        # 5. ŞEHİR VE ÖZEL İSİM KÖKLERI
        self.proper_nouns = {
            "ankara", "istanbul", "izmir", "bursa", "antalya", "adana",
            "ahmet", "mehmet", "ayşe", "fatma", "ali", "veli",
            "türkiye", "türkiyenin", "türkiyede",
        }
        
        print("✅ Sistem Hazır! (V13 - Akıllı Filtreleme)")

    def _is_valid(self, word):
        """Kelimenin Türkçe morfolojide geçerli olup olmadığını kontrol eder"""
        if not word or len(word) < 2:
            return False
        try:
            results = self.morphology.analyze(word)
            return results.analysisResults.size() > 0
        except:
            return False

    def _edit_distance(self, s1, s2):
        """İki kelime arasındaki Levenshtein mesafesini hesaplar"""
        if len(s1) < len(s2):
            return self._edit_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]

    def _is_similar_enough(self, original, suggestion):
        """Önerinin orijinale yeterince yakın olup olmadığını kontrol eder"""
        # Tamamen aynıysa kabul et
        if original == suggestion:
            return True
        
        # Uzunluk farkı çok fazlaysa reddet
        len_diff = abs(len(original) - len(suggestion))
        if len_diff > 3:
            return False
        
        # Edit distance çok büyükse reddet
        distance = self._edit_distance(original, suggestion)
        max_allowed = max(2, len(original) // 3)
        if distance > max_allowed:
            return False
        
        # İlk harf farklıysa şüpheli
        if original[0] != suggestion[0]:
            # İlk harf farklı ama edit distance 1 ise kabul et (örn: sağlayan -> bağlayan)
            if distance > 1:
                return False
        
        return True

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
        
        # İki harf değişimi
        changes = []
        for i, char in enumerate(word):
            if char in replacements:
                changes.append((i, replacements[char]))
        
        if len(changes) >= 2:
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
                if suffix in ["da", "de", "dır", "dir", "dan", "den", "ya", "ye", "nın", "nin", "nun", "nün"]:
                    return noun.capitalize() + "'" + suffix
        
        return None

    def _get_best_suggestion(self, word, suggestions):
        """En uygun öneriyi seç - ÇOK KATLI FİLTRELEME"""
        if not suggestions:
            return None
        
        # KARIŞTIRILABILIR KELIMELER KONTROLÜ
        for correct_word, similar_words in self.confusables.items():
            if word.lower() in similar_words:
                # Orijinal kelime zaten doğru olabilir, öneri alma
                if self._is_valid(word.lower()):
                    return None
        
        word_len = len(word)
        candidates = []
        
        for sugg in suggestions[:8]:  # İlk 8 öneriyi değerlendir
            # Benzerlik kontrolü
            if not self._is_similar_enough(word.lower(), sugg):
                continue
            
            score = 0
            
            # Uzunluk benzerliği
            len_diff = abs(len(sugg) - word_len)
            if len_diff == 0:
                score += 10
            elif len_diff == 1:
                score += 6
            elif len_diff == 2:
                score += 3
            else:
                score += 1
            
            # İlk harf aynı mı?
            if sugg[0] == word[0]:
                score += 8
            
            # Son harf aynı mı?
            if sugg[-1] == word[-1]:
                score += 5
            
            # İlk 3 harf benzerliği
            if len(sugg) >= 3 and len(word) >= 3 and sugg[:3] == word[:3]:
                score += 10
            
            # Edit distance bonusu
            distance = self._edit_distance(word.lower(), sugg)
            score += max(0, 10 - distance * 2)
            
            candidates.append((sugg, score))
        
        if not candidates:
            return None
        
        # En yüksek skoru bul
        candidates.sort(key=lambda x: x[1], reverse=True)
        best_sugg, best_score = candidates[0]
        
        # Eğer skor çok düşükse, öneri alma
        if best_score < 15:
            return None
        
        return best_sugg

    def correct(self, text):
        """Ana düzeltme fonksiyonu"""
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
                
                # 2. SABİT KELİMELER (Kesinlikle dokunma!)
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
                
                # 7. ZEMBEREK ÖNERİLERİ (ÇOK DİKKATLİ!)
                suggestions = self.spell.suggest_for_word(word_lower)
                if suggestions and len(suggestions) > 0:
                    best = self._get_best_suggestion(word_lower, suggestions)
                    if best:
                        if original_case:
                            best = best[0].upper() + best[1:]
                        corrected_words.append(best + punctuation)
                    else:
                        # Öneri güvenilir değil, olduğu gibi bırak
                        corrected_words.append(word + punctuation)
                else:
                    corrected_words.append(word + punctuation)
            
            except Exception as e:
                corrected_words.append(word + punctuation)
        
        return " ".join(corrected_words)


if __name__ == "__main__":
    c = SmartCorrector()
    print("=" * 60)
    print("🇹🇷 V13 GELİŞTİRİLMİŞ TÜRKÇE YAZIM DÜZELTİCİ")
    print("=" * 60)
    
    # NLP test metni
    nlp_text = """doğal dil işleme (NLP) bilgisayarlarin insan dilini anlamasini saglayan br teknolojidir günümüzde yapay zeka modelleri metinleri analiz ederken bazi zorluklar yaşayabilyor ozellikle turkçe gibi sondan eklemeli dillerde kelime yapısı karmasık oldugu icin analiz yapmak dahada zor olmaktadır bu yuzden veri setlerinin duzgun olması ve model egitiminin dogru yapılması gerekiyo ayrıca makine ogrenmesi algoritmalri her zaman bağlamı tam olarak anlıyamaz"""
    
    print("\n📋 NLP Test Metni:")
    print("-" * 60)
    print(f"📝 Giriş :\n{nlp_text}\n")
    result = c.correct(nlp_text)
    print(f"✅ Çıkış :\n{result}\n")
    
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