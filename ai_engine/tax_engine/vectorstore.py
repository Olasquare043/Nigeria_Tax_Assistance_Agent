from __future__ import annotations

import hashlib
from typing import List, Dict, Any

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma  # pip install -U langchain-chroma

from .config import settings


def _sha1_text(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()

def get_embeddings() -> OpenAIEmbeddings:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Put it in a .env file at the project root "
            "or set it in your terminal environment."
        )
    return OpenAIEmbeddings(api_key=settings.openai_api_key)

def load_chroma() -> Chroma:
    """
    Always open the SAME persistent Chroma DB regardless of current working directory.
    """
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name="nigeria_tax_bills",
        persist_directory=str(settings.chroma_dir),  # ✅ absolute path from config.py
        embedding_function=get_embeddings(),
    )


def upsert_incremental(all_docs: List[Document], batch_size: int = 200) -> Dict[str, Any]:
    """
    Incremental index update:
    - Identify existing docs by metadata['chunk_id']
    - Add NEW chunk_ids
    - Update CHANGED chunk_ids (by content_hash)
    - Skip unchanged
    - Deduplicate if duplicates exist
    """
    chroma = load_chroma()

    # Ensure content_hash exists for every doc
    for d in all_docs:
        if "content_hash" not in d.metadata:
            d.metadata["content_hash"] = _sha1_text(d.page_content)

    # Incoming: chunk_id -> doc (unique)
    incoming: Dict[str, Document] = {}
    for i, d in enumerate(all_docs):
        cid = d.metadata.get("chunk_id") or f"auto-{i:06d}"
        incoming[cid] = d

    incoming_cids = list(incoming.keys())

    # Load all existing ids + metadatas
    try:
        existing = chroma.get(include=["metadatas"])
        existing_ids = existing.get("ids", []) or []
        existing_metas = existing.get("metadatas", []) or []
    except Exception:
        existing_ids, existing_metas = [], []

    # Build: chunk_id -> [store_ids...]
    chunk_to_store_ids: Dict[str, List[str]] = {}
    for sid, meta in zip(existing_ids, existing_metas):
        if not meta:
            continue
        cid = meta.get("chunk_id")
        if cid:
            chunk_to_store_ids.setdefault(cid, []).append(sid)

    # Deduplicate (if DB somehow contains duplicates)
    deduped_removed = 0
    to_delete_dupes: List[str] = []
    for cid, sids in list(chunk_to_store_ids.items()):
        if len(sids) <= 1:
            continue
        # keep the first id (or keep cid if already used as id)
        keep = cid if cid in sids else sids[0]
        for sid in sids:
            if sid != keep:
                to_delete_dupes.append(sid)
                deduped_removed += 1
        chunk_to_store_ids[cid] = [keep]

    if to_delete_dupes:
        chroma.delete(ids=to_delete_dupes)

    existing_cids = set(chunk_to_store_ids.keys())

    to_add = [cid for cid in incoming_cids if cid not in existing_cids]
    to_check = [cid for cid in incoming_cids if cid in existing_cids]

    to_update: List[str] = []
    skipped: List[str] = []

    # Compare hashes for existing
    check_store_ids = [chunk_to_store_ids[cid][0] for cid in to_check]

    for i in range(0, len(check_store_ids), batch_size):
        batch_ids = check_store_ids[i : i + batch_size]
        got = chroma.get(ids=batch_ids, include=["metadatas"])
        got_metas = got.get("metadatas", []) or []

        for meta in got_metas:
            if not meta:
                continue
            cid = meta.get("chunk_id")
            if not cid or cid not in incoming:
                continue
            stored_hash = meta.get("content_hash")
            new_hash = incoming[cid].metadata.get("content_hash")
            if stored_hash != new_hash:
                to_update.append(cid)
            else:
                skipped.append(cid)

    # Apply updates: delete old store doc then add back using stable id = chunk_id
    if to_update:
        delete_ids = [chunk_to_store_ids[cid][0] for cid in to_update if cid in chunk_to_store_ids]
        if delete_ids:
            chroma.delete(ids=delete_ids)
        chroma.add_documents([incoming[cid] for cid in to_update], ids=to_update)

    # Apply adds
    if to_add:
        chroma.add_documents([incoming[cid] for cid in to_add], ids=to_add)

    return {
        "total_input_docs": len(all_docs),
        "existing_store_docs_before": len(existing_ids),
        "existing_unique_chunk_ids_before": len(existing_cids),
        "deduped_removed": deduped_removed,
        "added": len(to_add),
        "updated": len(to_update),
        "skipped": len(skipped),
    }
