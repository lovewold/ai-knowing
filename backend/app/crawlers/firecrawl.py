"""Firecrawl scrape crawler for dynamic hot-list pages (Weibo, Baidu, Zhihu, etc.)."""

import re
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

_LINK_RE = re.compile(r"\[([^\]]{4,200})\]\((https?://[^)]+)\)")
_TITLE_RE = re.compile(r"^#+\s*(.+)$")


def _parse_markdown_items(markdown: str, limit: int = 30) -> list[tuple[str, str]]:
    seen: set[str] = set()
    items: list[tuple[str, str]] = []

    for title, url in _LINK_RE.findall(markdown):
        title = title.strip()
        url = url.strip()
        if url in seen or len(title) < 4:
            continue
        seen.add(url)
        items.append((title, url))
        if len(items) >= limit:
            return items

    for line in markdown.splitlines():
        line = line.strip()
        if not line or line.startswith("!"):
            continue
        m = _TITLE_RE.match(line)
        if m:
            title = m.group(1).strip()
            if len(title) >= 4 and title not in seen:
                seen.add(title)
                items.append((title, ""))
                if len(items) >= limit:
                    break
    return items


async def crawl_firecrawl(source: SourceConfig) -> list[CrawledItem]:
    if not source.url:
        return []
    api_key = settings.firecrawl_api_key
    if not api_key:
        print(f"[crawl] {source.id}: FIRECRAWL_API_KEY not set, skip")
        return []

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.firecrawl.dev/v1/scrape",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"url": source.url, "formats": ["markdown", "links"]},
        )
        resp.raise_for_status()
        payload = resp.json()

    data = payload.get("data") or {}
    markdown = data.get("markdown") or ""
    links = data.get("links") or []

    parsed: list[tuple[str, str]] = []
    if links:
        for link in links[:40]:
            if isinstance(link, str):
                parsed.append((link, link))
            elif isinstance(link, dict):
                title = (link.get("title") or link.get("text") or link.get("url") or "").strip()
                url = (link.get("url") or "").strip()
                if title and url:
                    parsed.append((title, url))

    if not parsed:
        parsed = _parse_markdown_items(markdown)

    items: list[CrawledItem] = []
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for i, (title, url) in enumerate(parsed[:30]):
        if not url:
            continue
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title[:500],
                url=url,
                summary=None,
                language=source.language,
                published_at=now,
                external_id=url,
            )
        )
    return items
