import os
import re

from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)


def detect_format(title):

    title = title.lower()

    if any(
        x in title
        for x in [
            "tips",
            "truths",
            "lessons",
            "rules",
            "habits",
            "ways"
        ]
    ):
        return "listicle"

    if any(
        x in title
        for x in [
            "vlog",
            "day in my life"
        ]
    ):
        return "vlog"

    if any(
        x in title
        for x in [
            "podcast",
            "interview"
        ]
    ):
        return "podcast"

    return "standard"


def get_benchmark_candidates(
    topic,
    subtopic,
    intent,
    current_video_views,
    user_title,
    user_description,
    audience=None
):

    query = f"""
           {user_title}
            {topic}
            {subtopic}
           """

    search = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=50
    ).execute()

    ids = [
        item["id"]["videoId"]
        for item in search["items"]
    ]

    if not ids:
        return {
            "peers": [],
            "elites": []
        }

    videos = youtube.videos().list(
        id=",".join(ids),
        part="snippet,statistics"
    ).execute()

    peers = []
    elites = []

    user_format = detect_format(user_title)

    for item in videos["items"]:

        title = item["snippet"]["title"]

        views = int(
            item["statistics"].get(
                "viewCount",
                0
            )
        )

        data = {
            "title": title,
            "channel_name":
                item["snippet"]["channelTitle"],
            "views": views,
            "topic": topic,
            "intent": intent,
            "format": detect_format(title),
            "user_format": user_format,
            "url":
                f"https://www.youtube.com/watch?v={item['id']}"
        }

        if current_video_views < views <= current_video_views * 5:
            peers.append(data)

        elif views > current_video_views * 5:
            elites.append(data)

    peers.sort(
        key=lambda x: x["views"],
        reverse=True
    )

    elites.sort(
        key=lambda x: x["views"],
        reverse=True
    )

    return {
        "peers": peers[:10],
        "elites": elites[:10]
    }