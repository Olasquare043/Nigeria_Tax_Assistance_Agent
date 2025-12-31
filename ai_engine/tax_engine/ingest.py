from __future__ import annotations

from pathlib import Path
from typing import List
from langchain_core.documents import Document

from .config import settings
from .pdf_loader import extract_pages
from .chunker import chunk_document


def ingest_pdfs() -> List[Document]:
    docs_dir = Path(settings.docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))
    if not pdfs:
        raise FileNotFoundError(f"No PDFs found in {docs_dir}")

    all_docs: List[Document] = []

    for pdf in pdfs:
        pages = extract_pages(pdf)
        page_dicts = [{"page_num": p.page_num, "text": p.text} for p in pages]
        chunks = chunk_document(
            file_name=pdf.name,
            pages=page_dicts,
            chunk_chars=settings.chunk_chars,
            overlap=settings.chunk_overlap,
        )

        for ch in chunks:
            all_docs.append(Document(page_content=ch.text, metadata=ch.meta))

    return all_docs
