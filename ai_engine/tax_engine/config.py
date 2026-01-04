from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    # Paths (ABSOLUTE)
    docs_dir: Path = Path(os.getenv("TAX_DOCS_DIR", str(PROJECT_ROOT / "docs")))
    chroma_dir: Path = Path(os.getenv("CHROMA_DIR", str(PROJECT_ROOT / "chroma_db")))

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "8"))

    # Chunking (legal docs)
    chunk_chars: int = int(os.getenv("CHUNK_CHARS", "1200"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "150"))


settings = Settings()
