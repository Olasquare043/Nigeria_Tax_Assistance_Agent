import json
import uuid
from langchain_core.messages import HumanMessage

from ai_engine.tax_engine.agent_graph import build_graph


def ask(app, q: str, thread_id: str):
    out = app.invoke(
        {"messages": [HumanMessage(content=q)]},
        config={"configurable": {"thread_id": thread_id}},
    )
    payload = json.loads(out["messages"][-1].content)

    print("\n==============================")
    print("Q:", q)
    print("route:", payload.get("route"), "refusal:", payload.get("refusal"))
    print("citations:")
    for c in payload.get("citations", []):
        src = c.get("source")
        pages = c.get("pages")
        quote = (c.get("quote") or "")[:140]
        print(f"- {src} {pages} :: {quote}")
    print("\nanswer:\n", payload.get("answer"))


if __name__ == "__main__":
    app = build_graph()

    # Use ONE thread_id so the conversation memory is consistent across these 3 tests
    tid = f"smoke-{uuid.uuid4().hex[:8]}"

    ask(app, "I heard I will pay 50% tax now. Is it true?", tid)
    ask(app, "They increased VAT to 50%. True?", tid)
    ask(app, "Explain VAT derivation changes.", tid)
