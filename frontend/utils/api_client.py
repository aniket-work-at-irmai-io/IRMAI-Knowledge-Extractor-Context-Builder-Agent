import requests
import yaml
from typing import Dict, Any


def load_config(config_path="frontend/config.yaml"):
    """Load configuration from a YAML file."""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


CONFIG = load_config()
BASE_URL = CONFIG["server"]["api_url"]


def post_request(endpoint: str, data: Dict[Any, Any]) -> Dict[Any, Any]:
    """Make a POST request to the API."""
    url = f"{BASE_URL}{endpoint}"
    response = requests.post(url, json=data)

    if response.status_code != 200:
        error_msg = response.json().get("detail", "Unknown error")
        return {"status": "error", "message": error_msg}

    return response.json()