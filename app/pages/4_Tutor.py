from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

from core.agents.tutor_agent import TutorAgent
from core.llm.tutor_generator import TutorContentGenerator
from core.llm.quiz_evaluator import ConceptualQuizEvaluator
from core.memory.tutor_memory import SQLiteTutorMemory, TutorState
from core.memory.quiz_attempts import SQLiteQuizAttemptStore, QuizAttempt
from core.storage.chunk_store import JSONLChunkStore
from core.storage.registry import SQLiteDocumentRegistry
from core.storage.lesson_plan_store import SQLiteLessonPlanStore
from core.planning.lesson_context import LessonContextSelector
from core.utils.paths import (
    PROCESSED_DIR,
    REGISTRY_DB_PATH,
    ensure_data_dirs,
)
from core.config.settings import settings

# ---------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------
ensure_data_dirs()

st.title("🎓 AI Learning Tutor")

USER_ID = "default_user"

doc_registry = SQLiteDocumentRegistry(Path(REGISTRY_DB_PATH))
memory = SQLiteTutorMemory(Path(REGISTRY_DB_PATH))
attempt_store = SQLiteQuizAttemptStore(Path(REGISTRY_DB_PATH))
chunks_store = JSONLChunkStore(Path(PROCESSED_DIR))
plan_store = SQLiteLessonPlanStore(Path(REGISTRY_DB_PATH))

agent = TutorAgent()
context_selector = LessonContextSelector()

generator = TutorContentGenerator(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
)

evaluator = ConceptualQuizEvaluator(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
)

# ---------------------------------------------------------------------
# Document selection
# ---------------------------------------------------------------------
docs = doc_registry.list_all()
if not docs:
    st.info("No learning material found. Upload and process a PDF first.")
    st.stop()

doc_map = {d.filename: d for d in docs}
selected = st.selectbox("Choose learning material", list(doc_map.keys()))
doc = doc_map[selected]

# ---------------------------------------------------------------------
# Load chunks
# ---------------------------------------------------------------------
chunks = chunks_store.load(doc.doc_id)
if not chunks:
    st.warning("This document has not been processed yet.")
    st.stop()

# ---------------------------------------------------------------------
# Load lesson plan
# ---------------------------------------------------------------------
lesson_steps = plan_store.load(doc.doc_id)
if not lesson_steps:
    st.warning("No lesson plan found. Generate one from Step 8.")
    st.stop()

# ---------------------------------------------------------------------
# Load or initialize tutor state
# ---------------------------------------------------------------------
state = memory.get(USER_ID, doc.doc_id)

if state is None:
    state = TutorState(
        user_id=USER_ID,
        doc_id=doc.doc_id,
        step_index=0,
        difficulty="easy",
        last_action="explain",
        mastery_score=0.3,
        updated_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    memory.upsert(state)

# ---------------------------------------------------------------------
# Resolve current lesson step
# ---------------------------------------------------------------------
current_step = next(
    (s for s in lesson_steps if s.step_index == state.step_index),
    None,
)

if current_step is None:
    st.success("🎉 You have completed all lessons in this document!")
    st.stop()

lesson_context = context_selector.select(
    chunks=chunks,
    topic=current_step.topic,
    subtopic=current_step.subtopic,
)

if not lesson_context.strip():
    st.warning("Could not find relevant content for this lesson step.")
    st.stop()

# ---------------------------------------------------------------------
# Tutor header
# ---------------------------------------------------------------------
st.subheader(
    f"Lesson {current_step.step_index}: "
    f"{current_step.topic} → {current_step.subtopic}"
)
st.caption(
    f"Action: **{current_step.action.upper()}** | "
    f"Difficulty: **{state.difficulty}** | "
    f"Mastery: **{state.mastery_score:.2f}**"
)

# ---------------------------------------------------------------------
# Decide tutor action (agent-driven)
# ---------------------------------------------------------------------
action = agent.decide_next_action(state)

# ---------------------------------------------------------------------
# EXPLAIN
# ---------------------------------------------------------------------
if action == "explain":
    explanation = generator.explain(
        context=lesson_context,
        difficulty=state.difficulty,
    )
    st.write(explanation)

# ---------------------------------------------------------------------
# QUIZ + CONCEPTUAL EVALUATION
# ---------------------------------------------------------------------
elif action == "quiz":
    question = generator.quiz(
        context=lesson_context,
        difficulty=state.difficulty,
    )

    st.markdown("### 🧠 Quiz")
    st.write(question)

    user_answer = st.text_area("Your answer")

    if st.button("Submit answer", type="primary"):
        if not user_answer.strip():
            st.warning("Please write an answer before submitting.")
            st.stop()

        with st.spinner("Evaluating your understanding..."):
            evaluation = evaluator.evaluate(
                context=lesson_context,
                question=question,
                user_answer=user_answer,
            )

        # Feedback
        st.subheader("📝 Feedback")
        st.write(evaluation.feedback)
        st.write(f"**Score:** `{evaluation.score:.2f}`")

        # Persist quiz attempt
        attempt_store.insert(
            QuizAttempt(
                user_id=USER_ID,
                doc_id=doc.doc_id,
                step_index=current_step.step_index,
                question=question,
                answer=user_answer,
                score=evaluation.score,
                feedback=evaluation.feedback,
                created_at_utc=datetime.now(timezone.utc).isoformat(),
            )
        )

        # Update tutor memory using conceptual score
        new_state = agent.update_after_scored_quiz(
            state=state,
            score=evaluation.score,
        )
        memory.upsert(new_state)

        st.success("Progress saved. Moving to the next lesson step.")
        st.rerun()

# ---------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------
elif action == "review":
    st.info("Let’s review this concept in simpler terms.")
    explanation = generator.explain(
        context=lesson_context,
        difficulty="easy",
    )
    st.write(explanation)
