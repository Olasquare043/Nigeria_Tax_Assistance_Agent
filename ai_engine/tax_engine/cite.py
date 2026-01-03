from __future__ import annotations

import re
from typing import List, Dict, Any, Tuple
from langchain_core.documents import Document


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _word_clip_verbatim(text: str, max_words: int = 25) -> str:
    words = _norm_spaces(text).split(" ")
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words])


def _has_all(text: str, must: List[str]) -> bool:
    tl = (text or "").lower()
    return all(m.lower() in tl for m in must)


def _best_window_containing(text: str, must: List[str], window: int = 450) -> str:
    """
    Return a window around the first occurrence of the first must-word,
    but ensure the window contains all must words (if possible).
    """
    t = text or ""
    tl = t.lower()

    # find earliest position among must terms
    positions = []
    for m in must:
        i = tl.find(m.lower())
        if i != -1:
            positions.append(i)
    if not positions:
        return t[:window]

    pos = min(positions)
    start = max(0, pos - window // 2)
    end = min(len(t), pos + window // 2)
    win = t[start:end]

    # If not all must words in window, just expand to bigger
    if not _has_all(win, must):
        start = max(0, pos - window)
        end = min(len(t), pos + window)
        win = t[start:end]

    return win.strip()


def _score_doc_for_query(doc: Document, must: List[str], nice: List[str]) -> int:
    """
    Score doc:
    +10 if contains all must
    +1 for each nice keyword
    """
    text = (doc.page_content or "").lower()
    score = 0
    if must and all(m.lower() in text for m in must):
        score += 10
    score += sum(1 for k in nice if k.lower() in text)
    return score


def build_citations(query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    if not docs:
        return []

    ql = (query or "").lower()

    # Must-include logic for VAT derivation questions
    must: List[str] = []
    if "vat" in ql and "derivation" in ql:
        must = ["vat", "derivation"]

    # Nice-to-have keywords
    nice = []
    for kw in ["vat", "value added tax", "derivation", "allocation", "formula", "proceeds", "distribution", "taxable supplies", "location"]:
        if kw in ql or kw in ["vat", "derivation"]:
            nice.append(kw)

    scored: List[Tuple[int, Document]] = []
    for d in docs:
        scored.append((_score_doc_for_query(d, must=must, nice=nice), d))
    scored.sort(key=lambda x: x[0], reverse=True)

    chosen_docs: List[Document] = []
    # If must exists, ensure we pick at least one must-matching doc if available
    if must:
        must_docs = [d for score, d in scored if _has_all(d.page_content, must)]
        if must_docs:
            chosen_docs.append(must_docs[0])

    # Fill remaining slots with top-scored docs not already chosen
    for score, d in scored:
        if len(chosen_docs) >= max_cites:
            break
        if d in chosen_docs:
            continue
        if score <= 0:
            continue
        chosen_docs.append(d)

    # Build citation objects with clean quotes
    citations: List[Dict[str, Any]] = []
    for d in chosen_docs[:max_cites]:
        meta = d.metadata or {}
        cid = meta.get("chunk_id", "")
        src = meta.get("source", "")
        ps = meta.get("page_start", "")
        pe = meta.get("page_end", "")
        pages = f"p.{ps}–{pe}"

        snippet = _best_window_containing(d.page_content or "", must=must, window=450)
        quote = _word_clip_verbatim(snippet, max_words=25)

        citations.append(
            {"chunk_id": cid, "source": src, "pages": pages, "quote": quote}
        )

    return citations
