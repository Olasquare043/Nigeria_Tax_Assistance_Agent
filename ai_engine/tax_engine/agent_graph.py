from __future__ import annotations

import json
import re
from typing import Literal, Any, Dict

from langgraph.graph import START, END, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .config import settings
from .prompts import (
    ROUTER,
    SMALLTALK_PROMPT,
    CLARIFY_PROMPT,
    QA_PROMPT,
    CLAIM_CHECK_PROMPT,
    COMPARE_PROMPT,
)
from .retriever import retrieve
from .cite import build_citations


class TaxState(MessagesState, total=False):
    route: str
    need_retrieval: bool
    retrieved: list


# LLMs
ROUTER_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0)
SMALLTALK_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0.6)
CLARIFY_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0.4)
WRITE_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0)

# Patterns
PERCENT_RE = re.compile(r"\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*percent\b", re.IGNORECASE)
RATE_WORD_RE = re.compile(r"\brate(s)?\b", re.IGNORECASE)

SMALLTALK_RE = re.compile(
    r"^\s*(hi|hello|hey|good\s*(morning|afternoon|evening)|how\s+are\s+you|thanks?|thank\s+you)\b",
    re.IGNORECASE,
)

# too vague / generic
CLARIFY_RE = re.compile(
    r"^\s*(explain|help|tell\s+me|tax\s+changes\??|what\s+about\s+tax\??|tell\s+me\s+about\s+vat\??|what'?s\s+going\s+on)\b",
    re.IGNORECASE,
)

COMPARE_RE = re.compile(
    r"\b(compare|difference|different|what\s+changed|old\s+vs\s+new|before\s+vs\s+now|previous\s+system|current\s+system)\b",
    re.IGNORECASE,
)

CLAIM_RE = re.compile(
    r"\b(i\s+heard|rumou?r|twitter\s+says|people\s+said|is\s+it\s+true|true\s+or\s+false|they\s+increased|destroy\s+the\s+north|50%\b|50\s*percent\b)\b",
    re.IGNORECASE,
)

# strong policy keywords => should retrieve
STRONG_POLICY_RE = re.compile(
    r"\b(derivation|allocation|distribution|proceeds|exemptions?|exempt|rate|penalt(y|ies)|return(s)?|filing|credit|input\s+vat|output\s+vat)\b",
    re.IGNORECASE,
)

# explicit bill references => should retrieve
BILL_REF_RE = re.compile(
    r"\b(hb[-\s]?(1756|1757|1758|1759)|nigeria\s+tax\s+bill|tax\s+administration\s+bill|revenue\s+service\s+establishment|joint\s+revenue\s+board)\b",
    re.IGNORECASE,
)


def _json_call(llm: ChatOpenAI, system: str, user: str) -> Dict[str, Any]:
    resp = llm.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    txt = resp.content
    try:
        return json.loads(txt)
    except Exception:
        s, e = txt.find("{"), txt.rfind("}")
        if s != -1 and e != -1 and e > s:
            return json.loads(txt[s : e + 1])
        raise


def _last_user_text(state: TaxState) -> str:
    msgs = state.get("messages", [])
    for m in reversed(msgs):
        if isinstance(m, HumanMessage):
            return m.content
        if isinstance(m, dict) and m.get("type") == "human":
            return m.get("content", "")
    return ""


def _extract_claim_number(text: str) -> str | None:
    tl = (text or "").lower()
    m = re.search(r"(\d+(\.\d+)?)\s*%|\b(\d+(\.\d+)?)\s*percent\b", tl)
    if not m:
        return None
    return m.group(1) or m.group(3)


def _has_any_percent(text: str) -> bool:
    return bool(PERCENT_RE.search(text or ""))


def _has_exact_percent(text: str, num: str) -> bool:
    if not num:
        return False
    tl = (text or "").lower()
    return (f"{num}%" in tl) or (f"{num} percent" in tl)


