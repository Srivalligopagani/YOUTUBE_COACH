import os
from services.youtube_service import (
    extract_video_id,
    get_video_metadata
)
from services.transcript_service import (
    get_transcript
)
from services.topic_detector import (
    detect_topic
)
from services.benchmark_finder import (
    get_benchmark_candidates
)
from services.similarity_engine import (
    rank_benchmarks
)
from services.gap_analyzer import (
    analyze_gaps
)

def render_beautiful_report(report):
    """Parses the gap engine dictionary and renders a readable human strategy report."""
    print("\n🔥 ========================================================")
    print("🔥                  COMPETITIVE GAP REPORT                ")
    print("🔥 ========================================================")

    if not report or not isinstance(report, dict):
        print("❌ Error: Report data is unreadable or empty.")
        print("===========================================================")
        return

    # 1. Title Packaging Segment
    title_data = report.get("title_gap", {})
    print("\n🛑 1. TITLE & PACKAGING ANALYSIS:")
    print(f"   {title_data.get('analysis', 'Analysis missing.')}")
    print("\n   💡 Optimized Strategy Variations:")
    suggestions = title_data.get("actionable_suggestions", [])
    if suggestions:
        for alt in suggestions:
            print(f"     👉 {alt}")
    else:
        print("     👉 No alternative suggestions provided.")

    print("\n" + "-" * 50)

    # 2. Hook and Script Execution Segment
    hook_data = report.get("hook_gap", {})
    print("\n🪝 2. HOOK & RETENTION FLOW GAP:")
    print(f"   {hook_data.get('analysis', 'Analysis missing.')}")
    print("\n   🛠️ Script Revision Architecture:")
    # Ensure nested rewrites display nicely if they have newlines
    fix_text = hook_data.get('fix', 'Blueprint missing.')
    for line in fix_text.split('\n'):
        print(f"     {line}")

    print("\n" + "-" * 50)

    # 3. Structural Pacing Segment
    struct_data = report.get("structure_gap", {})
    print("\n📊 3. VALUE DENSITY & PACING SEPARATION:")
    print(f"   {struct_data.get('analysis', 'Analysis missing.')}")
    print(f"\n   ⚡ Strategic Implementation Plan:\n     {struct_data.get('recommendation', 'Plan missing.')}")
    
    print("\n===========================================================")

def main():
    # 1. Capture and Validate YouTube Link
    url = input("Enter YouTube URL: ")
    video_id = extract_video_id(url)

    if not video_id:
        print("❌ Invalid URL execution halted.")
        return

    # 2. Extract Basic Video Metrics
    metadata = get_video_metadata(video_id)
    print("\n📦 --- LIVE VIDEO METADATA LOGGED ---")
    print("-" * 40)
    
    # Safely handle the correct key naming conventions
    raw_views = metadata.get("views", metadata.get("Views", 0))
    user_title = metadata.get("title", metadata.get("Title", "Unknown Title"))
    user_desc = metadata.get("description", metadata.get("Description", ""))
    
    print(f"Title:       {user_title}")
    print(f"Views:       {raw_views:,}")
    print(f"Category ID: {metadata.get('category_id', metadata.get('categoryId', 'N/A'))}")

    # 3. Stream and Load the Script Transcript
    transcript = get_transcript(video_id)
    if not transcript:
        print("❌ Transcript unavailable. Analysis cannot proceed without raw copy content.")
        return

    print("\n📑 --- FETCHING TRANSCRIPT STREAM ---")
    print("-" * 40)
    print(f"Transcript Sync Success. Sample Header:\n\"{transcript[:300]}...\"")

    # 4. Fire up the Robust DNA Engine
    print("\n🤖 ANALYZING STRUCTURE AND INTENT WITH GEMINI AI...")
    print("-" * 40)
    creator_dna = detect_topic(transcript, metadata=metadata)
    
    if not creator_dna or not isinstance(creator_dna, dict):
        print("❌ AI Profiler Error: Failed to generate a clean structured classification dictionary.")
        return
        
    print("✅ Video Content DNA Extracted:")
    print(f"   • Topic:             {creator_dna.get('topic')}")
    print(f"   • Subtopic:          {creator_dna.get('subtopic')}")
    print(f"   • Intent:            {creator_dna.get('intent')}")
    print(f"   • Creator Archetype: {creator_dna.get('creator_archetype')}")
    print(f"   • Audience Persona:  {creator_dna.get('audience')}")
    print(f"   • Content Style:     {creator_dna.get('content_style')}")

    # 5. Execute Multi-Constraint Search Filters
    print("\n🔍 INITIATING MULTI-CONSTRAINT RETRIEVAL SEARCH...")
    print("-" * 40)
    benchmarks = get_benchmark_candidates(
        topic=creator_dna.get("topic"),
        subtopic=creator_dna.get("subtopic"),
        intent=creator_dna.get("intent"),
        audience=creator_dna.get("audience"),
        current_video_views=raw_views,
        user_title=user_title,
        user_description=user_desc
    )

    print(f"👥 Peers Found (1.1x - 5x Bracket): {len(benchmarks.get('peers', []))}")
    print(f"⭐ Elites Found (>5x Scale Benchmarks): {len(benchmarks.get('elites', []))}")

    # 6. Rank Candidates using our Semantic Relevance Engine
    top_matches = rank_benchmarks(
        user_title=user_title,
        topic=creator_dna.get("topic"),
        subtopic=creator_dna.get("subtopic"),
        intent=creator_dna.get("intent"),
        benchmark_results=benchmarks
    )

    print("\n🏆 --- TOP RANKED COMPETITIVE MATCHES ---")
    print("-" * 40)
    if not top_matches:
        print("⚠️ No benchmark candidates cleared the similarity thresholds.")
    for video in top_matches[:5]:  # Show top 5 clearest matches
        print(f"🎯 {video.get('similarity_score', 0)}% Match | {video.get('title')}")

    # 7. Calculate Strategic Report via Gap Analyzer
    print("\n🧠 [GAP ENGINE ACTIVE] Running retention gap calculations...")
    print("-" * 40)
    report = analyze_gaps(
        metadata,
        transcript,
        benchmarks
    )

    # Render clean human-readable text block layouts instead of raw JSON
    render_beautiful_report(report)

if __name__ == "__main__":
    main()