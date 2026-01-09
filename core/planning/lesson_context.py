from __future__ import annotations
from typing import List

from core.retrieval.bm25_retriever import BM25ChunkRetriever


class LessonContextSelector:
    """
    Selects relevant chunks for a specific lesson step.
    """

    def select(
        self,
        chunks: List[dict],
        topic: str,
        subtopic: str,
        top_k: int = 3,
    ) -> str:
        query = f"{topic} {subtopic}"
        retriever = BM25ChunkRetriever(chunks)
        results = retriever.query(query, top_k=top_k)

        if not results:
            return ""

        return "\n".join(r.text for r in results)
