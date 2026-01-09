from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class QuizAttempt:
    user_id: str
    doc_id: str
    step_index: int
    question: str
    answer: str
    score: float           # 0.0 → 1.0
    feedback: str
    created_at_utc: str


class SQLiteQuizAttemptStore:
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
                CREATE TABLE IF NOT EXISTS quiz_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    doc_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    score REAL NOT NULL,
                    feedback TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL
                );
                """
            )
            conn.commit()

    def insert(self, attempt: QuizAttempt) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO quiz_attempts
                (user_id, doc_id, step_index, question, answer, score, feedback, created_at_utc)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    attempt.user_id,
                    attempt.doc_id,
                    attempt.step_index,
                    attempt.question,
                    attempt.answer,
                    attempt.score,
                    attempt.feedback,
                    attempt.created_at_utc,
                ),
            )
            conn.commit()

    def list_for_doc(self, user_id: str, doc_id: str) -> List[QuizAttempt]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT user_id, doc_id, step_index, question, answer, score, feedback, created_at_utc
                FROM quiz_attempts
                WHERE user_id = ? AND doc_id = ?
                ORDER BY created_at_utc DESC;
                """,
                (user_id, doc_id),
            ).fetchall()

        return [
            QuizAttempt(
                user_id=row["user_id"],
                doc_id=row["doc_id"],
                step_index=row["step_index"],
                question=row["question"],
                answer=row["answer"],
                score=row["score"],
                feedback=row["feedback"],
                created_at_utc=row["created_at_utc"],
            )
            for row in rows
        ]
