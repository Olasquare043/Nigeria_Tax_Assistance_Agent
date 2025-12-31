from __future__ import annotations

import sys
from pathlib import Path
import hashlib
from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.config import settings
from ai_engine.tax_engine.pdf_loader import extract_pages
from ai_engine.tax_engine.chunker import chunk_document
from ai_engine.tax_engine.vectorstore import upsert_incremental


def sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()


def main():
    docs_dir = Path(settings.docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))

    print("\n=============================")
    print(" Nigeria Tax Assistant Indexer")
    print("=============================\n")
    print(f"[Stage 0] Docs folder: {docs_dir}")
    print(f"[Stage 0] Found {len(pdfs)} PDF(s)\n")

    if not pdfs:
        print("❌ No PDFs found in docs/.")
        return

    all_docs: list[Document] = []
    per_pdf_counts = []

    print("[Stage 1] Extracting + chunking\n")
    for i, pdf in enumerate(pdfs, start=1):
        print(f"  ({i}/{len(pdfs)}) Loading/extracting: {pdf.name}")
        pages = extract_pages(pdf)
        non_empty = sum(1 for p in pages if p.text.strip())
        print(f"      Extracted pages: {len(pages)} (non-empty: {non_empty})")

        print("      Chunking…")
        page_dicts = [{"page_num": p.page_num, "text": p.text} for p in pages]
        chunks = chunk_document(
            file_name=pdf.name,
            pages=page_dicts,
            chunk_chars=settings.chunk_chars,
            overlap=settings.chunk_overlap,
        )
        print(f"      ✅ Chunks created: {len(chunks)}\n")

        per_pdf_counts.append((pdf.name, len(chunks)))

        for ch in chunks:
            d = Document(page_content=ch.text, metadata=ch.meta)
            d.metadata["content_hash"] = sha1_text(d.page_content)
            all_docs.append(d)

    print("[Stage 2] Summary (chunks per PDF)")
    total = 0
    for name, count in per_pdf_counts:
        total += count
        print(f"  - {name}: {count}")
    print(f"  TOTAL chunks prepared: {total}\n")

    print("[Stage 3] Indexing into ChromaDB (incremental update)")
    stats = upsert_incremental(all_docs)

    print("\n✅ Index update complete.")
    print("Stats:")
    print(f"  Existing docs before: {stats['existing_store_docs_before']}")
    print(f"  Existing unique chunk_ids before: {stats['existing_unique_chunk_ids_before']}")
    print(f"  Deduped removed: {stats['deduped_removed']}")
    print(f"  Added (new): {stats['added']}")
    print(f"  Updated (changed): {stats['updated']}")
    print(f"  Skipped (same): {stats['skipped']}\n")


if __name__ == "__main__":
    main()
