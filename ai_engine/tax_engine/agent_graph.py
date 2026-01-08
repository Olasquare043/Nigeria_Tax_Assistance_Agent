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
    """Get the last user message (for backward compatibility)"""
    msgs = state.get("messages", [])
    for m in reversed(msgs):
        if isinstance(m, HumanMessage):
            return m.content
        if isinstance(m, dict) and m.get("type") == "human":
            return m.get("content", "")
    return ""


def _get_conversation_context(state: TaxState, window: int = 6) -> str:
    """Get recent conversation context as a formatted string"""
    msgs = state.get("messages", [])
    
    # Take last N messages (including current)
    recent = msgs[-window:] if len(msgs) > window else msgs
    
    context_parts = []
    for msg in recent:
        if isinstance(msg, HumanMessage):
            context_parts.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            # Try to parse AI message content
            content = msg.content
            try:
                # Check if it's JSON (QA/compare/claim_check response)
                data = json.loads(content)
                answer_text = data.get("answer", str(data))
                context_parts.append(f"Assistant: {answer_text}")
            except json.JSONDecodeError:
                # Not JSON, use as-is
                context_parts.append(f"Assistant: {content}")
        elif isinstance(msg, dict):
            role = "User" if msg.get("type") == "human" else "Assistant"
            context_parts.append(f"{role}: {msg.get('content', '')}")
    
    return "\n".join(context_parts)


def _get_user_message_with_context(state: TaxState, include_context: bool = True) -> str:
    """
    Get user message with conversation context.
    This is the main function to use for nodes that need context.
    """
    user_text = _last_user_text(state)
    
    if not include_context:
        return user_text
    
    context = _get_conversation_context(state, window=4)  # Last 4 messages
    
    # Combine context with current message
    return f"Conversation Context:\n{context}\n\nCurrent User Question: {user_text}"


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
    """Route node with conversation context awareness"""
    # Use context for routing decisions
    user_text_with_context = _get_user_message_with_context(state, include_context=True)
  
    current_user_text = _last_user_text(state)
    
   
    d = _deterministic_route(current_user_text)
    if d is not None:
        route = d
        need = route in ("qa", "claim_check", "compare")
        return {"route": route, "need_retrieval": need}

    # fallback to LLM router - but now with context
    router_prompt = ROUTER.replace("{user_message}", user_text_with_context)
    payload = _json_call(ROUTER_LLM, router_prompt, user_text_with_context)

    route = payload.get("route", "qa")
    need = bool(payload.get("need_retrieval", route in ("qa", "claim_check", "compare")))
    return {"route": route, "need_retrieval": need}


def smalltalk_node(state: TaxState) -> TaxState:
    """Smalltalk with conversation context"""
    user_text_with_context = _get_user_message_with_context(state, include_context=True)
    route = state.get("route", "smalltalk")

    ans = SMALLTALK_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=SMALLTALK_PROMPT.format(user_message=user_text_with_context)),
        ]
    ).content.strip()

    payload = {"answer": ans, "refusal": False, "route": route, "citations": []}
    return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))]}


def clarify_node(state: TaxState) -> TaxState:
    """Clarify with conversation context"""
    user_text_with_context = _get_user_message_with_context(state, include_context=True)
    route = state.get("route", "clarify")

    ans = CLARIFY_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=CLARIFY_PROMPT.format(user_message=user_text_with_context)),
        ]
    ).content.strip()

    payload = {"answer": ans, "refusal": False, "route": route, "citations": []}
    return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))]}


def retrieve_node(state: TaxState) -> TaxState:
    """Retrieve with conversation context for better search"""
    user_text_with_context = _get_user_message_with_context(state, include_context=True)
    docs = retrieve(user_text_with_context)
    return {"retrieved": docs}


def answer_node(state: TaxState) -> TaxState:
    """Answer with conversation context"""
    user_text_with_context = _get_user_message_with_context(state, include_context=True)
    current_user_text = _last_user_text(state)  
    retrieved = state.get("retrieved", []) or []
    route = state.get("route", "qa")

    citations = build_citations(current_user_text, retrieved, max_cites=3)

    if route == "claim_check":
        claim_num = _extract_claim_number(current_user_text)
        ql = (current_user_text or "").lower()

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

   
        if is_vat_claim and is_rate_claim and (not is_distribution_claim):
          
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
                citations = [c for c in citations if _looks_like_vat_quote(c.get("quote", ""))]

        quotes = [c.get("quote", "") for c in citations]

        evidence_quotes = "\n".join(
            f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"'
            for c in citations
        )

        
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
            user_message=user_text_with_context,  
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

    if not citations:
        
        refusal_answer = f"""I want to be careful here — I couldn’t find a clear clause in my memory that answers that exactly.

Quick ways to help me locate it:
• Mention the bill: HB-1759 / HB-1756 / HB-1757 / HB-1758
• Add keywords you expect to appear (e.g., “VAT derivation”, “distribution of proceeds”, “tax rate”, “exemption”)
• Or paste one sentence you saw online and I’ll verify it against the bills."""

        payload = {
            "answer": refusal_answer,
            "citations": [],
            "refusal": True,
            "route": route,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    if route == "compare":
        quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])

        
        prompt = COMPARE_PROMPT.format(
            user_message=user_text_with_context,  
            user_question=current_user_text,
            evidence_quotes=quotes_block,
        )

        answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()
        payload = {"answer": answer, "citations": citations, "refusal": False, "route": route}
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])

    prompt = QA_PROMPT.format(
        user_message=user_text_with_context,  
        user_question=current_user_text,
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