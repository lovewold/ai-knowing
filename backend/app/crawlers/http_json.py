"""Direct HTTP JSON crawlers: Bilibili, V2EX, Reddit."""

from datetime import datetime, timezone

import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

UA = {"User-Agent": "AI-Know-Bot/1.0 (+https://github.com/ai-know)"}


def _parse_bilibili(data: dict) -> list[tuple[str, str, str | None]]:
    rows = (data.get("data") or {}).get("list") or []
    out: list[tuple[str, str, str | None]] = []
    for row in rows:
        title = (row.get("title") or "").strip()
        url = (row.get("short_link_v2") or row.get("short_link") or "").strip()
        if not url and row.get("bvid"):
            url = f"https://www.bilibili.com/video/{row['bvid']}"
        desc = (row.get("desc") or row.get("rcmd_reason") or "")[:500] or None
        if title and url:
            out.append((title, url, desc))
    return out


def _parse_v2ex(data: list | dict) -> list[tuple[str, str, str | None]]:
    topics = data if isinstance(data, list) else data.get("result") or []
    out: list[tuple[str, str, str | None]] = []
    for t in topics:
        title = (t.get("title") or "").strip()
        url = (t.get("url") or "").strip()
        content = (t.get("content") or "")[:500] or None
        if title and url:
            out.append((title, url, content))
    return out


def _parse_reddit(data: dict) -> list[tuple[str, str, str | None]]:
    children = (data.get("data") or {}).get("children") or []
    out: list[tuple[str, str, str | None]] = []
    for child in children:
        d = child.get("data") or {}
        title = (d.get("title") or "").strip()
        permalink = (d.get("permalink") or "").strip()
        if not title or not permalink:
            continue
        url = f"https://www.reddit.com{permalink}" if permalink.startswith("/") else permalink
        summary = (d.get("selftext") or "")[:500] or None
        out.append((title, url, summary))
    return out


PARSERS = {
    "bilibili": _parse_bilibili,
    "v2ex": _parse_v2ex,
    "reddit": _parse_reddit,
}


async def crawl_http_json(source: SourceConfig) -> list[CrawledItem]:
    if not source.url:
        return []
    parser_name = source.parser or source.category or ""
    parser = PARSERS.get(parser_name)
    if not parser:
        raise ValueError(f"http_json source {source.id} needs parser: bilibili|v2ex|reddit")

    headers = {**UA}
    if parser_name == "reddit":
        headers["User-Agent"] = "AI-Know-Bot/1.0"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True, headers=headers) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()
        data = resp.json()

    parsed = parser(data)
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    items: list[CrawledItem] = []
    for title, url, summary in parsed[:30]:
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title[:500],
                url=url,
                summary=summary,
                language=source.language,
                published_at=now,
                external_id=url,
            )
        )
    return items
