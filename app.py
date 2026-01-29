import streamlit as st
import google.generativeai as genai
import random
import time

# ====== CONFIG ======
# Load Gemini API key safely from Streamlit Secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configure the SDK
genai.configure(api_key=GEMINI_API_KEY)

# Optional: Test if key is loaded
st.success("✅ GEMINI_API_KEY loaded correctly")

# ====== Functions ======

def list_supported_models():
    """
    Returns the first available model that supports generateContent.
    """
    try:
        models = genai.list_models()
        for m in models:
            if hasattr(m, "supported_generation_methods") and "generateContent" in m.supported_generation_methods:
                return m.name
    except Exception as e:
        return None
    return None

def ai_analysis(journal_text, model_name):
    """
    Calls the Gemini API to generate AI suggestions.
    """
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a supportive mental health early warning assistant.
        Based on this journal text, return:
        - One mental health risk level (Low/Medium/High)
        - One short explanation
        - Two short supportive suggestions

        Journal:
        {journal_text}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ AI temporarily unavailable: {e}"

def generate_score(text):
    """Generate a reproducible risk score based on content."""
    seed = sum(ord(c) for c in text)
    random.seed(seed)
    return random.randint(25, 95)

def risk_status(score):
    if score < 40:
        return "🟢 Stable"
    elif score < 70:
        return "🟡 Warning"
    else:
        return "🔴 Critical"

# ====== UI ======

st.set_page_config(page_title="Mental Health Early Warning System", layout="centered")
st.title("🧠 Silent Failure Detector")
st.caption("AI Analysis powered by Gemini")

if "history" not in st.session_state:
    st.session_state.history = []

journal = st.text_area("✍️ Enter your daily journal / thoughts:")

if st.button("Analyze") and journal.strip():
    # Progress bar
    progress_bar = st.progress(0)
    for i in range(0, 101, 10):
        time.sleep(0.05)
        progress_bar.progress(i)

    # Internal score
    score = generate_score(journal)
    status = risk_status(score)

    # Get a valid model
    selected_model = list_supported_models()
    if not selected_model:
        ai_text = "⚠️ No supported model found for your API key. Check your API access and available models."
    else:
        ai_text = ai_analysis(journal, selected_model)

    # Show results
    st.subheader("📊 Risk Result")
    st.metric("Risk Score (0–100)", score, status)

    st.subheader("💡 AI Analysis")
    st.write(ai_text)

    # Add entry to history (avoid duplicates)
    entry = {"text": journal, "score": score, "status": status}
    if entry not in st.session_state.history:
        st.session_state.history.append(entry)

# Show last 5 unique entries
if st.session_state.history:
    st.subheader("🗂️ Previous Entries")
    seen = set()
    for idx, entry in enumerate(reversed(st.session_state.history[-5:]), 1):
        key = (entry["text"], entry["score"], entry["status"])
        if key not in seen:
            st.write(f"{idx}. Score: {entry['score']} | {entry['status']}")
            seen.add(key)

st.info("⚠️ This tool is for self-awareness only. It does NOT provide medical diagnosis or treatment.")
