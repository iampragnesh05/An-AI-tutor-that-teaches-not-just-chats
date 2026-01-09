from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DocumentRecord:
    doc_id: str
    filename: str
    stored_path: str
    sha256: str
    size_bytes: int
    uploaded_at_utc: str  # ISO timestamp


class SQLiteDocumentRegistry:
    """
    Persists uploaded document metadata across sessions.
    No RAG logic here—just bookkeeping.
    """

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
                CREATE TABLE IF NOT EXISTS documents (
                    doc_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    stored_path TEXT NOT NULL,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    uploaded_at_utc TEXT NOT NULL
                );
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_documents_sha256 ON documents(sha256);")
            conn.commit()

    def upsert(self, record: DocumentRecord) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO documents (doc_id, filename, stored_path, sha256, size_bytes, uploaded_at_utc)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    filename=excluded.filename,
                    stored_path=excluded.stored_path,
                    sha256=excluded.sha256,
                    size_bytes=excluded.size_bytes,
                    uploaded_at_utc=excluded.uploaded_at_utc;
                """,
                (
                    record.doc_id,
                    record.filename,
                    record.stored_path,
                    record.sha256,
                    record.size_bytes,
                    record.uploaded_at_utc,
                ),
            )
            conn.commit()

    def list_all(self) -> list[DocumentRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT doc_id, filename, stored_path, sha256, size_bytes, uploaded_at_utc
                FROM documents
                ORDER BY uploaded_at_utc DESC;
                """
            ).fetchall()

        return [
            DocumentRecord(
                doc_id=row["doc_id"],
                filename=row["filename"],
                stored_path=row["stored_path"],
                sha256=row["sha256"],
                size_bytes=int(row["size_bytes"]),
                uploaded_at_utc=row["uploaded_at_utc"],
            )
            for row in rows
        ]

    def find_by_sha256(self, sha256: str) -> DocumentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT doc_id, filename, stored_path, sha256, size_bytes, uploaded_at_utc
                FROM documents
                WHERE sha256 = ?
                LIMIT 1;
                """,
                (sha256,),
            ).fetchone()

        if not row:
            return None

        return DocumentRecord(
            doc_id=row["doc_id"],
            filename=row["filename"],
            stored_path=row["stored_path"],
            sha256=row["sha256"],
            size_bytes=int(row["size_bytes"]),
            uploaded_at_utc=row["uploaded_at_utc"],
        )

    @staticmethod
    def now_utc_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
