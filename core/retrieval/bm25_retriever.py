from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from rank_bm25 import BM25Okapi


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any]


class BM25ChunkRetriever:
    """
    Builds an in-memory BM25 index from text chunks.
    Index can be rebuilt quickly per session.
    """

    def __init__(self, chunks: List[dict]) -> None:
        self.chunks = chunks
        self.tokenized_corpus = [
            self._tokenize(c["text"]) for c in chunks
        ]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return text.lower().split()

    def query(self, question: str, top_k: int = 5) -> List[RetrievedChunk]:
        tokens = self._tokenize(question)
        scores = self.bm25.get_scores(tokens)

        ranked = sorted(
            zip(self.chunks, scores),
            key=lambda x: x[1],
            reverse=True,
        )[:top_k]

        return [
            RetrievedChunk(
                chunk_id=chunk["chunk_id"],
                text=chunk["text"],
                score=float(score),
                metadata=chunk["metadata"],
            )
            for chunk, score in ranked
            if score > 0
        ]