def _deterministic_route(user_text: str) -> str | None:
    """
    Deterministic router for stable scoring:

    Priority:
    - smalltalk: greetings/thanks
    - compare: explicit compare language
    - claim_check: rumor framing / viral claims
    - qa: specific policy keywords or bill references
    - clarify: vague prompts without strong policy signals

    Return None to fall back to LLM router.
    """
    t = (user_text or "").strip()
    if not t:
        return "clarify"

    # 1) Smalltalk
    if SMALLTALK_RE.search(t):
        return "smalltalk"

    # 2) Compare
    if COMPARE_RE.search(t):
        return "compare"

    # 3) Claim check (rumors)
    if CLAIM_RE.search(t):
        return "claim_check"

    # 4) Strong policy signal => QA (retrieve)
    if BILL_REF_RE.search(t) or STRONG_POLICY_RE.search(t):
        return "qa"

    # 5) Clarify only when it's generic/vague
    if len(t.split()) <= 7 and CLARIFY_RE.search(t):
        return "clarify"

    return None


def route_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)

    # deterministic first
    d = _deterministic_route(user_text)
    if d is not None:
        route = d
        need = route in ("qa", "claim_check", "compare")
        return {"route": route, "need_retrieval": need}

    # fallback to LLM router
    router_prompt = ROUTER.replace("{user_message}", user_text)
    payload = _json_call(ROUTER_LLM, router_prompt, user_text)

    route = payload.get("route", "qa")
    need = bool(payload.get("need_retrieval", route in ("qa", "claim_check", "compare")))
    return {"route": route, "need_retrieval": need}


def smalltalk_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    route = state.get("route", "smalltalk")

    ans = SMALLTALK_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=SMALLTALK_PROMPT.format(user_message=user_text)),
        ]
    ).content.strip()

    payload = {"answer": ans, "refusal": False, "route": route, "citations": []}
    return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))]}


def clarify_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    route = state.get("route", "clarify")

    ans = CLARIFY_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=CLARIFY_PROMPT.format(user_message=user_text)),
        ]
    ).content.strip()

    payload = {"answer": ans, "refusal": False, "route": route, "citations": []}
    return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))]}


def retrieve_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    docs = retrieve(user_text)
    return {"retrieved": docs}


