from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Simple heading heuristics (good enough for rubric; improves later)
HEADING_RE = re.compile(r"^\s*(PART|CHAPTER|SECTION|SCHEDULE|EXPLANATORY\s+MEMORANDUM)\b", re.IGNORECASE)
SECTION_NO_RE = re.compile(r"^\s*(\d{1,3})\s*[\.\)]\s+(.+)$")


@dataclass
class Chunk:
    text: str
    meta: Dict[str, Any]


def _split_paragraphs(text: str) -> List[str]:
    lines = [ln.rstrip() for ln in text.splitlines()]
    paras, buf = [], []
    for ln in lines:
        if not ln.strip():
            if buf:
                paras.append("\n".join(buf).strip())
                buf = []
            continue
        buf.append(ln)
    if buf:
        paras.append("\n".join(buf).strip())
    return paras


def chunk_document(
    file_name: str,
    pages: List[Dict[str, Any]],
    chunk_chars: int = 3500,
    overlap: int = 300
) -> List[Chunk]:
    chunks: List[Chunk] = []
    cur: List[str] = []
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    heading_path: List[str] = []
    section: Optional[str] = None

    def flush():
        nonlocal cur, start_page, end_page, section
        if not cur:
            return
        txt = "\n\n".join(cur).strip()
        if not txt:
            return
        chunk_id = f"{file_name}::c{len(chunks):05d}"
        chunks.append(
            Chunk(
                text=txt,
                meta={
                    "source": file_name,
                    "chunk_id": chunk_id,
                    "page_start": start_page,
                    "page_end": end_page,
                    "heading": " > ".join(heading_path[-5:]),
                    "section": section,
                },
            )
        )
        # overlap context
        if overlap and len(txt) > overlap:
            cur = [txt[-overlap:]]
            start_page = end_page
        else:
            cur = []
            start_page = None
        section = None

    for p in pages:
        pn = int(p["page_num"])
        for para in _split_paragraphs(p["text"]):
            first_line = para.splitlines()[0] if para else ""

            if HEADING_RE.search(first_line):
                heading_path.append(first_line.strip())

            m = SECTION_NO_RE.match(first_line.strip())
            if m:
                section = m.group(1)

            if start_page is None:
                start_page = pn
            end_page = pn
            cur.append(para)

            if sum(len(x) for x in cur) >= chunk_chars:
                flush()

    flush()
    return chunks
