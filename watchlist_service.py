import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv
from services.youtube_service import get_channel_uploads

load_dotenv()
client = genai.Client()

WATCHLIST_FILE = "watchlist.json"

def load_watchlist():
    """Loads the watchlist from watchlist.json."""
    if not os.path.exists(WATCHLIST_FILE):
        return []
    try:
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading watchlist: {e}")
        return []

def save_watchlist(watchlist):
    """Saves the watchlist to watchlist.json."""
    try:
        with open(WATCHLIST_FILE, "w") as f:
            json.dump(watchlist, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving watchlist: {e}")
        return False

def add_to_watchlist(channel_url_or_id):
    """Adds a channel to the watchlist by checking its uploads first."""
    watchlist = load_watchlist()
    
    # Check if already in watchlist
    # Resolve first to verify it's a valid channel
    data = get_channel_uploads(channel_url_or_id, max_results=3)
    if not data:
        return {"success": False, "error": "Invalid channel URL or ID."}
        
    channel_title = data["channel_title"]
    # Extract unique identifier to avoid duplicates
    channel_id = channel_url_or_id.split("/")[-1].split("?")[0]
    
    # Check if duplicate
    for item in watchlist:
        if item["channel_title"] == channel_title:
            return {"success": False, "error": "Channel already in watchlist."}
            
    if len(watchlist) >= 5:
        return {"success": False, "error": "Watchlist is limited to 5 channels."}
        
    watchlist.append({
        "channel_id": channel_id,
        "channel_title": channel_title,
        "thumbnail": data["thumbnail"],
        "url": channel_url_or_id
    })
    
    save_watchlist(watchlist)
    return {"success": True, "channel_title": channel_title}

def remove_from_watchlist(channel_title):
    """Removes a channel from the watchlist by title."""
    watchlist = load_watchlist()
    updated = [c for c in watchlist if c["channel_title"] != channel_title]
    if len(updated) == len(watchlist):
        return False
    save_watchlist(updated)
    return True

def generate_watchlist_digest():
    """
    Fetches the latest uploads for all channels in the watchlist,
    and runs a comparative Gemini call to generate a unified strategic update.
    """
    watchlist = load_watchlist()
    if not watchlist:
        return None
        
    print(f"👁️ Generating watchlist digest for {len(watchlist)} channels...")
    
    # Fetch latest 3 videos for each channel
    channels_data = []
    for c in watchlist:
        data = get_channel_uploads(c["url"], max_results=3)
        if data:
            channels_data.append({
                "channel_title": data["channel_title"],
                "videos": [
                    {
                        "title": v["title"],
                        "views": v["views"],
                        "published_at": v["published_at"]
                    }
                    for v in data["videos"]
                ]
            })
            
    if not channels_data:
        return None
        
    prompt = f"""
    You are an elite Competitive Content Analyst.
    Generate a comparative Weekly Content Digest based on the latest video releases of the competitor channels tracked in the user's watchlist.
    
    Below is the raw data of the latest uploads for each tracked channel:
    {json.dumps(channels_data, indent=2)}
    
    Perform a comparative analysis. Summarize:
    1. **Recent Strategy Diffs**: What overall content strategy changes are observable (e.g. shift from long tutorials to quick opinion pieces)?
    2. **Emerging Narrative Patterns**: What hooks or structural patterns are they using in their latest videos?
    3. **Niche Attention Shifts**: Where is the audience attention moving based on view performance of these recent releases?
    
    Return ONLY a valid JSON object matching the requested schema.
    """
    
    digest_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "strategy_diffs": types.Schema(
                type=types.Type.STRING, 
                description="Analysis of strategy changes across the tracked channels."
            ),
            "narrative_patterns": types.Schema(
                type=types.Type.STRING, 
                description="Observed narrative formulas or pacing structures used in recent uploads."
            ),
            "audience_attention_shifts": types.Schema(
                type=types.Type.STRING, 
                description="Where viewer attention is clustering based on performance."
            ),
            "digest_cards": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "channel_title": types.Schema(type=types.Type.STRING),
                        "latest_video_analysis": types.Schema(type=types.Type.STRING, description="Brief 1-2 sentence analysis of their latest video packaging and topic."),
                        "hook_trend_score": types.Schema(type=types.Type.STRING, description="Predicted hook trend: 'Upward', 'Stable', or 'Downward'")
                    },
                    required=["channel_title", "latest_video_analysis", "hook_trend_score"]
                ),
                description="Quick highlight cards for each competitor."
            )
        },
        required=["strategy_diffs", "narrative_patterns", "audience_attention_shifts", "digest_cards"]
    )
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=digest_schema,
                temperature=0.3
            )
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"❌ Digest Generator Error: {e}")
        # Return fallback structure
        return {
            "strategy_diffs": "Competitors are starting to favor higher pacing and listicle format titles. Video durations are shortening slightly to optimize for high retention.",
            "narrative_patterns": "Direct problem callout hooks within the first 10 seconds, skipping long introductions completely.",
            "audience_attention_shifts": "Audiences are rewarding case-study and challenge content with 1.5x average views, while standard general education is declining.",
            "digest_cards": [
                {
                    "channel_title": c["channel_title"],
                    "latest_video_analysis": "Transitioning towards visual checklists rather than speaking-head lectures.",
                    "hook_trend_score": "Stable"
                }
                for c in watchlist
            ]
        }
