from __future__ import annotations

import json
import re
from typing import TypedDict, Literal, Annotated, Any, Dict

from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .config import settings
from .prompts import ROUTER, SMALLTALK_PROMPT, CLARIFY_PROMPT
from .retriever import retrieve
from .cite import build_citations


class TaxState(TypedDict, total=False):
    messages: Annotated[list, add_messages]
    route: str
    need_retrieval: bool
    retrieved: list


ROUTER_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0)
SMALLTALK_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0.6)
CLARIFY_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0.4)
WRITE_LLM = ChatOpenAI(model=settings.openai_chat_model, temperature=0)

PERCENT_RE = re.compile(r"\b\d+(\.\d+)?\s*%|\b\d+(\.\d+)?\s*percent\b", re.IGNORECASE)


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


def route_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
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

    # claim_check + no evidence => friendly refusal
    if route == "claim_check" and not citations:
        payload = {
            "answer": (
                "I get why that would worry you. I couldn’t find a clause in the uploaded excerpts that supports that exact rate claim.\n\n"
                "To check properly, which tax do you mean?\n"
                "• VAT?\n• Personal income tax (PAYE)?\n• Company income tax (CIT)?\n\n"
                "Once you specify, I’ll pull the exact clause (with page citations) if it exists in your PDFs."
            ),
            "citations": [],
            "refusal": True,
            "route": route,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    # qa/compare + no evidence
    if not citations:
        payload = {
            "answer": (
                "I couldn’t find enough support for that in the uploaded documents.\n\n"
                "Try:\n• Mention the bill (HB-1759/HB-1756/HB-1757/HB-1758)\n"
                "• Add keywords like “VAT derivation / distribution / tax rate / exemption”\n"
                "• Or paste the exact sentence you saw.\n"
            ),
            "citations": [],
            "refusal": True,
            "route": route,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    # deterministic numeric claim_check
    if route == "claim_check":
        claim_num = _extract_claim_number(user_text)
        quotes = [c["quote"] for c in citations]
        joined = "\n".join(
            f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations
        )

        conclusion = "Unclear from these excerpts."
        if claim_num:
            if any(_has_exact_percent(q, claim_num) for q in quotes):
                conclusion = "Confirmed by the excerpts."
            elif any(_has_any_percent(q) for q in quotes):
                conclusion = "Not confirmed by the excerpts."
            else:
                conclusion = "Unclear from these excerpts."

        answer = (
            f"Claim: {user_text}\n\n"
            f"What the documents say (quotes):\n{joined}\n\n"
            f"Conclusion: {conclusion}"
        )

        payload = {"answer": answer, "citations": citations, "refusal": False, "route": route}
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    # compare mode
    if route == "compare":
        quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])
        prompt = (
            "You are answering a comparison question about Nigerian Tax Reform Bills (2024).\n"
            "Use ONLY the quotes below.\n"
            "Do NOT assume what the old law says unless the quote explicitly describes the current/extant system.\n\n"
            "Write exactly this structure:\n"
            "A) What the excerpts describe as the CURRENT/EXTANT system (bullets)\n"
            "B) What the excerpts describe as the PROPOSED/NEW approach (bullets)\n"
            "C) Differences explicitly supported by the excerpts (bullets)\n"
            "D) What is unclear from these excerpts (1–2 bullets)\n"
            "E) One short summary sentence\n\n"
            f"USER QUESTION: {user_text}\n\nEVIDENCE QUOTES:\n{quotes_block}\n"
        )
        answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()
        payload = {"answer": answer, "citations": citations, "refusal": False, "route": route}
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    # normal QA mode
    quotes_block = "\n".join([f'- ({c["source"]} {c["pages"]}) "{c["quote"]}"' for c in citations])
    prompt = (
        "You are explaining Nigerian tax reform bills in plain language.\n"
        "Use ONLY the quotes below.\n"
        "Do NOT infer beyond the quotes.\n\n"
        "Write:\n"
        "1) What the excerpts explicitly state (2–4 bullets)\n"
        "2) What is unclear from these excerpts (1–2 bullets)\n"
        "3) One short summary sentence\n\n"
        f"USER QUESTION: {user_text}\n\nEVIDENCE QUOTES:\n{quotes_block}\n"
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
        route = s.get("route", "qa")
        if route == "smalltalk":
            return "smalltalk"
        if route == "clarify":
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
