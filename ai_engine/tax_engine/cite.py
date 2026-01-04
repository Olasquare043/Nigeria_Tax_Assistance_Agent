from __future__ import annotations

import re
from typing import List, Dict, Any, Tuple

from langchain_core.documents import Document


def _pages(meta: Dict[str, Any]) -> str:
    ps = meta.get("page_start")
    pe = meta.get("page_end")
    if ps and pe and ps != pe:
        return f"p.{ps}–{pe}"
    if ps:
        return f"p.{ps}"
    return "p.?"


def _clean(s: str) -> str:
    # normalize whitespace but keep meaning
    return re.sub(r"\s+", " ", (s or "").strip())


def _compact(s: str) -> str:
    # helps match across PDF hyphenation/linebreaks
    return re.sub(r"[\s\-]+", "", (s or "").lower())


def _find_best_hit(text: str, query: str) -> Tuple[int, int]:
    """
    Return (best_start, best_end) of a matched keyword span.
    If no hit, return (-1, -1).
    Robust to PDF breaks using compact matching.
    """
    t = text or ""
    tl = t.lower()
    tc = _compact(t)

    ql = (query or "").lower()

    # prioritize these “legal meaning” terms
    key_terms = [
        "basis of derivation",
        "distributed on the basis of derivation",
        "derivation",
        "distribution of proceeds",
        "distribution",
        "distributed",
        "proceeds",
        "states",
        "local governments",
        "attribution",
        "vat",
        "value added tax",
        "rate",
        "exempt",
        "exemption",
    ]

    # also add a few query words if they look meaningful
    extra = [w for w in re.findall(r"[a-zA-Z]{4,}", ql) if w not in {"explain", "changes", "about", "please"}]
    terms = key_terms + extra

    best = (-1, -1, -1)  # (score, start, end)

    for term in terms:
        term_l = term.lower()
        # 1) normal search
        idx = tl.find(term_l)
        if idx != -1:
            score = len(term_l)
            if term_l in {"derivation", "distributed", "distribution", "proceeds", "basis of derivation"}:
                score += 50
            if "vat" in term_l:
                score += 10
            span = (idx, idx + len(term_l))
            if score > best[0]:
                best = (score, span[0], span[1])
            continue

        # 2) compact search (handles breaks/hyphens)
        term_c = term_l.replace(" ", "")
        idxc = tc.find(term_c)
        if idxc != -1:
            # Map compact index back approximately by scanning original text
            # We take a fallback approach: find the first place in original text where compact matches begin.
            score = len(term_c)
            if term_l in {"derivation", "distributed", "distribution", "proceeds", "basis of derivation"}:
                score += 50
            if "vat" in term_l:
                score += 10

            # approximate mapping: walk original text and count compact chars
            start = 0
            count = 0
            for i, ch in enumerate(t):
                if ch.isspace() or ch == "-":
                    continue
                if count == idxc:
                    start = i
                    break
                count += 1

            end = start
            # extend by term length in compact chars
            needed = len(term_c)
            count2 = 0
            for i in range(start, len(t)):
                ch = t[i]
                if ch.isspace() or ch == "-":
                    continue
                count2 += 1
                end = i + 1
                if count2 >= needed:
                    break

            if score > best[0]:
                best = (score, start, end)

    if best[0] == -1:
        return (-1, -1)
    return (best[1], best[2])


def _window_snippet(text: str, start: int, end: int, max_len: int = 280) -> str:
    """
    Build a readable snippet around (start,end).
    Expands to nearby sentence boundaries when possible.
    """
    t = _clean(text)
    if not t:
        return ""

    if start < 0 or end < 0:
        return t[:max_len] + ("…" if len(t) > max_len else "")

    # choose a window around the hit
    w0 = max(0, start - 180)
    w1 = min(len(t), end + 180)

    # try to expand to sentence boundaries (period/semicolon/newline)
    left = t.rfind(".", 0, w0)
    left2 = t.rfind(";", 0, w0)
    left = max(left, left2)
    if left != -1:
        w0 = left + 1

    right = t.find(".", w1)
    right2 = t.find(";", w1)
    candidates = [x for x in [right, right2] if x != -1]
    if candidates:
        w1 = min(candidates) + 1

    snippet = t[w0:w1].strip()

    # clamp length
    if len(snippet) > max_len:
        # keep center around hit
        mid = max(0, start - w0)
        a = max(0, mid - max_len // 2)
        b = min(len(snippet), a + max_len)
        snippet = snippet[a:b].strip()
        snippet = ("…" if a > 0 else "") + snippet + ("…" if b < len(snippet) else "")

    return snippet


def build_citations(user_query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    """
    Return citations with meaningful quotes (not the first 200 chars).
    Output schema expected by backend/frontend:
      {chunk_id, source, pages, quote}
    """
    out: List[Dict[str, Any]] = []
    seen = set()

    for d in docs or []:
        meta = d.metadata or {}
        cid = meta.get("chunk_id")
        if not cid or cid in seen:
            continue
        seen.add(cid)

        src = meta.get("source", "unknown")
        pages = _pages(meta)

        text = d.page_content or ""
        s, e = _find_best_hit(text, user_query)
        quote = _window_snippet(text, s, e, max_len=280)

        out.append(
            {
                "chunk_id": cid,
                "source": src,
                "pages": pages,
                "quote": quote,
            }
        )

    # Prefer citations that actually contain strong terms from query
    # (simple score: presence of keywords)
    ql = (user_query or "").lower()
    strong = ["derivation", "distributed", "distribution", "proceeds", "vat", "rate", "exempt"]
    def score(c: Dict[str, Any]) -> int:
        qt = (c.get("quote") or "").lower()
        s = 0
        for w in strong:
            if w in ql and w in qt:
                s += 10
            elif w in qt:
                s += 2
        return s

    out.sort(key=score, reverse=True)
    return out[:max_cites]
