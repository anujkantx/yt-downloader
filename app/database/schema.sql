-- SQLite schema for Video Downloader download history

CREATE TABLE IF NOT EXISTS download_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id TEXT,
    source_url TEXT NOT NULL,
    title TEXT,
    uploader TEXT,
    duration INTEGER,
    thumbnail_url TEXT,
    selected_quality TEXT,
    selected_format TEXT,
    output_path TEXT,
    file_size INTEGER,
    status TEXT NOT NULL,
    error_message TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_download_history_status ON download_history(status);
CREATE INDEX IF NOT EXISTS idx_download_history_created_at ON download_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_download_history_video_id ON download_history(video_id);
