"""Seed and sync knowledge entries."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.knowledge.rag import reindex_entry
from app.models import AgentTool, KnowledgeEntry
from app.yaml_config import get_config_dir


def _slugify(name: str) -> str:
    s = name.lower().strip().replace(" ", "-")
    return "".join(c if c.isalnum() or c in "-_" else "-" for c in s)[:100]


def _load_yaml_entries(filename: str) -> list[dict]:
    path = get_config_dir() / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return list(data.get("entries") or [])


def _tags_from_raw(raw: dict) -> str | None:
    parts: list[str] = []
    if raw.get("category"):
        parts.append(str(raw["category"]))
    if raw.get("tags"):
        parts.extend(t.strip() for t in str(raw["tags"]).split(",") if t.strip())
    return ",".join(dict.fromkeys(parts)) if parts else None


async def _upsert_entry(db: Session, raw: dict, *, update_existing: bool = False) -> bool:
    slug = raw.get("slug") or _slugify(raw["name"])
    existing = db.query(KnowledgeEntry).filter(KnowledgeEntry.slug == slug).first()
    tags = _tags_from_raw(raw)
    if existing:
        if update_existing:
            existing.name = raw.get("name", existing.name)
            existing.summary = raw.get("summary") or existing.summary
            existing.external_url = raw.get("external_url") or existing.external_url
            if tags:
                existing.tags = tags
            if raw.get("content_md") and not existing.content_md:
                existing.content_md = raw["content_md"]
            # reindex if we filled content
            if raw.get("content_md") and existing.content_md == raw["content_md"]:
                await reindex_entry(db, existing)
        return False
    entry = KnowledgeEntry(
        slug=slug,
        kind=raw.get("kind", "model"),
        name=raw["name"],
        summary=raw.get("summary"),
        content_md=raw.get("content_md"),
        external_url=raw.get("external_url"),
        tags=tags,
        source_type=raw.get("source_type", "manual"),
        last_verified_at=datetime.utcnow(),
        enabled=raw.get("enabled", True),
    )
    db.add(entry)
    db.flush()
    await reindex_entry(db, entry)
    return True


async def seed_knowledge(db: Session) -> int:
    items = _load_yaml_entries("knowledge_seed.yaml") + _load_yaml_entries("product_catalog.yaml")
    created = 0
    for raw in items:
        if await _upsert_entry(db, raw, update_existing=True):
            created += 1
    db.commit()
    return created


async def seed_product_catalog(db: Session) -> int:
    """Import product catalog; update tags/summary for existing slugs."""
    items = _load_yaml_entries("product_catalog.yaml")
    created = 0
    for raw in items:
        if await _upsert_entry(db, raw, update_existing=True):
            created += 1
    db.commit()
    return created


def list_product_catalog() -> list[dict]:
    """Return product inventory grouped by category (for docs / admin)."""
    items = _load_yaml_entries("product_catalog.yaml")
    by_cat: dict[str, list[dict]] = {}
    for raw in items:
        cat = raw.get("category") or raw.get("kind") or "其他"
        by_cat.setdefault(cat, []).append(
            {
                "slug": raw.get("slug"),
                "name": raw.get("name"),
                "kind": raw.get("kind"),
                "summary": raw.get("summary"),
                "external_url": raw.get("external_url"),
            }
        )
    return [{"category": k, "count": len(v), "items": v} for k, v in sorted(by_cat.items())]


async def sync_agent_tools_to_knowledge(db: Session) -> int:
    tools = db.query(AgentTool).all()
    synced = 0
    for tool in tools:
        slug = f"skill-{_slugify(tool.name)}"
        entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.agent_tool_id == tool.id).first()
        if not entry:
            entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.slug == slug).first()
        if not entry:
            entry = KnowledgeEntry(
                slug=slug,
                kind="skill",
                name=tool.name,
                summary=tool.description or tool.description_zh,
                content_md=f"## {tool.name}\n\n{tool.description or ''}\n\n类型: {tool.tool_type or 'tool'}\n",
                external_url=tool.url,
                tags=tool.tool_type,
                source_type="crawl",
                agent_tool_id=tool.id,
                last_verified_at=tool.updated_at or datetime.utcnow(),
            )
            db.add(entry)
            db.flush()
            await reindex_entry(db, entry)
            synced += 1
        else:
            entry.agent_tool_id = tool.id
            entry.last_verified_at = tool.updated_at or entry.last_verified_at
    db.commit()
    return synced


async def ensure_knowledge_indexed(db: Session) -> int:
    """Reindex entries whose chunks lack vectors (e.g. after switching to local embed)."""
    from app.models import KnowledgeChunk

    entry_ids = {
        row[0]
        for row in db.query(KnowledgeChunk.entry_id)
        .filter(KnowledgeChunk.embedding_json.is_(None))
        .distinct()
        .all()
    }
    if not entry_ids:
        return 0
    n = 0
    for eid in entry_ids:
        entry = db.query(KnowledgeEntry).filter(KnowledgeEntry.id == eid).first()
        if entry:
            await reindex_entry(db, entry)
            n += 1
    return n
