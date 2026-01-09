from __future__ import annotations

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


class TutorContentGenerator:
    def __init__(self, model: str, api_key: str) -> None:
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.3,
        )

    def explain(self, context: str, difficulty: str) -> str:
        system = (
            f"You are a tutor explaining concepts at {difficulty} difficulty.\n"
            "Explain step-by-step using only the provided context.\n"
            "Be clear and concise."
        )

        msg = HumanMessage(
            content=f"Context:\n{context}\n\nExplain the next concept."
        )

        return self.llm([SystemMessage(content=system), msg]).content

    def quiz(self, context: str, difficulty: str) -> str:
        system = (
            f"You are a tutor creating a quiz question at {difficulty} difficulty.\n"
            "Ask ONE clear question based only on the context.\n"
            "Do not provide the answer."
        )

        msg = HumanMessage(
            content=f"Context:\n{context}\n\nCreate a quiz question."
        )

        return self.llm([SystemMessage(content=system), msg]).content
