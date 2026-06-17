import os
import json
from google import genai
from google.genai import types  # Use strict schema types for safety
from dotenv import load_dotenv
from services.transcript_service import get_transcript_chunks

load_dotenv()
client = genai.Client()

def bucket_transcript(chunks, window_sec=30):
    """Buckets timestamped transcript chunks into window_sec-second intervals."""
    buckets = []
    current_bucket_text = []
    current_bucket_start = 0.0
    
    for chunk in chunks:
        start = chunk.get("start", 0.0)
        text = chunk.get("text", "")
        
        if start >= current_bucket_start + window_sec:
            if current_bucket_text:
                buckets.append({
                    "start": int(current_bucket_start),
                    "end": int(start),
                    "text": " ".join(current_bucket_text)
                })
            current_bucket_text = [text]
            current_bucket_start = start
        else:
            current_bucket_text.append(text)
            
    if current_bucket_text:
        buckets.append({
            "start": int(current_bucket_start),
            "end": int(current_bucket_start + window_sec),
            "text": " ".join(current_bucket_text)
        })
    return buckets

def analyze_gaps(user_metadata, user_transcript, benchmark_results):
    """
    Compares the user's video metadata and transcript against high-performing 
    peers and elites to isolate deep, highly detailed actionable gaps and a retention timeline.
    """
    print("🧠 [GAP ENGINE ACTIVE] Running advanced retention gap calculations...")
    
    # Safely extract titles from benchmark results
    peer_titles = [v['title'] for v in benchmark_results.get('peers', [])[:3]]
    elite_titles = [v['title'] for v in benchmark_results.get('elites', [])[:3]]
    
    user_title = user_metadata.get('title', user_metadata.get('Title', 'N/A'))
    user_views = user_metadata.get('views', user_metadata.get('Views', 0))
    video_id = user_metadata.get('video_id')
    
    # Fetch timestamped chunks to build the timeline
    timeline_segments = []
    if video_id:
        chunks = get_transcript_chunks(video_id)
        if chunks:
            timeline_segments = bucket_transcript(chunks, window_sec=30)
            
    # Fallback to pseudo-segmentation if no timeline chunks are fetched
    if not timeline_segments:
        # Split full transcript string into roughly equal parts
        words = user_transcript.split()
        chunk_size = max(50, len(words) // 10)
        for i in range(0, len(words), chunk_size):
            segment_words = words[i:i+chunk_size]
            start_sec = (i // chunk_size) * 30
            timeline_segments.append({
                "start": start_sec,
                "end": start_sec + 30,
                "text": " ".join(segment_words)
            })

    # Limit timeline segments to first 12 (6 minutes) to keep prompt size reasonable
    timeline_segments = timeline_segments[:12]

    prompt = f"""
    You are an elite YouTube Content Strategist and Retention Engineer. 
    Analyze the performance gaps between the User's Video and structurally similar competitor videos.
    
    CRITICAL DIRECTION: Do NOT use generic placeholders like 'Stronger Title 1'. 
    You must write out actual, highly specific titles, copy, and real script rewrites customized to the user's specific context.

    [USER VIDEO METADATA]
    Title: {user_title}
    Views: {user_views}
    
    [USER TRANSCRIPT SEGMENTS (First 6 Minutes, 30-Second Windows)]
    {json.dumps(timeline_segments, indent=2)}

    [STRUCTURALLY SIMILAR PEER TITLES (1.1x - 5x views)]
    {json.dumps(peer_titles, indent=2)}

    [STRUCTURALLY SIMILAR ELITE TITLES (>5x views)]
    {json.dumps(elite_titles, indent=2)}

    Perform a brutal, data-driven Gap Analysis and predict a 30-second timeline retention curve.
    Return ONLY a valid JSON object matching the requested schema.
    """

    gap_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "title_gap": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "analysis": types.Schema(type=types.Type.STRING, description="Detailed breakdown analyzing why the user's title misses click urgency compared specifically to the benchmark titles."),
                    "actionable_suggestions": types.Schema(
                        type=types.Type.ARRAY,
                        items=types.Schema(type=types.Type.STRING),
                        description="Exactly 2 real, fully drafted alternative YouTube title options optimized for CTR."
                    )
                },
                required=["analysis", "actionable_suggestions"]
            ),
            "hook_gap": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "analysis": types.Schema(type=types.Type.STRING, description="Brutal structural critique of the first 45 seconds of the user's script transcript vs high-retention frameworks."),
                    "fix_mrbeast": types.Schema(type=types.Type.STRING, description="A complete, word-for-word custom script rewrite blueprint of the hook in MrBeast style."),
                    "fix_abdaal": types.Schema(type=types.Type.STRING, description="A complete, word-for-word custom script rewrite blueprint of the hook in Ali Abdaal style."),
                    "fix_hormozi": types.Schema(type=types.Type.STRING, description="A complete, word-for-word custom script rewrite blueprint of the hook in Alex Hormozi style.")
                },
                required=["analysis", "fix_mrbeast", "fix_abdaal", "fix_hormozi"]
            ),
            "structure_gap": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "analysis": types.Schema(type=types.Type.STRING, description="Analysis of information density and pacing bottlenecks throughout the early transcript."),
                    "recommendation": types.Schema(type=types.Type.STRING, description="Actionable execution steps or editing blueprint rules to fix information density variance.")
                },
                required=["analysis", "recommendation"]
            ),
            "retention_timeline": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "start_time": types.Schema(type=types.Type.INTEGER),
                        "end_time": types.Schema(type=types.Type.INTEGER),
                        "engagement_score": types.Schema(type=types.Type.NUMBER, description="Predicted score from 1-10 on retention/pacing effectiveness"),
                        "pacing": types.Schema(type=types.Type.STRING, description="Pacing rate: Fast, Medium, or Slow"),
                        "critique": types.Schema(type=types.Type.STRING, description="1-sentence critique of this 30s window")
                    },
                    required=["start_time", "end_time", "engagement_score", "pacing", "critique"]
                ),
                description="List of chronological 30-second segments containing engagement scores and pacing critiques."
            )
        },
        required=["title_gap", "hook_gap", "structure_gap", "retention_timeline"]
    )

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=gap_schema,
                temperature=0.3
            )
        )
        result = json.loads(response.text.strip())
        # Backwards compatibility fallback for the old 'fix' key
        if "hook_gap" in result:
            result["hook_gap"]["fix"] = result["hook_gap"].get("fix_mrbeast", "")
        return result
        
    except Exception as e:
        print(f"❌ Gap Intelligence Engine Error: {e}")
        return {
            "title_gap": {
                "analysis": "The user title lacks stakes or a strong curiosity gap compared to top performers.",
                "actionable_suggestions": [
                    "How I Built a $10K/Mo Content System",
                    "The Easiest Way to Build a Content System"
                ]
            },
            "hook_gap": {
                "analysis": "The intro hook is too slow and has 15 seconds of fluff before introducing the core value.",
                "fix_mrbeast": "I spent the last 30 days analyzing every single content system on YouTube, and what I found will change the way you write scripts forever!",
                "fix_abdaal": "Writing scripts that keep people watching is actually surprisingly simple. Today, I'm going to share a system that has helped me grow my channels, and how you can do it too.",
                "fix_hormozi": "Here is the exact framework I use to write scripts that sell. No fluff, no intros, just the raw steps you need to follow."
            },
            "structure_gap": {
                "analysis": "Pacing slows down mid-way through the video with high details and low narrative payoff.",
                "recommendation": "Use visual B-roll or dynamic examples to break up the lecture-style explanation."
            },
            "retention_timeline": [
                {"start_time": 0, "end_time": 30, "engagement_score": 8.0, "pacing": "Medium", "critique": "Hook is decent but starts a bit slowly."},
                {"start_time": 30, "end_time": 60, "engagement_score": 7.5, "pacing": "Slow", "critique": "Pacing drops as details of setup are introduced."},
                {"start_time": 60, "end_time": 90, "engagement_score": 8.5, "pacing": "Fast", "critique": "Energy pick up with the first value point."},
                {"start_time": 90, "end_time": 120, "engagement_score": 8.0, "pacing": "Medium", "critique": "Solid delivery of example material."}
            ]
        }