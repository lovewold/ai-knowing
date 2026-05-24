"""Daily morning briefing: high-signal articles + one batched LLM overview (token-efficient)."""

from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.llm.resolver import get_llm_provider
from app.models import DailyBriefing, DailyBriefingItem, RawArticle, Report, ReportType, SignalScore, SignalStatus
from app.yaml_config import DouyinCreator, DailyBriefingConfig, load_daily_briefing_config, load_douyin_creators

OVERVIEW_PROMPT = """你是 AI全知 平台的晨报编辑。以下是从过去 {hours} 小时内筛选出的 {count} 条高质量 AI 资讯（已含中文标题与摘要）。

请用中文撰写「今日 AI 晨报导语」，要求：
1. 3-5 句话，概括今日最重要趋势与共性主题
2. 不要逐条复述，只做宏观归纳
3. 末尾一行输出主题标签，格式：标签: 标签1, 标签2, 标签3（3-5个）

资讯清单：
{items}

只输出导语正文和标签行，不要其他说明。"""


def _article_title(a: RawArticle) -> str:
    return a.title_zh or a.title


def _article_summary(a: RawArticle) -> str:
    s = a.summary_zh or a.summary or ""
    return s[:180] + ("..." if len(s) > 180 else s)


def select_briefing_articles(db: Session, cfg: DailyBriefingConfig) -> list[tuple[RawArticle, float]]:
    since = datetime.utcnow() - timedelta(hours=cfg.window_hours)
    rows = (
        db.query(RawArticle, SignalScore)
        .join(SignalScore, SignalScore.article_id == RawArticle.id)
        .filter(RawArticle.fetched_at >= since)
        .all()
    )
    picked: list[tuple[RawArticle, float]] = []
    for article, signal in rows:
        score = signal.score
        ok = False
        if cfg.include_high_signal and signal.status == SignalStatus.HIGH and score >= cfg.min_score:
            ok = True
        elif (
            cfg.include_medium_zh
            and signal.status == SignalStatus.MEDIUM
            and article.language == "zh"
            and score >= cfg.medium_zh_min_score
        ):
            ok = True
        elif score >= cfg.min_score:
            ok = True
        if ok:
            picked.append((article, score))

    if cfg.prefer_localized:
        picked.sort(key=lambda x: (x[0].localized, x[1]), reverse=True)
    else:
        picked.sort(key=lambda x: x[1], reverse=True)

    seen_urls: set[str] = set()
    unique: list[tuple[RawArticle, float]] = []
    for article, score in picked:
        if article.url in seen_urls:
            continue
        seen_urls.add(article.url)
        unique.append((article, score))
        if len(unique) >= cfg.max_articles:
            break
    return unique


def _build_items_block(articles: list[tuple[RawArticle, float]]) -> str:
    lines = []
    for i, (a, score) in enumerate(articles, 1):
        lines.append(
            f"{i}. [{score:.0f}分] {_article_title(a)}\n"
            f"   来源: {a.source_name} | 摘要: {_article_summary(a)}"
        )
    return "\n".join(lines) if lines else "（暂无高质量资讯，请稍后抓取）"


async def _generate_overview(cfg: DailyBriefingConfig, articles: list[tuple[RawArticle, float]]) -> tuple[str, str | None]:
    if not articles:
        return "今日暂无达到质量阈值的新资讯，建议稍后刷新或触发抓取。", None

    llm = get_llm_provider(task="briefing")
    items_block = _build_items_block(articles)
    prompt = OVERVIEW_PROMPT.format(hours=cfg.window_hours, count=len(articles), items=items_block)
    raw = await llm.generate(
        "你是简洁专业的 AI 行业晨报编辑，输出精炼中文。",
        prompt,
    )
    theme_tags = None
    lines = raw.strip().split("\n")
    body_lines = []
    for line in lines:
        if line.strip().startswith("标签:") or line.strip().startswith("标签："):
            theme_tags = line.split(":", 1)[-1].split("：", 1)[-1].strip()
        else:
            body_lines.append(line)
    overview = "\n".join(body_lines).strip() or raw.strip()
    return overview[:2000], theme_tags


