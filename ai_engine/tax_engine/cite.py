from __future__ import annotations

import re
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document


RATE_WORD_RE = re.compile(r"\brate(s)?\b", re.IGNORECASE)
PERCENT_RE = re.compile(r"\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*percent\b", re.IGNORECASE)


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _tokens(text: str) -> List[str]:
    return _norm_spaces(text).split(" ")


def _has_percent_or_number(q: str) -> bool:
    ql = (q or "").lower()
    return bool(re.search(r"\b\d+\s*%|\b\d+\s*percent\b", ql)) or bool(re.search(r"\b\d{2,}\b", ql))


def _looks_like_rate_question(q: str) -> bool:
    ql = (q or "").lower()
    return _has_percent_or_number(ql) or ("rate" in ql) or ("percent" in ql) or ("%" in ql)


def _is_vat_query(q: str) -> bool:
    ql = (q or "").lower()
    return ("vat" in ql) or ("value added tax" in ql)


def _find_token_index(tokens: List[str], term: str) -> int:
    t = term.lower()
    for i, tok in enumerate(tokens):
        clean = re.sub(r"[^\w%\-]", "", tok.lower())
        if t in clean:
            return i
    return -1


def _clip_around(text: str, term: str, max_words: int = 25, pre_words: int = 7) -> str:
    toks = _tokens(text)
    if not toks:
        return ""
    idx = _find_token_index(toks, term)
    if idx == -1:
        return " ".join(toks[:max_words])
    start = max(0, idx - pre_words)
    end = min(len(toks), start + max_words)
    if end - start < max_words and start > 0:
        start = max(0, end - max_words)
    return " ".join(toks[start:end])


def _extract_claim_number(query: str) -> str | None:
    ql = (query or "").lower()
    m = re.search(r"(\d+(\.\d+)?)\s*%|\b(\d+(\.\d+)?)\s*percent\b", ql)
    if not m:
        return None
    return m.group(1) or m.group(3)


def _doc_score(doc: Document, anchors: List[str]) -> int:
    t = (doc.page_content or "").lower()
    score = 0
    for a in anchors:
        if a.lower() in t:
            score += 2
    # boost likely rate clauses
    if "rate" in t or "rates" in t:
        score += 3
    if "%" in t or "percent" in t:
        score += 2
    return score


def build_citations(query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    if not docs:
        return []

    is_rate_q = _looks_like_rate_question(query)
    is_vat_q = _is_vat_query(query)
    claim_num = _extract_claim_number(query)  # e.g., "50"

    anchors: List[str] = []
    if is_vat_q:
        anchors.extend(["vat", "value", "added", "tax"])
    if is_rate_q:
        anchors.extend(["rate", "rates", "%", "percent"])
        if claim_num:
            anchors.append(claim_num)

    if not anchors:
        anchors = ["vat", "tax", "derivation", "distribution"]

    scored: List[Tuple[int, Document]] = [(_doc_score(d, anchors), d) for d in docs]
    scored.sort(key=lambda x: x[0], reverse=True)

    citations: List[Dict[str, Any]] = []
    for score, d in scored:
        if len(citations) >= max_cites:
            break
        if score <= 0:
            continue

        meta = d.metadata or {}
        cid = meta.get("chunk_id", "")
        src = meta.get("source", "")
        ps = meta.get("page_start", "")
        pe = meta.get("page_end", "")
        pages = f"p.{ps}–{pe}"

        doc_text = d.page_content or ""
        doc_lower = doc_text.lower()

        chosen_anchor = anchors[0]
        for a in anchors:
            if a.lower() in doc_lower:
                chosen_anchor = a
                break

        quote = _clip_around(doc_text, chosen_anchor, max_words=25, pre_words=7)
        q_quote = quote.lower()

        # ---------------- Relevance Guards ----------------
        # If it's a rate question, require whole-word "rate/rates" AND some percent/number evidence.
        if is_rate_q:
            if not RATE_WORD_RE.search(quote):
                continue
            # must contain a percent expression OR (if claim_num exists) the claim number
            if not PERCENT_RE.search(quote) and not (claim_num and claim_num in q_quote):
                continue

        # If it's VAT + rate, require VAT in quote too (avoid unrelated tax rates)
        if is_vat_q and is_rate_q:
            if not ("vat" in q_quote or "value added tax" in q_quote):
                continue

        citations.append({"chunk_id": cid, "source": src, "pages": pages, "quote": quote})

    return citations
