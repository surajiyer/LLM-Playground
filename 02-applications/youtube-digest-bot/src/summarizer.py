from openai import OpenAI
from typing import Optional

class VideoSummarizer:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", 
                 max_tokens: int = 150, temperature: float = 0.3):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
    
    def summarize_video(self, title: str, transcript: str, channel_name: str) -> Optional[str]:
        """
        Summarize a video based on its title and transcript.
        Returns a concise summary or None if summarization fails.
        """
        if not transcript:
            return f"Video from {channel_name}: {title} (No transcript available)"
        
        prompt = self._create_prompt(title, transcript, channel_name)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise, informative summaries of YouTube videos. Focus on the main points and key takeaways."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error summarizing video '{title}': {e}")
            return f"Summary unavailable for: {title} (Channel: {channel_name})"
    
    def _create_prompt(self, title: str, transcript: str, channel_name: str) -> str:
        """Create a prompt for the summarization."""
        return f"""
Please summarize this YouTube video in 2-3 sentences, focusing on the main points and key takeaways:

Video Title: {title}
Channel: {channel_name}

Transcript:
{transcript}

Summary:"""
    
    def summarize_multiple_videos(self, videos_data: list) -> list:
        """
        Summarize multiple videos.
        videos_data should be a list of tuples: (video_id, title, link, channel_name, transcript)
        Returns list of dictionaries with video info and summaries.
        """
        summaries = []
        
        for video_id, title, link, channel_name, transcript in videos_data:
            summary = self.summarize_video(title, transcript, channel_name)
            
            summaries.append({
                'video_id': video_id,
                'title': title,
                'link': link,
                'channel_name': channel_name,
                'summary': summary,
                'has_transcript': bool(transcript)
            })
        
        return summaries