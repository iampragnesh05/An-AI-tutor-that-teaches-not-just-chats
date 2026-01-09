from pathlib import Path

import streamlit as st

from core.pdf.extractor import PDFTextExtractor
from core.storage.chunk_store import JSONLChunkStore
from core.storage.processing_registry import ProcessingRecord, SQLiteProcessingRegistry
from core.storage.registry import SQLiteDocumentRegistry
from core.text.chunker import SimpleTextChunker
from core.utils.paths import (
    PROCESSED_DIR,
    REGISTRY_DB_PATH,
    ensure_data_dirs,
)

ensure_data_dirs()

st.title("⚙️ Process PDFs")
st.caption("Extract text + create chunks. No embeddings/vector DB yet.")

doc_registry = SQLiteDocumentRegistry(db_path=Path(REGISTRY_DB_PATH))
proc_registry = SQLiteProcessingRegistry(db_path=Path(REGISTRY_DB_PATH))
chunk_store = JSONLChunkStore(processed_root=Path(PROCESSED_DIR))

docs = doc_registry.list_all()
if not docs:
    st.info("No uploaded PDFs found. Upload PDFs first.")
    st.stop()

doc_options = {f"{d.filename}  (id: {d.doc_id[:10]}...)": d for d in docs}
selection = st.selectbox("Select a document", list(doc_options.keys()))
selected_doc = doc_options[selection]

status = proc_registry.get(selected_doc.doc_id)
if status:
    st.write(f"**Current status:** {status.status} | pages: {status.num_pages} | chunks: {status.num_chunks}")
    if status.error:
        st.error(status.error)

st.divider()
st.subheader("Chunking settings (safe defaults)")

chunk_size = st.slider("Chunk size (chars)", min_value=400, max_value=2000, value=1200, step=100)
chunk_overlap = st.slider("Chunk overlap (chars)", min_value=0, max_value=600, value=200, step=50)

col1, col2 = st.columns(2)
with col1:
    run_btn = st.button("✅ Extract + Chunk", type="primary")
with col2:
    preview_btn = st.button("👀 Preview saved chunks (first 5)")

if run_btn:
    extractor = PDFTextExtractor()
    chunker = SimpleTextChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    try:
        with st.spinner("Extracting text from PDF..."):
            pages = extractor.extract(Path(selected_doc.stored_path))

        with st.spinner("Chunking extracted text..."):
            chunks = chunker.chunk_pages(
                doc_id=selected_doc.doc_id,
                pages=((p.page_number, p.text) for p in pages),
            )

        with st.spinner("Saving chunks to disk..."):
            chunk_store.save(selected_doc.doc_id, chunks)

        proc_registry.upsert(
            ProcessingRecord(
                doc_id=selected_doc.doc_id,
                status="processed",
                num_pages=len(pages),
                num_chunks=len(chunks),
                processed_at_utc=doc_registry.now_utc_iso(),
                error=None,
            )
        )

        st.success(f"Processed ✅ pages={len(pages)} | chunks={len(chunks)}")
        st.write(f"Saved to: `{chunk_store.chunks_path(selected_doc.doc_id)}`")

    except Exception as e:
        proc_registry.upsert(
            ProcessingRecord(
                doc_id=selected_doc.doc_id,
                status="failed",
                num_pages=0,
                num_chunks=0,
                processed_at_utc=doc_registry.now_utc_iso(),
                error=str(e),
            )
        )
        st.error(f"Processing failed: {e}")

if preview_btn:
    saved = chunk_store.load(selected_doc.doc_id, limit=5)
    if not saved:
        st.info("No saved chunks found yet. Click 'Extract + Chunk' first.")
    else:
        for i, ch in enumerate(saved, start=1):
            st.markdown(f"### Chunk {i}")
            st.code(ch["text"][:1200])
            st.json(ch["metadata"])
