"""Data models, enums, and utility formatters for download tasks."""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum


class TaskStatus(str, Enum):
    QUEUED = "queued"
    FETCHING_METADATA = "fetching_metadata"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_active(self) -> bool:
        return self in (
            TaskStatus.QUEUED,
            TaskStatus.FETCHING_METADATA,
            TaskStatus.DOWNLOADING,
            TaskStatus.PROCESSING,
        )

    @property
    def display_name(self) -> str:
        names = {
            TaskStatus.QUEUED: "Queued",
            TaskStatus.FETCHING_METADATA: "Fetching Info...",
            TaskStatus.DOWNLOADING: "Downloading...",
            TaskStatus.PROCESSING: "Processing...",
            TaskStatus.COMPLETED: "Completed",
            TaskStatus.FAILED: "Failed",
            TaskStatus.CANCELLED: "Cancelled",
        }
        return names.get(self, self.value)


def format_bytes(num_bytes: float | None) -> str:
    """Format bytes into human-readable string (KB, MB, GB)."""
    if num_bytes is None or num_bytes <= 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0 or unit == "TB":
            return f"{num_bytes:.1f} {unit}" if unit != "B" else f"{int(num_bytes)} B"
        num_bytes /= 1024.0
    return "0 B"


def format_seconds(seconds: float | None) -> str:
    """Format seconds into MM:SS or HH:MM:SS."""
    if seconds is None or seconds < 0:
        return "--:--"
    total_sec = int(seconds)
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


@dataclass
class VideoMetadata:
    title: str = "Unknown Title"
    uploader: str = "Unknown"
    duration_seconds: int = 0
    thumbnail_url: str = ""
    video_id: str = ""
    available_resolutions: list[str] = field(default_factory=list)

    @property
    def duration_str(self) -> str:
        return format_seconds(self.duration_seconds)


@dataclass
class DownloadProgress:
    task_id: str
    status: TaskStatus = TaskStatus.QUEUED
    percentage: float = 0.0
    downloaded_bytes: int = 0
    total_bytes: int | None = None
    speed_bytes_sec: float | None = None
    eta_seconds: int | None = None
    filename: str | None = None

    @property
    def speed_str(self) -> str:
        if self.speed_bytes_sec and self.speed_bytes_sec > 0:
            return f"{format_bytes(self.speed_bytes_sec)}/s"
        return "-- KB/s"

    @property
    def eta_str(self) -> str:
        return format_seconds(self.eta_seconds)

    @property
    def size_str(self) -> str:
        downloaded = format_bytes(self.downloaded_bytes)
        if self.total_bytes and self.total_bytes > 0:
            return f"{downloaded} / {format_bytes(self.total_bytes)}"
        return downloaded


@dataclass
class DownloadTask:
    url: str
    quality: str = "1080p"
    format: str = "mp4"
    output_dir: str = ""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: TaskStatus = TaskStatus.QUEUED
    metadata: VideoMetadata | None = None
    progress: DownloadProgress = field(init=False)
    output_file_path: str | None = None
    error_message: str | None = None
    db_record_id: int | None = None
    created_at: float = field(default_factory=time.time)
    completed_at: float | None = None

    def __post_init__(self):
        self.progress = DownloadProgress(task_id=self.task_id, status=self.status)
