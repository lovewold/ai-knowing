"""Hotspot aggregation queries (aihot-style multi-source feed)."""
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.models import RawArticle, SignalScore, SignalStatus


def _hotspot_dict(article: RawArticle, heat_level: str) -> dict:
    sig = article.signal
    return {
        "id": article.id,
        "title": article.title_zh or article.title,
        "title_original": article.title_original or (article.title if not article.localized else None),
        "summary": article.summary_zh or article.summary,
        "url": article.url,
        "source": article.source_name,
        "source_id": article.source_id,
        "category": article.category,
        "language": article.language,
        "signal_score": sig.score if sig else None,
        "signal_status": sig.status.value if sig else None,
        "heat_level": heat_level,
        "cross_source_count": sig.cross_validation_count if sig else 0,
        "fetched_at": article.fetched_at.isoformat(),
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "is_new": (datetime.utcnow() - article.fetched_at) <= timedelta(hours=24),
    }


def _assign_heat_levels(scored: list[tuple[RawArticle, float]]) -> list[tuple[RawArticle, str]]:
    if not scored:
        return []
    n = len(scored)
    high_cut = max(1, int(n * 0.34))
    med_cut = max(high_cut + 1, int(n * 0.67))
    out: list[tuple[RawArticle, str]] = []
    for i, (article, _) in enumerate(scored):
        if i < high_cut:
            level = "high"
        elif i < med_cut:
            level = "medium"
        else:
            level = "low"
        out.append((article, level))
    return out


def query_hotspots(
    db: Session,
    *,
    hours: int = 24,
    sort: str = "heat",
    heat_level: str | None = None,
    signal_status: str | None = None,
    source_id: str | None = None,
    category: str | None = None,
    min_score: float | None = None,
    min_sources: int | None = None,
    only_new: bool = False,
    q: str | None = None,
    limit: int = 30,
    page: int = 1,
) -> tuple[list[dict], int]:
    since = datetime.utcnow() - timedelta(hours=hours)
    query = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.signal))
        .filter(RawArticle.fetched_at >= since)
    )

    if source_id:
        query = query.filter(RawArticle.source_id == source_id)
    if category:
        query = query.filter(RawArticle.category == category)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(RawArticle.title.ilike(like), RawArticle.title_zh.ilike(like), RawArticle.summary.ilike(like), RawArticle.summary_zh.ilike(like)))
    if only_new:
        query = query.filter(RawArticle.fetched_at >= datetime.utcnow() - timedelta(hours=24))
    if min_score is not None or min_sources is not None or signal_status:
        query = query.join(SignalScore, RawArticle.id == SignalScore.article_id)
        if min_score is not None:
            query = query.filter(SignalScore.score >= min_score)
        if min_sources is not None and min_sources > 1:
            query = query.filter(SignalScore.cross_validation_count >= min_sources - 1)
        if signal_status:
            try:
                query = query.filter(SignalScore.status == SignalStatus(signal_status))
            except ValueError:
                pass

    articles = query.all()

    def score_of(a: RawArticle) -> float:
        return a.signal.score if a.signal else 0.0

    if sort == "newest":
        articles.sort(key=lambda a: a.fetched_at, reverse=True)
    elif sort == "cross_source":
        articles.sort(key=lambda a: (a.signal.cross_validation_count if a.signal else 0, score_of(a)), reverse=True)
    else:
        articles.sort(key=lambda a: (score_of(a), a.fetched_at), reverse=True)

    scored = [(a, score_of(a)) for a in articles]
    leveled = _assign_heat_levels(scored)

    if heat_level:
        leveled = [(a, lv) for a, lv in leveled if lv == heat_level]

    total = len(leveled)
    offset = max(0, (page - 1) * limit)
    page_items = leveled[offset : offset + limit]

    return [_hotspot_dict(a, lv) for a, lv in page_items], total


def hotspot_summary(db: Session, hours: int = 24) -> dict:
    since = datetime.utcnow() - timedelta(hours=hours)
    articles = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.signal))
        .filter(RawArticle.fetched_at >= since)
        .all()
    )
    scored = [(a, a.signal.score if a.signal else 0.0) for a in articles]
    leveled = _assign_heat_levels(scored)

    tier_counts = {"high": 0, "medium": 0, "low": 0}
    signal_counts = {"high": 0, "medium": 0, "low": 0}
    source_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    new_count = 0

    for article, level in leveled:
        tier_counts[level] += 1
        if article.signal:
            signal_counts[article.signal.status.value] += 1
        source_counts[article.source_name] = source_counts.get(article.source_name, 0) + 1
        category_counts[article.category] = category_counts.get(article.category, 0) + 1
        if (datetime.utcnow() - article.fetched_at) <= timedelta(hours=24):
            new_count += 1

    latest = max((a.fetched_at for a in articles), default=None)

    return {
        "hours": hours,
        "total": len(articles),
        "heat_tiers": tier_counts,
        "signal_tiers": signal_counts,
        "new_count": new_count,
        "by_source": source_counts,
        "by_category": category_counts,
        "last_updated": latest.isoformat() if latest else None,
    }
