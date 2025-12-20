import streamlit as st
import os
import sys
from difflib import SequenceMatcher

# ================= PATH SETUP =================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.correction_pipeline import TextCorrectionPipeline

# ================= DIFF UTILS =================
def diff_highlights(original: str, corrected: str):
    orig_tokens = original.split()
    corr_tokens = corrected.split()
    matcher = SequenceMatcher(None, orig_tokens, corr_tokens)

    highlighted = []
    changes = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            highlighted.extend(orig_tokens[i1:i2])

        elif tag == "replace":
            o = " ".join(orig_tokens[i1:i2])
            n = " ".join(corr_tokens[j1:j2])
            highlighted.append(f"<span class='bad-token'>{o}</span>")
            changes.append(
                f"<span class='tag grammar'>[Grammar]</span> <b>{o}</b> → <b>{n}</b>"
            )

        elif tag == "delete":
            o = " ".join(orig_tokens[i1:i2])
            highlighted.append(f"<span class='bad-token'>{o}</span>")
            changes.append(
                f"<span class='tag grammar'>[Grammar]</span> <b>{o}</b> silindi"
            )

        elif tag == "insert":
            n = " ".join(corr_tokens[j1:j2])
            changes.append(
                f"<span class='tag grammar'>[Grammar]</span> Yeni eklendi: <b>{n}</b>"
            )

    return " ".join(highlighted), changes


def highlight_new_tokens(new_text: str, old_text: str):
    """
    Highlight tokens in `new_text` that are inserted or replaced vs `old_text`.
    """
    new_tokens = new_text.split()
    old_tokens = old_text.split()
    matcher = SequenceMatcher(None, old_tokens, new_tokens)
    highlighted = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            highlighted.extend(new_tokens[j1:j2])
        elif tag in ("replace", "insert"):
            chunk = " ".join(new_tokens[j1:j2])
            highlighted.append(f"<span class='good-token'>{chunk}</span>")
        elif tag == "delete":
            # nothing to add from new side
            continue

    return " ".join(highlighted)


def summary_bar(lang, steps):
    raw = steps.get("raw", "")
    spelling_changed = raw != steps.get("spelling", raw)
    grammar_changed = steps.get("spelling", raw) != steps.get("grammar", steps.get("spelling", raw))

    confidence = "High" if grammar_changed else "Medium"

    return f"""
    <div class="summary-bar">
        <span>🌍 Language: <b>{'English' if lang == 'en' else 'Türkçe'}</b></span>
        <span>✍️ Spelling: {'✓' if spelling_changed else '–'}</span>
        <span>📐 Grammar: {'✓' if grammar_changed else '–'}</span>
        <span>🧠 Confidence: {confidence}</span>
    </div>
    """


# ================= STREAMLIT SETUP =================
st.set_page_config(
    page_title="Multilingual Text Correction System",
    page_icon="✨",
    layout="wide"
)

@st.cache_resource
def load_pipeline():
    return TextCorrectionPipeline()

pipeline = load_pipeline()

# ================= CSS =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.summary-bar {
    background: white;
    padding: 1rem 1.5rem;
    border-radius: 14px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.1);
    display: flex;
    justify-content: space-between;
    font-weight: 600;
    margin-bottom: 1.5rem;
}

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
}

.input-card {
    background: white;
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
}

.step-card {
    background: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 1rem;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    border-left: 5px solid #667eea;
}

.step-header {
    font-size: 0.85rem;
    font-weight: 700;
    color: #666;
    margin-bottom: 0.8rem;
    text-transform: uppercase;
}

.step-content {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    font-size: 1.05rem;
}

.final-result {
    background: #edf2ff;
    font-weight: 600;
}

.bad-token {
    background: #ffe3e3;
    color: #c53030;
    padding: 0.1rem 0.3rem;
    border-radius: 6px;
}

.tag {
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 8px;
    font-size: 0.8rem;
}

.tag.grammar {
    background: #e9d8fd;
    color: #553c9a;
}

.good-token {
    background: #c6f6d5;
    color: #22543d;
    padding: 0.05rem 0.2rem;
    border-radius: 6px;
}

.before-after {
    display: flex;
    gap: 1rem;
    margin-top: 1rem;
}

.before, .after {
    flex: 1;
    padding: 1rem;
    border-radius: 12px;
}

.before {
    background: #fff5f5;
}

.after {
    background: #f0fff4;
}

.footer {
    text-align: center;
    color: #666;
    font-size: 0.85rem;
    margin-top: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ================= TITLE =================
st.markdown("""
<div class="title-card">
    <h1>✨ Multilingual Text Correction System</h1>
    <p>Language Detection • Spelling Correction • Grammar Refinement</p>
</div>
""", unsafe_allow_html=True)

# ================= INPUT =================
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Text Input")
    user_input = st.text_area(
        "input",
        height=260,
        placeholder="This sentnce have a mistake ve düzeltilmesi gerek.",
        label_visibility="collapsed"
    )
    run = st.button("✨ Metni Düzelt", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ================= PROCESS =================
if run and user_input:
    with st.spinner("🔮 Processing..."):
        steps, lang, error = pipeline.process(user_input)

    if not error:
        with col2:
            st.markdown(summary_bar(lang, steps), unsafe_allow_html=True)

            st.markdown("""
            <div class="step-card">
                <div class="step-header">Step 1 – Spelling</div>
                <div class="step-content">{}</div>
            </div>
            """.format(highlight_new_tokens(steps["spelling"], steps["raw"])), unsafe_allow_html=True)

            st.markdown("""
            <div class="step-card">
                <div class="step-header">Step 2 – Grammar</div>
                <div class="step-content">{}</div>
            </div>
            """.format(highlight_new_tokens(steps["grammar"], steps["spelling"])), unsafe_allow_html=True)

            st.markdown("""
            <div class="step-card">
                <div class="step-header">Final Output</div>
                <div class="step-content final-result">{}</div>
            </div>
            """.format(steps["final"]), unsafe_allow_html=True)
        with col1:
            st.markdown("### 🔍 Before / After")
            st.markdown(f"""
            <div class="before-after">
                <div class="before"><b>Before</b><br/>{user_input}</div>
                <div class="after"><b>After</b><br/>{steps["final"]}</div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### 🧭 Changes Applied")
            _, changes = diff_highlights(user_input, steps["final"])
            if changes:
                for c in changes:
                    st.markdown(f"- {c}", unsafe_allow_html=True)
            else:
                st.info("No changes detected.")

# ================= FOOTER =================
st.markdown("""
<hr/>
<div class="footer">
Multilingual Text Correction System<br/>
Computer Engineering – Graduation Project<br/>
© 2025
</div>
""", unsafe_allow_html=True)
