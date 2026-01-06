from __future__ import annotations

import re
from typing import List, Dict, Any, Tuple

from langchain_core.documents import Document

# -----------------------------
# Intent detection (query-level)
# -----------------------------
PERCENT_IN_QUERY_RE = re.compile(r"\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*percent\b", re.IGNORECASE)

RATE_WORD_RE = re.compile(r"\brate(s)?\b", re.IGNORECASE)
PERCENT_IN_TEXT_RE = re.compile(r"\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*percent\b", re.IGNORECASE)

DISTRIBUTION_WORDS_RE = re.compile(
    r"\b(derivation|distribution|distributed|allocation|proceeds|formula|sharing)\b",
    re.IGNORECASE,
)
GOV_ALLOCATION_CONTEXT_RE = re.compile(
    r"\b(states?|local\s+governments?|f\.?c\.?t|federal\s+government|state\s+government|local\s+government)\b",
    re.IGNORECASE,
)

TAX_CONTEXT_RE = re.compile(
    r"\b(tax|vat|value\s+added\s+tax|income\s+tax|personal\s+income|companies\s+income|withholding|paye)\b",
    re.IGNORECASE,
)

REDUCTION_CONTEXT_RE = re.compile(r"\b(reduction|reduced|decrease|lower)\b", re.IGNORECASE)


def _is_rate_intent(query: str) -> bool:
    q = (query or "").lower()
    if PERCENT_IN_QUERY_RE.search(q):
        return True
    if "tax rate" in q or "rate" in q or "percent" in q or "%" in q:
        return True
    # common rate-related terms
    if any(k in q for k in ["paye", "withholding", "companies income tax", "personal income tax", "vat rate"]):
        return True
    return False


def _is_distribution_intent(query: str) -> bool:
    q = (query or "").lower()
    return any(k in q for k in ["derivation", "distribution", "distributed", "allocation", "proceeds", "sharing", "formula"])


# -----------------------------
# Snippet formatting utilities
# -----------------------------
def _pages(meta: Dict[str, Any]) -> str:
    ps = meta.get("page_start")
    pe = meta.get("page_end")
    if ps and pe and ps != pe:
        return f"p.{ps}–{pe}"
    if ps:
        return f"p.{ps}"
    return "p.?"


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    # Fix common PDF merge: "derivation15" -> "derivation 15"
    s = re.sub(r"([A-Za-z])(\d{1,4})\b", r"\1 \2", s)
    return s


def _compact(s: str) -> str:
    return re.sub(r"[\s\-]+", "", (s or "").lower())


