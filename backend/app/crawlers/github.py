from datetime import datetime, timezone

import httpx

from app.crawlers.base import CrawledItem
from app.yaml_config import SourceConfig


async def crawl_github_trending(source: SourceConfig) -> list[CrawledItem]:
    language = source.language or "python"
    url = f"https://github.com/trending/{language}?since=daily"

    headers = {
        "User-Agent": "AI-Know-Bot/1.0",
        "Accept": "text/html",
    }

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        html = resp.text

    import re

    items: list[CrawledItem] = []
    # Parse repo links from trending page
    pattern = re.compile(
        r'<h2 class="h3 lh-condensed">\s*'
        r'<a[^>]+href="/([^"]+)"[^>]*>\s*([^<]+)\s*</a>',
        re.DOTALL,
    )
    desc_pattern = re.compile(
        r'<p class="col-9 color-fg-muted my-1 pr-4">([^<]*)</p>'
    )

    matches = list(pattern.finditer(html))
    descs = desc_pattern.findall(html)

    for i, match in enumerate(matches[:15]):
        repo_path = match.group(1).strip()
        repo_name = match.group(2).strip()
        desc = descs[i].strip() if i < len(descs) else ""
        repo_url = f"https://github.com/{repo_path}"
        title = f"[Trending] {repo_name}"
        items.append(
            CrawledItem(
                source_id=source.id,
                source_name=source.name,
                source_weight=source.weight,
                title=title,
                url=repo_url,
                summary=desc[:500] if desc else None,
                language=source.language,
                published_at=datetime.now(timezone.utc).replace(tzinfo=None),
                external_id=repo_path,
            )
        )
    return items
