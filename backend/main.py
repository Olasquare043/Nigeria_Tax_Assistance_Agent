from __future__ import annotations

import sys
import json
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from langchain_core.messages import HumanMessage

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ai_engine.tax_engine.agent_graph import build_graph
from ai_engine.tax_engine.ingest import ingest_pdfs
from ai_engine.tax_engine.vectorstore import upsert_incremental

app = FastAPI(title="Nigeria Tax Bills Q&A API (Dev)")

# CORS (dev)
ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = build_graph()


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated session id")
    message: str


class Citation(BaseModel):
    chunk_id: str
    source: str
    pages: str
    quote: str


class ChatResponse(BaseModel):
    answer: str
    refusal: bool
    route: str
    citations: List[Citation] = []


class IngestResponse(BaseModel):
    indexed_chunks: int
    added: int
    updated: int
    skipped: int
    deduped_removed: int


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/ingest", response_model=IngestResponse)
def ingest():
    try:
        docs = ingest_pdfs()

        # Ensure content_hash exists
        import hashlib

        def sha1_text(t: str) -> str:
            return hashlib.sha1(t.encode("utf-8", errors="ignore")).hexdigest()

        for d in docs:
            if "content_hash" not in d.metadata:
                d.metadata["content_hash"] = sha1_text(d.page_content)

        stats = upsert_incremental(docs)
        return {
            "indexed_chunks": stats["total_input_docs"],
            "added": stats["added"],
            "updated": stats["updated"],
            "skipped": stats["skipped"],
            "deduped_removed": stats.get("deduped_removed", 0),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingest failed: {e}")


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        if not req.message or not req.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty.")

        # ✅ MessagesState: send only the new message
        out = graph.invoke(
            {"messages": [HumanMessage(content=req.message)]},
            config={"configurable": {"thread_id": req.session_id}},
        )

        # Last message should be assistant output
        msgs = out.get("messages", [])
        if not msgs:
            raise HTTPException(status_code=500, detail="Agent returned no messages.")

        last = msgs[-1]
        content = last.content if hasattr(last, "content") else str(last)

        # If content is JSON (QA/claim_check), parse it
        route = out.get("route", "qa")
        try:
            payload = json.loads(content)
            answer = payload.get("answer", "")
            citations = payload.get("citations", [])
            refusal = bool(payload.get("refusal", False))
            return {"answer": answer, "citations": citations, "refusal": refusal, "route": route}
        except Exception:
            # Smalltalk/clarify returns plain text
            return {"answer": content, "citations": [], "refusal": False, "route": route}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")