def _add_creator_items(briefing: DailyBriefing, creators: list[DouyinCreator], start_order: int) -> int:
    order = start_order
    for c in creators[:6]:
        briefing.items.append(
            DailyBriefingItem(
                sort_order=order,
                item_type="creator",
                title=c.name,
                summary=c.reason,
                url=c.profile_url,
                source_name="抖音",
                creator_focus=c.focus,
            )
        )
        order += 1
    return order


async def generate_daily_briefing(db: Session, target_date: date | None = None) -> DailyBriefing | None:
    cfg = load_daily_briefing_config()
    today = target_date or date.today()

    existing = db.query(DailyBriefing).filter(DailyBriefing.briefing_date == today).first()
    if existing:
        return existing

    articles = select_briefing_articles(db, cfg)
    overview, theme_tags = await _generate_overview(cfg, articles)

    title = f"AI 行业晨报 · {today.strftime('%Y年%m月%d日')}"
    briefing = DailyBriefing(
        briefing_date=today,
        title=title,
        overview=overview,
        theme_tags=theme_tags,
        article_count=len(articles),
    )

    for i, (article, score) in enumerate(articles):
        briefing.items.append(
            DailyBriefingItem(
                sort_order=i,
                item_type="article",
                article_id=article.id,
                title=_article_title(article),
                summary=_article_summary(article),
                url=article.url,
                source_name=article.source_name,
                signal_score=score,
            )
        )

    creators = load_douyin_creators()
    _add_creator_items(briefing, creators, start_order=len(articles))

    db.add(briefing)
    db.flush()

    report_md = _briefing_to_markdown(briefing, creators)
    report = Report(
        article_id=None,
        report_type=ReportType.DAILY_BRIEFING,
        title=f"[每日晨报] {title}",
        content_md=report_md,
        quality_label="AI晨报",
    )
    db.add(report)
    db.commit()
    db.refresh(briefing)
    return briefing


def _briefing_to_markdown(briefing: DailyBriefing, creators: list[DouyinCreator]) -> str:
    lines = [f"# {briefing.title}", "", briefing.overview, ""]
    if briefing.theme_tags:
        lines.extend([f"**今日主题**: {briefing.theme_tags}", ""])
    lines.append("## 高质量资讯")
    for item in briefing.items:
        if item.item_type != "article":
            continue
        score = f" ({item.signal_score:.2f})" if item.signal_score is not None else ""
        lines.append(f"### {item.title}{score}")
        if item.summary:
            lines.append(item.summary)
        lines.append(f"[阅读原文]({item.url}) · {item.source_name or ''}")
        lines.append("")
    if creators:
        lines.append("## 抖音博主推荐")
        for c in creators[:6]:
            lines.append(f"- **{c.name}**（{c.focus}）— {c.reason} [主页]({c.profile_url})")
    return "\n".join(lines)


async def generate_daily_briefing_if_needed(db: Session) -> DailyBriefing | None:
    today = date.today()
    existing = db.query(DailyBriefing).filter(DailyBriefing.briefing_date == today).first()
    if existing:
        return existing
    return await generate_daily_briefing(db, today)


def briefing_to_dict(b: DailyBriefing, include_items: bool = True) -> dict:
    data = {
        "id": b.id,
        "briefing_date": b.briefing_date.isoformat(),
        "title": b.title,
        "overview": b.overview,
        "theme_tags": b.theme_tags,
        "article_count": b.article_count,
        "created_at": b.created_at.isoformat(),
    }
    if include_items:
        data["items"] = [
            {
                "id": it.id,
                "sort_order": it.sort_order,
                "item_type": it.item_type,
                "article_id": it.article_id,
                "title": it.title,
                "summary": it.summary,
                "url": it.url,
                "source_name": it.source_name,
                "signal_score": it.signal_score,
                "creator_focus": it.creator_focus,
            }
            for it in sorted(b.items, key=lambda x: x.sort_order)
        ]
    return data
