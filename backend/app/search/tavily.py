from dataclasses import dataclass

import httpx

from app.config import settings

TAVILY_SEARCH_URL = "https://api.tavily.com/search"


@dataclass
class TavilySearchResult:
    title: str
    url: str
    content: str
    score: float = 0.0


class TavilySearch:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.tavily_api_key
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY is not configured")

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        search_depth: str = "advanced",
        include_raw_content: bool = True,
    ) -> list[TavilySearchResult]:
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": search_depth,
            "include_answer": False,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(TAVILY_SEARCH_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()

        results: list[TavilySearchResult] = []
        for item in data.get("results", []):
            content = (item.get("raw_content") or item.get("content") or "").strip()
            if len(content) > 2000:
                content = content[:2000] + "..."
            results.append(
                TavilySearchResult(
                    title=(item.get("title") or "Untitled").strip(),
                    url=(item.get("url") or "").strip(),
                    content=content,
                    score=float(item.get("score") or 0),
                )
            )
        return results

    async def search_many(
        self,
        queries: list[str],
        *,
        max_results_per_query: int = 4,
    ) -> list[TavilySearchResult]:
        seen_urls: set[str] = set()
        merged: list[TavilySearchResult] = []
        for query in queries:
            query = query.strip()
            if not query:
                continue
            try:
                batch = await self.search(query, max_results=max_results_per_query)
            except httpx.HTTPError:
                continue
            for item in batch:
                key = item.url.lower().rstrip("/")
                if not key or key in seen_urls:
                    continue
                seen_urls.add(key)
                merged.append(item)
        return merged
