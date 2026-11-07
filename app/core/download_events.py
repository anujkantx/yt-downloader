"""Thread-safe event system for downloader and UI communication."""

import queue
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.core.download_models import DownloadProgress, DownloadTask, TaskStatus, VideoMetadata
from app.utils.logging_config import get_logger

logger = get_logger("events")


class EventType(str, Enum):
    TASK_ADDED = "task_added"
    METADATA_FETCHED = "metadata_fetched"
    PROGRESS_UPDATED = "progress_updated"
    STATUS_CHANGED = "status_changed"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_CANCELLED = "task_cancelled"
    QUEUE_UPDATED = "queue_updated"


@dataclass
class DownloadEvent:
    event_type: EventType
    task_id: str
    task: DownloadTask | None = None
    progress: DownloadProgress | None = None
    metadata: VideoMetadata | None = None
    new_status: TaskStatus | None = None
    error_message: str | None = None
    output_path: str | None = None
    data: Any | None = None


class EventBus:
    """Thread-safe event bus that queues events for consumption by the UI main thread."""

    def __init__(self):
        self._queue: queue.Queue[DownloadEvent] = queue.Queue()
        self._listeners: dict[EventType, list[Callable[[DownloadEvent], None]]] = {}

    def emit(self, event: DownloadEvent) -> None:
        """Push an event to the thread-safe queue."""
        self._queue.put(event)

    def subscribe(self, event_type: EventType, callback: Callable[[DownloadEvent], None]) -> None:
        """Register a listener for an event type (invoked on processing)."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def process_pending_events(self, max_events: int = 50) -> int:
        """
        Process pending events from the queue on the calling thread (UI thread).
        Limits batch size to avoid starving the UI event loop.
        """
        processed = 0
        while processed < max_events:
            try:
                event = self._queue.get_nowait()
            except queue.Empty:
                break

            listeners = self._listeners.get(event.event_type, [])
            for listener in listeners:
                try:
                    listener(event)
                except Exception as e:
                    logger.error("Error in event listener for %s: %s", event.event_type, e, exc_info=True)

            self._queue.task_done()
            processed += 1

        return processed
