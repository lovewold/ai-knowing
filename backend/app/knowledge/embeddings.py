"""Text chunking and embedding for knowledge RAG (local model by default, no API key)."""

from __future__ import annotations

import asyncio
import json
import math
import re
from typing import Iterable

import httpx

from app.config import settings

CHUNK_SIZE = 800
CHUNK_OVERLAP = 120

_local_model = None
_local_model_failed = False


def split_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    text = (text or "").strip()
    if not text:
        return []
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks: list[str] = []
    buf = ""
    for para in paragraphs:
        if len(buf) + len(para) + 2 <= size:
            buf = f"{buf}\n\n{para}".strip() if buf else para
        else:
            if buf:
                chunks.append(buf)
            if len(para) <= size:
                buf = para
            else:
                for i in range(0, len(para), size - overlap):
                    chunks.append(para[i : i + size])
                buf = ""
    if buf:
        chunks.append(buf)
    return chunks


def _get_local_embedder():
    """Lazy-load fastembed model (downloads ~100MB on first run, then fully offline)."""
    global _local_model, _local_model_failed
    if _local_model_failed:
        return None
    if _local_model is not None:
        return _local_model
    try:
        from fastembed import TextEmbedding

        _local_model = TextEmbedding(model_name=settings.local_embedding_model)
        print(f"[embed] local model ready: {settings.local_embedding_model}")
        return _local_model
    except Exception as e:
        _local_model_failed = True
        print(f"[embed] local model unavailable: {e}")
        return None


def embed_texts_local(texts: list[str]) -> list[list[float] | None]:
    if not texts:
        return []
    model = _get_local_embedder()
    if model is None:
        return [None] * len(texts)
    out: list[list[float] | None] = []
    for vec in model.embed(texts):
        out.append(vec.tolist() if hasattr(vec, "tolist") else list(vec))
    return out


async def _embed_openai(texts: list[str]) -> list[list[float]]:
    key = settings.embedding_api_key or settings.openai_api_key
    if not key:
        raise ValueError("no embedding API key")
    base = settings.embedding_base_url.rstrip("/")
    url = f"{base}/v1/embeddings"
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            url,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": settings.embedding_model, "input": texts},
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        ordered = sorted(data, key=lambda x: x["index"])
        return [item["embedding"] for item in ordered]


async def embed_texts(texts: list[str]) -> list[list[float] | None]:
    if not texts:
        return []

    mode = (settings.embedding_provider or "local").lower()

    if mode == "openai":
        try:
            return await _embed_openai(texts)
        except Exception as e:
            print(f"[embed] openai failed, fallback local: {e}")

    if mode == "auto":
        key = settings.embedding_api_key or settings.openai_api_key
        if key:
            try:
                return await _embed_openai(texts)
            except Exception as e:
                print(f"[embed] openai failed, fallback local: {e}")

    return await asyncio.to_thread(embed_texts_local, texts)


def cosine_similarity(a: Iterable[float], b: Iterable[float]) -> float:
    av = list(a)
    bv = list(b)
    if len(av) != len(bv) or not av:
        return 0.0
    dot = sum(x * y for x, y in zip(av, bv))
    na = math.sqrt(sum(x * x for x in av))
    nb = math.sqrt(sum(x * x for x in bv))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def keyword_score(query: str, text: str) -> float:
    q = {w for w in re.findall(r"[\w\u4e00-\u9fff]{2,}", query.lower())}
    if not q:
        return 0.0
    t = text.lower()
    hits = sum(1 for w in q if w in t)
    return hits / len(q)


def parse_embedding(raw: str | None) -> list[float] | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def dump_embedding(vec: list[float] | None) -> str | None:
    if not vec:
        return None
    return json.dumps(vec)
