import streamlit as st
import google.generativeai as genai
import random
import time

# ====== CONFIG ======
# Replace with your real Gemini API key:
GEMINI_API_KEY = "AIzaSyD1coo3UsCfvJAZqpxPMothjoAXfmhqCO0"

# Configure the SDK
genai.configure(api_key="AIzaSyD1coo3UsCfvJAZqpxPMothjoAXfmhqCO0")


# ====== Functions ======

def list_supported_models():
    """
    List models that support generateContent dynamically
    and return the first available one.
    """
    try:
        available = genai.list_models()
        for m in available:
            # There can be supported_generation_methods containing "generateContent"
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
        # call the model
        response = model.generate_content(prompt)
        return response.text

    except Exception as e:
        return f"⚠️ AI temporarily unavailable: {e}"


def generate_score(text):
    """
    Generate a reproducible risk score based on content.
    """
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

analyze_btn = st.button("Analyze")

if analyze_btn and journal.strip():

    # progress
    progress_bar = st.progress(0)
    for i in range(0, 101, 10):
        time.sleep(0.05)
        progress_bar.progress(i)

    # internal score
    score = generate_score(journal)
    status = risk_status(score)

    # list models and pick one
    selected_model = list_supported_models()
    if not selected_model:
        ai_text = "⚠️ Could not find a supported model. Try again later."
    else:
        ai_text = ai_analysis(journal, selected_model)

    # results
    st.subheader("📊 Risk Result")
    st.metric("Risk Score (0–100)", score, status)

    st.subheader("💡 AI Analysis")
    st.write(ai_text)

    st.session_state.history.append({
        "text": journal,
        "score": score,
        "status": status
    })

# history
if st.session_state.history:
    st.subheader("🗂️ Previous Entries")
    for idx, entry in enumerate(reversed(st.session_state.history[-5:]), 1):
        st.write(f"{idx}. Score: {entry['score']} | {entry['status']}")
st.info("⚠️ This tool is for self-awareness only. It does NOT provide medical diagnosis or treatment.")

