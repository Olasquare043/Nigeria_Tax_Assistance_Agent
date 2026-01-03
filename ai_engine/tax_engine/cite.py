from __future__ import annotations

import re
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _tokenize(text: str) -> List[str]:
    return _norm_spaces(text).split(" ")


def _contains_term(text: str, term: str) -> bool:
    return term.lower() in (text or "").lower()


def _find_token_index(tokens: List[str], term: str) -> int:
    """
    Find first token index containing term (case-insensitive), stripping punctuation.
    """
    t = term.lower()
    for i, tok in enumerate(tokens):
        clean = re.sub(r"[^\w\-]", "", tok.lower())
        if t in clean:
            return i
    return -1


def _clip_around_term(text: str, anchor_term: str, max_words: int = 25, pre_words: int = 6) -> str:
    """
    Return a verbatim quote of max_words, centered around the anchor term
    so the quote definitely includes anchor_term (if present).
    """
    tokens = _tokenize(text)
    if not tokens:
        return ""

    idx = _find_token_index(tokens, anchor_term)
    if idx == -1:
        # fallback: first max_words
        return " ".join(tokens[:max_words])

    start = max(0, idx - pre_words)
    end = min(len(tokens), start + max_words)
    # if end clipped early and we have room on left, shift left
    if end - start < max_words and start > 0:
        start = max(0, end - max_words)

    return " ".join(tokens[start:end])


def _score_doc(doc: Document, must: List[str], nice: List[str]) -> int:
    text = (doc.page_content or "").lower()
    score = 0
    if must and all(m.lower() in text for m in must):
        score += 20
    score += sum(1 for k in nice if k.lower() in text)
    return score


def build_citations(query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    if not docs:
        return []

    ql = (query or "").lower()

    # Must-cover logic
    must = []
    if "vat" in ql and "derivation" in ql:
        must = ["vat", "derivation"]

    # nice keywords to rank docs
    nice = ["vat", "value added tax", "derivation", "allocation", "formula", "proceeds", "distribution", "taxable", "supplies", "location"]

    scored: List[Tuple[int, Document]] = []
    for d in docs:
        scored.append((_score_doc(d, must=must, nice=nice), d))
    scored.sort(key=lambda x: x[0], reverse=True)

    # Build candidate citation objects with anchored quotes
    candidates = []
    for score, d in scored:
        if score <= 0:
            continue

        meta = d.metadata or {}
        cid = meta.get("chunk_id", "")
        src = meta.get("source", "")
        ps = meta.get("page_start", "")
        pe = meta.get("page_end", "")
        pages = f"p.{ps}–{pe}"

        text = d.page_content or ""

        # Anchor preference: derivation first (for VAT derivation queries)
        anchor = "derivation" if "derivation" in ql else ("vat" if "vat" in ql else nice[0])

        quote = _clip_around_term(text, anchor_term=anchor, max_words=25, pre_words=7)

        has_vat = _contains_term(quote, "vat") or _contains_term(quote, "value added tax")
        has_der = _contains_term(quote, "derivation")

        candidates.append({
            "chunk_id": cid,
            "source": src,
            "pages": pages,
            "quote": quote,
            "_has_vat": has_vat,
            "_has_derivation": has_der,
            "_score": score
        })

    if not candidates:
        return []

    # Selection strategy:
    # - If VAT+derivation query: ensure at least one citation has derivation, and one has VAT (if possible)
    selected = []

    if must == ["vat", "derivation"]:
        der_candidates = [c for c in candidates if c["_has_derivation"]]
        vat_candidates = [c for c in candidates if c["_has_vat"]]

        if der_candidates:
            selected.append(der_candidates[0])
        if vat_candidates and (vat_candidates[0]["chunk_id"] not in {s["chunk_id"] for s in selected}):
            selected.append(vat_candidates[0])

    # Fill remaining slots by score
    for c in candidates:
        if len(selected) >= max_cites:
            break
        if c["chunk_id"] in {s["chunk_id"] for s in selected}:
            continue
        selected.append(c)

    # Remove internal fields
    clean = []
    for c in selected[:max_cites]:
        clean.append({
            "chunk_id": c["chunk_id"],
            "source": c["source"],
            "pages": c["pages"],
            "quote": c["quote"],
        })

    return clean
