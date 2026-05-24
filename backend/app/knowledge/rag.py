"""Knowledge base indexing and RAG retrieval."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.knowledge.embeddings import (
    cosine_similarity,
    dump_embedding,
    embed_texts,
    keyword_score,
    parse_embedding,
    split_text,
)
from app.llm.resolver import get_llm_provider
from app.models import KnowledgeChunk, KnowledgeEntry

ASK_SYSTEM = """你是 AI全知 知识库助手。仅根据提供的知识库片段回答问题。
若资料不足，明确说明并给出可查阅的外链建议。回答简洁、专业、中文。"""


def entry_to_dict(entry: KnowledgeEntry, *, include_content: bool = False) -> dict:
    stale = False
    if entry.last_verified_at:
        days = (datetime.utcnow() - entry.last_verified_at).days
        stale = days > 30
    data = {
        "id": entry.id,
        "slug": entry.slug,
        "kind": entry.kind,
        "name": entry.name,
        "summary": entry.summary,
        "external_url": entry.external_url,
        "tags": entry.tags,
        "source_type": entry.source_type,
        "agent_tool_id": entry.agent_tool_id,
        "last_verified_at": entry.last_verified_at.isoformat() if entry.last_verified_at else None,
        "updated_at": entry.updated_at.isoformat(),
        "stale": stale,
        "enabled": entry.enabled,
    }
    if include_content:
        data["content_md"] = entry.content_md
    return data


async def reindex_entry(db: Session, entry: KnowledgeEntry) -> int:
    db.query(KnowledgeChunk).filter(KnowledgeChunk.entry_id == entry.id).delete()
    parts: list[str] = []
    if entry.summary:
        parts.append(entry.summary)
    if entry.content_md:
        parts.append(entry.content_md)
    if entry.name:
        parts.append(f"# {entry.name}")
    if entry.tags:
        parts.append(f"标签: {entry.tags}")
    full = "\n\n".join(parts)
    texts = split_text(full)
    if not texts and entry.summary:
        texts = [entry.summary]

    vectors = await embed_texts(texts)
    for i, (text, vec) in enumerate(zip(texts, vectors)):
        db.add(
            KnowledgeChunk(
                entry_id=entry.id,
                chunk_index=i,
                content=text,
                embedding_json=dump_embedding(vec),
            )
        )
    db.commit()
    return len(texts)


async def retrieve_chunks(db: Session, entry_id: int, query: str, top_k: int = 5) -> list[str]:
    chunks = db.query(KnowledgeChunk).filter(KnowledgeChunk.entry_id == entry_id).order_by(KnowledgeChunk.chunk_index).all()
    if not chunks:
        return []

    query_vecs = await embed_texts([query])
    qvec = query_vecs[0] if query_vecs else None

    scored: list[tuple[float, str]] = []
    for ch in chunks:
        emb = parse_embedding(ch.embedding_json)
        if qvec and emb:
            score = cosine_similarity(qvec, emb)
        else:
            score = keyword_score(query, ch.content)
        scored.append((score, ch.content))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for s, t in scored[:top_k] if s > 0.05]


async def ask_entry(db: Session, entry: KnowledgeEntry, question: str) -> dict:
    contexts = await retrieve_chunks(db, entry.id, question, top_k=6)
    ctx_block = "\n\n---\n\n".join(contexts) if contexts else (entry.summary or "（暂无索引内容）")
    llm = get_llm_provider(task="custom", db=db)
    answer = await llm.generate(
        ASK_SYSTEM,
        f"知识条目：{entry.name}\n类型：{entry.kind}\n外链：{entry.external_url or '无'}\n\n"
        f"知识片段：\n{ctx_block}\n\n用户问题：{question}",
    )
    return {"answer": answer.strip(), "context_count": len(contexts)}


async def generate_entry_report(db: Session, entry: KnowledgeEntry, prompt: str | None):
    from app.models import Report, ReportType
    from app.reports.workflow import generate_research_report

    user_prompt = prompt or (
        f"基于知识库条目「{entry.name}」撰写 AI 教程型报告，涵盖能力说明、调用方式、适用场景、定价或限制、最佳实践。"
    )
    ctx = f"\n\n### 知识库条目\n\n**{entry.name}** ({entry.kind})\n\n{entry.summary or ''}\n\n{entry.content_md or ''}"
    report: Report = await generate_research_report(user_prompt + ctx, db=db, include_db_match=False)
    report.report_type = ReportType.KNOWLEDGE
    if not report.title.startswith("[知识库]"):
        report.title = f"[知识库] {entry.name} · {report.title}"[:500]
    db.commit()
    db.refresh(report)
    return report
