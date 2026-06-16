import streamlit as st
import json
from services.youtube_service import extract_video_id, get_video_metadata, get_latest_video_from_channel
from services.transcript_service import get_transcript
from services.topic_detector import detect_topic
from services.benchmark_finder import get_benchmark_candidates
from services.similarity_engine import rank_benchmarks
from services.gap_analyzer import analyze_gaps

# --- ENGINE CONFIGURATION & RESET ---
st.set_page_config(
    page_title="Content DNA Engine — Elite Script Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- PREMIUM ADVANCED SKILL INJECTION LAYER (UI OVERHAUL) ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght=200;300;400;500;600&display=swap" rel="stylesheet">
    
    <style>
    /* Remove native blocky margins and set deep minimalist dark background */
    .stApp {
        background: linear-gradient(180deg, #07090C 0%, #0D1117 100%) !important;
        color: #E2E8F0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Make the core container narrow and elegant like an editorial column */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 5rem !important;
        max-width: 1100px !important;
    }

    /* Headings styling */
    .serif-hero-title {
        font-family: 'Playfair Display', serif !important;
        font-weight: 400;
        font-size: 3.8rem !important;
        line-height: 1.15 !important;
        color: #FFFFFF !important;
        letter-spacing: -0.02em;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    
    .serif-section-title {
        font-family: 'Playfair Display', serif !important;
        font-weight: 400;
        font-size: 2.3rem !important;
        line-height: 1.25 !important;
        color: #FFFFFF !important;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .gold-label {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.75rem !important;
        letter-spacing: 0.35em !important;
        color: #C5A059 !important;
        text-transform: uppercase;
        display: block;
    }
    
    .editorial-number {
        font-family: 'Playfair Display', serif;
        font-size: 7.5rem;
        font-weight: 700;
        color: rgba(197, 160, 89, 0.04);
        line-height: 0.8;
        margin-bottom: -2rem;
        user-select: none;
    }
    
    .editorial-body {
        font-size: 1.02rem;
        line-height: 1.85;
        color: #94A3B8;
        font-weight: 300;
        margin-bottom: 1.5rem;
    }
    
    /* Premium Glassmorphic floating card blocks for layout segments */
    .premium-card {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        border-radius: 12px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3) !important;
    }

    .dna-pill {
        background: rgba(197, 160, 89, 0.03);
        border: 1px solid rgba(197, 160, 89, 0.1);
        border-left: 3px solid #C5A059;
        padding: 12px 18px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.92rem;
    }

    /* Completely redesigning native Streamlit UI elements to match dark theme */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.06) !important;
        border-radius: 50px !important; /* Pill shaped input launcher */
        padding: 8px 16px 8px 24px !important;
    }
    
    div[data-testid="stForm"] input {
        color: #FFFFFF !important;
        background-color: transparent !important;
        border: none !important;
    }
    
    div[data-testid="stForm"] button {
        background-color: #C5A059 !important;
        color: #0A0D10 !important;
        font-weight: 600 !important;
        letter-spacing: 0.05em !important;
        border-radius: 30px !important;
        border: none !important;
        transition: all 0.2s ease;
    }
    
    div[data-testid="stForm"] button:hover {
        background-color: #DFB873 !important;
        transform: scale(1.02);
    }

    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.01) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        margin-bottom: 0.8rem !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- WORKER CONTEXT CONTAINER (PREVENTS UI THREAD FREEZES) ---
def execute_pipeline(url_path):
    """Safely handles data pipeline orchestration outside Streamlit's state loops."""
    
    # NEW INTELLIGENCE CHECK: Intercept and find the latest video if given a channel link
    if "/channel/" in url_path or "/@" in url_path:
        video_id = get_latest_video_from_channel(url_path)
    else:
        # Standard video ID extraction
        video_id = extract_video_id(url_path)
        
    if not video_id:
        return {"error": "Could not extract or locate a valid video upload from this link."}
        
    metadata = get_video_metadata(video_id)
    raw_views = metadata.get("views", metadata.get("Views", 0))
    
    transcript = get_transcript(video_id)
    if not transcript:
        return {"error": "Video script transcript is unreadable or restricted."}
        
    dna = detect_topic(transcript, metadata=metadata)
    benchmarks = get_benchmark_candidates(
        topic=dna.get("topic"),
        subtopic=dna.get("subtopic"),
        intent=dna.get("intent"),
        audience=dna.get("audience"),
        current_video_views=raw_views,
        user_title=metadata.get("title", "N/A"),
        user_description=metadata.get("description", "")
    )
    
    ranked = rank_benchmarks(
        user_title=metadata.get("title", "N/A"),
        topic=dna.get("topic"),
        subtopic=dna.get("subtopic"),
        intent=dna.get("intent"),
        benchmark_results=benchmarks
    )
    
    report = analyze_gaps(metadata, transcript, benchmarks)
    
    return {
        "metadata": metadata,
        "views": raw_views,
        "dna": dna,
        "benchmarks": benchmarks,
        "ranked": ranked,
        "report": report
    }


