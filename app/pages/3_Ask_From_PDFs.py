from pathlib import Path
from core.llm.answer_generator import PDFAnswerGenerator
from core.config.settings import settings

import streamlit as st

from core.retrieval.bm25_retriever import BM25ChunkRetriever
from core.storage.chunk_store import JSONLChunkStore
from core.storage.processing_registry import SQLiteProcessingRegistry
from core.storage.registry import SQLiteDocumentRegistry
from core.utils.paths import (
    PROCESSED_DIR,
    REGISTRY_DB_PATH,
    ensure_data_dirs,
)

ensure_data_dirs()

st.title("🔎 Ask from PDFs")
st.caption("BM25 keyword-based retrieval (no embeddings, Python 3.14 safe).")

doc_registry = SQLiteDocumentRegistry(db_path=Path(REGISTRY_DB_PATH))
proc_registry = SQLiteProcessingRegistry(db_path=Path(REGISTRY_DB_PATH))
chunk_store = JSONLChunkStore(processed_root=Path(PROCESSED_DIR))

docs = doc_registry.list_all()
if not docs:
    st.info("No PDFs uploaded yet.")
    st.stop()

doc_map = {f"{d.filename} ({d.doc_id[:8]}...)": d for d in docs}
selected_label = st.selectbox("Select document", list(doc_map.keys()))
selected_doc = doc_map[selected_label]

status = proc_registry.get(selected_doc.doc_id)
if not status or status.status != "processed":
    st.warning("This document has not been processed yet. Go to 'Process PDFs' first.")
    st.stop()

chunks = chunk_store.load(selected_doc.doc_id)
if not chunks:
    st.warning("No chunks found for this document.")
    st.stop()

retriever = BM25ChunkRetriever(chunks)

question = st.text_input(
    "Ask a question based on this PDF",
    placeholder="e.g. What is the main conclusion of the study?",
)

top_k = st.slider("Top results", min_value=3, max_value=10, value=5)

if question:
    with st.spinner("Retrieving relevant sections..."):
        results = retriever.query(question, top_k=top_k)

    if not results:
        st.info("No relevant sections found.")
        st.stop()

    st.subheader("📄 Retrieved Evidence")
    retrieved_chunks = []
    for i, r in enumerate(results, start=1):
        st.markdown(f"**Source {i} (Page {r.metadata['page_number']})**")
        st.code(r.text[:800])
        retrieved_chunks.append(
            {
                "chunk_id": r.chunk_id,
                "text": r.text,
                "metadata": r.metadata,
            }
        )

    st.divider()

    if st.button("🧠 Generate Answer from PDF", type="primary"):
        generator = PDFAnswerGenerator(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
        )

        with st.spinner("Generating grounded answer..."):
            grounded = generator.answer(
                question=question,
                chunks=retrieved_chunks,
            )

        st.subheader("✅ Answer (Grounded)")
        st.write(grounded.answer)

        st.subheader("📚 Citations")
        for c in grounded.citations:
            st.json(c)

    with st.spinner("Searching relevant sections..."):
        results = retriever.query(question, top_k=top_k)

    if not results:
        st.info("No relevant sections found.")
    else:
        st.subheader("📄 Relevant Sections")
        for i, r in enumerate(results, start=1):
            st.markdown(f"### Result {i}")
            st.code(r.text[:1200])
            st.json(
                {
                    "score": round(r.score, 4),
                    "doc_id": r.metadata["doc_id"],
                    "page": r.metadata["page_number"],
                    "chunk_index": r.metadata["chunk_index"],
                }
            )
