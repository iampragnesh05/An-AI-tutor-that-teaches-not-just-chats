from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    page_number: int  # 1-based
    text: str


class PDFTextExtractor:
    """Extracts text from a PDF page-by-page using pypdf (no OCR)."""

    def extract(self, pdf_path: Path) -> List[PageText]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        reader = PdfReader(str(pdf_path))
        pages: List[PageText] = []

        for idx, page in enumerate(reader.pages, start=1):
            raw = page.extract_text() or ""
            text = raw.strip()
            pages.append(PageText(page_number=idx, text=text))

        return pages
