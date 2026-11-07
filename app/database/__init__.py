"""Database layer for SQLite persistence."""

from app.database.database import Database
from app.database.repository import DownloadRecord, HistoryRepository

__all__ = ["Database", "DownloadRecord", "HistoryRepository"]
