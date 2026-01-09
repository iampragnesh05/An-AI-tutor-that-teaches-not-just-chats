from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass(frozen=True)
class LessonPlanRow:
    doc_id: str
    step_index: int
    topic: str
    subtopic: str
    action: str


class SQLiteLessonPlanStore:
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
                CREATE TABLE IF NOT EXISTS lesson_plan (
                    doc_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    topic TEXT NOT NULL,
                    subtopic TEXT NOT NULL,
                    action TEXT NOT NULL,
                    PRIMARY KEY (doc_id, step_index)
                );
                """
            )
            conn.commit()

    def save(self, doc_id: str, steps: List[LessonPlanRow]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM lesson_plan WHERE doc_id = ?", (doc_id,))
            for s in steps:
                conn.execute(
                    """
                    INSERT INTO lesson_plan
                    (doc_id, step_index, topic, subtopic, action)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (s.doc_id, s.step_index, s.topic, s.subtopic, s.action),
                )
            conn.commit()

    def load(self, doc_id: str) -> List[LessonPlanRow]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT doc_id, step_index, topic, subtopic, action
                FROM lesson_plan
                WHERE doc_id = ?
                ORDER BY step_index
                """,
                (doc_id,),
            ).fetchall()

        return [
            LessonPlanRow(
                doc_id=row["doc_id"],
                step_index=row["step_index"],
                topic=row["topic"],
                subtopic=row["subtopic"],
                action=row["action"],
            )
            for row in rows
        ]
