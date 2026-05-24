"""AI-generated knowledge base documentation."""

from __future__ import annotations

import asyncio
from datetime import datetime

from sqlalchemy.orm import Session

from app.knowledge.rag import reindex_entry
from app.llm.resolver import get_llm_provider
from app.models import KnowledgeEntry

DOC_SYSTEM = """你是 AI全知 知识库文档撰写专家。为给定的 AI 产品、模型或 Skill 撰写结构化中文教程文档。

要求：
- 直接输出 Markdown 正文（以 # 标题开头），不要输出前言或「以下是文档」等套话
- 章节建议：概述、核心能力、适用场景、快速上手/调用方式、配置与定价（如适用）、最佳实践、注意事项
- 内容专业、实用、中文；不确定的信息标注「待核实」
- 若有官方链接，在文末「参考链接」一节列出
- 适当使用列表、表格与代码块示例"""


def has_substantial_doc(content_md: str | None) -> bool:
    return bool(content_md and len(content_md.strip()) > 80)


async def generate_entry_doc(
    db: Session,
    entry: KnowledgeEntry,
    *,
    force: bool = False,
) -> bool:
    if not force and has_substantial_doc(entry.content_md):
        return False

    llm = get_llm_provider(task="report", db=db)
    user = f"""请为以下知识库条目撰写完整教程文档：

- 名称：{entry.name}
- 类型：{entry.kind}
- 摘要：{entry.summary or '（无）'}
- 标签：{entry.tags or '（无）'}
- 官方链接：{entry.external_url or '（无）'}
- 标识：{entry.slug}"""

    md = (await llm.generate(DOC_SYSTEM, user)).strip()
    if len(md) < 80:
        return False

    entry.content_md = md
    entry.source_type = "ai"
    entry.last_verified_at = datetime.utcnow()
    await reindex_entry(db, entry)
    return True


async def generate_docs_batch(
    db: Session,
    *,
    limit: int = 50,
    force: bool = False,
    delay_sec: float = 0.5,
) -> dict:
    q = db.query(KnowledgeEntry).filter(KnowledgeEntry.enabled == True)  # noqa: E712
    if not force:
        q = q.filter(
            (KnowledgeEntry.content_md.is_(None))
            | (KnowledgeEntry.content_md == "")
            | (KnowledgeEntry.source_type == "crawl")
        )
    rows = q.order_by(KnowledgeEntry.updated_at.asc()).limit(limit).all()
    updated = 0
    failed = 0
    for entry in rows:
        try:
            if await generate_entry_doc(db, entry, force=force):
                updated += 1
            else:
                failed += 1
        except Exception as e:
            failed += 1
            print(f"[ai_doc] {entry.slug}: {e}")
        if delay_sec > 0:
            await asyncio.sleep(delay_sec)
    return {"processed": len(rows), "updated": updated, "failed": failed}
