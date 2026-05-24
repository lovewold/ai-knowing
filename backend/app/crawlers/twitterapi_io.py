"""Twitter/X crawler via twitterapi.io advanced search."""

from datetime import datetime

import httpx
from dateutil import parser as date_parser

from app.config import settings
from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

API_BASE = "https://api.twitterapi.io"


def _engagement(tweet: dict) -> int:
    return int(tweet.get("likeCount") or 0) + int(tweet.get("retweetCount") or 0) + int(tweet.get("replyCount") or 0)


def _parse_created_at(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return date_parser.parse(raw).replace(tzinfo=None)
    except (ValueError, TypeError):
        return None


async def crawl_twitterapi_io(source: SourceConfig) -> list[CrawledItem]:
    api_key = settings.twitterapi_io_key
    if not api_key:
        print(f"[crawl] {source.id}: TWITTERAPI_IO_KEY not set, skip")
        return []

    query = source.query or '(AI OR LLM OR "machine learning") lang:en'
    min_engagement = source.min_engagement or 100
    query_type = source.filter or "Top"

    async with httpx.AsyncClient(timeout=45) as client:
        resp = await client.get(
            f"{API_BASE}/twitter/tweet/advanced_search",
            headers={"X-API-Key": api_key},
            params={"query": query, "queryType": query_type, "cursor": ""},
        )
        resp.raise_for_status()
        payload = resp.json()

    tweets = payload.get("tweets") or []
    items: list[CrawledItem] = []
    for tw in tweets:
        if _engagement(tw) < min_engagement:
            continue
        text = (tw.get("text") or "").strip()
        url = (tw.get("url") or "").strip()
        tid = tw.get("id")
        if not text or not url:
            continue
        title = text.replace("\n", " ")[:280]
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title,
                url=url,
                summary=f"互动 {_engagement(tw)}" if min_engagement else None,
                language=source.language,
                published_at=_parse_created_at(tw.get("createdAt")),
                external_id=str(tid) if tid else url,
            )
        )
    return items[:30]
