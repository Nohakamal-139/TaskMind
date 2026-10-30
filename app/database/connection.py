"""One place that creates database connections and the schema."""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

DB_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = DB_DIR.parent.parent
SCHEMA_PATH = DB_DIR / "schema.sql"
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "taskmind.db"


def get_connection(db_path: str | Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a connection. Use ":" + "memory:" as db_path for tests."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # required on EVERY connection
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Create all tables if they do not exist yet (safe to call every run)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()


@contextmanager
def transaction(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Run several changes as ONE unit: all saved, or none (rollback on any error).

        with transaction(conn):
            tasks.add(conn, t1)
            deps.add(conn, t1_id, t2_id)

    If a transaction is already open (nested call) it simply joins it.
    """
    if conn.in_transaction:
        yield conn
        return
    conn.execute("BEGIN IMMEDIATE")
    try:
        yield conn
    except BaseException:
        conn.rollback()
        raise
    else:
        conn.commit()