def _finish_clean(snippet: str, max_len: int = 320) -> str:
    s = _clean(snippet)
    if not s:
        return ""

    if len(s) > max_len:
        s = s[:max_len].rstrip()

    if s[-1] in [".", ";", ":"]:
        return s

    # If there is a boundary near the end, cut there (within last 80 chars)
    tail = s[-80:]
    best = max(tail.rfind("."), tail.rfind(";"), tail.rfind(":"))
    if best != -1:
        cut = len(s) - 80 + best + 1
        s2 = s[:cut].rstrip()
        if s2:
            return s2

    # Avoid ending on awkward stopwords if we're going to add ellipsis
    stopwords = {"of", "and", "to", "the", "a", "an", "in", "on", "for", "by", "with", "at", "or", "but"}
    parts = s.split()
    if parts and parts[-1].lower().strip(" ,") in stopwords and len(parts) >= 2:
        s = " ".join(parts[:-1]).rstrip()

    # Avoid ending mid-word (trim if last fragment is tiny)
    last_space = s.rfind(" ")
    if last_space > 0 and len(s) - last_space < 4:
        s = s[:last_space].rstrip()

    if s and s[-1] not in [".", ";", ":"]:
        s = s.rstrip(" ,") + "…"

    return s


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
    want_rate = _is_rate_intent(ql)
    want_dist = _is_distribution_intent(ql)

    # Query-adaptive key terms
    if want_rate and not want_dist:
        key_terms = [
            "tax rate",
            "rate",
            "rates",
            "income tax",
            "personal income tax",
            "companies income tax",
            "withholding tax",
            "paye",
            "vat rate",
            "value added tax rate",
            "percent",
        ]
    elif want_dist:
        key_terms = [
            "basis of derivation",
            "distributed on the basis of derivation",
            "derivation",
            "distribution of proceeds",
            "distribution",
            "distributed",
            "proceeds",
            "allocation",
            "formula",
            "states",
            "local governments",
            "vat",
            "value added tax",
            "attribution",
            "place of supply",
            "place of consumption",
        ]
    else:
        key_terms = [
            "derivation",
            "distribution",
            "proceeds",
            "vat",
            "value added tax",
            "rate",
            "exempt",
            "exemption",
            "penalty",
            "return",
        ]

    extra = [
        w
        for w in re.findall(r"[a-zA-Z]{4,}", ql)
        if w not in {"explain", "changes", "about", "please", "what", "does", "mean"}
    ]
    terms = key_terms + extra

    best = (-1, -1, -1)  # (score, start, end)

    for term in terms:
        term_l = term.lower()

        # 1) normal search
        idx = tl.find(term_l)
        if idx != -1:
            score = len(term_l)

            # Boost by intent
            if want_rate and term_l in {"rate", "rates", "tax rate", "income tax", "companies income tax", "vat rate"}:
                score += 60
            if want_dist and term_l in {"derivation", "distribution", "distributed", "proceeds", "basis of derivation"}:
                score += 60
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
            score = len(term_c)

            if want_rate and term_l in {"rate", "rates", "taxrate", "incometax", "companiesincometax", "vatrate"}:
                score += 60
            if want_dist and term_l in {"derivation", "distribution", "distributed", "proceeds", "basisofderivation"}:
                score += 60
            if "vat" in term_l:
                score += 10

            # approximate mapping compact -> original indices
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
    t = _clean(text)
    if not t:
        return ""

    if start < 0 or end < 0:
        raw = t[:max_len]
        return _finish_clean(raw, max_len=max_len)

    w0 = max(0, start - 180)
    w1 = min(len(t), end + 180)

    left_candidates = [t.rfind(".", 0, w0), t.rfind(";", 0, w0), t.rfind(":", 0, w0)]
    left = max(left_candidates)
    if left != -1:
        w0 = left + 1

    right_candidates = []
    for ch in [".", ";", ":"]:
        idx = t.find(ch, w1)
        if idx != -1:
            right_candidates.append(idx + 1)
    if right_candidates:
        w1 = min(right_candidates)

    snippet = t[w0:w1].strip()

    if len(snippet) > max_len:
        mid = max(0, start - w0)
        a = max(0, mid - max_len // 2)
        b = min(len(snippet), a + max_len)
        snippet = snippet[a:b].strip()
        snippet = ("…" if a > 0 else "") + snippet + ("…" if b < len(snippet) else "")

    return _finish_clean(snippet, max_len=max_len)


# -----------------------------
# Relevance guards (quote-level)
# -----------------------------
def _looks_like_distribution_quote(q: str) -> bool:
    if not q:
        return False
    return bool(DISTRIBUTION_WORDS_RE.search(q) and GOV_ALLOCATION_CONTEXT_RE.search(q))


def _looks_like_rate_quote(q: str) -> bool:
    if not q:
        return False

    # Best case: explicit "rate" + percent + tax context
    if RATE_WORD_RE.search(q) and PERCENT_IN_TEXT_RE.search(q) and TAX_CONTEXT_RE.search(q):
        return True

    # Accept: percent + tax context (even if "rate" isn't present)
    if PERCENT_IN_TEXT_RE.search(q) and TAX_CONTEXT_RE.search(q):
        return True

    # Accept: "reduction in income tax" statements as supportive context (no percent)
    if ("income tax" in q.lower() or "tax" in q.lower()) and REDUCTION_CONTEXT_RE.search(q):
        return True

    return False


def build_citations(user_query: str, docs: List[Document], max_cites: int = 3) -> List[Dict[str, Any]]:
    """
    Output schema expected by backend/frontend:
      {chunk_id, source, pages, quote}
    """
    want_rate = _is_rate_intent(user_query)
    want_dist = _is_distribution_intent(user_query)

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
        quote = _window_snippet(text, s, e, max_len=320)

        if not quote:
            continue

        # ---- Key guard: avoid mismatched “percent” citations ----
        if want_rate and not want_dist:
            # For rate questions, only keep rate-like quotes
            if not _looks_like_rate_quote(quote):
                continue
            # And explicitly drop distribution-allocation quotes (unless also rate-like)
            if _looks_like_distribution_quote(quote) and not RATE_WORD_RE.search(quote):
                continue

        if want_dist:
            # For derivation/distribution questions, prioritize distribution-like quotes,
            # but don't hard-drop rate quotes (sometimes both are relevant).
            pass

        out.append({"chunk_id": cid, "source": src, "pages": pages, "quote": quote})

    if not out:
        return []

    # -----------------------------
    # Scoring/sorting
    # -----------------------------
    ql = (user_query or "").lower()

    strong_rate = ["rate", "percent", "%", "income tax", "companies income tax", "personal income tax", "paye", "withholding", "vat rate"]
    strong_dist = ["derivation", "distribution", "distributed", "allocation", "proceeds", "states", "local governments", "formula", "place of consumption", "place of supply", "vat"]

    def score(c: Dict[str, Any]) -> int:
        qt = (c.get("quote") or "").lower()
        s = 0

        if want_rate:
            if _looks_like_rate_quote(qt):
                s += 80
            for w in strong_rate:
                if w in ql and w in qt:
                    s += 15
                elif w in qt:
                    s += 3

            # penalize distribution language when the user wanted rate
            if not want_dist and _looks_like_distribution_quote(qt):
                s -= 40

        if want_dist:
            if _looks_like_distribution_quote(qt):
                s += 70
            for w in strong_dist:
                if w in ql and w in qt:
                    s += 12
                elif w in qt:
                    s += 2

        # generic small boost for direct tax context
        if TAX_CONTEXT_RE.search(qt):
            s += 3

        return s

    out.sort(key=score, reverse=True)
    return out[:max_cites]
