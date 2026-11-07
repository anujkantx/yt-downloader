"""Default configuration values."""

from typing import Any

from app.utils.paths import get_default_download_dir

DEFAULT_FILENAME_TEMPLATE = "%(title).200s [%(id)s].%(ext)s"

AVAILABLE_QUALITIES = [
    "best",
    "2160p",
    "1440p",
    "1080p",
    "720p",
    "480p",
    "360p",
    "audio",
]

AVAILABLE_FORMATS = [
    "mp4",
    "mkv",
    "mp3",
    "m4a",
    "best",
]

AVAILABLE_THEMES = ["dark", "light", "system"]

DEFAULT_SETTINGS: dict[str, Any] = {
    "download_dir": str(get_default_download_dir()),
    "default_quality": "1080p",
    "default_format": "mp4",
    "max_concurrent_downloads": 2,
    "theme": "dark",
    "ffmpeg_path": "",
    "filename_template": DEFAULT_FILENAME_TEMPLATE,
    "auto_open_folder": False,
    "embed_metadata": True,
}
