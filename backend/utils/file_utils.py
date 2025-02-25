import os
import json
from pathlib import Path


def ensure_directory_exists(directory_path):
    """Ensure that a directory exists, creating it if necessary."""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def save_text_to_file(text, file_path):
    """Save text to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def read_text_from_file(file_path):
    """Read text from a file."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_json_to_file(data, file_path):
    """Save JSON data to a file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def read_json_from_file(file_path):
    """Read JSON data from a file."""
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_chat_history(chat_history, file_path):
    """Save chat history to a text file."""
    chat_file_content = "\n\n".join(
        [f"User: {chat['user']}\nBot: {chat['bot']}" for chat in chat_history]
    )
    save_text_to_file(chat_file_content, file_path)