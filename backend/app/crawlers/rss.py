from datetime import datetime
from email.utils import parsedate_to_datetime

import feedparser
import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig


def _parse_date(entry) -> datetime | None:
    for key in ("published_parsed", "updated_parsed"):
        parsed = entry.get(key)
        if parsed:
            try:
                return datetime(*parsed[:6])
            except (TypeError, ValueError):
                pass
    for key in ("published", "updated"):
        raw = entry.get(key)
        if raw:
            try:
                return parsedate_to_datetime(raw)
            except (TypeError, ValueError):
                pass
    return None


def _clean_html(text: str | None) -> str:
    if not text:
        return ""
    import re

    return re.sub(r"<[^>]+>", "", text).strip()


async def crawl_rss(source: SourceConfig) -> list[CrawledItem]:
    if not source.url:
        return []

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(source.url)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

    items: list[CrawledItem] = []
    for entry in feed.entries[:30]:
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()
        if not title or not url:
            continue
        summary = _clean_html(entry.get("summary") or entry.get("description"))
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title,
                url=url,
                summary=summary[:2000] if summary else None,
                language=source.language,
                published_at=_parse_date(entry),
                external_id=entry.get("id") or url,
            )
        )
    return items
