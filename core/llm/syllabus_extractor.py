from __future__ import annotations

import json
from typing import List, Dict

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


class SyllabusExtractor:
    """
    Extracts a structured syllabus from learning material.
    Output is purely structural (topics & subtopics).
    """

    SYSTEM_PROMPT = (
        "You are an expert curriculum designer.\n"
        "From the provided study material, extract a clear syllabus.\n\n"
        "Rules:\n"
        "- Use ONLY the provided content\n"
        "- Identify main topics and their subtopics\n"
        "- Keep titles concise and educational\n\n"
        "Return JSON in this format:\n"
        "{\n"
        '  "topics": [\n'
        '    {"title": "...", "subtopics": ["...", "..."]}\n'
        "  ]\n"
        "}"
    )

    def __init__(self, model: str, api_key: str) -> None:
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.1,
        )

    def extract(self, context: str) -> Dict:
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(content=f"Study material:\n{context}"),
        ]

        response = self.llm(messages).content

        try:
            return json.loads(response)
        except Exception:
            return {"topics": []}
