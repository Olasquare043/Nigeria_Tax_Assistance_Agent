from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import pdfplumber


@dataclass
class Page:
    file_name: str
    page_num: int  # 1-indexed
    text: str


def extract_pages(pdf_path: Path) -> List[Page]:
    pages: List[Page] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        for idx, page in enumerate(pdf.pages):
            txt = (page.extract_text() or "").replace("\u00a0", " ").strip()
            pages.append(Page(file_name=pdf_path.name, page_num=idx + 1, text=txt))
    return pages
