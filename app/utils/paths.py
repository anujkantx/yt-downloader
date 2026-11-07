"""Application path management with platformdirs and PyInstaller support."""

import os
import sys
from pathlib import Path

from platformdirs import user_data_dir, user_downloads_dir

APP_NAME = "VideoDownloader"
APP_AUTHOR = "VideoDownloader"


def get_base_dir() -> Path:
    """Return the base application directory (dev or PyInstaller bundle)."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running as PyInstaller bundle
        return Path(sys._MEIPASS)
    # Running from source
    return Path(__file__).resolve().parent.parent.parent


def get_assets_dir() -> Path:
    """Return path to the assets directory."""
    return get_base_dir() / "assets"


def get_app_data_dir() -> Path:
    """Return the persistent user data directory in LocalAppData."""
    data_dir = Path(user_data_dir(APP_NAME, APP_AUTHOR))
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def get_config_path() -> Path:
    """Return path to the JSON configuration file."""
    config_dir = get_app_data_dir() / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def get_database_path() -> Path:
    """Return path to the SQLite database file."""
    db_dir = get_app_data_dir() / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "downloads.db"


def get_log_dir() -> Path:
    """Return path to the log directory."""
    log_dir = get_app_data_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_default_download_dir() -> Path:
    """Return default user download directory."""
    try:
        downloads = Path(user_downloads_dir())
        if downloads.exists() and os.access(downloads, os.W_OK):
            return downloads
    except Exception:
        pass
    # Fallback to user home Downloads
    fallback = Path.home() / "Downloads"
    if not fallback.exists():
        fallback.mkdir(parents=True, exist_ok=True)
    return fallback


def ensure_app_dirs() -> None:
    """Ensure all core application directories exist."""
    get_app_data_dir()
    get_config_path().parent.mkdir(parents=True, exist_ok=True)
    get_database_path().parent.mkdir(parents=True, exist_ok=True)
    get_log_dir().mkdir(parents=True, exist_ok=True)
