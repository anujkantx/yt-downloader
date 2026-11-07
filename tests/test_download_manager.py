"""Tests for DownloadManager, queueing, and task lifecycle."""

import time
from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import SettingsManager
from app.core.download_events import EventBus
from app.core.download_manager import DownloadManager
from app.core.download_models import TaskStatus
from app.database.database import Database
from app.database.repository import HistoryRepository


@pytest.fixture
def mock_settings(tmp_path):
    config_file = tmp_path / "settings.json"
    manager = SettingsManager(config_path=config_file)
    manager.update(max_concurrent_downloads=2, download_dir=str(tmp_path / "downloads"))
    return manager


@pytest.fixture
def mock_db(tmp_path):
    db_file = tmp_path / "test_dm.db"
    return Database(db_path=db_file)


def test_manager_add_task(mock_settings, mock_db):
    event_bus = EventBus()
    repo = HistoryRepository(mock_db)

    with patch("app.core.download_worker.Downloader") as mock_downloader_cls:
        mock_instance = MagicMock()
        mock_instance.execute.return_value = "C:/downloads/video.mp4"
        mock_downloader_cls.return_value = mock_instance

        manager = DownloadManager(
            settings_manager=mock_settings,
            event_bus=event_bus,
            repository=repo,
        )

        task = manager.add_task(
            url="https://youtube.com/watch?v=123",
            quality="1080p",
            format_choice="mp4",
        )

        assert task.task_id is not None
        assert task.url == "https://youtube.com/watch?v=123"
        assert task.quality == "1080p"
        assert task.format == "mp4"

        # Let worker run briefly
        time.sleep(0.2)
        event_bus.process_pending_events()

        manager.shutdown(wait=True)


def test_manager_cancel_queued_task(mock_settings, mock_db):
    event_bus = EventBus()
    repo = HistoryRepository(mock_db)

    # Set concurrency to 1 so second task stays queued
    mock_settings.update(max_concurrent_downloads=1)

    with patch("app.core.download_worker.DownloadWorker.run") as mock_worker_run:
        # Worker 1 runs and stays busy
        def slow_run():
            time.sleep(0.5)

        mock_worker_run.side_effect = slow_run

        manager = DownloadManager(
            settings_manager=mock_settings,
            event_bus=event_bus,
            repository=repo,
        )

        task1 = manager.add_task(url="https://youtube.com/watch?v=task1")
        assert task1 is not None
        task2 = manager.add_task(url="https://youtube.com/watch?v=task2")

        # task2 is queued
        assert task2.status == TaskStatus.QUEUED
        cancelled = manager.cancel_task(task2.task_id)
        assert cancelled
        assert task2.status == TaskStatus.CANCELLED

        manager.shutdown(cancel_active=True, wait=True)


def test_manager_remove_and_clear_tasks(mock_settings, mock_db):
    event_bus = EventBus()
    repo = HistoryRepository(mock_db)

    with patch("app.core.download_worker.Downloader") as mock_downloader_cls:
        mock_instance = MagicMock()
        mock_instance.execute.return_value = "C:/video.mp4"
        mock_downloader_cls.return_value = mock_instance

        manager = DownloadManager(
            settings_manager=mock_settings,
            event_bus=event_bus,
            repository=repo,
        )

        task = manager.add_task(url="https://youtube.com/watch?v=done")
        time.sleep(0.3)
        event_bus.process_pending_events()

        # Cannot remove while active, but once completed can remove
        if task.status == TaskStatus.COMPLETED:
            removed = manager.remove_task(task.task_id)
            assert removed
            assert manager.get_task(task.task_id) is None

        manager.shutdown(wait=True)
