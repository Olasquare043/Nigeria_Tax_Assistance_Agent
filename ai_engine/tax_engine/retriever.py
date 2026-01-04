from __future__ import annotations

import re
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


def _has_percent_or_number(q: str) -> bool:
    ql = (q or "").lower()
    return bool(re.search(r"\b\d+\s*%|\b\d+\s*percent\b", ql)) or bool(re.search(r"\b\d{2,}\b", ql))


def _looks_like_rate_question(q: str) -> bool:
    ql = (q or "").lower()
    # if the user mentions %/number OR says rate/percent explicitly, treat it as rate-related
    return _has_percent_or_number(ql) or ("rate" in ql) or ("percent" in ql) or ("%" in ql)


def _expand_query(q: str) -> List[str]:
    ql = (q or "").lower()
    expansions = [q]

    # VAT distribution / derivation expansions
    if "vat" in ql or "value added tax" in ql:
        expansions.extend([
            "VAT derivation",
            "VAT allocation formula",
            "distribution of VAT proceeds",
            "VAT sharing formula",
            "derivation principle VAT",
            "Value Added Tax distribution among states",
        ])

    # Rate expansions (handles “50% tax” type claims)
    if _looks_like_rate_question(ql):
        expansions.extend([
            "rate of tax",
            "tax rate",
            "income tax rate",
            "companies income tax rate",
            "personal income tax rate",
            "PAYE rate",
            "Value Added Tax rate",
            "VAT rate",
            "withholding tax rate",
        ])

    return list(dict.fromkeys([x for x in expansions if x.strip()]))


@lru_cache(maxsize=1)
def _all_chunks_cached() -> List[Document]:
    chroma = load_chroma()
    got = chroma.get(include=["documents", "metadatas"])
    docs = got.get("documents", []) or []
    metas = got.get("metadatas", []) or []
    out: List[Document] = []
    for text, meta in zip(docs, metas):
        out.append(Document(page_content=text or "", metadata=meta or {}))
    return out


def _strict_rate_filter(query: str) -> List[Document]:
    """
    For numeric/rate claims, return chunks that look like *rates*,
    not penalties or revenue splits.
    Heuristic: must contain 'rate' (or 'rates') and 'tax' (or a tax type like VAT/income tax).
    """
    ql = (query or "").lower()
    if not _looks_like_rate_question(ql):
        return []

    hits = []
    for d in _all_chunks_cached():
        t = (d.page_content or "").lower()

        has_rate_word = ("rate" in t) or ("rates" in t)
        has_tax_context = ("tax" in t) or ("vat" in t) or ("income tax" in t) or ("paye" in t)

        # this avoids picking "40% penalty" chunks (often have % but not "rate")
        if has_rate_word and has_tax_context:
            hits.append(d)

    return hits


def retrieve(query: str) -> List[Document]:
    chroma = load_chroma()

    final_k = max(settings.top_k, 8)
    candidate_k = max(25, final_k)

    queries = _expand_query(query)

    results: List[Document] = []
    for qq in queries[:8]:
        results.extend(chroma.similarity_search(qq, k=candidate_k))

    results = _dedupe(results)

    # Add strict rate matches for “50% tax” claims
    strict = _strict_rate_filter(query)
    if strict:
        results = _dedupe(strict + results)

    return results[:final_k]
