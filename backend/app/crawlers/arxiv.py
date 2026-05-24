from datetime import datetime

import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

ARXIV_API = "https://export.arxiv.org/api/query"


async def crawl_arxiv(source: SourceConfig) -> list[CrawledItem]:
    category = source.category or "cs.AI"
    params = {
        "search_query": f"cat:{category}",
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "max_results": 20,
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(ARXIV_API, params=params)
        resp.raise_for_status()
        import feedparser

        feed = feedparser.parse(resp.text)

    items: list[CrawledItem] = []
    for entry in feed.entries:
        title = entry.get("title", "").replace("\n", " ").strip()
        url = entry.get("link", "").strip()
        if not title or not url:
            continue
        summary = entry.get("summary", "").replace("\n", " ").strip()
        published = None
        if entry.get("published_parsed"):
            published = datetime(*entry.published_parsed[:6])
        arxiv_id = url.split("/abs/")[-1] if "/abs/" in url else url
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title,
                url=url,
                summary=summary[:2000],
                language=source.language,
                published_at=published,
                external_id=arxiv_id,
            )
        )
    return items
