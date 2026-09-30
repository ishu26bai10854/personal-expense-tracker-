"""SQLite connection, schema creation and small execute/query helpers."""

import sqlite3
from pathlib import Path

from .logger import get_logger

logger = get_logger("database")
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 username TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL,
 salt TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS expenses (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 amount REAL NOT NULL CHECK (amount > 0),
 category TEXT NOT NULL,
 description TEXT NOT NULL DEFAULT '',
 date TEXT NOT NULL,
 created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_expenses_user_date ON expenses (user_id, date);
CREATE TABLE IF NOT EXISTS budgets (
 user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
 category TEXT NOT NULL,
 monthly_limit REAL NOT NULL CHECK (monthly_limit > 0),
 PRIMARY KEY (user_id, category)
);
"""


class Database:
    """Thin wrapper around sqlite3. Pass ':memory:' for tests."""

    def __init__(self, path=":memory:"):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        logger.info("Database ready (%s)", path)

    def execute(self, sql, params=()):
        """Run one write statement in a transaction; roll back on any failure."""
        try:
            cursor = self.conn.execute(sql, tuple(params))
            self.conn.commit()
            return cursor
        except sqlite3.IntegrityError:
            self.conn.rollback()
            raise
        except sqlite3.Error:
            self.conn.rollback()
            logger.error("Database write failed", exc_info=True)
            raise

    def query(self, sql, params=()):
        """Run a SELECT and return all rows."""
        return self.conn.execute(sql, tuple(params)).fetchall()

    def query_one(self, sql, params=()):
        """Run a SELECT and return the first row (or None)."""
        return self.conn.execute(sql, tuple(params)).fetchone()

    def close(self):
        self.conn.close()
