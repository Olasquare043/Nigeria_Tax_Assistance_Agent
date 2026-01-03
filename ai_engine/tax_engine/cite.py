from __future__ import annotations

import re
from typing import List, Dict, Any
from langchain_core.documents import Document


SENT_BOUNDARY_RE = re.compile(r"[\.!\?;:]\s+")


def _norm_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def _keywords_from_query(q: str) -> List[str]:
    ql = (q or "").lower()
    kws = []
    for kw in ["vat", "value added tax", "derivation", "allocation", "formula", "proceeds", "distribution"]:
        if kw in ql:
            kws.append(kw)
    if "vat" in ql and "derivation" not in kws:
        kws.append("derivation")
    return list(dict.fromkeys(kws))


def _word_clip_verbatim(text: str, max_words: int = 25) -> str:
    words = _norm_spaces(text).split(" ")
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words])


def _find_keyword_pos(text: str, keywords: List[str]) -> int:
    tl = (text or "").lower()
    positions = []
    for kw in keywords:
        i = tl.find(kw.lower())
        if i != -1:
            positions.append(i)
    return min(positions) if positions else -1


def _extract_sentence_like_snippet(text: str, pos: int, span_chars: int = 500) -> str:
    """
    Extract a readable snippet around pos by expanding to nearby punctuation boundaries.
    """
    if not text:
        return ""

    if pos < 0:
        # fallback: beginning
        return text[:span_chars]

    start = max(0, pos - span_chars // 2)
    end = min(len(text), pos + span_chars // 2)
    window = text[start:end]

    # Within the window, try to find boundaries around the keyword
    rel_pos = pos - start
    left = window.rfind(".", 0, rel_pos)
    left = max(left, window.rfind(";", 0, rel_pos))
    left = max(left, window.rfind(":", 0, rel_pos))
    left = max(left, window.rfind("\n", 0, rel_pos))

    right_candidates = [window.find(ch, rel_pos) for ch in [".", ";", ":", "\n"]]
    right_candidates = [x for x in right_candidates if x != -1]
    right = min(right_candidates) if right_candidates else len(window)

    # move past boundary char if found
    if left != -1:
        left = left + 1
    else:
        left = 0

    snippet = window[left:right].strip()

    # If snippet is too short, expand a bit
    if len(snippet) < 80:
        snippet = window[max(0, left - 80): min(len(window), right + 80)].strip()

    return snippet


def build_citations(query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    if not docs:
        return []

    keywords = _keywords_from_query(query)

    scored = []
    for d in docs:
        t = (d.page_content or "").lower()
        score = sum(1 for kw in keywords if kw.lower() in t)
        scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)

    top = [d for score, d in scored if score > 0][:max_cites]

    citations: List[Dict[str, Any]] = []
    for d in top:
        meta = d.metadata or {}
        cid = meta.get("chunk_id", "")
        src = meta.get("source", "")
        ps = meta.get("page_start", "")
        pe = meta.get("page_end", "")
        pages = f"p.{ps}–{pe}"

        text = d.page_content or ""
        pos = _find_keyword_pos(text, keywords)
        raw = _extract_sentence_like_snippet(text, pos)
        quote = _word_clip_verbatim(raw, max_words=25)

        citations.append(
            {"chunk_id": cid, "source": src, "pages": pages, "quote": quote}
        )

    return citations
