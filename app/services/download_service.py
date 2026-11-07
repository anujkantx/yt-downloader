"""Application service facade connecting core engine and UI presentation layer."""

from collections.abc import Callable
from pathlib import Path

from app.config.settings import SettingsManager
from app.core.download_events import EventBus
from app.core.download_manager import DownloadManager
from app.core.download_models import DownloadTask, VideoMetadata
from app.database.database import Database
from app.database.repository import DownloadRecord, HistoryRepository
from app.services.ffmpeg_service import FFmpegService
from app.services.file_service import FileService
from app.services.metadata_service import MetadataService
from app.utils.logging_config import get_logger

logger = get_logger("download_service")


class DownloadService:
    """Unified service coordinating manager, metadata, history, and filesystem."""

    def __init__(
        self,
        settings_manager: SettingsManager,
        database: Database | None = None,
        event_bus: EventBus | None = None,
    ):
        self.settings_manager = settings_manager
        self.event_bus = event_bus or EventBus()
        self.database = database or Database()
        self.repository = HistoryRepository(self.database)

        self.ffmpeg_service = FFmpegService(
            configured_path=self.settings_manager.current.ffmpeg_path
        )
        self.metadata_service = MetadataService()
        self.download_manager = DownloadManager(
            settings_manager=self.settings_manager,
            event_bus=self.event_bus,
            repository=self.repository,
            ffmpeg_service=self.ffmpeg_service,
        )

    def fetch_metadata(
        self,
        url: str,
        on_success: Callable[[VideoMetadata], None],
        on_error: Callable[[str], None],
    ) -> None:
        """Fetch metadata asynchronously."""
        self.metadata_service.fetch_metadata_async(url, on_success, on_error)

    def enqueue_downloads(
        self,
        urls: list[str],
        quality: str | None = None,
        format_choice: str | None = None,
        output_dir: str | None = None,
        metadata_map: dict[str, VideoMetadata] | None = None,
    ) -> list[DownloadTask]:
        """Enqueue one or multiple URLs for download."""
        tasks: list[DownloadTask] = []
        meta_dict = metadata_map or {}
        for url in urls:
            meta = meta_dict.get(url)
            task = self.download_manager.add_task(
                url=url,
                quality=quality,
                format_choice=format_choice,
                output_dir=output_dir,
                metadata=meta,
            )
            tasks.append(task)
        return tasks

    def cancel_task(self, task_id: str) -> bool:
        return self.download_manager.cancel_task(task_id)

    def retry_task(self, task_id: str) -> bool:
        return self.download_manager.retry_task(task_id)

    def remove_task(self, task_id: str) -> bool:
        return self.download_manager.remove_task(task_id)

    def clear_completed_tasks(self) -> int:
        return self.download_manager.clear_completed_tasks()

    def get_history(self, limit: int = 100, offset: int = 0) -> list[DownloadRecord]:
        return self.repository.list_records(limit=limit, offset=offset)

    def delete_history_record(self, record_id: int, delete_file: bool = False) -> bool:
        """Delete history entry, optionally deleting file on disk if requested."""
        if delete_file:
            record = self.repository.get_record(record_id)
            if record and record.output_path:
                FileService.delete_file_safely(record.output_path)
        return self.repository.delete_record(record_id)

    def clear_all_history(self, delete_files: bool = False) -> int:
        """Clear all download history."""
        if delete_files:
            for record in self.repository.list_records(limit=1000):
                if record.output_path:
                    FileService.delete_file_safely(record.output_path)
        return self.repository.clear_history()

    def open_file(self, file_path: str) -> bool:
        return FileService.open_file(file_path)

    def open_containing_folder(self, file_path_or_dir: str) -> bool:
        p = Path(file_path_or_dir)
        if p.is_dir():
            return FileService.open_directory(p)
        return FileService.open_containing_folder(p)

    def shutdown(self, wait: bool = True) -> None:
        """Gracefully shutdown all background services."""
        self.metadata_service.shutdown(wait=False)
        self.download_manager.shutdown(cancel_active=True, wait=wait)
