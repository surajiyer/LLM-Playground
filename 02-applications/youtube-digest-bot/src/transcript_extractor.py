from youtube_transcript_api import YouTubeTranscriptApi
from typing import Optional

class TranscriptExtractor:
    def __init__(self, max_length: int = 5000):
        self.max_length = max_length
    
    def extract_transcript(self, video_id: str) -> Optional[str]:
        """
        Extract transcript from a YouTube video.
        Returns the transcript text or None if unavailable.
        """
        try:
            # Try to get transcript in English first, then fall back to auto-generated
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            transcript = None
            
            # Try to find manual English transcript first
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                # Fall back to auto-generated English
                try:
                    transcript = transcript_list.find_generated_transcript(['en'])
                except:
                    # Try any available transcript
                    try:
                        transcript = transcript_list[0]
                    except:
                        return None
            
            if transcript is None:
                return None
            
            # Fetch the actual transcript
            transcript_data = transcript.fetch()
            
            # Combine all text
            full_text = ' '.join([entry['text'] for entry in transcript_data])
            
            # Clean up the text
            full_text = self._clean_transcript(full_text)
            
            # Truncate if too long
            if len(full_text) > self.max_length:
                full_text = full_text[:self.max_length] + "..."
            
            return full_text
            
        except Exception as e:
            print(f"Error extracting transcript for video {video_id}: {e}")
            return None
    
    def _clean_transcript(self, text: str) -> str:
        """Clean up transcript text."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common transcript artifacts
        text = text.replace('[Music]', '')
        text = text.replace('[Applause]', '')
        text = text.replace('[Laughter]', '')
        
        return text.strip()
    
    def is_transcript_available(self, video_id: str) -> bool:
        """Check if transcript is available for a video."""
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            return len(list(transcript_list)) > 0
        except:
            return False