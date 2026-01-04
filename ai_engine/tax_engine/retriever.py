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
        cid = (d.metadata or {}).get("chunk_id")
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
    return _has_percent_or_number(ql) or ("rate" in ql) or ("percent" in ql) or ("%" in ql)


def _looks_like_vat_derivation_question(q: str) -> bool:
    ql = (q or "").lower()
    return ("vat" in ql or "value added tax" in ql) and (
        "derivation" in ql or "distribution" in ql or "allocation" in ql or "proceeds" in ql
    )


def _compact(text: str) -> str:
    # remove whitespace + hyphens so "distribu\n ted" still matches "distributed"
    return re.sub(r"[\s\-]+", "", (text or "").lower())


def _has_token(text: str, token: str) -> bool:
    """
    Robust substring check that survives PDF line breaks/hyphenation.
    Example: "distribu\n ted" should match "distributed".
    """
    t = (text or "").lower()
    if token.lower() in t:
        return True
    return token.lower().replace(" ", "") in _compact(t)


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
            "Value Added Tax distribution among states",
            "basis of derivation",
            "distributed on the basis of derivation",
            "amount standing to the credit of states and local governments",
            "distribution of proceeds to states and local governments",
            "attribution of taxable supplies by location",
        ])

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
    ql = (query or "").lower()
    if not _looks_like_rate_question(ql):
        return []

    hits = []
    for d in _all_chunks_cached():
        t = (d.page_content or "").lower()
        has_rate_word = ("rate" in t) or ("rates" in t)
        has_tax_context = ("tax" in t) or ("vat" in t) or ("income tax" in t) or ("paye" in t)
        if has_rate_word and has_tax_context:
            hits.append(d)
    return hits


def _strict_vat_derivation_filter(query: str) -> List[Document]:
    """
    Force-retrieve derivation/distribution clauses even if PDF breaks words across lines.
    """
    if not _looks_like_vat_derivation_question(query):
        return []

    hits: List[Document] = []
    for d in _all_chunks_cached():
        text = d.page_content or ""

        # must mention derivation (robust)
        if not _has_token(text, "derivation"):
            continue

        # and must have distribution mechanics (robust)
        if (
            _has_token(text, "distributed")
            or _has_token(text, "distribution")
            or _has_token(text, "proceeds")
            or _has_token(text, "amount standing to the credit")
            or _has_token(text, "local governments")
            or _has_token(text, "states")
            or _has_token(text, "basis of derivation")
            or _has_token(text, "attribution")
        ):
            hits.append(d)

    return hits


def _boost_sort(query: str, docs: List[Document]) -> List[Document]:
    if not _looks_like_vat_derivation_question(query):
        return docs

    def score(d: Document) -> int:
        text = d.page_content or ""
        src = ((d.metadata or {}).get("source") or "").lower()
        s = 0

        if _has_token(text, "derivation"):
            s += 6
        if _has_token(text, "basis of derivation"):
            s += 5
        if _has_token(text, "distributed") or _has_token(text, "distribution"):
            s += 5
        if _has_token(text, "proceeds"):
            s += 3
        if _has_token(text, "states") or _has_token(text, "local governments"):
            s += 3
        if _has_token(text, "attribution"):
            s += 2
        if "hb-1756" in src:
            s += 2

        return s

    return sorted(docs, key=score, reverse=True)


def retrieve(query: str) -> List[Document]:
    chroma = load_chroma()

    final_k = max(settings.top_k, 8)
    candidate_k = max(25, final_k)

    queries = _expand_query(query)

    results: List[Document] = []
    for qq in queries[:8]:
        results.extend(chroma.similarity_search(qq, k=candidate_k))

    results = _dedupe(results)

    strict_rate = _strict_rate_filter(query)
    if strict_rate:
        results = _dedupe(strict_rate + results)

    # ✅ robust strict VAT derivation injection
    strict_vat = _strict_vat_derivation_filter(query)
    if strict_vat:
        results = _dedupe(strict_vat + results)

    results = _boost_sort(query, results)

    return results[:final_k]
