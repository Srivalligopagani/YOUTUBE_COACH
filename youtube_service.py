import re
import os

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def extract_video_id(url):
    patterns = [
        r"v=([a-zA-Z0-9_-]{11})",
        r"youtu\.be/([a-zA-Z0-9_-]{11})"
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_video_metadata(video_id):

    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )

    response = request.execute()

    if not response["items"]:
        return None

    video = response["items"][0]

    snippet = video["snippet"]
    stats = video["statistics"]

    return {
        "video_id": video_id,
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "channel": snippet.get("channelTitle"),
        "published_at": snippet.get("publishedAt"),
        "views": int(stats.get("viewCount", 0)),
        "likes": int(stats.get("likeCount", 0))
    }
def search_videos(query, max_results=25):

    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )

    response = request.execute()

    videos = []

    for item in response["items"]:

        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"]
        })

    return videos
#           https://www.youtube.com/watch?v=_xlGhmkUjoI
def get_latest_video_from_channel(channel_url_or_id):
    """
    Takes a YouTube channel URL or ID, finds its default 'Uploads' playlist,
    and automatically retrieves the video ID of the most recent upload.
    """
    try:
        # Extract the channel ID if a full URL was passed
        channel_id = channel_url_or_id.split("/channel/")[-1].split("/@")[-1].split("?")[0]
        
        # 1. Request the channel profile to find their hidden Uploads Playlist ID
        channel_response = youtube.channels().list(
            part="contentDetails",
            id=channel_id if channel_id.startswith("UC") else None,
            forHandle=channel_id if not channel_id.startswith("UC") else None
        ).execute()
        
        if not channel_response.get("items"):
            print("❌ Channel not found.")
            return None
            
        uploads_playlist_id = channel_response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
        
        # 2. Grab the single newest item inside that uploads playlist
        playlist_response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=1
        ).execute()
        
        if not playlist_response.get("items"):
            print("⚠️ This channel has 0 public video uploads.")
            return None
            
        # Extract the video ID of that single upload!
        latest_video_id = playlist_response["items"][0]["snippet"]["resourceId"]["videoId"]
        return latest_video_id

    except Exception as e:
        print(f"❌ Failed to auto-fetch latest video from channel link: {e}")
        return None