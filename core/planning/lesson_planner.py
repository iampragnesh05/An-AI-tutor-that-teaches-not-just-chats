from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class LessonStep:
    step_index: int
    topic: str
    subtopic: str
    action: str        # explain | quiz | review


class LessonPlanner:
    """
    Converts a syllabus into an ordered lesson plan.
    """

    def build(self, syllabus: Dict) -> List[LessonStep]:
        steps: List[LessonStep] = []
        index = 0

        for topic in syllabus.get("topics", []):
            title = topic.get("title", "Untitled Topic")
            subtopics = topic.get("subtopics", [])

            for sub in subtopics:
                steps.append(
                    LessonStep(
                        step_index=index,
                        topic=title,
                        subtopic=sub,
                        action="explain",
                    )
                )
                index += 1

                steps.append(
                    LessonStep(
                        step_index=index,
                        topic=title,
                        subtopic=sub,
                        action="quiz",
                    )
                )
                index += 1

        return steps
