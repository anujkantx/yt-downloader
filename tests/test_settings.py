"""Tests for settings persistence and validation."""

import json

from app.config.settings import SettingsManager


def test_settings_default_creation(tmp_path):
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_path=config_file)

    assert config_file.exists()
    settings = manager.current
    assert settings.default_quality == "1080p"
    assert settings.default_format == "mp4"
    assert settings.max_concurrent_downloads == 2
    assert settings.theme == "dark"


def test_settings_update_and_persist(tmp_path):
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_path=config_file)

    manager.update(
        default_quality="720p",
        default_format="mkv",
        max_concurrent_downloads=4,
        auto_open_folder=True,
    )

    # Reload from disk
    new_manager = SettingsManager(config_path=config_file)
    settings = new_manager.current
    assert settings.default_quality == "720p"
    assert settings.default_format == "mkv"
    assert settings.max_concurrent_downloads == 4
    assert settings.auto_open_folder is True


def test_settings_invalid_values_fallback(tmp_path):
    config_file = tmp_path / "settings.json"
    # Write corrupted/invalid JSON
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "default_quality": "fake_10000k",
                "default_format": "avi_unsupported",
                "max_concurrent_downloads": 999,
                "theme": "rainbow",
            },
            f,
        )

    manager = SettingsManager(config_path=config_file)
    settings = manager.current
    # Should fall back to safe defaults
    assert settings.default_quality == "1080p"
    assert settings.default_format == "mp4"
    assert settings.max_concurrent_downloads == 2
    assert settings.theme == "dark"
