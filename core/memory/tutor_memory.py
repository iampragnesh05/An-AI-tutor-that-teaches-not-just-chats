from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class TutorState:
    user_id: str
    doc_id: str
    step_index: int
    difficulty: str          # easy | medium | hard
    last_action: str         # explain | quiz | review
    mastery_score: float     # 0.0 → 1.0
    updated_at_utc: str


class SQLiteTutorMemory:
    """
    Persistent learner memory for the Tutor Agent.
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
                CREATE TABLE IF NOT EXISTS tutor_memory (
                    user_id TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    last_action TEXT NOT NULL,
                    mastery_score REAL NOT NULL,
                    updated_at_utc TEXT NOT NULL,
                    PRIMARY KEY (user_id, doc_id)
                );
                """
            )
            conn.commit()

    def get(self, user_id: str, doc_id: str) -> Optional[TutorState]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM tutor_memory
                WHERE user_id = ? AND doc_id = ?
                """,
                (user_id, doc_id),
            ).fetchone()

        if not row:
            return None

        return TutorState(
            user_id=row["user_id"],
            doc_id=row["doc_id"],
            step_index=row["step_index"],
            difficulty=row["difficulty"],
            last_action=row["last_action"],
            mastery_score=row["mastery_score"],
            updated_at_utc=row["updated_at_utc"],
        )

    def upsert(self, state: TutorState) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tutor_memory
                (user_id, doc_id, step_index, difficulty, last_action, mastery_score, updated_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, doc_id) DO UPDATE SET
                    step_index=excluded.step_index,
                    difficulty=excluded.difficulty,
                    last_action=excluded.last_action,
                    mastery_score=excluded.mastery_score,
                    updated_at_utc=excluded.updated_at_utc;
                """,
                (
                    state.user_id,
                    state.doc_id,
                    state.step_index,
                    state.difficulty,
                    state.last_action,
                    state.mastery_score,
                    state.updated_at_utc,
                ),
            )
            conn.commit()
