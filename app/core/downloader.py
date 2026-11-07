"""Downloader service wrapping yt-dlp Python API."""

import re
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yt_dlp

from app.core.download_models import DownloadProgress, TaskStatus
from app.core.exceptions import (
    DownloadCancelledError,
    DownloaderError,
    FFmpegNotFoundError,
    UnsupportedURLError,
)
from app.services.ffmpeg_service import FFmpegService
from app.utils.logging_config import get_logger

logger = get_logger("downloader")


class Downloader:
    """Executes a single download task via yt-dlp with cooperative cancellation."""

    def __init__(
        self,
        task_id: str,
        url: str,
        output_dir: str,
        quality: str = "1080p",
        format_choice: str = "mp4",
        filename_template: str = "%(title).200s [%(id)s].%(ext)s",
        embed_metadata: bool = True,
        ffmpeg_service: FFmpegService | None = None,
        progress_callback: Callable[[DownloadProgress], None] | None = None,
    ):
        self.task_id = task_id
        self.url = url
        self.output_dir = Path(output_dir).resolve()
        self.quality = quality.lower().strip()
        self.format_choice = format_choice.lower().strip()
        self.filename_template = filename_template
        self.embed_metadata = embed_metadata
        self.ffmpeg_service = ffmpeg_service or FFmpegService()
        self.progress_callback = progress_callback

        self._cancel_event = threading.Event()
        self._final_filepath: str | None = None
        self._downloaded_files: list[str] = []

    def cancel(self) -> None:
        """Signal cooperative cancellation."""
        logger.info("Cancellation requested for task %s", self.task_id)
        self._cancel_event.set()

    def is_cancelled(self) -> bool:
        return self._cancel_event.is_set()

    def build_format_selector(self, ffmpeg_available: bool) -> str:
        """Construct safe yt-dlp format selection string based on quality and FFmpeg."""
        is_audio = self.quality == "audio" or self.format_choice in ("mp3", "m4a")

        if is_audio:
            return "bestaudio/best"

        # If FFmpeg is missing, separate video+audio streams cannot be merged.
        # Fallback to single pre-merged stream format.
        if not ffmpeg_available:
            logger.warning("FFmpeg not available. Using fallback pre-merged format selector.")
            if self.quality == "720p":
                return "best[height<=720]/best"
            elif self.quality == "480p":
                return "best[height<=480]/best"
            elif self.quality == "360p":
                return "best[height<=360]/best"
            return "best/best"

        # FFmpeg is available - select best video + best audio
        resolution_map = {
            "best": "bv*+ba/b",
            "2160p": "bv*[height<=2160]+ba/b[height<=2160]/b[height<=2160]/best",
            "1440p": "bv*[height<=1440]+ba/b[height<=1440]/b[height<=1440]/best",
            "1080p": "bv*[height<=1080]+ba/b[height<=1080]/b[height<=1080]/best",
            "720p": "bv*[height<=720]+ba/b[height<=720]/b[height<=720]/best",
            "480p": "bv*[height<=480]+ba/b[height<=480]/b[height<=480]/best",
            "360p": "bv*[height<=360]+ba/b[height<=360]/b[height<=360]/best",
        }
        return resolution_map.get(self.quality, "bv*+ba/b")

    def build_options(self) -> dict[str, Any]:
        """Build dictionary of yt-dlp options."""
        ffmpeg_path = self.ffmpeg_service.get_ffmpeg_path()
        ffmpeg_available = bool(ffmpeg_path and self.ffmpeg_service.is_available())

        format_selector = self.build_format_selector(ffmpeg_available)
        is_audio = self.quality == "audio" or self.format_choice in ("mp3", "m4a")

        outtmpl = str(self.output_dir / self.filename_template)

        ydl_opts: dict[str, Any] = {
            "format": format_selector,
            "outtmpl": outtmpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "no_color": True,
            "progress_hooks": [self._progress_hook],
            "postprocessor_hooks": [self._postprocessor_hook],
            "windowsfilenames": True,
            "retries": 3,
            "fragment_retries": 5,
        }

        if ffmpeg_path:
            ydl_opts["ffmpeg_location"] = ffmpeg_path

        # Post-processors
        postprocessors: list[dict[str, Any]] = []

        if is_audio:
            audio_codec = "mp3" if self.format_choice == "mp3" else "m4a"
            if not ffmpeg_available:
                logger.warning("Audio extraction requested without FFmpeg. Output will be source audio container.")
            else:
                postprocessors.append({
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_codec,
                    "preferredquality": "192",
                })
        else:
            # Video output format
            if ffmpeg_available:
                if self.format_choice == "mp4":
                    ydl_opts["merge_output_format"] = "mp4"
                elif self.format_choice == "mkv":
                    ydl_opts["merge_output_format"] = "mkv"

        if self.embed_metadata and ffmpeg_available:
            postprocessors.append({"key": "FFmpegMetadata", "add_chapters": True})

        if postprocessors:
            ydl_opts["postprocessors"] = postprocessors

        return ydl_opts

    def _progress_hook(self, d: dict[str, Any]) -> None:
        """Handle progress reports from yt-dlp."""
        if self._cancel_event.is_set():
            raise DownloadCancelledError("Download cancelled by user.")

        status_str = d.get("status")
        filename = d.get("filename")
        if filename and filename not in self._downloaded_files:
            self._downloaded_files.append(filename)

        if status_str == "downloading":
            downloaded = d.get("downloaded_bytes") or 0
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            speed = d.get("speed")
            eta = d.get("eta")

            percentage = 0.0
            if total and total > 0:
                percentage = min(100.0, max(0.0, (downloaded / total) * 100.0))

            progress = DownloadProgress(
                task_id=self.task_id,
                status=TaskStatus.DOWNLOADING,
                percentage=percentage,
                downloaded_bytes=downloaded,
                total_bytes=total,
                speed_bytes_sec=speed,
                eta_seconds=eta,
                filename=Path(filename).name if filename else None,
            )

            if self.progress_callback:
                self.progress_callback(progress)

        elif status_str == "finished":
            # Download phase finished, entering postprocessing
            progress = DownloadProgress(
                task_id=self.task_id,
                status=TaskStatus.PROCESSING,
                percentage=100.0,
                downloaded_bytes=d.get("total_bytes") or 0,
                total_bytes=d.get("total_bytes"),
                filename=Path(filename).name if filename else None,
            )
            if self.progress_callback:
                self.progress_callback(progress)

    def _postprocessor_hook(self, d: dict[str, Any]) -> None:
        """Handle postprocessing status."""
        if self._cancel_event.is_set():
            raise DownloadCancelledError("Download cancelled during postprocessing.")

        status = d.get("status")
        if status == "started":
            progress = DownloadProgress(
                task_id=self.task_id,
                status=TaskStatus.PROCESSING,
                percentage=100.0,
            )
            if self.progress_callback:
                self.progress_callback(progress)
        elif status == "finished":
            # Postprocessing finished
            output_filepath = d.get("info_dict", {}).get("_filename") or d.get("filename")
            if output_filepath:
                self._final_filepath = output_filepath

    def execute(self) -> str:
        """
        Execute the download. Returns the absolute path of the output file.
        Raises DownloadCancelledError, DownloaderError, etc.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        ydl_opts = self.build_options()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                if not info:
                    raise DownloaderError("yt-dlp returned empty info dictionary.")

                # Determine final file path
                if not self._final_filepath:
                    candidate = ydl.prepare_filename(info)
                    # Check if audio conversion changed extension
                    if self.format_choice in ("mp3", "m4a") or self.quality == "audio":
                        audio_ext = ".mp3" if self.format_choice == "mp3" else ".m4a"
                        alt_cand = Path(candidate).with_suffix(audio_ext)
                        if alt_cand.exists():
                            self._final_filepath = str(alt_cand)

                    # Check if merge changed extension
                    if not self._final_filepath:
                        if self.format_choice == "mp4":
                            alt_mp4 = Path(candidate).with_suffix(".mp4")
                            if alt_mp4.exists():
                                self._final_filepath = str(alt_mp4)
                        elif self.format_choice == "mkv":
                            alt_mkv = Path(candidate).with_suffix(".mkv")
                            if alt_mkv.exists():
                                self._final_filepath = str(alt_mkv)

                    if not self._final_filepath:
                        self._final_filepath = candidate

                # Verify file exists on disk
                if not Path(self._final_filepath).exists():
                    # Try finding in downloaded files
                    for df in reversed(self._downloaded_files):
                        if Path(df).exists():
                            self._final_filepath = df
                            break

                logger.info("Task %s completed: %s", self.task_id, self._final_filepath)
                return str(self._final_filepath)

        except DownloadCancelledError:
            self._cleanup_partial_files()
            raise
        except yt_dlp.utils.DownloadError as e:
            if self._cancel_event.is_set():
                self._cleanup_partial_files()
                raise DownloadCancelledError("Download was cancelled.") from e
            raw_err = str(e)
            clean_err = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw_err)
            clean_err = re.sub(r"^ERROR:\s*", "", clean_err).strip()
            logger.error("Download error for %s: %s", self.url, clean_err)
            if "Unsupported URL" in clean_err:
                raise UnsupportedURLError(f"Unsupported URL: {self.url}") from e
            if "Requested format is not available" in clean_err:
                if not self.ffmpeg_service.is_available():
                    raise FFmpegNotFoundError(
                        "FFmpeg is required to merge separate video and audio streams for this video. "
                        "Please install FFmpeg (Settings > FFmpeg) or choose Audio Only."
                    ) from e
                else:
                    raise DownloaderError(
                        f"The requested quality ({self.quality}) is not available for this video. "
                        "Try selecting 'Best Available'."
                    ) from e
            if "ffmpeg" in clean_err.lower() and not self.ffmpeg_service.is_available():
                raise FFmpegNotFoundError(
                    "This download requires FFmpeg to merge streams or convert audio."
                ) from e
            raise DownloaderError(clean_err) from e
        except Exception as e:
            if self._cancel_event.is_set():
                self._cleanup_partial_files()
                raise DownloadCancelledError("Download was cancelled.") from e
            raw_err = str(e)
            clean_err = re.sub(r"\x1b\[[0-9;]*[a-zA-Z]", "", raw_err)
            clean_err = re.sub(r"^ERROR:\s*", "", clean_err).strip()
            logger.error("Unexpected error in task %s: %s", self.task_id, clean_err, exc_info=True)
            raise DownloaderError(clean_err) from e

    def _cleanup_partial_files(self) -> None:
        """Clean up partially downloaded files (.part, .ytdl) after cancellation."""
        try:
            for filepath in self._downloaded_files:
                p = Path(filepath)
                part_candidates = [
                    p,
                    Path(str(p) + ".part"),
                    Path(str(p) + ".ytdl"),
                ]
                for part in part_candidates:
                    if part.exists() and part.is_file():
                        part.unlink()
                        logger.info("Cleaned up partial file: %s", part)
        except Exception as e:
            logger.warning("Error cleaning up partial files: %s", e)
