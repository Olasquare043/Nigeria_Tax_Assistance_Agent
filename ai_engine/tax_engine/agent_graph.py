from __future__ import annotations

import json
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


def route_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    payload = _json_call(ROUTER_LLM, ROUTER, user_text)
    route = payload.get("route", "qa")
    need = bool(payload.get("need_retrieval", route in ("qa", "claim_check")))
    return {"route": route, "need_retrieval": need}


def smalltalk_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    ans = SMALLTALK_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=SMALLTALK_PROMPT.format(user_message=user_text)),
        ]
    ).content.strip()
    return {"messages": [AIMessage(content=ans)]}


def clarify_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    ans = CLARIFY_LLM.invoke(
        [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=CLARIFY_PROMPT.format(user_message=user_text)),
        ]
    ).content.strip()
    return {"messages": [AIMessage(content=ans)]}


def retrieve_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    docs = retrieve(user_text)
    return {"retrieved": docs}


def answer_node(state: TaxState) -> TaxState:
    user_text = _last_user_text(state)
    retrieved = state.get("retrieved", []) or []
    route = state.get("route", "qa")

    citations = build_citations(user_text, retrieved, max_cites=3)

    if not citations:
        payload = {
            "answer": (
                "I couldn’t find enough support for that in the uploaded documents.\n\n"
                "Try:\n• Mention the bill (HB-1759/HB-1756/HB-1757/HB-1758)\n"
                "• Add keywords like “VAT allocation / derivation / distribution”\n"
                "• Or paste the exact sentence you saw.\n"
            ),
            "citations": [],
            "refusal": True,
        }
        return {"messages": [AIMessage(content=json.dumps(payload, ensure_ascii=False))], "retrieved": []}

    quotes_block = "\n".join(
        [f"- ({c['source']} {c['pages']}) \"{c['quote']}\"" for c in citations]
    )

    if route == "claim_check":
        prompt = (
            "You are fact-checking a claim about the Nigerian Tax Reform Bills (2024).\n"
            "Use ONLY the quotes below. Do not add interpretation.\n"
            "If the quotes do not directly confirm or deny the claim, say you can’t confirm from the uploaded documents.\n\n"
            f"CLAIM / QUESTION: {user_text}\n\n"
            f"EVIDENCE QUOTES:\n{quotes_block}\n\n"
            "Write in this format:\n"
            "Claim:\n"
            "What the documents say:\n"
            "Conclusion (confirmed / not confirmed / unclear from sources):\n"
        )
    else:
        prompt = (
            "You are explaining Nigerian tax reform bills in plain language.\n"
            "Use ONLY the quotes below. Do NOT add assumptions or extra facts.\n"
            "If a detail is not stated in the quotes, explicitly say it is not confirmed in the provided excerpts.\n"
            "Write 4–8 sentences.\n\n"
            f"USER QUESTION: {user_text}\n\n"
            f"EVIDENCE QUOTES:\n{quotes_block}\n"
        )

    answer = WRITE_LLM.invoke([HumanMessage(content=prompt)]).content.strip()

    payload = {"answer": answer, "citations": citations, "refusal": False}
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
