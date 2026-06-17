import os
import json
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    """Loads the analysis history from history.json."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_history(history):
    """Saves the history array to history.json."""
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving history: {e}")
        return False

def add_to_history(video_id, title, views, channel, duration, dna, gap_report, timeline_report=None):
    """Adds a new analysis record to history.json or updates an existing one."""
    history = load_history()
    
    # Check if this video is already in history, remove it to place at the top
    history = [item for item in history if item["video_id"] != video_id]
    
    new_record = {
        "video_id": video_id,
        "title": title,
        "views": views,
        "channel": channel,
        "duration": duration,
        "dna": dna,
        "gap_report": gap_report,
        "timeline_report": timeline_report,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Insert at the beginning of the list
    history.insert(0, new_record)
    
    # Cap history at 20 runs
    if len(history) > 20:
        history = history[:20]
        
    save_history(history)
    return new_record

def get_history_item(video_id):
    """Retrieves a single history item by video_id."""
    history = load_history()
    for item in history:
        if item["video_id"] == video_id:
            return item
    return None

def clear_history():
    """Clears all history logs."""
    return save_history([])
