"""
Stage 4: Persistence layer.

Uses SQLite - a single file database, zero setup required. Good fit for
this project's scale: one file (finai.db) that lives next to your code,
no separate database server to install or manage.
"""

import sqlite3
import json
from datetime import datetime, timezone
from contextlib import contextmanager

DB_PATH = "finai.db"


def init_db():
    """Create the analyses table if it doesn't exist yet. Safe to call every startup."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                input_json TEXT NOT NULL,
                ratios_json TEXT NOT NULL,
                analysis_json TEXT NOT NULL
            )
        """)
        conn.commit()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def save_analysis(company_name: str, input_data: dict, ratios: dict, analysis: dict) -> int:
    """Save a completed analysis. Returns the new row's id."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO analyses (company_name, created_at, input_json, ratios_json, analysis_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                company_name,
                datetime.now(timezone.utc).isoformat(),
                json.dumps(input_data),
                json.dumps(ratios),
                json.dumps(analysis),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def list_analyses() -> list[dict]:
    """Return a lightweight list of past analyses (no full detail) for a history view."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, company_name, created_at FROM analyses ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_analysis(analysis_id: int) -> dict | None:
    """Fetch one full analysis by id, or None if it doesn't exist."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM analyses WHERE id = ?", (analysis_id,)
        ).fetchone()
        if row is None:
            return None
        result = dict(row)
        result["input"] = json.loads(result.pop("input_json"))
        result["ratios"] = json.loads(result.pop("ratios_json"))
        result["analysis"] = json.loads(result.pop("analysis_json"))
        return result