def answer_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    retrieved = state.get("retrieved", []) or []
    route = state.get("route", "qa")

    citations = build_citations(user_text, retrieved, max_cites=3)

    # -------------------------
    # CLAIM CHECK PATH
    # -------------------------
    if route == "claim_check":
        claim_num = _extract_claim_number(user_text)
        ql = (user_text or "").lower()

        # Detect claim type
        is_vat_claim = ("vat" in ql) or ("value added tax" in ql)
        is_distribution_claim = any(
            k in ql for k in ["derivation", "distribution", "allocation", "proceeds", "vat sharing"]
        )
        is_rate_claim = (claim_num is not None) or ("rate" in ql) or ("%" in ql) or ("percent" in ql)

        def _looks_like_vat_quote(q: str) -> bool:
            t = (q or "").lower()
            return ("vat" in t) or ("value added tax" in t)

        def _looks_like_distribution_quote(q: str) -> bool:
            t = (q or "").lower()
            return (
                (
                    "distributed" in t
                    or "distribution" in t
                    or "allocation" in t
                    or "credit of states" in t
                    or "local government" in t
                    or "states" in t
                    or "f.c.t" in t
                    or "derivation" in t
                )
                and ("rate" not in t)
            )

        def _looks_like_penalty_quote(q: str) -> bool:
            t = (q or "").lower()
            return ("penalty" in t) or ("administrative penalty" in t)

        def _looks_like_vat_rate_quote(q: str) -> bool:
            """
            A "VAT rate" quote must:
            - mention VAT (or Value Added Tax)
            - AND contain either an explicit percent OR the word rate/rates
            """
            if not _looks_like_vat_quote(q):
                return False
            return bool(PERCENT_RE.search(q or "")) or bool(RATE_WORD_RE.search(q or ""))

        # 1) Filter obvious mismatches (penalties, distribution-share % when user means "tax rate")
        filtered = []
        for c in citations:
            q = (c.get("quote") or "")

            if _looks_like_penalty_quote(q) and ("penalty" not in ql):
                continue

            # If user is asking about a "rate" claim (e.g., "50% tax") but not distribution,
            # do not use distribution-share percentages as evidence.
            if is_rate_claim and (not is_distribution_claim):
                if _looks_like_distribution_quote(q):
                    continue

            filtered.append(c)

        if filtered:
            citations = filtered

        # 2) Special guard: VAT + RATE claims should NEVER cite non-VAT evidence (e.g., CIT rates).
        if is_vat_claim and is_rate_claim and (not is_distribution_claim):
            # Try targeted retrieval for VAT rate clauses
            extra_docs = []
            for qq in [
                "VAT rate",
                "Value Added Tax rate",
                "rate of Value Added Tax",
                "Charge of VAT",
                "VAT is imposed",
                "chapter six Value Added Tax",
            ]:
                extra_docs.extend(retrieve(qq))

            extra_cites = build_citations("VAT rate", extra_docs, max_cites=8)
            extra_cites = [c for c in extra_cites if _looks_like_vat_rate_quote(c.get("quote", ""))]

            if extra_cites:
                citations = extra_cites[:3]
            else:
                # Fallback: at least keep VAT-related evidence only (drop CIT-only quotes).
                citations = [c for c in citations if _looks_like_vat_quote(c.get("quote", ""))]

        quotes = [c.get("quote", "") for c in citations]

        evidence_quotes = "\n".join(
            f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"'
            for c in citations
        )

        # Verdict logic (deterministic)
        verdict = "Unclear"
        if claim_num:
            if any(_has_exact_percent(q, claim_num) for q in quotes):
                verdict = "Confirmed"
            elif any(_has_any_percent(q) for q in quotes):
                verdict = "Not confirmed"
            else:
                verdict = "Unclear"
        else:
            verdict = "Not confirmed"

        prompt = CLAIM_CHECK_PROMPT.format(
            claim=user_text.strip(),
            verdict=verdict,
            evidence_quotes=evidence_quotes,
        )

        answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()

        payload = {
            "answer": answer,
            "citations": citations,
            "refusal": False,
            "route": route,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    # -------------------------
    # QA / COMPARE PATHS
    # -------------------------
    if not citations:
        payload = {
            "answer": (
                "I want to be careful here — I couldn’t find a clear clause in my memory that answers that exactly.\n\n"
                "Quick ways to help me locate it:\n"
                "• Mention the bill: HB-1759 / HB-1756 / HB-1757 / HB-1758\n"
                "• Add keywords you expect to appear (e.g., “VAT derivation”, “distribution of proceeds”, “tax rate”, “exemption”)\n"
                "• Or paste one sentence you saw online and I’ll verify it against the bills.\n"
            ),
            "citations": [],
            "refusal": True,
            "route": route,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    if route == "compare":
        quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])

        prompt = COMPARE_PROMPT.format(
            user_question=user_text,
            evidence_quotes=quotes_block,
        )

        answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()
        payload = {"answer": answer, "citations": citations, "refusal": False, "route": route}
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])

    prompt = QA_PROMPT.format(
        user_question=user_text,
        evidence_quotes=quotes_block,
    )

    answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()
    payload = {"answer": answer, "citations": citations, "refusal": False, "route": route}
    return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}


def build_graph():
    g = StateGraph(TaxState)

    g.add_node("route", route_node)
    g.add_node("smalltalk", smalltalk_node)
    g.add_node("clarify", clarify_node)
    g.add_node("retrieve", retrieve_node)
    g.add_node("answer", answer_node)

    g.add_edge(START, "route")

    def pick_path(s: TaxState) -> Literal["smalltalk", "clarify", "retrieve"]:
        r = s.get("route", "qa")
        if r == "smalltalk":
            return "smalltalk"
        if r == "clarify":
            return "clarify"
        return "retrieve"

    g.add_conditional_edges(
        "route",
        pick_path,
        {"smalltalk": "smalltalk", "clarify": "clarify", "retrieve": "retrieve"},
    )

    g.add_edge("smalltalk", END)
    g.add_edge("clarify", END)
    g.add_edge("retrieve", "answer")
    g.add_edge("answer", END)

    return g.compile(checkpointer=MemorySaver())
