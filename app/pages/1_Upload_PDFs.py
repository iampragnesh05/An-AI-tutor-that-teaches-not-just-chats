from pathlib import Path

import streamlit as st

from core.storage.pdf_store import save_pdf_bytes
from core.storage.registry import DocumentRecord, SQLiteDocumentRegistry
from core.utils.paths import UPLOADS_DIR, REGISTRY_DB_PATH, ensure_data_dirs

ensure_data_dirs()

st.title("📄 Upload PDFs")
st.caption("Uploads are stored locally and tracked in a SQLite registry (persistent).")

registry = SQLiteDocumentRegistry(db_path=Path(REGISTRY_DB_PATH))

uploaded_files = st.file_uploader(
    "Upload one or more PDF files",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:
    saved_count = 0
    skipped_count = 0

    for f in uploaded_files:
        content = f.getvalue()
        saved = save_pdf_bytes(upload_dir=Path(UPLOADS_DIR), original_name=f.name, content=content)

        # Prevent duplicate “registry rows” by sha
        existing = registry.find_by_sha256(saved.sha256)
        if existing is not None:
            skipped_count += 1
            continue

        record = DocumentRecord(
            doc_id=saved.doc_id,
            filename=saved.original_name,
            stored_path=str(saved.stored_path),
            sha256=saved.sha256,
            size_bytes=saved.size_bytes,
            uploaded_at_utc=registry.now_utc_iso(),
        )
        registry.upsert(record)
        saved_count += 1

    st.success(f"Uploaded: {saved_count} | Skipped duplicates: {skipped_count}")

st.divider()
st.subheader("📚 Uploaded PDFs (from registry)")

docs = registry.list_all()
if not docs:
    st.info("No PDFs uploaded yet.")
else:
    for d in docs:
        st.write(
            f"**{d.filename}**  \n"
            f"- id: `{d.doc_id}`  \n"
            f"- size: {d.size_bytes} bytes  \n"
            f"- stored: `{d.stored_path}`  \n"
            f"- uploaded (UTC): {d.uploaded_at_utc}"
        )
        st.caption(f"sha256: {d.sha256}")
        st.divider()
