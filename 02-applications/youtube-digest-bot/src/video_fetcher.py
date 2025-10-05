import feedparser
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple, Set

class VideoFetcher:
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.seen_file = data_path / "seen_videos.txt"
        
    def load_seen_videos(self) -> Set[str]:
        """Load previously seen video IDs from file."""
        if self.seen_file.exists():
            with open(self.seen_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()
    
    def save_seen_videos(self, seen_videos: Set[str]):
        """Save seen video IDs to file."""
        self.data_path.mkdir(exist_ok=True)
        with open(self.seen_file, 'w') as f:
            for video_id in seen_videos:
                f.write(f"{video_id}\n")
    
    def get_latest_videos(self, channel_ids: List[str], hours_back: int = 24) -> List[Tuple[str, str, str, str]]:
        """
        Fetch latest videos from YouTube channels using RSS feeds.
        Returns list of tuples: (video_id, title, link, channel_name)
        """
        seen_videos = self.load_seen_videos()
        new_videos = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        for channel_id in channel_ids:
            try:
                feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
                feed = feedparser.parse(feed_url)
                
                if not hasattr(feed, 'entries'):
                    print(f"Warning: Could not fetch feed for channel {channel_id}")
                    continue
                
                channel_name = getattr(feed.feed, 'title', 'Unknown Channel')
                
                for entry in feed.entries:
                    # Extract video ID from entry.id or link
                    video_id = entry.id.split(':')[-1] if ':' in entry.id else entry.id
                    
                    # Check if we've seen this video before
                    if video_id in seen_videos:
                        continue
                    
                    # Check if video is recent enough
                    published = datetime(*entry.published_parsed[:6])
                    if published < cutoff_time:
                        continue
                    
                    new_videos.append((
                        video_id,
                        entry.title,
                        entry.link,
                        channel_name
                    ))
                    seen_videos.add(video_id)
                    
            except Exception as e:
                print(f"Error fetching videos from channel {channel_id}: {e}")
                continue
        
        # Save updated seen videos
        self.save_seen_videos(seen_videos)
        
        return new_videos
    
    def get_video_info(self, video_id: str) -> dict:
        """Get additional video information if needed."""
        # This could be extended to use YouTube Data API for more details
        return {
            'id': video_id,
            'url': f"https://www.youtube.com/watch?v={video_id}"
        }