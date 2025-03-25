import streamlit as st
import requests
import re

# Hugging Face API details
API_URL = "https://router.huggingface.co/hf-inference/models/phishbot/ScamLLM"
HF_API_KEY = "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"  # Replace with your actual API key

# Authorization header
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# Model Label Mapping
LABEL_MAPPING = {
    "LABEL_0": "Not a Scam",
    "LABEL_1": "Scam"
}

# Function to analyze text
def analyze_text(input_text):
    if not input_text.strip():
        return "Please enter text", 0.0

    payload = {"inputs": input_text}
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        result = response.json()
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
            result = result[0]

        best_match = max(result, key=lambda x: x["score"])
        readable_label = LABEL_MAPPING.get(best_match["label"], "Unknown")
        return readable_label, best_match["score"]
    
    return "API Error", 0.0

# Function to detect URLs and Emails
def detect_links_emails(text):
    url_pattern = re.compile(r"https?://[^\s]+|www\.[^\s]+")
    email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    
    urls = url_pattern.findall(text)
    emails = email_pattern.findall(text)
    
    return {"urls": urls, "emails": emails}

# Function to check suspicious URLs
def is_suspicious_url(url):
    suspicious_patterns = ["free", "win", "claim", "click", "verify", "login", "secure", "bank", "update"]
    for word in suspicious_patterns:
        if word in url.lower():
            return True
    return False

# Streamlit UI
st.set_page_config(page_title="Scam Detector", page_icon="🔍", layout="centered")

st.title("🔍 Scam Detection App")
st.write("Enter a text below to check if it's a scam or not.")

# User input box
user_input = st.text_area("Enter text to analyze:", value="", height=150)

# Auto-analyze option
auto_check = st.checkbox("Auto-analyze while typing")

if auto_check or st.button("Analyze"):
    prediction, confidence = analyze_text(user_input)

    # Confidence bar
    st.progress(confidence)

    # Display result
    if prediction == "Scam":
        st.error(f"🚨 **Prediction: {prediction}** (Confidence: {confidence:.2%})")
    elif prediction == "Not a Scam":
        st.success(f"✅ **Prediction: {prediction}** (Confidence: {confidence:.2%})")
    else:
        st.warning(f"⚠️ {prediction}")

    # Check for URLs & Emails
    detected = detect_links_emails(user_input)
    url_warning = any(is_suspicious_url(url) for url in detected["urls"])

    if detected["urls"]:
        st.warning(f"🔗 **Detected URLs:** {', '.join(detected['urls'])}")
        if url_warning:
            st.error("🚨 **Suspicious URL detected! Be careful before clicking.**")

    if detected["emails"]:
        st.warning(f"📧 **Detected Emails:** {', '.join(detected['emails'])}")
