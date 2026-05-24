import json
import re
from dataclasses import dataclass

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.config import settings
from app.llm.resolver import get_llm_provider
from app.models import AgentCombo, RawArticle, Report, ReportType
from app.reports.citations import (
    Citation,
    citations_to_json,
    clean_report_content,
    queries_to_json,
)
from app.reports.generator import _extract_title
from app.reports.prompts import PLANNER_SYSTEM, RESEARCHER_NOTE, WRITER_SYSTEM
from app.search.tavily import TavilySearch


@dataclass
class ResearchPlan:
    title_hint: str
    outline: list[str]
    search_queries: list[str]


def _parse_json_object(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]
    return json.loads(text)


async def _plan_research(llm, user_prompt: str, combo: AgentCombo | None) -> ResearchPlan:
    combo_ctx = ""
    if combo and combo.system_prompt:
        combo_ctx = f"\n\n工作流编排说明：{combo.system_prompt}"
    user = f"用户需求：\n{user_prompt.strip()}{combo_ctx}\n\n请输出 JSON 计划。"
    raw = await llm.generate(PLANNER_SYSTEM, user)
    try:
        data = _parse_json_object(raw)
    except (json.JSONDecodeError, ValueError):
        data = {
            "title_hint": user_prompt.strip()[:30],
            "outline": ["背景概述", "核心分析", "趋势判断", "行动建议"],
            "search_queries": [user_prompt.strip()[:80]],
        }
    queries = [str(q).strip() for q in data.get("search_queries", []) if str(q).strip()]
    if not queries:
        queries = [user_prompt.strip()[:100]]
    outline = [str(o).strip() for o in data.get("outline", []) if str(o).strip()]
    return ResearchPlan(
        title_hint=str(data.get("title_hint") or user_prompt[:30]).strip(),
        outline=outline or ["核心分析", "结论与建议"],
        search_queries=queries[:5],
    )


def _match_db_articles(
    db: Session,
    *,
    user_prompt: str,
    queries: list[str],
    article_ids: list[int] | None,
    include_db_match: bool = True,
    limit: int = 5,
) -> list[RawArticle]:
    q = db.query(RawArticle).options(joinedload(RawArticle.signal))
    manual: list[RawArticle] = []
    if article_ids:
        manual = q.filter(RawArticle.id.in_(article_ids)).all()
        order = {aid: i for i, aid in enumerate(article_ids)}
        manual.sort(key=lambda a: order.get(a.id, 999))

    if not include_db_match:
        return manual

    terms: list[str] = []
    for part in [user_prompt, *queries]:
        for token in re.split(r"[\s,，、/|]+", part):
            token = token.strip()
            if len(token) >= 2:
                terms.append(token)
    terms = list(dict.fromkeys(terms))[:8]
    if not terms:
        return manual

    filters = []
    for term in terms:
        like = f"%{term}%"
        filters.append(RawArticle.title.ilike(like))
        filters.append(RawArticle.title_zh.ilike(like))
        filters.append(RawArticle.summary.ilike(like))
        filters.append(RawArticle.summary_zh.ilike(like))

    articles = q.filter(or_(*filters)).order_by(RawArticle.fetched_at.desc()).limit(limit * 3).all()

    def score_article(a: RawArticle) -> float:
        text = " ".join(
            filter(None, [a.title, a.title_zh, a.summary, a.summary_zh])
        ).lower()
        hits = sum(1 for t in terms if t.lower() in text)
        sig = a.signal.score if a.signal else 0.0
        return hits * 10 + sig

    articles.sort(key=score_article, reverse=True)

    seen = {a.id for a in manual}
    for article in articles:
        if article.id in seen:
            continue
        manual.append(article)
        seen.add(article.id)
        if len(manual) >= len(article_ids or []) + limit:
            break
    return manual


def _build_citations(
    web_results: list,
    articles: list[RawArticle],
) -> list[Citation]:
    citations: list[Citation] = []
    cid = 1
    for item in web_results:
        citations.append(
            Citation(
                id=cid,
                title=item.title,
                url=item.url,
                snippet=item.content[:500] if item.content else "",
                source_type="web",
            )
        )
        cid += 1
    for article in articles:
        title = article.title_zh or article.title
        snippet = (article.summary_zh or article.summary or "")[:500]
        citations.append(
            Citation(
                id=cid,
                title=title,
                url=article.url,
                snippet=snippet,
                source_type="article",
                article_id=article.id,
            )
        )
        cid += 1
    return citations


def _format_sources_for_writer(citations: list[Citation]) -> str:
    if not citations:
        return "（未检索到可用资料，请基于 AI 行业通识撰写并标注推测）"
    blocks = []
    for c in citations:
        src_label = "网络检索" if c.source_type == "web" else "平台资讯"
        blocks.append(
            f"- ({src_label}) **{c.title}**\n"
            f"  摘要: {c.snippet or '（无摘要）'}"
        )
    return "\n".join(blocks)


async def generate_research_report(
    user_prompt: str,
    *,
    db: Session,
    article_ids: list[int] | None = None,
    include_db_match: bool = True,
    combo_id: int | None = None,
) -> Report:
    llm = get_llm_provider(task="custom", db=db)
    lang = "中文" if settings.report_language == "zh" else "English"

    combo: AgentCombo | None = None
    if combo_id:
        combo = db.query(AgentCombo).filter(AgentCombo.id == combo_id, AgentCombo.enabled == True).first()  # noqa: E712

    plan = await _plan_research(llm, user_prompt, combo)

    tavily = TavilySearch()
    web_results = await tavily.search_many(plan.search_queries)

    db_articles: list[RawArticle] = []
    if include_db_match or article_ids:
        db_articles = _match_db_articles(
            db,
            user_prompt=user_prompt,
            queries=plan.search_queries,
            article_ids=article_ids or None,
            include_db_match=include_db_match,
        )

    citations = _build_citations(web_results, db_articles)
    sources_block = _format_sources_for_writer(citations)
    outline_block = "\n".join(f"- {h}" for h in plan.outline)

    writer_user = f"""{RESEARCHER_NOTE}

## 用户需求
{user_prompt.strip()}

## 建议大纲
{outline_block}

## 检索资料
{sources_block}

请按大纲撰写 AI 行业报告，标题方向：{plan.title_hint}
"""
    if combo and combo.system_prompt:
        writer_user += f"\n## 编排要求\n{combo.system_prompt}\n"

    content = await llm.generate(WRITER_SYSTEM.format(language=lang), writer_user)
    content = clean_report_content(content)

    fallback_title = plan.title_hint or user_prompt.strip()[:80]
    title, body = _extract_title(content, fallback_title)
    if body != content:
        content = clean_report_content(f"# {title}\n\n{body}")

    primary_article_id = None
    if article_ids and len(article_ids) == 1:
        primary_article_id = article_ids[0]
    elif len(db_articles) == 1:
        primary_article_id = db_articles[0].id

    return Report(
        article_id=primary_article_id,
        report_type=ReportType.CUSTOM,
        title=f"[AI行业] {title}"[:500],
        content_md=content,
        user_prompt=user_prompt.strip(),
        quality_label="AI行业",
        citations_json=citations_to_json(citations),
        search_queries_json=queries_to_json(plan.search_queries),
        combo_id=combo_id,
    )
