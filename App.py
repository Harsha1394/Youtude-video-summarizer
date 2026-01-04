# Install dependencies before running:
# pip install streamlit youtube-transcript-api transformers torch

import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

# ---------------- Functions ----------------
def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript])
        return text
    except Exception as e:
        st.error(f"Error fetching transcript: {e}")
        return None

# Cache the summarizer model so it loads only once
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="facebook/bart-large-cnn")

summarizer = load_summarizer()

def summarize_text(text, length="Medium", max_chunk=500):
    length_settings = {
        "Short": {"max_length": 60, "min_length": 20},
        "Medium": {"max_length": 120, "min_length": 40},
        "Long": {"max_length": 200, "min_length": 80},
    }
    settings = length_settings.get(length, length_settings["Medium"])

    chunks = [text[i:i+max_chunk] for i in range(0, len(text), max_chunk)]
    summaries = []

    for chunk in chunks:
        summary = summarizer(
            chunk,
            max_length=settings["max_length"],
            min_length=settings["min_length"],
            do_sample=False
        )
        summaries.append(summary[0]['summary_text'])

    return " ".join(summaries)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="YouTube Summarizer", page_icon="🎬", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background: linear-gradient(to right, #1f1c2c, #928dab);
        color: white;
    }
    .stTextInput > div > div > input {
        background-color: #f0f0f0;
        border-radius: 10px;
    }
    .stSelectbox > div > div {
        background-color: #f0f0f0;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        font-size: 16px;
        padding: 0.5em 1em;
    }
    </style>
""", unsafe_allow_html=True)

# Title and subtitle
st.markdown("<h1 style='text-align: center; color: white;'>YouTube Video Summarizer</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #ddd;'>Paste a YouTube link and choose summary length.</p>", unsafe_allow_html=True)

# Input layout
col1, col2 = st.columns([2,1])

with col1:
    url = st.text_input("🔗 Enter YouTube Video Link:")

with col2:
    length_option = st.selectbox("📏 Choose summary length:", ["Short", "Medium", "Long"])

# Summarize button
if st.button("✨ Summarize Video"):
    if url:
        if "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        else:
            st.error("Invalid YouTube URL format.")
            st.stop()

        st.info("Fetching transcript...")
        transcript_text = get_transcript(video_id)

        if transcript_text:
            st.info("Generating summary...")
            summary = summarize_text(transcript_text, length=length_option)
            st.success("Summary generated successfully!")

            st.markdown("### 📌 Video Summary")
            st.markdown(f"<div style='background-color:#2c2c54; padding:15px; border-radius:10px; color:white;'>{summary}</div>", unsafe_allow_html=True)

            # 📥 Download button
            st.download_button(
                label="📥 Download Summary as .txt",
                data=summary,
                file_name="video_summary.txt",
                mime="text/plain"
            )
    else:
        st.warning("Please enter a YouTube link.")