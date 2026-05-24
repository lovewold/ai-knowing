from dataclasses import dataclass
from datetime import datetime


@dataclass
class CrawledItem:
    source_id: str
    source_name: str
    source_weight: int
    title: str
    url: str
    summary: str | None = None
    content: str | None = None
    language: str = "en"
    published_at: datetime | None = None
    external_id: str | None = None
