import sqlite3
import os
from contextlib import contextmanager

class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, db_name="klyp.db"):
        if self._initialized:
            return

        self.db_path = os.path.join(self._get_data_dir(), db_name)
        self._initialized = True
        self._create_tables()

    def _get_data_dir(self):
        if os.name == 'nt':
            data_dir = os.path.join(os.environ['APPDATA'], "KLYP")
        else:
            data_dir = os.path.join(os.path.expanduser("~"), ".klyp")

        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    label TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tags TEXT,
                    group_name TEXT,
                    hotkey TEXT UNIQUE,
                    is_pinned BOOLEAN NOT NULL DEFAULT 0,
                    is_sensitive BOOLEAN NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sticky_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    snippet_id INTEGER NOT NULL,
                    pos_x INTEGER NOT NULL,
                    pos_y INTEGER NOT NULL,
                    width INTEGER NOT NULL,
                    height INTEGER NOT NULL,
                    color TEXT NOT NULL,
                    is_visible BOOLEAN NOT NULL DEFAULT 1,
                    FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()

    def execute_query(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor

    def fetch_one(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query, params=()):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
