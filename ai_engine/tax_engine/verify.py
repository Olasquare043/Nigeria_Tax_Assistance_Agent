from __future__ import annotations

import re
from typing import Dict, Any, List
from langchain_core.documents import Document


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def citations_are_valid(payload: Dict[str, Any], retrieved: List[Document]) -> bool:
    cited = payload.get("citations", []) or []
    refusal = bool(payload.get("refusal", False))

    # No citations is only OK if refusal=true
    if not cited:
        return refusal

    id_to_text = {}
    for d in retrieved:
        cid = d.metadata.get("chunk_id")
        if cid:
            id_to_text[cid] = d.page_content

    for c in cited:
        cid = c.get("chunk_id")
        quote = _norm(c.get("quote", ""))

        if not cid or cid not in id_to_text:
            return False

        chunk_text = _norm(id_to_text[cid])
        if not quote or quote not in chunk_text:
            return False

    return True
