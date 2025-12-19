import streamlit as st
import os
import sys

# Kök dizini ekle
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.correction_pipeline import TextCorrectionPipeline

st.set_page_config(page_title="Türkçe Metin Düzeltici", page_icon="✨", layout="wide")

@st.cache_resource
def load_pipeline():
    return TextCorrectionPipeline()

# Gelişmiş CSS tasarımı
st.markdown("""
    <style>
    /* Ana arka plan */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Ana container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Başlık kartı */
    .title-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .title-card h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .title-card p {
        color: #666;
        font-size: 1.1rem;
    }
    
    /* Giriş kartı */
    .input-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        height: 100%;
    }
    
    /* Adım kartları */
    .step-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 5px solid;
        transition: transform 0.2s, box-shadow 0.2s;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .step-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .step-1 { border-left-color: #ff6b6b; }
    .step-2 { border-left-color: #4ecdc4; }
    .step-3 { border-left-color: #45b7d1; }
    
    .step-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        font-weight: 700;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 1rem;
    }
    
    .step-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        color: white;
    }
    
    .step-1 .step-icon { background: #ff6b6b; }
    .step-2 .step-icon { background: #4ecdc4; }
    .step-3 .step-icon { background: #45b7d1; }
    
    .step-content {
        color: #333;
        font-size: 1.05rem;
        line-height: 1.6;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
    }
    
    .final-result {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        font-weight: 600;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: white;
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }
    
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }
    
    /* Buton stilleri */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        font-size: 1rem;
        padding: 1rem;
        transition: border-color 0.3s;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(17, 153, 142, 0.3);
    }
    
    /* Başlıklar */
    h2, h3 {
        color: #2d3748;
        font-weight: 700;
    }
    
    /* Uyarı mesajları */
    .stAlert {
        border-radius: 12px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

try:
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Sistem Durumu")
        pipeline = load_pipeline()
        st.markdown('<div class="status-badge">✓ Tüm Modeller Aktif</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 📊 Pipeline Adımları")
        st.markdown("""
        <div style='font-size: 0.9rem; color: #666; line-height: 1.8;'>
        <b>1️⃣ Yazım Denetimi</b><br/>
        <small>Zemberek motoru ile Türkçe yazım kuralları</small><br/><br/>
        
        <b>2️⃣ Gramer Düzeltme</b><br/>
        <small>Seq2Seq derin öğrenme modeli</small><br/><br/>
        
        <b>3️⃣ Noktalama & Format</b><br/>
        <small>Büyük harf ve noktalama optimizasyonu</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 💡 İpuçları")
        st.markdown("""
        <small>
        • Doğal cümleler yazın<br/>
        • Yazım hatalarından endişe etmeyin<br/>
        • Pipeline her adımda iyileştirme yapar
        </small>
        """, unsafe_allow_html=True)

    # Ana başlık
    st.markdown("""
    <div class="title-card">
        <h1>✨ Akıllı Türkçe Metin Düzeltici</h1>
        <p>Yapay zeka destekli çok katmanlı metin işleme sistemi</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ana içerik
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="input-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Metin Girişi")
        user_input = st.text_area(
            "Düzeltmek istediğiniz metni yazın...",
            height=300,
            placeholder="Örnek: bu cumlede yazim hatalari var ve duzeltilmesi gerek",
            label_visibility="collapsed"
        )
        
        st.markdown("<br/>", unsafe_allow_html=True)
        run_btn = st.button("🚀 Pipeline'ı Başlat", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("### 🔄 İşlem Sonuçları")
        
        if run_btn and user_input:
            with st.spinner("🔮 Yapay zeka çalışıyor..."):
                steps, lang, error = pipeline.process(user_input)
                
                if error:
                    st.warning(f"⚠️ Tespit edilen dil: **{lang}** - {error}")
                else:
                    # Adım 1
                    st.markdown(f"""
                    <div class="step-card step-1">
                        <div class="step-header">
                            <div class="step-icon">1</div>
                            <span>Yazım Denetimi</span>
                        </div>
                        <div class="step-content">{steps["spelling"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Adım 2
                    st.markdown(f"""
                    <div class="step-card step-2">
                        <div class="step-header">
                            <div class="step-icon">2</div>
                            <span>Gramer Düzeltme</span>
                        </div>
                        <div class="step-content">{steps["grammar"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Adım 3 - Final
                    st.markdown(f"""
                    <div class="step-card step-3">
                        <div class="step-header">
                            <div class="step-icon">✓</div>
                            <span>Nihai Sonuç</span>
                        </div>
                        <div class="step-content final-result">{steps["final"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.button("📋 Sonucu Panoya Kopyala", use_container_width=True)
                    
        elif run_btn:
            st.error("❌ Lütfen bir metin girin!")
        else:
            st.info("👆 Soldaki alana metninizi girin ve butona tıklayın")

except Exception as e:
    st.error(f"🚨 Sistem Hatası: {e}")
    st.exception(e)