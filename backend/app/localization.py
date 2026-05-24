import json
import re

from app.config import settings
from app.llm.resolver import get_llm_provider
from app.models import RawArticle

AGENT_KEYWORDS = {
    "agent", "agents", "autogpt", "crewai", "autogen", "langgraph", "langchain",
    "llamaindex", "mcp", "tool use", "function calling", "multi-agent",
    "agentic", "swarm", "dify", "coze", "n8n", "workflow", "reAct", "react agent",
    "openai agents", "claude agent", "agent framework", "agent sdk",
}


def is_agent_related(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in AGENT_KEYWORDS)


def is_chinese_text(text: str, threshold: float = 0.25) -> bool:
    if not text or not text.strip():
        return False
    cjk = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
    return cjk / len(text) >= threshold


def classify_category(article: RawArticle) -> str:
    text = f"{article.title} {article.summary or ''} {article.url}".lower()
    if article.source_id.startswith("arxiv"):
        return "paper"
    if is_agent_related(text):
        return "agent"
    if "github.com" in article.url or "trending" in text:
        return "tool"
    return "news"


def apply_localization(article: RawArticle, title_zh: str, summary_zh: str) -> None:
    """Write Chinese into primary fields; preserve originals when translating from English."""
    if not article.title_original:
        article.title_original = article.title
    if article.summary and not article.summary_original:
        article.summary_original = article.summary

    article.title_zh = (title_zh or article.title)[:500]
    article.summary_zh = summary_zh or article.summary or ""
    article.title = article.title_zh
    article.summary = article.summary_zh
    article.language = "zh"
    article.localized = True
    article.category = classify_category(article)


async def localize_article(article: RawArticle) -> tuple[str, str]:
    """Generate Chinese title and summary via LLM."""
    if article.language == "zh" or is_chinese_text(article.title):
        summary = article.summary_zh or article.summary or ""
        return article.title, summary

    llm = get_llm_provider(task="localize")
    prompt = f"""请将以下 AI 行业资讯翻译并整理为中文。

原始标题：{article.title_original or article.title}
原始摘要：{article.summary_original or article.summary or '（无摘要，请根据标题推断并生成80字以内中文摘要）'}
来源：{article.source_name}
链接：{article.url}

请严格按 JSON 格式输出，不要其他内容：
{{"title_zh": "中文标题（简洁准确）", "summary_zh": "中文摘要（80-150字，概括核心信息）"}}"""
    raw = await llm.generate("你是专业的 AI 行业资讯编辑，输出简洁准确的中文。", prompt)
    try:
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            data = json.loads(match.group())
            return data.get("title_zh", article.title), data.get("summary_zh", article.summary or "")
    except (json.JSONDecodeError, AttributeError):
        pass
    return article.title, article.summary or "暂无摘要，请查看原文链接。"


async def localize_articles_batch(
    db,
    articles: list[RawArticle],
    limit: int | None = None,
) -> int:
    """Localize articles. limit=None or 0 means no cap."""
    count = 0
    for article in articles:
        if article.localized and article.title_zh:
            continue
        if limit is not None and limit > 0 and count >= limit:
            break
        title_zh, summary_zh = await localize_article(article)
        apply_localization(article, title_zh, summary_zh)
        count += 1
    if count:
        db.commit()
    return count
