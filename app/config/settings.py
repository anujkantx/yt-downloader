"""Application settings model and manager."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.config.defaults import (
    AVAILABLE_FORMATS,
    AVAILABLE_QUALITIES,
    AVAILABLE_THEMES,
    DEFAULT_FILENAME_TEMPLATE,
    DEFAULT_SETTINGS,
)
from app.utils.logging_config import get_logger
from app.utils.paths import get_config_path, get_default_download_dir
from app.utils.validators import validate_output_directory

logger = get_logger("config")


@dataclass
class Settings:
    download_dir: str
    default_quality: str = "1080p"
    default_format: str = "mp4"
    max_concurrent_downloads: int = 2
    theme: str = "dark"
    ffmpeg_path: str = ""
    filename_template: str = DEFAULT_FILENAME_TEMPLATE
    auto_open_folder: bool = False
    embed_metadata: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class SettingsManager:
    """Manages loading, validating, updating, and persisting user settings."""

    def __init__(self, config_path: Path | None = None):
        self.config_path = config_path or get_config_path()
        self._settings = self._load()

    @property
    def current(self) -> Settings:
        """Return the current settings snapshot."""
        return self._settings

    def _get_defaults(self) -> Settings:
        return Settings(
            download_dir=str(get_default_download_dir()),
            default_quality=DEFAULT_SETTINGS["default_quality"],
            default_format=DEFAULT_SETTINGS["default_format"],
            max_concurrent_downloads=DEFAULT_SETTINGS["max_concurrent_downloads"],
            theme=DEFAULT_SETTINGS["theme"],
            ffmpeg_path=DEFAULT_SETTINGS["ffmpeg_path"],
            filename_template=DEFAULT_SETTINGS["filename_template"],
            auto_open_folder=DEFAULT_SETTINGS["auto_open_folder"],
            embed_metadata=DEFAULT_SETTINGS["embed_metadata"],
        )

    def _validate_and_sanitize(self, data: dict[str, Any]) -> Settings:
        """Validate raw dictionary and construct a clean Settings object."""
        defaults = self._get_defaults()

        # Validate download_dir
        download_dir = str(data.get("download_dir", defaults.download_dir))
        is_valid, _ = validate_output_directory(download_dir)
        if not is_valid:
            logger.warning("Invalid download directory '%s', falling back to default", download_dir)
            download_dir = defaults.download_dir

        # Validate default_quality
        quality = str(data.get("default_quality", defaults.default_quality))
        if quality not in AVAILABLE_QUALITIES:
            quality = defaults.default_quality

        # Validate default_format
        fmt = str(data.get("default_format", defaults.default_format)).lower()
        if fmt not in AVAILABLE_FORMATS:
            fmt = defaults.default_format

        # Validate max_concurrent_downloads
        try:
            concurrency = int(data.get("max_concurrent_downloads", defaults.max_concurrent_downloads))
            if concurrency < 1 or concurrency > 10:
                concurrency = defaults.max_concurrent_downloads
        except (ValueError, TypeError):
            concurrency = defaults.max_concurrent_downloads

        # Validate theme
        theme = str(data.get("theme", defaults.theme)).lower()
        if theme not in AVAILABLE_THEMES:
            theme = defaults.theme

        # FFmpeg path
        ffmpeg_path = str(data.get("ffmpeg_path", defaults.ffmpeg_path)).strip()

        # Filename template
        template = str(data.get("filename_template", defaults.filename_template)).strip()
        if not template:
            template = defaults.filename_template

        # Booleans
        auto_open = bool(data.get("auto_open_folder", defaults.auto_open_folder))
        embed_meta = bool(data.get("embed_metadata", defaults.embed_metadata))

        return Settings(
            download_dir=download_dir,
            default_quality=quality,
            default_format=fmt,
            max_concurrent_downloads=concurrency,
            theme=theme,
            ffmpeg_path=ffmpeg_path,
            filename_template=template,
            auto_open_folder=auto_open,
            embed_metadata=embed_meta,
        )

    def _load(self) -> Settings:
        """Load settings from JSON file, falling back to defaults on error."""
        if not self.config_path.exists():
            defaults = self._get_defaults()
            self._save_to_file(defaults)
            return defaults

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Settings file does not contain a JSON object")
            return self._validate_and_sanitize(data)
        except Exception as e:
            logger.error("Error reading configuration file '%s': %s. Reverting to defaults.", self.config_path, e)
            defaults = self._get_defaults()
            self._save_to_file(defaults)
            return defaults

    def _save_to_file(self, settings: Settings) -> None:
        """Persist settings to disk atomically."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path = self.config_path.with_suffix(".tmp")
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(settings.to_dict(), f, indent=4)
            # Atomic replace
            temp_path.replace(self.config_path)
            logger.info("Settings saved to %s", self.config_path)
        except Exception as e:
            logger.error("Failed to save settings to '%s': %s", self.config_path, e)

    def update(self, **kwargs: Any) -> Settings:
        """Update specific settings fields and save to disk."""
        current_dict = self._settings.to_dict()
        current_dict.update(kwargs)
        self._settings = self._validate_and_sanitize(current_dict)
        self._save_to_file(self._settings)
        return self._settings

    def reset_to_defaults(self) -> Settings:
        """Reset all settings to default values and persist."""
        self._settings = self._get_defaults()
        self._save_to_file(self._settings)
        return self._settings
