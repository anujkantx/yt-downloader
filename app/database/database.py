"""SQLite database connection and schema management."""

import sqlite3
import threading
from pathlib import Path

from app.utils.logging_config import get_logger
from app.utils.paths import get_database_path

logger = get_logger("database")


class Database:
    """Manages SQLite connection lifecycle and schema initialization."""

    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or get_database_path()
        self._lock = threading.Lock()
        self._initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Create and return a new SQLite connection with foreign keys and row factory."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=10.0,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        return conn

    def _initialize_schema(self) -> None:
        """Read schema.sql and create tables if not existing."""
        schema_file = Path(__file__).resolve().parent / "schema.sql"
        try:
            if not schema_file.exists():
                raise FileNotFoundError(f"Schema file not found: {schema_file}")

            schema_sql = schema_file.read_text(encoding="utf-8")
            with self._lock, self.get_connection() as conn:
                conn.executescript(schema_sql)
            logger.info("Database schema initialized at %s", self.db_path)
        except Exception as e:
            logger.error("Failed to initialize database schema: %s", e)
            raise
