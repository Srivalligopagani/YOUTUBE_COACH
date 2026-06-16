import os
import json
from google import genai
from google.genai import types  # Use strict schema types for safety
from dotenv import load_dotenv

load_dotenv()
client = genai.Client()

def analyze_gaps(user_metadata, user_transcript, benchmark_results):
    """
    Compares the user's video metadata and transcript against high-performing 
    peers and elites to isolate deep, highly detailed actionable gaps.
    """
    print("🧠 [GAP ENGINE ACTIVE] Running advanced retention gap calculations...")
    
    # Safely extract titles from benchmark results
    peer_titles = [v['title'] for v in benchmark_results.get('peers', [])[:3]]
    elite_titles = [v['title'] for v in benchmark_results.get('elites', [])[:3]]
    
    user_title = user_metadata.get('title', user_metadata.get('Title', 'N/A'))
    user_views = user_metadata.get('views', user_metadata.get('Views', 0))

    prompt = f"""
    You are an elite YouTube Content Strategist and Retention Engineer. 
    Analyze the performance gaps between the User's Video and structurally similar competitor videos.
    
    CRITICAL DIRECTION: Do NOT use generic placeholders like 'Stronger Title 1' or 'Provide an asset fix'. 
    You must write out actual, highly specific titles, copy, and real script rewrites customized to the user's specific context.

    [USER VIDEO METADATA]
    Title: {user_title}
    Views: {user_views}
    
    [USER TRANSCRIPT SNIPPET (First 5 Minutes)]
    {user_transcript[:6000]}

    [STRUCTURALLY SIMILAR PEER TITLES (1.1x - 5x views)]
    {json.dumps(peer_titles, indent=2)}

    [STRUCTURALLY SIMILAR ELITE TITLES (>5x views)]
    {json.dumps(elite_titles, indent=2)}

    Perform a brutal, data-driven Gap Analysis. Return ONLY a valid JSON object matching the requested schema.
    """

    # Forcing detailed property rules using Schema constraints stops the AI from getting lazy
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
                        description="Exactly 2 real, fully drafted alternative YouTube title options optimized for CTR. No placeholders allowed."
                    )
                },
                required=["analysis", "actionable_suggestions"]
            ),
            "hook_gap": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "analysis": types.Schema(type=types.Type.STRING, description="Brutal structural critique of the first 45 seconds of the user's script transcript vs high-retention frameworks."),
                    "fix": types.Schema(type=types.Type.STRING, description="A complete, word-for-word custom script rewrite blueprint for the user's opening hook that fixes the drop-off problem.")
                },
                required=["analysis", "fix"]
            ),
            "structure_gap": types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "analysis": types.Schema(type=types.Type.STRING, description="Analysis of information density and pacing bottlenecks throughout the early transcript."),
                    "recommendation": types.Schema(type=types.Type.STRING, description="Actionable execution steps or editing blueprint rules to fix information density variance.")
                },
                required=["analysis", "recommendation"]
            )
        },
        required=["title_gap", "hook_gap", "structure_gap"]
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
        return json.loads(response.text.strip())
        
    except Exception as e:
        print(f"❌ Gap Intelligence Engine Error: {e}")
        return None