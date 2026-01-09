from __future__ import annotations

from datetime import datetime, timezone
from core.memory.tutor_memory import TutorState


class TutorAgent:
    """
    Decides what the tutor should do next.
    No UI, no Streamlit, no DB access here.
    """

    def decide_next_action(self, state: TutorState | None) -> str:
        if state is None:
            return "explain"

        if state.mastery_score < 0.4:
            return "review"

        if state.mastery_score < 0.7:
            return "quiz"

        return "explain"

    def update_after_scored_quiz(
        self,
        state: TutorState,
        score: float,
    ) -> TutorState:
        mastery = (state.mastery_score * 0.7) + (score * 0.3)
        mastery = max(0.0, min(1.0, mastery))

        if mastery > 0.75:
            difficulty = "hard"
        elif mastery > 0.4:
            difficulty = "medium"
        else:
            difficulty = "easy"

        return TutorState(
            user_id=state.user_id,
            doc_id=state.doc_id,
            step_index=state.step_index + (1 if score >= 0.7 else 0),
            difficulty=difficulty,
            last_action="quiz",
            mastery_score=mastery,
            updated_at_utc=datetime.now(timezone.utc).isoformat(),
        )
