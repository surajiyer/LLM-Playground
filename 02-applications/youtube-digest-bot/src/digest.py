#!/usr/bin/env python3
"""
YouTube Daily Digest Bot
Fetches new videos, extracts transcripts, summarizes with LLM, and sends email digest.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from utils.config import load_config, get_data_path, get_template_path
from video_fetcher import VideoFetcher
from transcript_extractor import TranscriptExtractor
from summarizer import VideoSummarizer
from email_sender import EmailSender

def main():
    """Main function to run the daily digest process."""
    print("🚀 Starting YouTube Daily Digest Bot...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Load configuration
        config = load_config()
        print("✅ Configuration loaded")
        
        # Validate required environment variables
        required_keys = ['youtube', 'openai']
        for key in required_keys:
            if not config['api_keys'].get(key):
                raise ValueError(f"Missing required API key: {key.upper()}_API_KEY")
        
        if not config['email'].get('user') or not config['email'].get('password'):
            raise ValueError("Missing email credentials: EMAIL_USER and EMAIL_PASS")
        
        if not config['email'].get('recipient'):
            raise ValueError("Missing recipient email: RECIPIENT_EMAIL")
        
        # Initialize components
        data_path = get_data_path()
        template_path = get_template_path() / "email_template.html"
        
        video_fetcher = VideoFetcher(data_path)
        transcript_extractor = TranscriptExtractor(
            max_length=config['limits']['max_transcript_length']
        )
        summarizer = VideoSummarizer(
            api_key=config['api_keys']['openai'],
            model=config['openai']['model'],
            max_tokens=config['openai']['max_tokens'],
            temperature=config['openai']['temperature']
        )
        email_sender = EmailSender(
            smtp_server=config['email']['smtp_server'],
            smtp_port=config['email']['smtp_port'],
            username=config['email']['user'],
            password=config['email']['password']
        )
        
        print("✅ Components initialized")
        
        # Fetch new videos
        print("🔍 Fetching new videos...")
        channel_ids = config['channels']
        new_videos = video_fetcher.get_latest_videos(channel_ids)
        
        print(f"📹 Found {len(new_videos)} new videos")
        
        if not new_videos:
            print("📧 No new videos found. Sending empty digest...")
            success = email_sender.send_digest(
                recipient=config['email']['recipient'],
                summaries=[],
                subject_template=config['email']['subject'],
                html_template_path=template_path
            )
            if success:
                print("✅ Empty digest sent successfully")
            else:
                print("❌ Failed to send empty digest")
            return
        
        # Limit number of videos if specified
        max_videos = config['limits']['max_videos_per_day']
        if len(new_videos) > max_videos:
            print(f"⚠️  Limiting to {max_videos} videos (found {len(new_videos)})")
            new_videos = new_videos[:max_videos]
        
        # Extract transcripts and summarize
        print("📝 Extracting transcripts and generating summaries...")
        videos_with_transcripts = []
        
        for i, (video_id, title, link, channel_name) in enumerate(new_videos, 1):
            print(f"  Processing {i}/{len(new_videos)}: {title[:50]}...")
            
            # Extract transcript
            transcript = transcript_extractor.extract_transcript(video_id)
            
            videos_with_transcripts.append((
                video_id, title, link, channel_name, transcript
            ))
        
        # Generate summaries
        print("🤖 Generating AI summaries...")
        summaries = summarizer.summarize_multiple_videos(videos_with_transcripts)
        
        # Send email digest
        print("📧 Sending email digest...")
        success = email_sender.send_digest(
            recipient=config['email']['recipient'],
            summaries=summaries,
            subject_template=config['email']['subject'],
            html_template_path=template_path
        )
        
        if success:
            print(f"✅ Daily digest sent successfully! ({len(summaries)} videos)")
        else:
            print("❌ Failed to send digest")
            sys.exit(1)
        
        # Print summary
        print("\n📊 Summary:")
        print(f"  • Videos processed: {len(summaries)}")
        print(f"  • Videos with transcripts: {sum(1 for s in summaries if s['has_transcript'])}")
        print(f"  • Videos without transcripts: {sum(1 for s in summaries if not s['has_transcript'])}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()