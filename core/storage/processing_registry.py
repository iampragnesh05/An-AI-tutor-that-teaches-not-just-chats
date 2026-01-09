from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProcessingRecord:
    doc_id: str
    status: str              # "processed" | "failed"
    num_pages: int
    num_chunks: int
    processed_at_utc: str
    error: str | None


class SQLiteProcessingRegistry:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS processing (
                    doc_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    num_pages INTEGER NOT NULL,
                    num_chunks INTEGER NOT NULL,
                    processed_at_utc TEXT NOT NULL,
                    error TEXT
                );
                """
            )
            conn.commit()

    def upsert(self, rec: ProcessingRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO processing (doc_id, status, num_pages, num_chunks, processed_at_utc, error)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    status=excluded.status,
                    num_pages=excluded.num_pages,
                    num_chunks=excluded.num_chunks,
                    processed_at_utc=excluded.processed_at_utc,
                    error=excluded.error;
                """,
                (rec.doc_id, rec.status, rec.num_pages, rec.num_chunks, rec.processed_at_utc, rec.error),
            )
            conn.commit()

    def get(self, doc_id: str) -> ProcessingRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT doc_id, status, num_pages, num_chunks, processed_at_utc, error
                FROM processing
                WHERE doc_id = ?
                """,
                (doc_id,),
            ).fetchone()

        if not row:
            return None

        return ProcessingRecord(
            doc_id=row["doc_id"],
            status=row["status"],
            num_pages=int(row["num_pages"]),
            num_chunks=int(row["num_chunks"]),
            processed_at_utc=row["processed_at_utc"],
            error=row["error"],
        )
