from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.knowledge.ai_doc import generate_docs_batch, generate_entry_doc
from app.knowledge.rag import ask_entry, entry_to_dict, generate_entry_report, reindex_entry
from app.knowledge.seed import seed_knowledge, sync_agent_tools_to_knowledge
from app.models import KnowledgeEntry

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])

KINDS = {"model", "product", "skill"}


class AskRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)


class ReportRequest(BaseModel):
    prompt: str | None = Field(default=None, max_length=4000)


class KnowledgeEntryWrite(BaseModel):
    slug: str = Field(..., min_length=2, max_length=120)
    kind: str = Field(..., min_length=2, max_length=20)
    name: str = Field(..., min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=4000)
    content_md: str | None = Field(default=None, max_length=200_000)
    external_url: str | None = Field(default=None, max_length=1000)
    tags: str | None = Field(default=None, max_length=500)
    enabled: bool = True

    @field_validator("kind")
    @classmethod
    def validate_kind(cls, v: str) -> str:
        if v not in KINDS:
            raise ValueError(f"kind 必须是 {', '.join(sorted(KINDS))}")
        return v

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        slug = v.strip().lower()
        if not re.match(r"^[a-z0-9][a-z0-9_-]*$", slug):
            raise ValueError("slug 仅允许小写字母、数字、连字符与下划线")
        return slug


def _get_entry_or_404(entry_id: int, db: Session, *, admin: bool = False) -> KnowledgeEntry:
    q = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == entry_id)
    if not admin:
        q = q.filter(KnowledgeEntry.enabled == True)  # noqa: E712
    entry = q.first()
    if not entry:
        raise HTTPException(404, "条目不存在")
    return entry


def _apply_write(entry: KnowledgeEntry, body: KnowledgeEntryWrite) -> None:
    entry.slug = body.slug
    entry.kind = body.kind
    entry.name = body.name.strip()
    entry.summary = body.summary.strip() if body.summary else None
    entry.content_md = body.content_md.strip() if body.content_md else None
    entry.external_url = body.external_url.strip() if body.external_url else None
    entry.tags = body.tags.strip() if body.tags else None
    entry.enabled = body.enabled
    entry.source_type = "manual"
    entry.last_verified_at = datetime.utcnow()


@router.get("")
def list_knowledge(
    kind: str | None = None,
    category: str | None = None,
    q: str | None = None,
    admin: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    query = db.query(KnowledgeEntry)
    if not admin:
        query = query.filter(KnowledgeEntry.enabled == True)  # noqa: E712
    if kind:
        query = query.filter(KnowledgeEntry.kind == kind)
    if category:
        query = query.filter(KnowledgeEntry.tags.ilike(f"%{category}%"))
    if q:
        like = f"%{q}%"
        query = query.filter(
            KnowledgeEntry.name.ilike(like)
            | KnowledgeEntry.summary.ilike(like)
            | KnowledgeEntry.tags.ilike(like)
            | KnowledgeEntry.slug.ilike(like)
        )
    limit = 500 if admin else 200
    rows = query.order_by(KnowledgeEntry.kind, KnowledgeEntry.name).limit(limit).all()
    return [entry_to_dict(r, include_content=admin) for r in rows]


@router.get("/catalog")
def product_catalog():
    from app.knowledge.seed import list_product_catalog

    groups = list_product_catalog()
    return {"groups": groups, "total": sum(g["count"] for g in groups)}


@router.post("")
async def create_knowledge(body: KnowledgeEntryWrite, db: Session = Depends(get_db)):
    exists = db.query(KnowledgeEntry).filter(KnowledgeEntry.slug == body.slug).first()
    if exists:
        raise HTTPException(409, f"slug 已存在: {body.slug}")
    entry = KnowledgeEntry(
        slug=body.slug,
        kind=body.kind,
        name=body.name.strip(),
        summary=body.summary,
        content_md=body.content_md,
        external_url=body.external_url,
        tags=body.tags,
        enabled=body.enabled,
        source_type="manual",
        last_verified_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    if entry.content_md:
        await reindex_entry(db, entry)
    return entry_to_dict(entry, include_content=True)


@router.post("/seed")
async def run_seed(db: Session = Depends(get_db)):
    n = await seed_knowledge(db)
    return {"created": n}


@router.post("/sync/agent-tools")
async def sync_tools(db: Session = Depends(get_db)):
    n = await sync_agent_tools_to_knowledge(db)
    return {"synced": n}


@router.post("/generate-docs")
async def generate_all_docs(
    limit: int = Query(default=50, ge=1, le=100),
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return await generate_docs_batch(db, limit=limit, force=force)


@router.get("/{entry_id}")
def get_knowledge(
    entry_id: int,
    admin: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    entry = _get_entry_or_404(entry_id, db, admin=admin)
    return entry_to_dict(entry, include_content=True)


@router.put("/{entry_id}")
async def update_knowledge(
    entry_id: int,
    body: KnowledgeEntryWrite,
    db: Session = Depends(get_db),
):
    entry = _get_entry_or_404(entry_id, db, admin=True)
    conflict = (
        db.query(KnowledgeEntry)
        .filter(KnowledgeEntry.slug == body.slug, KnowledgeEntry.id != entry_id)
        .first()
    )
    if conflict:
        raise HTTPException(409, f"slug 已被其他条目使用: {body.slug}")
    _apply_write(entry, body)
    db.commit()
    db.refresh(entry)
    await reindex_entry(db, entry)
    return entry_to_dict(entry, include_content=True)


@router.delete("/{entry_id}")
def delete_knowledge(
    entry_id: int,
    hard: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    entry = _get_entry_or_404(entry_id, db, admin=True)
    if hard:
        db.delete(entry)
        db.commit()
        return {"deleted": True, "hard": True}
    entry.enabled = False
    db.commit()
    return {"deleted": True, "hard": False}


@router.post("/{entry_id}/generate-doc")
async def generate_one_doc(
    entry_id: int,
    force: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    entry = _get_entry_or_404(entry_id, db, admin=True)
    try:
        ok = await generate_entry_doc(db, entry, force=force)
        return {"updated": ok, "entry": entry_to_dict(entry, include_content=True)}
    except Exception as e:
        raise HTTPException(502, f"AI 文档生成失败: {e}") from e


@router.post("/{entry_id}/ask")
async def knowledge_ask(entry_id: int, body: AskRequest, db: Session = Depends(get_db)):
    entry = _get_entry_or_404(entry_id, db, admin=False)
    return await ask_entry(db, entry, body.question)


@router.post("/{entry_id}/report")
async def knowledge_report(entry_id: int, body: ReportRequest, db: Session = Depends(get_db)):
    entry = _get_entry_or_404(entry_id, db, admin=True)
    report = await generate_entry_report(db, entry, body.prompt)
    from app.reports.citations import citations_from_json, queries_from_json

    citations = citations_from_json(report.citations_json)
    return {
        "id": report.id,
        "title": report.title,
        "type": report.report_type.value,
        "content_md": report.content_md,
        "quality_label": report.quality_label,
        "created_at": report.created_at.isoformat(),
        "citations": [c.to_dict() for c in citations],
        "search_queries": queries_from_json(report.search_queries_json),
    }


@router.post("/{entry_id}/reindex")
async def reindex(entry_id: int, db: Session = Depends(get_db)):
    entry = _get_entry_or_404(entry_id, db, admin=True)
    count = await reindex_entry(db, entry)
    return {"chunks": count}
