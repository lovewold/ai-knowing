from datetime import datetime, timezone

import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

HN_API = "https://hacker-news.firebaseio.com/v0"


async def _fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    resp = await client.get(f"{HN_API}/item/{item_id}.json")
    if resp.status_code != 200:
        return None
    return resp.json()


def _is_ai_related(title: str, url: str) -> bool:
    keywords = [
        "ai", "ml", "llm", "gpt", "claude", "gemini", "model", "agent",
        "rag", "transformer", "deepseek", "openai", "anthropic", "machine learning",
        "artificial intelligence", "neural", "diffusion", "embedding",
    ]
    text = f"{title} {url}".lower()
    return any(kw in text for kw in keywords)


async def crawl_hackernews(source: SourceConfig) -> list[CrawledItem]:
    async with httpx.AsyncClient(timeout=30) as client:
        if source.filter == "show":
            resp = await client.get(f"{HN_API}/showstories.json")
        else:
            resp = await client.get(f"{HN_API}/topstories.json")
        resp.raise_for_status()
        story_ids = resp.json()[:50]

        items: list[CrawledItem] = []
        for sid in story_ids:
            story = await _fetch_item(client, sid)
            if not story or story.get("type") != "story":
                continue
            title = story.get("title", "")
            url = story.get("url") or f"https://news.ycombinator.com/item?id={sid}"
            if source.filter != "show" and not _is_ai_related(title, url):
                continue
            ts = story.get("time")
            published = datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None) if ts else None
            items.append(
                CrawledItem(
                    source_id=source.id,
                    source_name=source.name,
                    source_weight=source.weight,
                    title=title,
                    url=url,
                    summary=None,
                    language=source.language,
                    published_at=published,
                    external_id=str(sid),
                )
            )
    return items
