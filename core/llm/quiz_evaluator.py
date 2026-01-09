from __future__ import annotations

import json
from dataclasses import dataclass

from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage


@dataclass(frozen=True)
class EvaluationResult:
    score: float        # 0.0 → 1.0
    feedback: str


class ConceptualQuizEvaluator:
    """
    Evaluates answers conceptually using a rubric.
    """

    SYSTEM_PROMPT = (
        "You are an expert tutor evaluating a student's answer.\n"
        "Evaluate conceptual understanding, not wording.\n\n"
        "Scoring rubric:\n"
        "- 1.0: Fully correct, complete understanding\n"
        "- 0.7: Mostly correct, minor gaps\n"
        "- 0.4: Partial understanding, important gaps\n"
        "- 0.0: Incorrect or irrelevant\n\n"
        "Return JSON with keys: score (0–1), feedback (string).\n"
        "Feedback must explain what is correct and what is missing."
    )

    def __init__(self, model: str, api_key: str) -> None:
        self.llm = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.0,
        )

    def evaluate(
        self,
        context: str,
        question: str,
        user_answer: str,
    ) -> EvaluationResult:
        messages = [
            SystemMessage(content=self.SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}\n\n"
                    f"Student answer:\n{user_answer}\n\n"
                    "Evaluate now."
                )
            ),
        ]

        response = self.llm(messages).content

        try:
            parsed = json.loads(response)
            score = float(parsed["score"])
            feedback = parsed["feedback"]
        except Exception:
            score = 0.0
            feedback = "Unable to evaluate answer reliably."

        score = max(0.0, min(1.0, score))

        return EvaluationResult(score=score, feedback=feedback)
