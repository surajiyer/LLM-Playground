import os
import yaml
from pathlib import Path

def load_config():
    """Load configuration from config.yml and environment variables."""
    config_path = Path(__file__).parent.parent.parent / "config.yml"
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if available
    config['api_keys'] = {
        'youtube': os.getenv('YT_API_KEY'),
        'openai': os.getenv('OPENAI_API_KEY')
    }
    
    config['email']['user'] = os.getenv('EMAIL_USER')
    config['email']['password'] = os.getenv('EMAIL_PASS')
    config['email']['recipient'] = os.getenv('RECIPIENT_EMAIL')
    
    return config

def get_data_path():
    """Get the path to the data directory."""
    return Path(__file__).parent.parent.parent / "data"

def get_template_path():
    """Get the path to the templates directory."""
    return Path(__file__).parent.parent.parent / "templates"