from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List

from core.text.chunker import Chunk


class JSONLChunkStore:
    """
    Stores chunks in: data/processed/<doc_id>/chunks.jsonl
    This is NOT a vector DB. Just a clean persistence layer for extracted text chunks.
    """

    def __init__(self, processed_root: Path) -> None:
        self.processed_root = processed_root
        self.processed_root.mkdir(parents=True, exist_ok=True)

    def doc_dir(self, doc_id: str) -> Path:
        d = self.processed_root / doc_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def chunks_path(self, doc_id: str) -> Path:
        return self.doc_dir(doc_id) / "chunks.jsonl"

    def save(self, doc_id: str, chunks: Iterable[Chunk]) -> Path:
        path = self.chunks_path(doc_id)
        with path.open("w", encoding="utf-8") as f:
            for ch in chunks:
                f.write(json.dumps(asdict(ch), ensure_ascii=False) + "\n")
        return path

    def load(self, doc_id: str, limit: int | None = None) -> List[dict]:
        path = self.chunks_path(doc_id)
        if not path.exists():
            return []

        out: List[dict] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                out.append(json.loads(line))
                if limit is not None and len(out) >= limit:
                    break
        return out
