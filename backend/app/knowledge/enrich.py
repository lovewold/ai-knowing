"""Fetch official README / docs to enrich knowledge entries."""

from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urlparse

import httpx

from app.models import KnowledgeEntry

MAX_MD_LEN = 48000
USER_AGENT = "Mozilla/5.0 (compatible; AIKnow/1.0)"


def _github_readme_urls(url: str) -> list[str]:
    m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", url.strip().rstrip("/"))
    if not m:
        return []
    owner, repo = m.group(1), m.group(2)
    return [
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/main/readme.md",
        f"https://raw.githubusercontent.com/{owner}/{repo}/HEAD/README.md",
    ]


def _gitlab_readme_urls(url: str) -> list[str]:
    m = re.match(r"https?://gitlab\.com/([^/]+/[^/]+?)(?:\.git)?/?$", url.strip().rstrip("/"))
    if not m:
        return []
    path = m.group(1)
    return [
        f"https://gitlab.com/{path}/-/raw/main/README.md",
        f"https://gitlab.com/{path}/-/raw/master/README.md",
    ]


def _doc_site_urls(url: str) -> list[str]:
    u = url.strip().rstrip("/")
    parsed = urlparse(u)
    if not parsed.netloc:
        return []
    host = parsed.netloc.lower()
    out: list[str] = []
    if host == "cursor.com":
        out.extend(["https://docs.cursor.com", "https://cursor.com/docs"])
    elif host in ("www.coze.cn", "coze.cn"):
        out.append("https://www.coze.cn/open/docs")
    elif host in ("platform.openai.com", "openai.com"):
        out.append("https://platform.openai.com/docs")
    elif host in ("docs.anthropic.com", "anthropic.com", "claude.ai"):
        out.append("https://docs.anthropic.com")
    elif "deepseek" in host:
        out.append("https://platform.deepseek.com/api-docs")
    elif host.endswith("langchain.com") or "langchain" in host:
        out.append("https://python.langchain.com/docs/introduction/")
    elif host == "ollama.com":
        out.append("https://github.com/ollama/ollama/blob/main/README.md")
    if u not in out:
        out.append(u)
    return out


def _candidate_urls(entry: KnowledgeEntry, readme_url: str | None = None, docs_url: str | None = None) -> list[str]:
    urls: list[str] = []
    if readme_url:
        urls.append(readme_url)
    if docs_url:
        urls.append(docs_url)
    ext = (entry.external_url or "").strip()
    if ext:
        urls.extend(_github_readme_urls(ext))
        urls.extend(_gitlab_readme_urls(ext))
        urls.extend(_doc_site_urls(ext))
    return list(dict.fromkeys(urls))


def _fallback_content(entry: KnowledgeEntry) -> str:
    lines = [
        f"# {entry.name}",
        "",
        entry.summary or "",
        "",
    ]
    if entry.tags:
        lines.extend([f"**分类/标签**: {entry.tags}", ""])
    if entry.external_url:
        lines.extend([f"**官方链接**: {entry.external_url}", ""])
    lines.extend(
        [
            "",
            "## 说明",
            "",
            "暂未抓取到完整官方文档，可通过右侧 AI 问答或生成报告获取更多信息。",
            "管理员可在后台执行「补齐官网 README」自动拉取文档。",
        ]
    )
    return "\n".join(lines).strip()


async def fetch_text(url: str) -> str | None:
    async with httpx.AsyncClient(timeout=45, follow_redirects=True, headers={"User-Agent": USER_AGENT}) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        ctype = resp.headers.get("content-type", "")
        text = resp.text
        if "html" in ctype and len(text) > 500:
            text = re.sub(r"(?is)<script.*?>.*?</script>", "", text)
            text = re.sub(r"(?is)<style.*?>.*?</style>", "", text)
            text = re.sub(r"(?is)<nav.*?>.*?</nav>", "", text)
            text = re.sub(r"(?is)<footer.*?>.*?</footer>", "", text)
            text = re.sub(r"<[^>]+>", "\n", text)
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(text.strip()) < 120:
            return None
        return text[:MAX_MD_LEN]


async def enrich_entry_content(
    entry: KnowledgeEntry,
    readme_url: str | None = None,
    docs_url: str | None = None,
    *,
    allow_fallback: bool = True,
) -> tuple[bool, str]:
    """Return (updated, source_url)."""
    for url in _candidate_urls(entry, readme_url, docs_url):
        try:
            content = await fetch_text(url)
            if content and len(content) > 120:
                header = f"## 官方文档摘录\n\n来源: {url}\n\n---\n\n"
                entry.content_md = header + content
                entry.source_type = "crawl"
                entry.last_verified_at = datetime.utcnow()
                return True, url
        except Exception as e:
            print(f"[enrich] {entry.slug} {url}: {e}")
    if allow_fallback and not (entry.content_md and len(entry.content_md) > 80):
        entry.content_md = _fallback_content(entry)
        entry.source_type = "manual"
        entry.last_verified_at = datetime.utcnow()
        return True, "fallback"
    return False, ""


def _readme_maps() -> tuple[dict[str, str], dict[str, str]]:
    from app.knowledge.seed import _load_yaml_entries

    readme_map: dict[str, str] = {}
    docs_map: dict[str, str] = {}
    for raw in _load_yaml_entries("product_catalog.yaml") + _load_yaml_entries("knowledge_seed.yaml"):
        slug = raw.get("slug")
        if not slug:
            continue
        if raw.get("readme_url"):
            readme_map[slug] = raw["readme_url"]
        if raw.get("docs_url"):
            docs_map[slug] = raw["docs_url"]
    return readme_map, docs_map


async def enrich_knowledge_batch(db, *, limit: int = 50, force: bool = False) -> dict:
    readme_map, docs_map = _readme_maps()
    q = db.query(KnowledgeEntry).filter(KnowledgeEntry.enabled == True)  # noqa: E712
    if not force:
        q = q.filter((KnowledgeEntry.content_md.is_(None)) | (KnowledgeEntry.content_md == ""))
    rows = q.order_by(KnowledgeEntry.updated_at.asc()).limit(limit).all()
    updated = 0
    failed = 0
    for entry in rows:
        ok, _ = await enrich_entry_content(
            entry,
            readme_url=readme_map.get(entry.slug),
            docs_url=docs_map.get(entry.slug),
        )
        if ok:
            updated += 1
            from app.knowledge.rag import reindex_entry

            await reindex_entry(db, entry)
        else:
            failed += 1
    db.commit()
    return {"processed": len(rows), "updated": updated, "failed": failed}


async def enrich_all_empty(db, *, batch_size: int = 30, max_rounds: int = 10) -> dict:
    total_updated = 0
    rounds = 0
    while rounds < max_rounds:
        result = await enrich_knowledge_batch(db, limit=batch_size, force=False)
        rounds += 1
        total_updated += result["updated"]
        if result["processed"] == 0 or result["updated"] == 0:
            break
    return {"rounds": rounds, "updated": total_updated}