# --- LANDING PAGE GRAPHIC ARRAYS ---
st.markdown("<span class='gold-label'>—— A CONTENT DNA ENGINE GUIDE</span>", unsafe_allow_html=True)
st.markdown("<h1 class='serif-hero-title'>Be Prepared For The<br>Algorithm And Beyond</h1>", unsafe_allow_html=True)

# Pill-shaped Launcher Input Bar
with st.form(key="pipeline_input_portal", clear_on_submit=False):
    col_in, col_btn = st.columns([3.5, 1])
    with col_in:
        url_input = st.text_input(
            "Gateway Path", 
            placeholder="Paste video link or channel handle directly...", 
            label_visibility="collapsed"
        )
    with col_btn:
        trigger_pipeline = st.form_submit_button(label="RUN PIPELINE →")

# --- CORE RENDER STREAM ---
if trigger_pipeline and url_input:
    with st.spinner("⚡ Extracting metrics & indexing competitive layers..."):
        res = execute_pipeline(url_input)
        
    if "error" in res:
        st.error(f"⚠️ Initialization Error: {res['error']}")
    else:
        st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05); margin-bottom: 3.5rem;'>", unsafe_allow_html=True)
        
        # --- SECTION 01: CREATOR IDENTITY ---
        c1_left, c1_right = st.columns([1.1, 1])
        with c1_left:
            st.markdown("<div class='editorial-number'>01</div>", unsafe_allow_html=True)
            st.markdown("<span class='gold-label'>NARRATIVE IDENTITY PROFILE</span>", unsafe_allow_html=True)
            st.markdown("<h2 class='serif-section-title'>What level of Creator DNA are you?</h2>", unsafe_allow_html=True)
            st.markdown(
                "<p class='editorial-body'>Understanding your core creative blueprint is the single most important step when scaling "
                "an audience. The Content DNA Profiler parses spoken transcripts to isolate your target audience "
                "and narrative archetype, checking if your production style matches the core expectations of your viewers.</p>", 
                unsafe_allow_html=True
            )
            st.markdown(f"<p style='font-size:0.9rem; color:#C5A059;'><b>Active Target:</b> {res['metadata'].get('title')} <br><b>Performance Baseline:</b> {res['views']:,} views</p>", unsafe_allow_html=True)
        
        with c1_right:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>🎯 Target Market Vector (Topic):</b> {res['dna'].get('topic')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>🔍 Core Subtopic Niche:</b> {res['dna'].get('subtopic')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>⚡ Viewer Intent Framework:</b> {res['dna'].get('intent')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>🎭 Primary Creator Archetype:</b> {res['dna'].get('creator_archetype')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>👥 Intentional Target Audience:</b> {res['dna'].get('audience')}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='dna-pill'><b>🎬 Narrative Blueprint Style:</b> {res['dna'].get('content_style')}</div>", unsafe_allow_html=True)

        st.markdown("<br><br><br>", unsafe_allow_html=True)

        # --- SECTION 02: RETRIEVAL MATRIX ---
        c2_left, c2_right = st.columns([1, 1.1])
        with c2_left:
            st.markdown("<br><br><br>", unsafe_allow_html=True)
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            col_p, col_e = st.columns(2)
            col_p.metric(label="Peer Group Channels Identified", value=len(res['benchmarks'].get('peers', [])))
            col_e.metric(label="Elite Scale Competitors", value=len(res['benchmarks'].get('elites', [])))
            st.markdown("</div>", unsafe_allow_html=True)
            
            for item in res['ranked'][:3]:
                st.markdown(f"<div style='font-size:0.88rem; opacity:0.75; margin-bottom:6px;'>📐 <b>[{item.get('similarity_score', 0)}% Relevance]</b> {item.get('title')[:60]}...</div>", unsafe_allow_html=True)
                
        with c2_right:
            st.markdown("<div class='editorial-number'>02</div>", unsafe_allow_html=True)
            st.markdown("<span class='gold-label'>COMPETITIVE RETRIEVAL SEPARATION</span>", unsafe_allow_html=True)
            st.markdown("<h2 class='serif-section-title'>Isolating the right Competitive Benchmarks</h2>", unsafe_allow_html=True)
            st.markdown(
                "<p class='editorial-body'>True audience growth doesn't happen by guessing in isolation; it happens by decoding the elite tier of "
                "your specific niche. Our Multi-Constraint Similarity Engine filters out formatting noise to map performance baselines "
                "belonging exclusively to creators winning your exact target audience's attention span.</p>", 
                unsafe_allow_html=True
            )

        st.markdown("<br><br><br>", unsafe_allow_html=True)

        # --- SECTION 03: THE REPORT MATRIX ---
        st.markdown("<div class='editorial-number'>03</div>", unsafe_allow_html=True)
        st.markdown("<span class='gold-label'>ARCHITECTURAL GAP AUDIT DELIVERABLES</span>", unsafe_allow_html=True)
        st.markdown("<h2 class='serif-section-title'>Understand Your Packaging & Structural Timing</h2>", unsafe_allow_html=True)
        st.markdown(
            "<p class='editorial-body' style='max-width: 750px;'>The final bridge to elite scale is eliminating structural friction "
            "points. The Strategic Gap Engine performs an intense script breakdown against the top benchmark matches to deliver explicit, "
            "actionable structural changes.</p>", 
            unsafe_allow_html=True
        )
        
        with st.expander("🛑 STRATEGIC PACKAGING & HIGH-CTR TITLE FRAMEWORKS", expanded=True):
            st.markdown("<div style='padding:12px;'>", unsafe_allow_html=True)
            st.write(res['report'].get('title_gap', {}).get('analysis', 'Analysis missing.'))
            st.markdown("<br><b>🔥 High-Click Alternative Variations:</b>", unsafe_allow_html=True)
            for suggestion in res['report'].get('title_gap', {}).get('actionable_suggestions', []):
                st.markdown(f"* `🌟 {suggestion}`")
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("🪝 RETENTION HOOK BLUEPRINT & TRANSCRIPT REWRITE", expanded=True):
            st.markdown("<div style='padding:12px;'>", unsafe_allow_html=True)
            st.write(res['report'].get('hook_gap', {}).get('analysis', 'Analysis missing.'))
            st.markdown("<br><b>📝 Full Structural Script Revision:</b>", unsafe_allow_html=True)
            st.code(res['report'].get('hook_gap', {}).get('fix', 'Rewrite blueprint missing.'), language="text")
            st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("📊 VALUE PACING DENSITY SEPARATION STRATEGY", expanded=True):
            st.markdown("<div style='padding:12px;'>", unsafe_allow_html=True)
            st.write(res['report'].get('structure_gap', {}).get('analysis', 'Analysis missing.'))
            st.markdown("<br><b>⚡ Optimization Roadmap:</b>", unsafe_allow_html=True)
            st.success(res['report'].get('structure_gap', {}).get('recommendation', 'Plan missing.'))
            st.markdown("</div>", unsafe_allow_html=True)

else:
    # Minimalist, clean image placeholder block matching editorial vibe
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.05); margin-bottom: 4rem;'>", unsafe_allow_html=True)
    img_col, txt_col = st.columns([1.2, 1])
    with img_col:
        st.image("https://images.unsplash.com/photo-1536240478700-b869070f9279?auto=format&fit=crop&w=1200&q=80")
    with txt_col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<span style='font-size: 0.75rem; letter-spacing: 0.25em; color: #475569;'>SYSTEM POSITIONING MATRIX</span>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-family: \"Playfair Display\", serif; font-size: 1.8rem; font-weight:400; color: #FFFFFF;'>Engine Standing By</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #64748B; font-weight: 300; font-size: 0.98rem; max-width: 420px; line-height:1.7;'>Feed an active public video path link into the input gateway block above to stream transcription records, isolate benchmarks, and unpack retention variables.</p>", unsafe_allow_html=True)

# Footer Layout
st.markdown("<br><br><br><br><hr style='border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
f_left, f_right = st.columns(2)
f_left.markdown("<p style='font-size: 0.75rem; color: #475569;'>ENGINE ARCHITECTURE: Python Integration Framework • Gemini AI Infrastructure Layer</p>", unsafe_allow_html=True)
f_right.markdown("<p style='font-size: 0.75rem; color: #475569; text-align: right;'>© 2026 Content DNA Intelligence. Editorial Visual Package Layout.</p>", unsafe_allow_html=True)