from pathlib import Path
import streamlit as st

from core.llm.syllabus_extractor import SyllabusExtractor
from core.planning.lesson_planner import LessonPlanner
from core.storage.lesson_plan_store import SQLiteLessonPlanStore, LessonPlanRow
from core.storage.chunk_store import JSONLChunkStore
from core.storage.registry import SQLiteDocumentRegistry
from core.utils.paths import (
    PROCESSED_DIR,
    REGISTRY_DB_PATH,
    ensure_data_dirs,
)
from core.config.settings import settings

ensure_data_dirs()

st.title("📘 Syllabus & Lesson Plan")

doc_registry = SQLiteDocumentRegistry(Path(REGISTRY_DB_PATH))
chunk_store = JSONLChunkStore(Path(PROCESSED_DIR))
plan_store = SQLiteLessonPlanStore(Path(REGISTRY_DB_PATH))

docs = doc_registry.list_all()
if not docs:
    st.info("Upload and process a PDF first.")
    st.stop()

doc_map = {d.filename: d for d in docs}
selected = st.selectbox("Select document", list(doc_map.keys()))
doc = doc_map[selected]

chunks = chunk_store.load(doc.doc_id)
context = "\n".join(c["text"] for c in chunks[:5])

if st.button("🧠 Generate syllabus & lesson plan", type="primary"):
    extractor = SyllabusExtractor(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )
    planner = LessonPlanner()

    with st.spinner("Extracting syllabus..."):
        syllabus = extractor.extract(context)

    with st.spinner("Building lesson plan..."):
        steps = planner.build(syllabus)

    plan_store.save(
        doc_id=doc.doc_id,
        steps=[
            LessonPlanRow(
                doc_id=doc.doc_id,
                step_index=s.step_index,
                topic=s.topic,
                subtopic=s.subtopic,
                action=s.action,
            )
            for s in steps
        ],
    )

    st.success("Lesson plan created and saved.")

    st.subheader("📚 Syllabus")
    st.json(syllabus)

    st.subheader("🗺️ Lesson Plan")
    for s in steps:
        st.write(f"{s.step_index}. [{s.action.upper()}] {s.topic} → {s.subtopic}")
