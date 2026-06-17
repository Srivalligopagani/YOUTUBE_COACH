import streamlit as st
from services.youtube_service import extract_video_id, get_video_metadata, get_latest_video_from_channel
from services.transcript_service import get_transcript
from services.topic_detector import detect_topic
from services.benchmark_finder import get_benchmark_candidates
from services.similarity_engine import rank_benchmarks
from services.gap_analyzer import analyze_gaps

# --- ENGINE CONFIGURATION & RESET ---
st.set_page_config(
    page_title="RIVALREACH — Script Intelligence Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- WORKSTATION CYBERPUNK CSS LAYER ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
    /* Main Workspace Canvas Override */
    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
        font-family: 'Space Grotesk', sans-serif !important;
    }
    
    /* Strict Width Container Lock */
    .block-container {
        padding-top: 3rem !important;
        padding-bottom: 5rem !important;
        max-width: 1300px !important;
    }
    
    /* Top Header Navigation Matrix */
    .brand-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 4rem;
    }
    
    .brand-logo {
        font-size: 1.4rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: #FFFFFF;
    }
    
    .brand-logo span {
        color: #A78BFA;
    }
    
    .pill-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #A78BFA;
        border: 1px solid rgba(139, 92, 246, 0.3);
        padding: 6px 14px;
        border-radius: 4px;
        background: rgba(139, 92, 246, 0.05);
    }
    
    /* Giant Hero Core Branding Layout */
    .hero-center {
        text-align: center;
        margin-bottom: 4rem;
    }
    
    .hero-tags {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #6D28D9;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
    
    .hero-main-title {
        font-size: 5rem;
        font-weight: 700;
        line-height: 0.9;
        letter-spacing: -0.04em;
        color: #FFFFFF;
        margin: 0;
        text-transform: uppercase;
    }
    
    .hero-shadow-title {
        font-size: 5rem;
        font-weight: 700;
        line-height: 0.9;
        letter-spacing: -0.04em;
        color: transparent;
        -webkit-text-stroke: 1px rgba(255, 255, 255, 0.15);
        text-transform: uppercase;
        margin-top: -5px;
    }
    
    /* Station Tab Switches Matrix */
    .station-btn {
        background: #8B5CF6;
        color: #FFFFFF;
        text-align: center;
        padding: 14px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        border-radius: 4px;
        margin-bottom: 3rem;
    }
    
    .station-btn-inactive {
        background: #2E2547;
        color: #A78BFA;
        opacity: 0.7;
    }

    /* Section Label Systems */
    .meta-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #6D28D9;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 2rem;
        letter-spacing: -0.02em;
    }
    
    /* Cyber Performance Cards */
    .cyber-card {
        background: #09090B;
        border: 1px solid #1E1B4B;
        border-radius: 4px;
        padding: 20px;
        margin-bottom: 1rem;
    }
    
    .cyber-card-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #4B5563;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
            
    .cyber-card-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-top: 4px;
    }

    /* Streamlit Native Input Form Remapping */
    div[data-testid="stForm"] {
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    div[data-testid="stForm"] input {
        background-color: #09090B !important;
        color: #FFFFFF !important;
        border: 1px solid #1F2937 !important;
        border-radius: 4px !important;
        padding: 12px 16px !important;
        font-family: 'JetBrains Mono', monospace;
    }
    
    div[data-testid="stForm"] button {
        background-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.05em !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 12px 28px !important;
        width: 100% !important;
    }
    
    div[data-testid="stForm"] button:hover {
        background-color: #7C3AED !important;
    }

    div[data-testid="stExpander"] {
        background: #050507 !important;
        border: 1px solid #1E1B4B !important;
        border-radius: 4px !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- BACKGROUND PROCESSING FUNCTION ---
def run_pipeline(url_path):
    if "/channel/" in url_path or "/@" in url_path:
        video_id = get_latest_video_from_channel(url_path)
    else:
        video_id = extract