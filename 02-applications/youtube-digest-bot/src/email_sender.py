import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from jinja2 import Template
from pathlib import Path
from typing import List, Dict

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_digest(self, recipient: str, summaries: List[Dict], 
                   subject_template: str, html_template_path: Path) -> bool:
        """
        Send the daily digest email.
        Returns True if successful, False otherwise.
        """
        try:
            # Generate subject with current date
            subject = subject_template.format(date=datetime.now().strftime("%Y-%m-%d"))
            
            # Generate HTML content
            html_content = self._generate_html_content(summaries, html_template_path)
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.username
            msg['To'] = recipient
            
            # Create plain text version
            text_content = self._generate_text_content(summaries)
            
            # Attach both versions
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False
    
    def _generate_html_content(self, summaries: List[Dict], template_path: Path) -> str:
        """Generate HTML content from template."""
        try:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            return template.render(
                summaries=summaries,
                date=datetime.now().strftime("%B %d, %Y"),
                total_videos=len(summaries)
            )
            
        except Exception as e:
            print(f"Error generating HTML content: {e}")
            return self._generate_fallback_html(summaries)
    
    def _generate_text_content(self, summaries: List[Dict]) -> str:
        """Generate plain text version of the digest."""
        lines = [
            f"YouTube Daily Digest - {datetime.now().strftime('%B %d, %Y')}",
            "=" * 50,
            f"\nFound {len(summaries)} new videos:\n"
        ]
        
        for i, summary in enumerate(summaries, 1):
            lines.extend([
                f"{i}. {summary['title']}",
                f"   Channel: {summary['channel_name']}",
                f"   Link: {summary['link']}",
                f"   Summary: {summary['summary']}",
                ""
            ])
        
        if not summaries:
            lines.append("No new videos found today.")
        
        return "\n".join(lines)
    
    def _generate_fallback_html(self, summaries: List[Dict]) -> str:
        """Generate simple HTML if template fails."""
        html_parts = [
            "<html><body>",
            f"<h1>YouTube Daily Digest - {datetime.now().strftime('%B %d, %Y')}</h1>",
            f"<p>Found {len(summaries)} new videos:</p>"
        ]
        
        if summaries:
            html_parts.append("<ol>")
            for summary in summaries:
                html_parts.extend([
                    "<li>",
                    f"<h3><a href='{summary['link']}'>{summary['title']}</a></h3>",
                    f"<p><strong>Channel:</strong> {summary['channel_name']}</p>",
                    f"<p><strong>Summary:</strong> {summary['summary']}</p>",
                    "</li>"
                ])
            html_parts.append("</ol>")
        else:
            html_parts.append("<p>No new videos found today.</p>")
        
        html_parts.append("</body></html>")
        
        return "".join(html_parts)