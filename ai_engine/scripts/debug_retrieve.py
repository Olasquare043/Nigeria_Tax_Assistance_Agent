from __future__ import annotations

import sys
from pathlib import Path

# ✅ Ensure project root is on PYTHONPATH when running as a file
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.retriever import retrieve  # noqa: E402


def main():
    q = " ".join(sys.argv[1:]).strip()
    if not q:
        print('Usage: python ai_engine/scripts/debug_retrieve.py "your question"')
        return

    docs = retrieve(q)
    print(f"Query: {q}")
    print(f"Retrieved: {len(docs)} docs\n")

    for i, d in enumerate(docs, 1):
        meta = d.metadata or {}
        src = meta.get("source", "?")
        pages = f"p.{meta.get('page_start')}–{meta.get('page_end')}"
        cid = meta.get("chunk_id", "?")
        snippet = (d.page_content or "").replace("\n", " ")
        snippet = snippet[:220] + ("..." if len(snippet) > 220 else "")
        print(f"{i}. {src} {pages} [{cid}]")
        print(f"   {snippet}\n")


if __name__ == "__main__":
    main()
