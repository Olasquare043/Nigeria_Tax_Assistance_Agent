from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Load .env (project root)
load_dotenv()

# Project root: .../nigeria-tax-assistant-dev
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def _resolve_path(p: str) -> str:
    """Resolve relative paths against project root (works from any folder)."""
    if not p:
        return p
    pp = Path(p)
    if pp.is_absolute():
        return str(pp)
    return str((PROJECT_ROOT / pp).resolve())


@dataclass(frozen=True)
class Settings:
    # Models / Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    openai_embed_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    # Paths
    docs_dir: str = _resolve_path(os.getenv("DOCS_DIR", "./docs"))
    chroma_dir: str = _resolve_path(os.getenv("CHROMA_DIR", "./data/chroma"))
    chroma_collection: str = os.getenv("CHROMA_COLLECTION", "nigeria_tax_bills_dev")

    # Chunking
    chunk_chars: int = int(os.getenv("CHUNK_CHARS", "3500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "300"))

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "8"))


settings = Settings()
