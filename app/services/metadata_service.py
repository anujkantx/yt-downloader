"""Asynchronous metadata extraction using yt-dlp Python API."""

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

import yt_dlp

from app.core.download_models import VideoMetadata
from app.core.exceptions import MetadataExtractionError
from app.utils.logging_config import get_logger

logger = get_logger("metadata_service")


class MetadataService:
    """Fetches video metadata asynchronously without blocking the UI."""

    def __init__(self, max_workers: int = 2):
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="MetadataWorker")

    def fetch_metadata_async(
        self,
        url: str,
        on_success: Callable[[VideoMetadata], None],
        on_error: Callable[[str], None],
    ) -> Future:
        """Submit background metadata fetch task."""
        future = self._executor.submit(self._fetch_sync, url)

        def _callback(f: Future) -> None:
            try:
                metadata = f.result()
                on_success(metadata)
            except Exception as e:
                on_error(str(e))

        future.add_done_callback(_callback)
        return future

    def fetch_metadata(self, url: str) -> VideoMetadata:
        """Synchronously fetch metadata."""
        return self._fetch_sync(url)

    def _fetch_sync(self, url: str) -> VideoMetadata:
        ydl_opts: dict[str, Any] = {
            "extract_flat": False,
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "simulate": True,
            "noplaylist": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise MetadataExtractionError("No metadata returned by extractor.")

                title = info.get("title") or "Unknown Title"
                uploader = info.get("uploader") or info.get("channel") or "Unknown"
                duration = int(info.get("duration") or 0)
                thumbnail = info.get("thumbnail") or ""
                video_id = info.get("id") or ""

                # Extract available video resolutions
                formats = info.get("formats", [])
                resolutions = set()
                for fmt in formats:
                    height = fmt.get("height")
                    if height:
                        resolutions.add(f"{height}p")

                # Sort resolutions descending
                def _res_key(r: str) -> int:
                    try:
                        return int(r.replace("p", ""))
                    except ValueError:
                        return 0

                sorted_resolutions = sorted(list(resolutions), key=_res_key, reverse=True)

                return VideoMetadata(
                    title=title,
                    uploader=uploader,
                    duration_seconds=duration,
                    thumbnail_url=thumbnail,
                    video_id=video_id,
                    available_resolutions=sorted_resolutions,
                )

        except yt_dlp.utils.DownloadError as e:
            err_msg = str(e)
            logger.warning("yt-dlp metadata extraction failed for %s: %s", url, err_msg)
            if "Private video" in err_msg:
                raise MetadataExtractionError("This video is private.") from e
            elif "Sign in to confirm" in err_msg or "login" in err_msg.lower():
                raise MetadataExtractionError("Video requires authentication or age verification.") from e
            elif "Video unavailable" in err_msg:
                raise MetadataExtractionError("Video is unavailable or has been removed.") from e
            raise MetadataExtractionError(f"Failed to fetch video details: {err_msg}") from e
        except Exception as e:
            logger.error("Unexpected error fetching metadata for %s: %s", url, e)
            raise MetadataExtractionError(f"Unexpected error: {e}") from e

    def shutdown(self, wait: bool = False) -> None:
        """Shutdown executor."""
        self._executor.shutdown(wait=wait)
