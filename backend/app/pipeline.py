import asyncio

from sqlalchemy.orm import Session

from app.agent.catalog import seed_known_agent_tools, sync_agent_tools_from_articles
from app.crawlers.registry import crawl_all_sources
from app.config import settings
from app.localization import classify_category, is_chinese_text, localize_articles_batch
from app.models import AgentTool, RawArticle, Report, ReportType, SignalScore, SignalStatus
from app.reports.generator import generate_agent_survey_report, generate_report, generate_scenario_report
from app.scoring.signal import (
    classify_report_type,
    is_duplicate_title,
    passes_quality_gate,
    rescore_recent_articles,
    upsert_signal_score,
)
from app.yaml_config import load_scoring_config


def save_crawled_items(db: Session, items) -> list[RawArticle]:
    config = load_scoring_config()
    dedup_threshold = config.dedup.get("title_similarity_threshold", 0.85)
    dedup_hours = config.dedup.get("window_hours", 48)

    seen_urls: set[str] = set()
    saved: list[RawArticle] = []
    skipped = {"duplicate_url": 0, "duplicate_title": 0, "quality": 0}

    for item in items:
        if item.url in seen_urls:
            continue
        seen_urls.add(item.url)
        if db.query(RawArticle).filter(RawArticle.url == item.url).first():
            skipped["duplicate_url"] += 1
            continue
        if is_duplicate_title(db, item.title, dedup_threshold, dedup_hours):
            skipped["duplicate_title"] += 1
            continue

        category = "agent" if "agent" in item.source_id.lower() or "[Agent" in item.title else "news"
        already_zh = item.language == "zh" or is_chinese_text(item.title)
        article = RawArticle(
            source_id=item.source_id,
            source_name=item.source_name,
            source_weight=item.source_weight,
            title=item.title,
            title_original=item.title,
            url=item.url,
            summary=item.summary,
            summary_original=item.summary,
            content=item.content,
            language="zh" if already_zh else item.language,
            category=category,
            published_at=item.published_at,
            external_id=item.external_id,
        )
        if already_zh:
            article.title_zh = item.title[:500]
            article.summary_zh = item.summary or ""
            article.localized = True

        if not passes_quality_gate(article, config):
            skipped["quality"] += 1
            continue

        db.add(article)
        try:
            db.commit()
            db.refresh(article)
            saved.append(article)
        except Exception:
            db.rollback()

    if skipped["duplicate_url"] or skipped["duplicate_title"] or skipped["quality"]:
        print(f"[pipeline] skipped: {skipped}")
    return saved


def score_articles(db: Session, articles: list[RawArticle]) -> list[SignalScore]:
    scores: list[SignalScore] = []
    for article in articles:
        article.category = classify_category(article)
        signal = upsert_signal_score(db, article)
        scores.append(signal)
    db.commit()
    return scores


async def generate_reports_for_articles(db: Session) -> list[Report]:
    candidates = (
        db.query(SignalScore)
        .join(RawArticle)
        .filter(
            (SignalScore.status == SignalStatus.HIGH)
            | (
                (SignalScore.status == SignalStatus.MEDIUM)
                & (RawArticle.category == "agent")
            )
        )
        .all()
    )
    reports: list[Report] = []
    for signal in candidates:
        existing = db.query(Report).filter(Report.article_id == signal.article_id).first()
        if existing:
            continue
        article = db.query(RawArticle).filter(RawArticle.id == signal.article_id).first()
        if not article:
            continue
        report_type = "agent" if article.category == "agent" else classify_report_type(article)
        primary = await generate_report(article, report_type, signal.score)
        db.add(primary)
        db.flush()
        if article.category != "agent":
            scenario = await generate_scenario_report(article, primary)
            db.add(scenario)
            reports.append(scenario)
        reports.append(primary)
    db.commit()
    return reports


async def generate_agent_survey_if_needed(db: Session) -> Report | None:
    existing = (
        db.query(Report)
        .filter(Report.report_type == ReportType.AGENT_SURVEY)
        .order_by(Report.created_at.desc())
        .first()
    )
    tools = db.query(AgentTool).order_by(AgentTool.stars.desc().nullslast()).all()
    if len(tools) < 3:
        return None
    if existing:
        from datetime import datetime, timedelta
        if existing.created_at > datetime.utcnow() - timedelta(hours=24):
            return None
    report = await generate_agent_survey_report(tools)
    db.add(report)
    db.commit()
    return report


async def run_full_pipeline(db: Session) -> dict:
    seed_known_agent_tools(db)
    items = await crawl_all_sources()
    saved = save_crawled_items(db, items)

    localized = 0
    # 抓取后强制全部翻译为中文再评分
    if saved:
        localized = await localize_articles_batch(db, saved, limit=None)

    if settings.localize_backlog_per_run > 0:
        backlog = (
            db.query(RawArticle)
            .filter(RawArticle.localized == False)  # noqa: E712
            .order_by(RawArticle.fetched_at.desc())
            .limit(settings.localize_backlog_per_run)
            .all()
        )
        localized += await localize_articles_batch(db, backlog, limit=settings.localize_backlog_per_run)

    scores = score_articles(db, saved)
    rescored = rescore_recent_articles(db, window_hours=72)
    sync_agent_tools_from_articles(db, saved)
    reports: list[Report] = []
    try:
        reports = await generate_reports_for_articles(db)
        survey = await generate_agent_survey_if_needed(db)
        if survey:
            reports.append(survey)
    except Exception as exc:
        print(f"[pipeline] report generation skipped: {exc}")
        db.rollback()

    from app.reports.daily_briefing import generate_daily_briefing_if_needed
    briefing = await generate_daily_briefing_if_needed(db)

    high_count = sum(1 for s in scores if s.status == SignalStatus.HIGH)
    agent_count = db.query(AgentTool).count()
    return {
        "crawled": len(items),
        "saved": len(saved),
        "localized": localized,
        "scored": len(scores),
        "rescored_window": rescored,
        "high_signal": high_count,
        "agent_tools": agent_count,
        "reports_generated": len(reports),
        "daily_briefing": briefing.id if briefing else None,
    }


async def backfill_localization(db: Session, limit: int = 50) -> dict:
    articles = (
        db.query(RawArticle)
        .filter((RawArticle.localized == False) | (RawArticle.title_zh == None))  # noqa: E711
        .order_by(RawArticle.fetched_at.desc())
        .limit(limit)
        .all()
    )
    count = await localize_articles_batch(db, articles, limit=limit)
    for a in articles:
        a.category = classify_category(a)
    db.commit()
    rescore_recent_articles(db, window_hours=168)
    sync_agent_tools_from_articles(db, articles)
    return {"localized": count, "total_articles": db.query(RawArticle).count()}


def run_full_pipeline_sync(db: Session) -> dict:
    return asyncio.run(run_full_pipeline(db))
