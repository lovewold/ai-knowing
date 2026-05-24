from app.crawlers.arxiv import crawl_arxiv
from app.crawlers.base import CrawledItem
from app.crawlers.firecrawl import crawl_firecrawl
from app.crawlers.github import crawl_github_trending
from app.crawlers.github_search import crawl_github_search
from app.crawlers.hackernews import crawl_hackernews
from app.crawlers.http_json import crawl_http_json
from app.crawlers.rss import crawl_rss
from app.crawlers.twitterapi_io import crawl_twitterapi_io
from app.yaml_config import SourceConfig, load_sources

CRAWLER_MAP = {
    "rss": crawl_rss,
    "arxiv": crawl_arxiv,
    "hackernews": crawl_hackernews,
    "github_trending": crawl_github_trending,
    "github_search": crawl_github_search,
    "firecrawl": crawl_firecrawl,
    "twitterapi_io": crawl_twitterapi_io,
    "http_json": crawl_http_json,
}


async def crawl_source(source: SourceConfig) -> list[CrawledItem]:
    crawler = CRAWLER_MAP.get(source.type)
    if not crawler:
        raise ValueError(f"Unknown source type: {source.type}")
    return await crawler(source)


async def crawl_all_sources() -> list[CrawledItem]:
    sources = load_sources()
    all_items: list[CrawledItem] = []
    for source in sources:
        try:
            items = await crawl_source(source)
            all_items.extend(items)
        except Exception as e:
            print(f"[crawl] {source.id} failed: {e}")
    return all_items
