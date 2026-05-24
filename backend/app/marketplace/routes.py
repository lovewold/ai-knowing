"""Model marketplace API."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.marketplace.agicto import (
    apply_fetched_detail,
    entry_doc_dict,
    entry_to_dict,
    fetch_agicto_detail,
    fetch_agicto_list,
    has_doc_content,
)
from app.models import ModelCatalogEntry

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


def _get_model_row(slug: str, db: Session) -> ModelCatalogEntry:
    row = (
        db.query(ModelCatalogEntry)
        .filter(ModelCatalogEntry.slug == slug, ModelCatalogEntry.enabled == True)  # noqa: E712
        .first()
    )
    if not row:
        raise HTTPException(404, "模型不存在")
    return row


@router.get("/meta")
def marketplace_meta(db: Session = Depends(get_db)):
    base = db.query(ModelCatalogEntry).filter(ModelCatalogEntry.enabled == True)  # noqa: E712
    total = base.count()
    with_docs = base.filter(func.length(ModelCatalogEntry.content_md) > 80).count()
    provider_rows = (
        db.query(ModelCatalogEntry.provider, func.count(ModelCatalogEntry.id))
        .filter(ModelCatalogEntry.enabled == True)  # noqa: E712
        .group_by(ModelCatalogEntry.provider)
        .all()
    )
    scene_rows = (
        db.query(ModelCatalogEntry.scene, func.count(ModelCatalogEntry.id))
        .filter(ModelCatalogEntry.enabled == True)  # noqa: E712
        .group_by(ModelCatalogEntry.scene)
        .all()
    )
    providers: dict[str, int] = {}
    for provider, count in provider_rows:
        key = provider or "其他"
        providers[key] = providers.get(key, 0) + count
    scenes: dict[str, int] = {}
    for scene, count in scene_rows:
        key = scene or "其他"
        scenes[key] = scenes.get(key, 0) + count
    return {
        "total": total,
        "with_docs": with_docs,
        "providers": sorted(providers.items(), key=lambda x: (-x[1], x[0])),
        "scenes": sorted(scenes.items(), key=lambda x: (-x[1], x[0])),
        "source": "https://agicto.com/model",
    }


@router.get("/models")
def list_models(
    provider: str | None = None,
    scene: str | None = None,
    q: str | None = None,
    free: bool | None = None,
    limit: int = Query(default=60, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(ModelCatalogEntry).filter(ModelCatalogEntry.enabled == True)  # noqa: E712
    if provider:
        query = query.filter(
            (ModelCatalogEntry.provider == provider) | (ModelCatalogEntry.company_name == provider)
        )
    if scene:
        query = query.filter(ModelCatalogEntry.scene == scene)
    if free is True:
        query = query.filter(ModelCatalogEntry.is_free == True)  # noqa: E712
    elif free is False:
        query = query.filter(ModelCatalogEntry.is_free == False)  # noqa: E712
    if q:
        like = f"%{q}%"
        query = query.filter(
            ModelCatalogEntry.name.ilike(like)
            | ModelCatalogEntry.slug.ilike(like)
            | ModelCatalogEntry.provider.ilike(like)
        )
    total = query.count()
    rows = query.order_by(ModelCatalogEntry.input_price.asc().nullslast(), ModelCatalogEntry.name).offset(offset).limit(limit).all()
    return {"items": [entry_to_dict(r) for r in rows], "total": total, "offset": offset, "limit": limit}


@router.get("/models/{slug}")
def get_model(slug: str, db: Session = Depends(get_db)):
    row = _get_model_row(slug, db)
    return entry_to_dict(row)


@router.get("/models/{slug}/doc")
async def get_model_doc(slug: str, response: Response, db: Session = Depends(get_db)):
    row = _get_model_row(slug, db)
    if has_doc_content(row.content_md):
        response.headers["Cache-Control"] = "public, max-age=3600"
        return entry_doc_dict(row)
    try:
        meta, md = await fetch_agicto_detail(slug)
        if apply_fetched_detail(row, meta, md):
            db.commit()
            response.headers["Cache-Control"] = "public, max-age=3600"
    except Exception as e:
        print(f"[marketplace] doc fetch {slug}: {e}")
    return entry_doc_dict(row)


@router.post("/sync")
async def sync_marketplace(
    fetch_docs: bool = Query(default=False),
    doc_limit: int = Query(default=30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    remote = await fetch_agicto_list()
    upserted = 0
    now = datetime.utcnow()
    for item in remote:
        row = db.query(ModelCatalogEntry).filter(ModelCatalogEntry.slug == item["slug"]).first()
        if row:
            row.name = item["name"]
            row.provider = item["provider"]
            row.company_name = item["company_name"]
            row.scene = item["scene"]
            row.type_id = item["type_id"]
            row.context_len = item["context_len"]
            row.input_price = item["input_price"]
            row.output_price = item["output_price"]
            row.is_free = item["is_free"]
            row.agicto_model_id = item["agicto_model_id"]
            row.summary = item["summary"] or row.summary
            row.source_url = item["source_url"]
            row.synced_at = now
        else:
            db.add(ModelCatalogEntry(**item, synced_at=now))
            upserted += 1
    db.commit()

    docs_fetched = 0
    if fetch_docs:
        pending = (
            db.query(ModelCatalogEntry)
            .filter(ModelCatalogEntry.enabled == True)  # noqa: E712
            .filter(
                (ModelCatalogEntry.content_md.is_(None))
                | (ModelCatalogEntry.content_md == "")
            )
            .order_by(ModelCatalogEntry.synced_at.desc())
            .limit(doc_limit)
            .all()
        )
        import asyncio

        for row in pending:
            try:
                meta, md = await fetch_agicto_detail(row.slug)
                if apply_fetched_detail(row, meta, md):
                    docs_fetched += 1
            except Exception as e:
                print(f"[marketplace] detail failed {row.slug}: {e}")
            await asyncio.sleep(0.35)
        db.commit()

    total = db.query(ModelCatalogEntry).count()
    return {
        "list_count": len(remote),
        "created": upserted,
        "total": total,
        "docs_fetched": docs_fetched,
        "source": "https://agicto.com/model",
    }
