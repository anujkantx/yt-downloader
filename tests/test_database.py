"""Tests for SQLite database and history repository."""

from app.database.database import Database
from app.database.repository import DownloadRecord, HistoryRepository


def test_database_init(tmp_path):
    db_file = tmp_path / "test.db"
    db = Database(db_path=db_file)
    assert db_file.exists()
    with db.get_connection() as conn:
        assert conn is not None


def test_repository_crud(tmp_path):
    db_file = tmp_path / "test.db"
    db = Database(db_path=db_file)
    repo = HistoryRepository(db)

    # 1. Add record
    record = DownloadRecord(
        video_id="abc12345",
        source_url="https://youtube.com/watch?v=abc12345",
        title="Sample Video",
        uploader="Test Channel",
        duration=120,
        selected_quality="1080p",
        selected_format="mp4",
        status="queued",
    )
    rec_id = repo.add_record(record)
    assert rec_id > 0

    # 2. Get record
    fetched = repo.get_record(rec_id)
    assert fetched is not None
    assert fetched.title == "Sample Video"
    assert fetched.status == "queued"
    assert fetched.uploader == "Test Channel"

    # 3. Update status
    repo.update_status(
        record_id=rec_id,
        status="completed",
        output_path="C:/downloads/Sample_Video.mp4",
        file_size=1024 * 1024,
        completed=True,
    )
    updated = repo.get_record(rec_id)
    assert updated is not None
    assert updated.status == "completed"
    assert updated.output_path == "C:/downloads/Sample_Video.mp4"
    assert updated.file_size == 1024 * 1024
    assert updated.completed_at is not None

    # 4. List records
    all_records = repo.list_records()
    assert len(all_records) == 1

    # 5. Delete record
    deleted = repo.delete_record(rec_id)
    assert deleted
    assert repo.get_record(rec_id) is None
    assert len(repo.list_records()) == 0


def test_clear_history(tmp_path):
    db_file = tmp_path / "test.db"
    db = Database(db_path=db_file)
    repo = HistoryRepository(db)

    for i in range(5):
        repo.add_record(DownloadRecord(source_url=f"https://example.com/{i}"))

    assert len(repo.list_records()) == 5
    cleared_count = repo.clear_history()
    assert cleared_count == 5
    assert len(repo.list_records()) == 0
