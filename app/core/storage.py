"""
core/storage.py

Local, offline, account-free persistence for conversion history / favorites.
Backed by SQLite (per spec section 27, preferred for larger history sets).

Design goals:
- Never crash the app on a corrupted or missing database file.
- Safe to call from a background thread; the UI layer is responsible for
  not blocking on long operations (see services / screens).
- No network access of any kind.
"""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional

from .models import ConversionRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    mode TEXT NOT NULL,
    input_text TEXT NOT NULL,
    output_text TEXT NOT NULL,
    is_favorite INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_history_favorite ON history (is_favorite);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history (timestamp);
"""


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class HistoryStore:
    """Thin, dependency-free wrapper around a SQLite history database."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)) or ".", exist_ok=True)
        self._ensure_schema()

    # -- connection / schema -------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _ensure_schema(self) -> None:
        """Create the schema, recovering gracefully from a corrupted DB file."""
        try:
            with self._connect() as conn:
                conn.executescript(SCHEMA)
        except sqlite3.DatabaseError:
            # Corrupted file: quarantine it and start fresh rather than crash.
            if os.path.exists(self.db_path):
                corrupt_path = self.db_path + ".corrupt"
                try:
                    shutil.move(self.db_path, corrupt_path)
                except OSError:
                    os.remove(self.db_path)
            with self._connect() as conn:
                conn.executescript(SCHEMA)

    # -- writes ---------------------------------------------------------------

    def add(self, mode: str, input_text: str, output_text: str) -> ConversionRecord:
        ts = _utc_now_iso()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO history (timestamp, mode, input_text, output_text, is_favorite) "
                "VALUES (?, ?, ?, ?, 0)",
                (ts, mode, input_text, output_text),
            )
            new_id = cur.lastrowid
        return ConversionRecord(new_id, ts, mode, input_text, output_text, False)

    def set_favorite(self, record_id: int, favorite: bool) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE history SET is_favorite = ? WHERE id = ?",
                (1 if favorite else 0, record_id),
            )

    def delete(self, record_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM history WHERE id = ?", (record_id,))

    def clear_all(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM history")

    def clear_non_favorites(self) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM history WHERE is_favorite = 0")

    def enforce_limit(self, limit: Optional[int]) -> None:
        """Trim oldest non-favorite rows beyond `limit`. None/<=0 means unlimited."""
        if not limit or limit <= 0:
            return
        with self._connect() as conn:
            conn.execute(
                """
                DELETE FROM history WHERE id IN (
                    SELECT id FROM history
                    WHERE is_favorite = 0
                    ORDER BY id DESC
                    LIMIT -1 OFFSET ?
                )
                """,
                (limit,),
            )

    # -- reads ------------------------------------------------------------------

    def list_history(self, query: str = "", limit: int = 500) -> List[ConversionRecord]:
        sql = "SELECT id, timestamp, mode, input_text, output_text, is_favorite FROM history"
        params: tuple = ()
        if query:
            sql += " WHERE input_text LIKE ? OR output_text LIKE ?"
            like = f"%{query}%"
            params = (like, like)
        sql += " ORDER BY id DESC LIMIT ?"
        params = params + (limit,)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [ConversionRecord.from_row(r) for r in rows]

    def list_favorites(self, query: str = "", limit: int = 50) -> List[ConversionRecord]:
        sql = (
            "SELECT id, timestamp, mode, input_text, output_text, is_favorite "
            "FROM history WHERE is_favorite = 1"
        )
        params: tuple = ()
        if query:
            sql += " AND (input_text LIKE ? OR output_text LIKE ?)"
            like = f"%{query}%"
            params = (like, like)
        sql += " ORDER BY id DESC LIMIT ?"
        params = (*params, limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [ConversionRecord.from_row(r) for r in rows]

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

    def storage_bytes(self) -> int:
        try:
            return os.path.getsize(self.db_path)
        except OSError:
            return 0

    # -- export / import ---------------------------------------------------------

    def export_json(self, path: str) -> None:
        records = self.list_history(limit=1_000_000)
        payload = {"version": 1, "records": [r.to_dict() for r in records]}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def import_json(self, path: str) -> int:
        """Import records from a previously exported JSON file. Returns count imported."""
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        records = payload.get("records", [])
        imported = 0
        with self._connect() as conn:
            for r in records:
                conn.execute(
                    "INSERT INTO history (timestamp, mode, input_text, output_text, is_favorite) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (
                        r.get("timestamp", _utc_now_iso()),
                        r.get("mode", "encode"),
                        r.get("input_text", ""),
                        r.get("output_text", ""),
                        1 if r.get("is_favorite") else 0,
                    ),
                )
                imported += 1
        return imported
