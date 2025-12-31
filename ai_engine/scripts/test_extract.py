from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.config import settings
from ai_engine.tax_engine.pdf_loader import extract_pages
from ai_engine.tax_engine.chunker import chunk_document


def main():
    docs_dir = Path(settings.docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))
    print("Docs dir:", docs_dir)
    print("PDFs found:", len(pdfs))
    if not pdfs:
        return

    pdf = pdfs[0]
    print("\nTesting on:", pdf.name)

    pages = extract_pages(pdf)
    print("Pages:", len(pages))
    print("Page 1 chars:", len(pages[0].text))

    page_dicts = [{"page_num": p.page_num, "text": p.text} for p in pages]
    chunks = chunk_document(pdf.name, page_dicts, chunk_chars=settings.chunk_chars, overlap=settings.chunk_overlap)
    print("Chunks:", len(chunks))
    print("First chunk meta:", chunks[0].meta)


if __name__ == "__main__":
    main()
