import json
import os
from dotenv import load_dotenv
from utils.irmai_utils import get_azure_openai_client  # Add this import

# Load environment variables
load_dotenv()

def load_config(config_path="backend/config.json"):
    """Load configuration from a JSON file."""
    with open(config_path, "r") as f:
        return json.load(f)

def get_api_key(key_name):
    """Get API key from environment variables."""
    return os.getenv(key_name)

# Initialize Azure OpenAI client once during module import
get_azure_openai_client()  # Add this line

# Load config once at module import
CONFIG = load_config()