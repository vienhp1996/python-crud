import os
import json
from fastapi import Request


def load_locale(lang: str):
    """Load file JSON theo ngôn ngữ, fallback về en nếu không tồn tại."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "locales", f"{lang}.json")
    if not os.path.exists(file_path):
        file_path = os.path.join(base_dir, "locales", "en.json")
    with open(file_path, "r", encoding="utf-8") as f:
        messages = json.load(f)
    return messages


def get_message(key: str, request: Request):
    """Lấy thông báo dựa theo key và header Accept-Language của request."""
    lang = request.headers.get("accept-language", "vi").split(",")[0].lower()
    messages = load_locale(lang)
    return messages.get(key, key)
