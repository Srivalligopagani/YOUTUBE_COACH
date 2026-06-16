from youtube_transcript_api import YouTubeTranscriptApi

def get_transcript(video_id):
    """
    Fetches the transcript for a given YouTube video ID
    and reads the modern object data properties.
    """
    try:
        # 1. Initialize the modern API instance
        yt_api_instance = YouTubeTranscriptApi()
        
        # 2. Fetch the transcript objects
        transcript_list = yt_api_instance.fetch(video_id)
        
        # 3. Use dot notation (.text) to cleanly extract the data strings
        full_text = " ".join(chunk.text for chunk in transcript_list)
        return full_text
        
    except Exception as e:
        print(f"Transcript Error: {e}")
        return None