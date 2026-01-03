from __future__ import annotations

import sys
from pathlib import Path

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.vectorstore import load_chroma


def snippet(text: str, kw: str, width: int = 120) -> str:
    t = text.lower()
    i = t.find(kw.lower())
    if i == -1:
        return text[:240].replace("\n", " ").strip()
    s = max(0, i - width)
    e = min(len(text), i + width)
    return text[s:e].replace("\n", " ").strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: python ai_engine/scripts/search_index.py <keyword1> [keyword2] ...")
        print('Example: python ai_engine/scripts/search_index.py vat derivation')
        return

    keywords = [k.lower() for k in sys.argv[1:]]
    chroma = load_chroma()

    got = chroma.get(include=["documents", "metadatas"])
    docs = got.get("documents", []) or []
    metas = got.get("metadatas", []) or []

    matches = []
    for text, meta in zip(docs, metas):
        t = (text or "").lower()
        if all(k in t for k in keywords):
            cid = (meta or {}).get("chunk_id", "")
            src = (meta or {}).get("source", "")
            ps = (meta or {}).get("page_start", "")
            pe = (meta or {}).get("page_end", "")
            matches.append((src, ps, pe, cid, text))

    print(f"Total chunks in DB: {len(docs)}")
    print(f"Keywords: {keywords}")
    print(f"Matching chunks: {len(matches)}\n")

    for i, (src, ps, pe, cid, text) in enumerate(matches[:20], start=1):
        print(f"{i}. {src} p.{ps}–{pe}  [{cid}]")
        print(f"   {snippet(text, keywords[0])}\n")

    if len(matches) > 20:
        print(f"... showing 20 of {len(matches)} matches")


if __name__ == "__main__":
    main()
