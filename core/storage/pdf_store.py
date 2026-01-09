from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


_FILENAME_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


@dataclass(frozen=True)
class SavedPDF:
    doc_id: str
    original_name: str
    stored_path: Path
    sha256: str
    size_bytes: int


def _safe_filename(name: str) -> str:
    name = name.strip()
    name = _FILENAME_SAFE.sub("_", name)
    return name or "uploaded.pdf"


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def save_pdf_bytes(upload_dir: Path, original_name: str, content: bytes) -> SavedPDF:
    """
    Saves PDF bytes to disk under a deterministic name derived from content hash.
    This avoids duplicates and keeps names stable across sessions.
    """
    upload_dir.mkdir(parents=True, exist_ok=True)

    sha = _sha256_bytes(content)
    safe_name = _safe_filename(original_name)

    # Store as: <sha256>__<safe_filename>.pdf
    stored_name = f"{sha}__{safe_name}"
    if not stored_name.lower().endswith(".pdf"):
        stored_name += ".pdf"

    stored_path = upload_dir / stored_name

    # Write only if file doesn't exist (content-addressed)
    if not stored_path.exists():
        stored_path.write_bytes(content)

    # doc_id can be the sha for now (unique + stable)
    return SavedPDF(
        doc_id=sha,
        original_name=original_name,
        stored_path=stored_path,
        sha256=sha,
        size_bytes=len(content),
    )
