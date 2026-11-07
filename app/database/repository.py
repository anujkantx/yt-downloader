"""Repository for managing download history records in SQLite."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.database.database import Database
from app.utils.logging_config import get_logger

logger = get_logger("repository")


@dataclass
class DownloadRecord:
    id: int | None = None
    video_id: str | None = None
    source_url: str = ""
    title: str | None = None
    uploader: str | None = None
    duration: int | None = None
    thumbnail_url: str | None = None
    selected_quality: str | None = None
    selected_format: str | None = None
    output_path: str | None = None
    file_size: int | None = None
    status: str = "queued"
    error_message: str | None = None
    created_at: str | None = None
    completed_at: str | None = None


class HistoryRepository:
    """Provides typed CRUD operations for download history."""

    def __init__(self, database: Database):
        self.db = database

    def add_record(self, record: DownloadRecord) -> int:
        """Insert a new download record and return its generated ID."""
        now_iso = datetime.now(UTC).isoformat()
        created_at = record.created_at or now_iso

        query = """
        INSERT INTO download_history (
            video_id, source_url, title, uploader, duration, thumbnail_url,
            selected_quality, selected_format, output_path, file_size,
            status, error_message, created_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            record.video_id,
            record.source_url,
            record.title or "Unknown Title",
            record.uploader,
            record.duration,
            record.thumbnail_url,
            record.selected_quality,
            record.selected_format,
            record.output_path,
            record.file_size,
            record.status,
            record.error_message,
            created_at,
            record.completed_at,
        )

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            record_id = cursor.lastrowid
            conn.commit()
            logger.info("Added history record id=%s for url=%s", record_id, record.source_url)
            return record_id or 0

    def update_status(
        self,
        record_id: int,
        status: str,
        error_message: str | None = None,
        output_path: str | None = None,
        file_size: int | None = None,
        completed: bool = False,
    ) -> None:
        """Update task status and execution outcome."""
        completed_at = datetime.now(UTC).isoformat() if completed else None

        query = """
        UPDATE download_history
        SET status = ?,
            error_message = COALESCE(?, error_message),
            output_path = COALESCE(?, output_path),
            file_size = COALESCE(?, file_size),
            completed_at = CASE WHEN ? IS NOT NULL THEN ? ELSE completed_at END
        WHERE id = ?
        """
        params = (
            status,
            error_message,
            output_path,
            file_size,
            completed_at,
            completed_at,
            record_id,
        )

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def update_metadata(
        self,
        record_id: int,
        title: str | None = None,
        uploader: str | None = None,
        duration: int | None = None,
        thumbnail_url: str | None = None,
        video_id: str | None = None,
    ) -> None:
        """Update video metadata in history record."""
        query = """
        UPDATE download_history
        SET title = COALESCE(?, title),
            uploader = COALESCE(?, uploader),
            duration = COALESCE(?, duration),
            thumbnail_url = COALESCE(?, thumbnail_url),
            video_id = COALESCE(?, video_id)
        WHERE id = ?
        """
        params = (title, uploader, duration, thumbnail_url, video_id, record_id)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()

    def get_record(self, record_id: int) -> DownloadRecord | None:
        """Fetch a single record by ID."""
        query = "SELECT * FROM download_history WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (record_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return DownloadRecord(**dict(row))

    def list_records(
        self, limit: int = 200, offset: int = 0, status: str | None = None
    ) -> list[DownloadRecord]:
        """List records with optional status filter, ordered by most recent first."""
        if status:
            query = "SELECT * FROM download_history WHERE status = ? ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (status, limit, offset)
        else:
            query = "SELECT * FROM download_history ORDER BY id DESC LIMIT ? OFFSET ?"
            params = (limit, offset)

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [DownloadRecord(**dict(row)) for row in rows]

    def delete_record(self, record_id: int) -> bool:
        """Delete a record by ID. Note: Does not touch files on disk."""
        query = "DELETE FROM download_history WHERE id = ?"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (record_id,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_history(self) -> int:
        """Clear all records from download history."""
        query = "DELETE FROM download_history"
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()
            return cursor.rowcount
