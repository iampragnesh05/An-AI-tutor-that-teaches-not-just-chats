from __future__ import annotations

from dataclasses import dataclass
from typing import List

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: List[dict]


class PDFAnswerGenerator:
    """
    Generates answers strictly from retrieved chunks.
    No hallucinations allowed.
    """

    SYSTEM_PROMPT = (
        "You are a careful AI tutor.\n"
        "Answer the user's question ONLY using the provided context.\n"
        "If the answer is not contained in the context, say:\n"
        "'The provided document does not contain enough information to answer this.'\n"
        "Do not add external knowledge."
    )

    def __init__(self, model: str, api_key: str) -> None:
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.2,
        )

    def answer(self, question: str, chunks: List[dict]) -> GroundedAnswer:
        context_blocks = []
        citations = []

        for i, ch in enumerate(chunks, start=1):
            context_blocks.append(
                f"[Source {i} | Page {ch['metadata']['page_number']}]\n{ch['text']}"
            )
            citations.append(
                {
                    "source": i,
                    "doc_id": ch["metadata"]["doc_id"],
                    "page": ch["metadata"]["page_number"],
                    "chunk_index": ch["metadata"]["chunk_index"],
                }
            )

        context_text = "\n\n".join(context_blocks)

        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Context:\n{context_text}\n\n"
                    f"Question:\n{question}\n\n"
                    "Answer using only the context above."
                )
            ),
        ]

        response = self.llm(messages)

        return GroundedAnswer(
            answer=response.content.strip(),
            citations=citations,
        )
