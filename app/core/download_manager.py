"""Central download manager orchestrating concurrent tasks and queue execution."""

import threading
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor

from app.config.settings import SettingsManager
from app.core.download_events import DownloadEvent, EventBus, EventType
from app.core.download_models import DownloadTask, TaskStatus, VideoMetadata
from app.core.download_worker import DownloadWorker
from app.database.repository import DownloadRecord, HistoryRepository
from app.services.ffmpeg_service import FFmpegService
from app.utils.logging_config import get_logger

logger = get_logger("download_manager")


class DownloadManager:
    """Manages task queue, concurrency scheduling, and worker dispatching."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        event_bus: EventBus,
        repository: HistoryRepository | None = None,
        ffmpeg_service: FFmpegService | None = None,
    ):
        self.settings_manager = settings_manager
        self.event_bus = event_bus
        self.repository = repository
        self.ffmpeg_service = ffmpeg_service or FFmpegService(
            configured_path=self.settings_manager.current.ffmpeg_path
        )

        self._lock = threading.Lock()
        self._tasks: dict[str, DownloadTask] = {}
        self._workers: dict[str, DownloadWorker] = {}
        self._futures: dict[str, Future] = {}
        self._queue: deque[str] = deque()

        max_concurrent = self.settings_manager.current.max_concurrent_downloads
        self._executor = ThreadPoolExecutor(
            max_workers=max_concurrent,
            thread_name_prefix="DownloadWorker",
        )

        # Listen to completion/failure/cancellation to trigger next queued item
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self._on_task_finished)
        self.event_bus.subscribe(EventType.TASK_FAILED, self._on_task_finished)
        self.event_bus.subscribe(EventType.TASK_CANCELLED, self._on_task_finished)

    def add_task(
        self,
        url: str,
        quality: str | None = None,
        format_choice: str | None = None,
        output_dir: str | None = None,
        metadata: VideoMetadata | None = None,
    ) -> DownloadTask:
        """Create a new download task, save to database, and enqueue it."""
        settings = self.settings_manager.current
        selected_quality = quality or settings.default_quality
        selected_format = format_choice or settings.default_format
        target_dir = output_dir or settings.download_dir

        task = DownloadTask(
            url=url,
            quality=selected_quality,
            format=selected_format,
            output_dir=target_dir,
            metadata=metadata,
        )

        # Persist to database
        if self.repository:
            record = DownloadRecord(
                video_id=metadata.video_id if metadata else None,
                source_url=url,
                title=metadata.title if metadata else None,
                uploader=metadata.uploader if metadata else None,
                duration=metadata.duration_seconds if metadata else None,
                thumbnail_url=metadata.thumbnail_url if metadata else None,
                selected_quality=selected_quality,
                selected_format=selected_format,
                status="queued",
            )
            task.db_record_id = self.repository.add_record(record)

        with self._lock:
            self._tasks[task.task_id] = task
            self._queue.append(task.task_id)

        logger.info("Enqueued task %s for URL: %s", task.task_id, url)

        self.event_bus.emit(
            DownloadEvent(
                event_type=EventType.TASK_ADDED,
                task_id=task.task_id,
                task=task,
            )
        )

        self._process_queue()
        return task

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or queued task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task:
                return False

            # If queued and not running yet
            if task.status == TaskStatus.QUEUED:
                if task_id in self._queue:
                    self._queue.remove(task_id)
                task.status = TaskStatus.CANCELLED
                task.progress.status = TaskStatus.CANCELLED

                if self.repository and task.db_record_id:
                    self.repository.update_status(task.db_record_id, status="cancelled")

                self.event_bus.emit(
                    DownloadEvent(
                        event_type=EventType.TASK_CANCELLED,
                        task_id=task_id,
                        task=task,
                        new_status=TaskStatus.CANCELLED,
                    )
                )
                return True

            # If currently running
            worker = self._workers.get(task_id)
            if worker:
                worker.cancel()
                return True

            return False

    def retry_task(self, task_id: str) -> bool:
        """Retry a failed or cancelled task."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.status.is_active:
                return False

            task.status = TaskStatus.QUEUED
            task.error_message = None
            task.progress.percentage = 0.0
            task.progress.downloaded_bytes = 0
            task.progress.status = TaskStatus.QUEUED

            if self.repository and task.db_record_id:
                self.repository.update_status(task.db_record_id, status="queued")

            self._queue.append(task_id)

        logger.info("Retrying task %s", task_id)
        self.event_bus.emit(
            DownloadEvent(
                event_type=EventType.STATUS_CHANGED,
                task_id=task_id,
                task=task,
                new_status=TaskStatus.QUEUED,
            )
        )
        self._process_queue()
        return True

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the active tasks list (only if finished/cancelled)."""
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.status.is_active:
                return False

            self._tasks.pop(task_id, None)
            self._workers.pop(task_id, None)
            self._futures.pop(task_id, None)

        self.event_bus.emit(
            DownloadEvent(
                event_type=EventType.QUEUE_UPDATED,
                task_id=task_id,
            )
        )
        return True

    def clear_completed_tasks(self) -> int:
        """Remove all completed, failed, or cancelled tasks from active UI manager."""
        with self._lock:
            to_remove = [
                tid for tid, task in self._tasks.items()
                if not task.status.is_active
            ]
            for tid in to_remove:
                self._tasks.pop(tid, None)
                self._workers.pop(tid, None)
                self._futures.pop(tid, None)

        self.event_bus.emit(
            DownloadEvent(
                event_type=EventType.QUEUE_UPDATED,
                task_id="",
            )
        )
        return len(to_remove)

    def get_task(self, task_id: str) -> DownloadTask | None:
        with self._lock:
            return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[DownloadTask]:
        with self._lock:
            return list(self._tasks.values())

    def get_active_count(self) -> int:
        with self._lock:
            return sum(1 for task in self._tasks.values() if task.status.is_active)

    def _process_queue(self) -> None:
        """Schedule queued tasks up to max_concurrent limit."""
        with self._lock:
            active_workers = len(self._workers)
            max_concurrent = self.settings_manager.current.max_concurrent_downloads

            while active_workers < max_concurrent and self._queue:
                next_task_id = self._queue.popleft()
                task = self._tasks.get(next_task_id)
                if not task or task.status != TaskStatus.QUEUED:
                    continue

                settings = self.settings_manager.current
                worker = DownloadWorker(
                    task=task,
                    event_bus=self.event_bus,
                    repository=self.repository,
                    ffmpeg_service=self.ffmpeg_service,
                    filename_template=settings.filename_template,
                    embed_metadata=settings.embed_metadata,
                    auto_open_folder=settings.auto_open_folder,
                )
                self._workers[next_task_id] = worker
                future = self._executor.submit(worker.run)
                self._futures[next_task_id] = future
                active_workers += 1

    def _on_task_finished(self, event: DownloadEvent) -> None:
        """Callback when a task transitions to finished/failed/cancelled."""
        with self._lock:
            self._workers.pop(event.task_id, None)
            self._futures.pop(event.task_id, None)

        # Trigger processing of next item in queue
        self._process_queue()

    def shutdown(self, cancel_active: bool = True, wait: bool = True) -> None:
        """Clean shutdown: cancel active workers if requested and shutdown executor."""
        logger.info("Shutting down DownloadManager...")
        with self._lock:
            self._queue.clear()
            if cancel_active:
                for worker in list(self._workers.values()):
                    try:
                        worker.cancel()
                    except Exception as e:
                        logger.error("Error cancelling worker during shutdown: %s", e)

        self._executor.shutdown(wait=wait, cancel_futures=True)
        logger.info("DownloadManager shutdown complete.")
