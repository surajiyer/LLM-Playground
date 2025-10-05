# YouTube Daily Digest Bot

An automated GitHub Actions bot that fetches new YouTube videos from subscribed channels, extracts transcripts, generates AI-powered summaries, and sends a daily email digest.

## Features

- 🔄 **Automated Daily Runs**: Scheduled via GitHub Actions at 6 AM UTC
- 📺 **Multi-Channel Support**: Monitor multiple YouTube channels via RSS feeds
- 📝 **Transcript Extraction**: Automatic transcript retrieval using YouTube Transcript API
- 🤖 **AI Summaries**: Generate concise summaries using OpenAI GPT models
- 📧 **Email Digest**: Beautiful HTML email with video summaries and links
- 💾 **State Management**: Tracks processed videos to avoid duplicates
- 🎨 **Professional Templates**: Clean, responsive email design
- ⚡ **Fast Dependencies**: Uses UV for lightning-fast dependency management

## Setup

### 1. Repository Secrets

Configure the following secrets in your GitHub repository (Settings → Secrets and variables → Actions):

- `YT_API_KEY`: YouTube Data API v3 key (optional, RSS feeds used by default)
- `OPENAI_API_KEY`: OpenAI API key for generating summaries
- `EMAIL_USER`: SMTP username (e.g., your Gmail address)
- `EMAIL_PASS`: SMTP password (use App Password for Gmail)
- `RECIPIENT_EMAIL`: Email address to receive the digest

### 2. Configuration

Edit `config.yml` to add your YouTube channel IDs:

```yaml
channels:
  - "UCJ0-OtVpF0wOKEqT2Z1HEtA"  # Example channel ID
  - "UC2eYFnH61tmytImy1mTYvhA"  # Add more channels here
```

To find a channel ID:
1. Go to the channel's page on YouTube
2. View page source and search for `"channelId":"` or use browser extensions

### 3. Email Configuration

The bot uses Gmail SMTP by default. For other providers, update `config.yml`:

```yaml
email:
  smtp_server: "smtp.gmail.com"  # Change for other providers
  smtp_port: 587
  subject: "Daily YouTube Digest - {date}"
```

## Usage

### Automatic (Recommended)
The bot runs automatically every day at 6 AM UTC via GitHub Actions.

### Manual Run
1. Go to Actions tab in your GitHub repository
2. Select "YouTube Daily Digest" workflow
3. Click "Run workflow"

### Local Development
```bash
cd 02-applications/youtube-digest-bot

# Install UV if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies and create virtual environment
uv sync

# Set environment variables
export OPENAI_API_KEY="your-key"
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASS="your-app-password"
export RECIPIENT_EMAIL="recipient@email.com"

# Run the bot
uv run python src/digest.py
```

## How It Works

1. **Video Fetching**: Uses RSS feeds to get latest videos from subscribed channels
2. **Transcript Extraction**: Attempts to extract transcripts (manual → auto-generated → skip)
3. **AI Summarization**: Generates concise summaries using OpenAI's GPT models
4. **Email Generation**: Creates HTML email using Jinja2 templates
5. **State Tracking**: Saves processed video IDs to avoid duplicates

## File Structure

```
youtube-digest-bot/
├── src/
│   ├── digest.py              # Main script
│   ├── video_fetcher.py       # YouTube RSS feed handler
│   ├── transcript_extractor.py # Transcript extraction
│   ├── summarizer.py          # OpenAI summarization
│   ├── email_sender.py        # SMTP email sending
│   └── utils/
│       ├── __init__.py
│       └── config.py          # Configuration loader
├── templates/
│   └── email_template.html    # Email template
├── data/
│   └── seen_videos.txt        # Processed video IDs
├── config.yml                 # Main configuration
├── pyproject.toml             # Project dependencies & config
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## Configuration Options

### Video Limits
```yaml
limits:
  max_videos_per_day: 10        # Maximum videos to process
  max_transcript_length: 5000   # Truncate long transcripts
```

### OpenAI Settings
```yaml
openai:
  model: "gpt-3.5-turbo"        # Or "gpt-4" for better quality
  max_tokens: 150               # Summary length
  temperature: 0.3              # Creativity (0-1)
```

## Troubleshooting

### Common Issues

1. **No videos found**: Check channel IDs and RSS feeds
2. **Transcript errors**: Some videos don't have transcripts (bot will still summarize title)
3. **Email sending fails**: Verify SMTP credentials and use App Passwords for Gmail
4. **API rate limits**: Reduce `max_videos_per_day` or upgrade OpenAI plan

### Debugging

Enable verbose logging by running locally and checking console output.

### GitHub Actions Logs

View workflow runs in the Actions tab for detailed execution logs.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - feel free to use and modify for your needs.

## Tips

- Use App Passwords for Gmail (not your regular password)
- Start with a few channels to test before adding many
- Check OpenAI usage in their dashboard to monitor costs
- The bot gracefully handles missing transcripts and API errors