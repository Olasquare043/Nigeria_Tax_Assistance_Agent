from __future__ import annotations

from typing import List
from functools import lru_cache

from langchain_core.documents import Document

from .config import settings
from .vectorstore import load_chroma


def _dedupe(docs: List[Document]) -> List[Document]:
    seen = set()
    out = []
    for d in docs:
        cid = d.metadata.get("chunk_id")
        if cid and cid in seen:
            continue
        if cid:
            seen.add(cid)
        out.append(d)
    return out


def _expand_query(q: str) -> List[str]:
    ql = (q or "").lower()
    expansions = [q]

    if "vat" in ql or "value added tax" in ql:
        expansions.extend([
            "VAT derivation",
            "VAT allocation formula",
            "distribution of VAT proceeds",
            "VAT sharing formula",
            "derivation principle VAT",
        ])

    if "derivation" in ql and "vat" not in ql:
        expansions.extend([
            "VAT derivation",
            q + " VAT",
        ])

    return list(dict.fromkeys([x for x in expansions if x.strip()]))


@lru_cache(maxsize=1)
def _all_chunks_cached() -> List[Document]:
    """Load all chunks from Chroma (dev mode)."""
    chroma = load_chroma()
    got = chroma.get(include=["documents", "metadatas"])
    docs = got.get("documents", []) or []
    metas = got.get("metadatas", []) or []
    out: List[Document] = []
    for text, meta in zip(docs, metas):
        out.append(Document(page_content=text or "", metadata=meta or {}))
    return out


def _keyword_filter(query: str) -> List[Document]:
    """
    Strict keyword filter: if query contains VAT + derivation,
    return chunks that contain both words (high precision).
    """
    ql = (query or "").lower()
    must = []
    if "vat" in ql:
        must.append("vat")
    if "derivation" in ql:
        must.append("derivation")

    # Only apply strict filter for this specific scenario
    if not ("vat" in must and "derivation" in must):
        return []

    hits = []
    for d in _all_chunks_cached():
        tl = (d.page_content or "").lower()
        if all(m in tl for m in must):
            hits.append(d)

    return hits


def retrieve(query: str) -> List[Document]:
    chroma = load_chroma()

    final_k = max(settings.top_k, 8)
    candidate_k = max(20, final_k)

    # 1) Normal vector retrieval + expansions
    queries = _expand_query(query)
    results: List[Document] = []
    for qq in queries[:6]:
        results.extend(chroma.similarity_search(qq, k=candidate_k))
    results = _dedupe(results)

    # 2) Add strict keyword matches if needed (VAT+derivation case)
    strict_hits = _keyword_filter(query)
    if strict_hits:
        results = _dedupe(strict_hits + results)

    return results[:final_k]
