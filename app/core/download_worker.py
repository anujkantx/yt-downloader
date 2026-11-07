"""Worker runnable for executing downloads in background threads."""

import time

from app.core.download_events import DownloadEvent, EventBus, EventType
from app.core.download_models import DownloadProgress, DownloadTask, TaskStatus
from app.core.downloader import Downloader
from app.core.exceptions import DownloadCancelledError
from app.database.repository import HistoryRepository
from app.services.ffmpeg_service import FFmpegService
from app.services.file_service import FileService
from app.utils.logging_config import get_logger

logger = get_logger("download_worker")


class DownloadWorker:
    """Encapsulates execution of a single DownloadTask within a thread pool."""

    def __init__(
        self,
        task: DownloadTask,
        event_bus: EventBus,
        repository: HistoryRepository | None = None,
        ffmpeg_service: FFmpegService | None = None,
        filename_template: str = "%(title).200s [%(id)s].%(ext)s",
        embed_metadata: bool = True,
        auto_open_folder: bool = False,
    ):
        self.task = task
        self.event_bus = event_bus
        self.repository = repository
        self.ffmpeg_service = ffmpeg_service or FFmpegService()
        self.filename_template = filename_template
        self.embed_metadata = embed_metadata
        self.auto_open_folder = auto_open_folder

        self._downloader: Downloader | None = None
        self._last_progress_time = 0.0

    def cancel(self) -> None:
        """Cancel the running download."""
        if self._downloader:
            self._downloader.cancel()

    def run(self) -> None:
        """Worker main execution method."""
        logger.info("Worker started for task %s (url: %s)", self.task.task_id, self.task.url)

        # Update status to DOWNLOADING
        self.task.status = TaskStatus.DOWNLOADING
        self.event_bus.emit(
            DownloadEvent(
                event_type=EventType.STATUS_CHANGED,
                task_id=self.task.task_id,
                task=self.task,
                new_status=TaskStatus.DOWNLOADING,
            )
        )

        if self.repository and self.task.db_record_id:
            self.repository.update_status(self.task.db_record_id, status="downloading")

        self._downloader = Downloader(
            task_id=self.task.task_id,
            url=self.task.url,
            output_dir=self.task.output_dir,
            quality=self.task.quality,
            format_choice=self.task.format,
            filename_template=self.filename_template,
            embed_metadata=self.embed_metadata,
            ffmpeg_service=self.ffmpeg_service,
            progress_callback=self._on_progress,
        )

        try:
            output_path = self._downloader.execute()
            file_size = FileService.get_file_size(output_path) if output_path else None

            self.task.status = TaskStatus.COMPLETED
            self.task.output_file_path = output_path
            self.task.completed_at = time.time()
            self.task.progress.percentage = 100.0
            self.task.progress.status = TaskStatus.COMPLETED

            # Persist completion
            if self.repository and self.task.db_record_id:
                self.repository.update_status(
                    record_id=self.task.db_record_id,
                    status="completed",
                    output_path=output_path,
                    file_size=file_size,
                    completed=True,
                )

            # Emit completion event
            self.event_bus.emit(
                DownloadEvent(
                    event_type=EventType.TASK_COMPLETED,
                    task_id=self.task.task_id,
                    task=self.task,
                    new_status=TaskStatus.COMPLETED,
                    output_path=output_path,
                )
            )

            # Auto open folder if requested
            if self.auto_open_folder and output_path:
                FileService.open_containing_folder(output_path)

        except DownloadCancelledError:
            logger.info("Worker: Task %s was cancelled.", self.task.task_id)
            self.task.status = TaskStatus.CANCELLED
            self.task.progress.status = TaskStatus.CANCELLED

            if self.repository and self.task.db_record_id:
                self.repository.update_status(
                    record_id=self.task.db_record_id,
                    status="cancelled",
                    completed=False,
                )

            self.event_bus.emit(
                DownloadEvent(
                    event_type=EventType.TASK_CANCELLED,
                    task_id=self.task.task_id,
                    task=self.task,
                    new_status=TaskStatus.CANCELLED,
                )
            )

        except Exception as e:
            err_msg = str(e)
            logger.error("Worker: Task %s failed: %s", self.task.task_id, err_msg)
            self.task.status = TaskStatus.FAILED
            self.task.error_message = err_msg
            self.task.progress.status = TaskStatus.FAILED

            if self.repository and self.task.db_record_id:
                self.repository.update_status(
                    record_id=self.task.db_record_id,
                    status="failed",
                    error_message=err_msg,
                    completed=False,
                )

            self.event_bus.emit(
                DownloadEvent(
                    event_type=EventType.TASK_FAILED,
                    task_id=self.task.task_id,
                    task=self.task,
                    new_status=TaskStatus.FAILED,
                    error_message=err_msg,
                )
            )

    def _on_progress(self, progress: DownloadProgress) -> None:
        """Throttle progress updates to ~10 per second to avoid flooding the UI."""
        now = time.time()
        # Always emit status changes (e.g. processing), throttle periodic downloading percentage
        is_stage_transition = progress.status != self.task.progress.status
        if is_stage_transition or (now - self._last_progress_time >= 0.1):
            self._last_progress_time = now
            self.task.progress = progress
            self.event_bus.emit(
                DownloadEvent(
                    event_type=EventType.PROGRESS_UPDATED,
                    task_id=self.task.task_id,
                    task=self.task,
                    progress=progress,
                )
            )
