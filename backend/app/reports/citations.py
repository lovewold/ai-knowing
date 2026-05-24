import json
import re
from dataclasses import asdict, dataclass


@dataclass
class Citation:
    id: int
    title: str
    url: str
    snippet: str
    source_type: str  # web | article
    article_id: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def citations_to_json(citations: list[Citation]) -> str:
    return json.dumps([c.to_dict() for c in citations], ensure_ascii=False)


def citations_from_json(raw: str | None) -> list[Citation]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    out: list[Citation] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        out.append(
            Citation(
                id=int(item.get("id", len(out) + 1)),
                title=str(item.get("title", "")),
                url=str(item.get("url", "")),
                snippet=str(item.get("snippet", "")),
                source_type=str(item.get("source_type", "web")),
                article_id=item.get("article_id"),
            )
        )
    return out


def queries_to_json(queries: list[str]) -> str:
    return json.dumps(queries, ensure_ascii=False)


def queries_from_json(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [str(q) for q in data if q]


def clean_report_content(content: str) -> str:
    """Remove inline citation marks and reference sections from report body."""
    text = content.strip()
    text = re.sub(r"\n##\s*参考来源[\s\S]*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n##\s*参考资料[\s\S]*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\[(\d+(?:-\d+)?(?:,\s*\d+)*)\]", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def format_references_section(citations: list[Citation]) -> str:
    if not citations:
        return ""
    lines = ["## 参考来源", ""]
    for c in citations:
        lines.append(f"[{c.id}] [{c.title}]({c.url})")
    return "\n".join(lines)


def ensure_references_in_content(content: str, citations: list[Citation]) -> str:
    """Deprecated: links are stored separately; keep body clean."""
    return clean_report_content(content)
