import os
import json
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

# Local hardcoded backup map ONLY used as a emergency fallback
FALLBACK_CATEGORY_MAP = {
    "1": {"topic": "Creative & Cinema", "subtopic": "Animation & Film", "archetype": "Director", "intent": "Storytelling"},
    "10": {"topic": "Entertainment", "subtopic": "Music & Performance", "archetype": "Artist", "intent": "Entertainment"},
    "17": {"topic": "Sports", "subtopic": "Match Highlights & Athletics", "archetype": "Commentator", "intent": "Entertainment"},
    "20": {"topic": "Gaming", "subtopic": "Gameplay & Lore", "archetype": "Gamer", "intent": "Entertainment"},
    "22": {"topic": "Lifestyle & Vlogging", "subtopic": "Personal Vlogs", "archetype": "Casual Storyteller", "intent": "Emotional Resonance"},
    "24": {"topic": "Entertainment", "subtopic": "Pop Culture Commentary", "archetype": "Commentator", "intent": "Storytelling"},
    "26": {"topic": "Creative Fields", "subtopic": "Video Editing & Design", "archetype": "Teacher", "intent": "Educational"},
    "27": {"topic": "Education", "subtopic": "Learning & Explainers", "archetype": "Educator", "intent": "Educational"},
    "28": {"topic": "Technology", "subtopic": "Coding & Software", "archetype": "Peer Programmer", "intent": "Educational"}
}

def _local_fallback_detector(transcript, category_id):
    """Indestructible local execution when Gemini is unavailable."""
    print("⚠️ [FALLBACK ACTIVE] Gemini unavailable. Running local heuristic profiles...")
    cat_str = str(category_id) if category_id else "27"
    
    base_dna = FALLBACK_CATEGORY_MAP.get(cat_str, {
        "topic": "General Content", 
        "subtopic": "General Discussion", 
        "archetype": "Educator", 
        "intent": "Educational"
    })
    
    text = transcript.lower()
    lessons_count = len(re.findall(r'\b\d+\b', text[:3000]))
    content_format = "Listicle" if lessons_count >= 5 else "Essay"
    
    return {
        "topic": base_dna["topic"],
        "subtopic": base_dna["subtopic"],
        "intent": base_dna["intent"],
        "creator_archetype": base_dna["archetype"],
        "audience": "General Niche Viewers",
        "format": content_format,
        "content_style": f"Standard {content_format}"
    }

def detect_topic(transcript, metadata=None):
    """
    Primary: Gemini Intelligence Layer. Dynamically infers exact video DNA 
    regardless of edge cases (MrBeast, IPL, Vlogs, Coding).
    Secondary: Gracefully falls back to local Python heuristics on 503/network errors.
    """
    user_title = metadata.get("title", "Unknown Title") if metadata else "Unknown Title"
    user_desc = metadata.get("description", "") if metadata else ""
    category_id = metadata.get("category_id", None) if metadata else None

    print(f"🤖 [DNA PROFILER] Running Gemini Context Engine for: '{user_title}'")

    prompt = f"""
    You are an elite YouTube Content Architect. Analyze the following video assets (Title, Description, and Transcript).
    Extract its absolute core DNA attributes. You must handle any niche accurately (Sports, Gaming, Music, Vlogs, Tech, Commentary).

    [VIDEO METADATA]
    Title: {user_title}
    Description: {user_desc}

    [TRANSCRIPT SNIPPET]
    {transcript[:7000]}

    Return ONLY a valid JSON object matching this exact schema:
    {{
        "topic": "The macro niche or industry (e.g., Sports, Personal Development, Entertainment, Technology)",
        "subtopic": "The micro domain focus (e.g., Cricket Match Highlights, Introspective Essays, Coding Tutorials)",
        "intent": "Primary viewer motivation (e.g., Entertainment, Educational, Emotional Resonance, Motivational)",
        "creator_archetype": "The host profile framework (e.g., The Analyst, The Introspective Essayist, The Entertainer, The Mentor)",
        "audience": "Brief target user persona description (e.g., Cricket enthusiasts, 21-year old solo creators)",
        "format": "Structural core layout (e.g., Commentary, Listicle, Essay, Review, Gameplay)",
        "content_style": "Visual/narrative signature (e.g., High-energy rapid cuts, Aesthetic mood-driven pacing, Textual screen code-along)"
    }}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        )
        return json.loads(response.text.strip())
        
    except Exception as e:
        print(f"❌ Gemini Connection Traffic Spike ({e}). Diverting to backup algorithms...")
        return _local_fallback_detector(transcript, category_id)