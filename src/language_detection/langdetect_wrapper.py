from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # Ensure consistent results across runs

def detect_lang_simple(text: str) -> str:
    try:
        lang = detect(text)
        if lang.startswith("tr"):
            return "tr"
        elif lang.startswith("en"):
            return "en"
        else:
            return "unknown"
    except:
        return "unknown"