from datetime import datetime, timezone

import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig

GITHUB_SEARCH = "https://api.github.com/search/repositories"


async def crawl_github_search(source: SourceConfig) -> list[CrawledItem]:
    query = source.query or source.url or "ai agent stars:>100"
    params = {"q": query, "sort": "stars", "order": "desc", "per_page": 20}

    headers = {"Accept": "application/vnd.github+json", "User-Agent": "AI-Know-Bot/1.0"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(GITHUB_SEARCH, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    items: list[CrawledItem] = []
    for repo in data.get("items", []):
        name = repo.get("full_name", "")
        url = repo.get("html_url", "")
        desc = repo.get("description") or ""
        stars = repo.get("stargazers_count", 0)
        title = f"[Agent工具] {name} ({stars} stars)"
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title,
                url=url,
                summary=desc[:500] if desc else None,
                language=source.language,
                published_at=datetime.now(timezone.utc).replace(tzinfo=None),
                external_id=str(repo.get("id", url)),
            )
        )
    return items
