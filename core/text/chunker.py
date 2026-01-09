from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Dict, Any


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]


class SimpleTextChunker:
    """
    Deterministic chunking by character length + overlap.
    - Good enough for foundation
    - We can upgrade later to token-based chunking (tiktoken) once deps are stable
    """

    def __init__(self, chunk_size: int = 1200, chunk_overlap: int = 200) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be >= 0")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be < chunk_size")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, doc_id: str, pages: Iterable[tuple[int, str]]) -> List[Chunk]:
        """
        pages: iterable of (page_number, text)
        Returns chunks with page metadata.
        """
        chunks: List[Chunk] = []
        chunk_index = 0

        for page_number, text in pages:
            cleaned = (text or "").strip()
            if not cleaned:
                continue

            start = 0
            while start < len(cleaned):
                end = min(start + self.chunk_size, len(cleaned))
                slice_text = cleaned[start:end].strip()

                if slice_text:
                    chunk_id = f"{doc_id}::p{page_number}::c{chunk_index}"
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            text=slice_text,
                            metadata={
                                "doc_id": doc_id,
                                "page_number": page_number,
                                "chunk_index": chunk_index,
                                "char_start": start,
                                "char_end": end,
                            },
                        )
                    )
                    chunk_index += 1

                if end == len(cleaned):
                    break

                start = end - self.chunk_overlap

        return chunks
