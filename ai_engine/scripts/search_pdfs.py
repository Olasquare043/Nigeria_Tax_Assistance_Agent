from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.config import settings
from ai_engine.tax_engine.pdf_loader import extract_pages


def snippet_around(text: str, idx: int, width: int = 120) -> str:
    start = max(0, idx - width)
    end = min(len(text), idx + width)
    return text[start:end].replace("\n", " ").strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_engine/scripts/search_pdfs.py <keyword1> [keyword2] [keyword3]")
        print('Example: python ai_engine/scripts/search_pdfs.py vat derivation')
        return

    keywords = [k.lower() for k in sys.argv[1:]]
    docs_dir = Path(settings.docs_dir)
    pdfs = sorted(docs_dir.glob("*.pdf"))

    print(f"Docs dir: {docs_dir}")
    print(f"PDFs found: {len(pdfs)}")
    print(f"Keywords: {keywords}\n")

    total_hits = 0

    for pdf in pdfs:
        pages = extract_pages(pdf)
        file_hits = 0

        for p in pages:
            txt = (p.text or "")
            t = txt.lower()
            if all(k in t for k in keywords):
                file_hits += 1
                total_hits += 1

                # find first keyword occurrence
                first_kw = keywords[0]
                idx = t.find(first_kw) if first_kw in t else 0
                snip = snippet_around(txt, idx)

                print(f"[HIT] {pdf.name}  page {p.page_num}")
                print(f"      {snip}\n")

        if file_hits:
            print(f"--- {pdf.name}: {file_hits} matching page(s)\n")

    print(f"TOTAL matching pages across all PDFs: {total_hits}")


if __name__ == "__main__":
    main()
