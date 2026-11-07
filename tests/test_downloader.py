"""Tests for Downloader format selection, option construction, and cancellation."""

from unittest.mock import MagicMock

import pytest

from app.core.downloader import Downloader
from app.core.exceptions import DownloadCancelledError
from app.services.ffmpeg_service import FFmpegService


def test_format_selector_with_ffmpeg(tmp_path):
    mock_ffmpeg = MagicMock(spec=FFmpegService)
    mock_ffmpeg.is_available.return_value = True
    mock_ffmpeg.get_ffmpeg_path.return_value = "C:/ffmpeg/bin/ffmpeg.exe"

    dl_1080 = Downloader(
        task_id="t1",
        url="https://example.com/video",
        output_dir=str(tmp_path),
        quality="1080p",
        format_choice="mp4",
        ffmpeg_service=mock_ffmpeg,
    )
    fmt = dl_1080.build_format_selector(ffmpeg_available=True)
    assert "1080" in fmt
    assert "bv*" in fmt

    dl_audio = Downloader(
        task_id="t2",
        url="https://example.com/audio",
        output_dir=str(tmp_path),
        quality="audio",
        format_choice="mp3",
        ffmpeg_service=mock_ffmpeg,
    )
    assert dl_audio.build_format_selector(ffmpeg_available=True) == "bestaudio/best"


def test_format_selector_without_ffmpeg(tmp_path):
    mock_ffmpeg = MagicMock(spec=FFmpegService)
    mock_ffmpeg.is_available.return_value = False
    mock_ffmpeg.get_ffmpeg_path.return_value = None

    dl = Downloader(
        task_id="t3",
        url="https://example.com/video",
        output_dir=str(tmp_path),
        quality="720p",
        format_choice="mp4",
        ffmpeg_service=mock_ffmpeg,
    )
    fmt = dl.build_format_selector(ffmpeg_available=False)
    # Should fall back to single stream format
    assert fmt == "best[height<=720]/best"


def test_downloader_build_options_postprocessors(tmp_path):
    mock_ffmpeg = MagicMock(spec=FFmpegService)
    mock_ffmpeg.is_available.return_value = True
    mock_ffmpeg.get_ffmpeg_path.return_value = "C:/ffmpeg/bin/ffmpeg.exe"

    dl = Downloader(
        task_id="t4",
        url="https://example.com/music",
        output_dir=str(tmp_path),
        quality="audio",
        format_choice="mp3",
        ffmpeg_service=mock_ffmpeg,
    )
    opts = dl.build_options()
    assert opts["ffmpeg_location"] == "C:/ffmpeg/bin/ffmpeg.exe"
    pps = opts.get("postprocessors", [])
    assert any(p.get("key") == "FFmpegExtractAudio" and p.get("preferredcodec") == "mp3" for p in pps)


def test_downloader_cancellation(tmp_path):
    dl = Downloader(
        task_id="t5",
        url="https://example.com/video",
        output_dir=str(tmp_path),
    )
    assert not dl.is_cancelled()
    dl.cancel()
    assert dl.is_cancelled()

    # Progress hook should raise DownloadCancelledError
    with pytest.raises(DownloadCancelledError):
        dl._progress_hook({"status": "downloading", "downloaded_bytes": 100})
