import markdown
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.admin.routes import router as admin_router
from app.admin.seed import seed_admin_data
from app.database import get_db, init_db
from app.models import AgentCombo, AgentComboMember, AgentTool, DailyBriefing, RawArticle, Report, ReportType, SignalScore, SignalStatus
from app.hotspots import hotspot_summary, query_hotspots
from app.pipeline import backfill_localization, run_full_pipeline
from app.reports.daily_briefing import briefing_to_dict, generate_daily_briefing, generate_daily_briefing_if_needed
from app.reports.generator import generate_custom_report
from app.yaml_config import load_douyin_creators, load_sources

app = FastAPI(title="AI全知", description="AI 行业知识库 - 抓取与报告系统")
templates = Jinja2Templates(directory="app/templates")
app.include_router(admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateReportRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=4000)
    article_ids: list[int] = Field(default_factory=list)
    include_recent_articles: int = Field(default=10, ge=0, le=30)
    include_agent_tools: bool = False
    include_existing_reports: int = Field(default=3, ge=0, le=10)


def _report_summary(r: Report) -> dict:
    return {
        "id": r.id,
        "title": r.title,
        "type": r.report_type.value,
        "quality_label": r.quality_label,
        "created_at": r.created_at.isoformat(),
        "article_url": r.article.url if r.article else None,
        "source_name": r.article.source_name if r.article else None,
        "user_prompt": r.user_prompt,
    }


@app.on_event("startup")
def startup():
    init_db()
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        seed_admin_data(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    reports = (
        db.query(Report)
        .options(joinedload(Report.article))
        .order_by(Report.created_at.desc())
        .limit(50)
        .all()
    )
    articles = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.signal))
        .order_by(RawArticle.fetched_at.desc())
        .limit(30)
        .all()
    )
    sources = load_sources()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "reports": reports, "articles": articles, "sources": sources},
    )


@app.get("/reports/{report_id}", response_class=HTMLResponse)
def report_detail(report_id: int, request: Request, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .options(joinedload(Report.article))
        .filter(Report.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    html_content = markdown.markdown(report.content_md, extensions=["tables", "fenced_code"])
    return templates.TemplateResponse(
        "report.html",
        {"request": request, "report": report, "html_content": html_content},
    )


def _article_dict(a: RawArticle) -> dict:
    return {
        "id": a.id,
        "title": a.title_zh or a.title,
        "title_original": a.title_original or (a.title if not a.localized else None),
        "summary": a.summary_zh or a.summary,
        "url": a.url,
        "source": a.source_name,
        "category": a.category,
        "signal_score": a.signal.score if a.signal else None,
        "signal_status": a.signal.status.value if a.signal else None,
        "fetched_at": a.fetched_at.isoformat(),
    }


@app.get("/api/agent-combos")
def api_agent_combos_public(db: Session = Depends(get_db)):
    from app.admin.routes import _combo_dict
    from app.models import AgentCombo, AgentComboMember
    combos = (
        db.query(AgentCombo)
        .options(joinedload(AgentCombo.members).joinedload(AgentComboMember.agent_tool), joinedload(AgentCombo.llm_model))
        .filter(AgentCombo.enabled == True)  # noqa: E712
        .order_by(AgentCombo.id)
        .all()
    )
    return [_combo_dict(c) for c in combos]


@app.get("/api/stats")
def api_stats(db: Session = Depends(get_db)):
    report_count = db.query(Report).count()
    article_count = db.query(RawArticle).count()
    high_signal = db.query(SignalScore).filter(SignalScore.status == SignalStatus.HIGH).count()
    agent_tools = db.query(AgentTool).count()
    agent_articles = db.query(RawArticle).filter(RawArticle.category == "agent").count()
    sources = load_sources()
    return {
        "reports": report_count,
        "articles": article_count,
        "high_signal": high_signal,
        "agent_tools": agent_tools,
        "agent_articles": agent_articles,
        "sources": len(sources),
    }


@app.get("/api/reports")
def api_reports(report_type: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Report).options(joinedload(Report.article)).order_by(Report.created_at.desc())
    if report_type:
        try:
            query = query.filter(Report.report_type == ReportType(report_type))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid report type")
    reports = query.limit(100).all()
    return [_report_summary(r) for r in reports]


@app.post("/api/reports/generate")
async def api_generate_report(body: GenerateReportRequest, db: Session = Depends(get_db)):
    articles: list[RawArticle] = []
    if body.article_ids:
        articles = (
            db.query(RawArticle)
            .options(joinedload(RawArticle.signal))
            .filter(RawArticle.id.in_(body.article_ids))
            .all()
        )
    elif body.include_recent_articles > 0:
        articles = (
            db.query(RawArticle)
            .options(joinedload(RawArticle.signal))
            .order_by(RawArticle.fetched_at.desc())
            .limit(body.include_recent_articles)
            .all()
        )

    tools: list[AgentTool] = []
    if body.include_agent_tools:
        tools = db.query(AgentTool).order_by(AgentTool.stars.desc().nullslast()).all()

    existing: list[Report] = []
    if body.include_existing_reports > 0:
        existing = (
            db.query(Report)
            .order_by(Report.created_at.desc())
            .limit(body.include_existing_reports)
            .all()
        )

    report = await generate_custom_report(
        body.prompt,
        articles=articles or None,
        tools=tools or None,
        existing_reports=existing or None,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        "id": report.id,
        "title": report.title,
        "type": report.report_type.value,
        "content_md": report.content_md,
        "quality_label": report.quality_label,
        "created_at": report.created_at.isoformat(),
        "user_prompt": report.user_prompt,
    }


@app.get("/api/reports/{report_id}/download")
def api_report_download(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404)
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in report.title)[:80]
    content = f"# {report.title}\n\n> 生成时间: {report.created_at.isoformat()}\n\n{report.content_md}"
    if report.user_prompt:
        content = f"# {report.title}\n\n> 用户需求: {report.user_prompt}\n> 生成时间: {report.created_at.isoformat()}\n\n{report.content_md}"
    return Response(
        content=content.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}.md"'},
    )


@app.get("/api/reports/{report_id}")
def api_report_detail(report_id: int, db: Session = Depends(get_db)):
    report = (
        db.query(Report)
        .options(joinedload(Report.article))
        .filter(Report.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404)
    article = report.article
    return {
        "id": report.id,
        "title": report.title,
        "type": report.report_type.value,
        "content_md": report.content_md,
        "quality_label": report.quality_label,
        "created_at": report.created_at.isoformat(),
        "article_url": article.url if article else None,
        "article_title": article.title if article else None,
        "source_name": article.source_name if article else None,
        "user_prompt": report.user_prompt,
    }


@app.get("/api/hotspots")
def api_hotspots(
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
    db: Session = Depends(get_db),
):
    items, total = query_hotspots(
        db,
        hours=hours,
        sort=sort,
        heat_level=heat_level,
        signal_status=signal_status,
        source_id=source_id,
        category=category,
        min_score=min_score,
        min_sources=min_sources,
        only_new=only_new,
        q=q,
        limit=min(limit, 100),
        page=max(page, 1),
    )
    return {"items": items, "total": total, "page": page, "limit": limit}


@app.get("/api/hotspots/summary")
def api_hotspots_summary(hours: int = 24, db: Session = Depends(get_db)):
    return hotspot_summary(db, hours=hours)


@app.get("/api/articles")
def api_articles(
    category: str | None = None,
    min_score: float | None = None,
    sort: str = "score",
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(RawArticle).options(joinedload(RawArticle.signal))
    if category:
        query = query.filter(RawArticle.category == category)
    if min_score is not None:
        query = query.join(SignalScore, RawArticle.id == SignalScore.article_id).filter(
            SignalScore.score >= min_score
        )
    articles = query.limit(min(limit, 200)).all()
    if sort == "score":
        articles.sort(key=lambda a: (a.signal.score if a.signal else 0), reverse=True)
    else:
        articles.sort(key=lambda a: a.fetched_at, reverse=True)
    return [_article_dict(a) for a in articles]


@app.get("/api/articles/{article_id}")
def api_article_detail(article_id: int, db: Session = Depends(get_db)):
    article = (
        db.query(RawArticle)
        .options(joinedload(RawArticle.signal))
        .filter(RawArticle.id == article_id)
        .first()
    )
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    d = _article_dict(article)
    d["content"] = article.content
    d["summary_original"] = article.summary_original
    d["title_original"] = article.title_original
    return d


@app.get("/api/daily-briefings")
def api_daily_briefings(db: Session = Depends(get_db)):
    rows = db.query(DailyBriefing).order_by(DailyBriefing.briefing_date.desc()).limit(30).all()
    return [briefing_to_dict(b, include_items=False) for b in rows]


@app.get("/api/daily-briefings/latest")
def api_daily_briefing_latest(db: Session = Depends(get_db)):
    b = (
        db.query(DailyBriefing)
        .options(joinedload(DailyBriefing.items))
        .order_by(DailyBriefing.briefing_date.desc())
        .first()
    )
    if not b:
        raise HTTPException(status_code=404, detail="暂无晨报")
    return briefing_to_dict(b, include_items=True)


@app.get("/api/daily-briefings/{briefing_id}")
def api_daily_briefing_detail(briefing_id: int, db: Session = Depends(get_db)):
    b = (
        db.query(DailyBriefing)
        .options(joinedload(DailyBriefing.items))
        .filter(DailyBriefing.id == briefing_id)
        .first()
    )
    if not b:
        raise HTTPException(status_code=404)
    return briefing_to_dict(b, include_items=True)


@app.post("/api/daily-briefings/generate")
async def api_generate_daily_briefing(db: Session = Depends(get_db)):
    briefing = await generate_daily_briefing_if_needed(db)
    if not briefing:
        briefing = await generate_daily_briefing(db)
    return briefing_to_dict(briefing, include_items=True)


@app.get("/api/creators/douyin")
def api_douyin_creators():
    return [c.model_dump() for c in load_douyin_creators()]


@app.get("/api/agent-tools")
def api_agent_tools(db: Session = Depends(get_db)):
    tools = db.query(AgentTool).order_by(AgentTool.stars.desc().nullslast()).all()
    return [
        {
            "id": t.id,
            "name": t.name_zh or t.name,
            "name_original": t.name,
            "url": t.url,
            "description": t.description_zh or t.description,
            "stars": t.stars,
            "tool_type": t.tool_type,
            "report_id": t.report_id,
            "article_id": t.article_id,
        }
        for t in tools
    ]


@app.post("/api/localize/backfill")
async def trigger_backfill(background_tasks: BackgroundTasks, limit: int = 20):
    import asyncio

    def _run():
        from app.database import SessionLocal
        session = SessionLocal()
        try:
            asyncio.run(backfill_localization(session, limit=limit))
        finally:
            session.close()

    background_tasks.add_task(_run)
    return {"status": "queued", "message": f"正在后台翻译 {limit} 条资讯为中文"}


@app.post("/api/agent-tools/survey")
async def trigger_agent_survey(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from app.agent.catalog import seed_known_agent_tools
    seeded = seed_known_agent_tools(db)
    tools = db.query(AgentTool).all()
    if not tools:
        return {"status": "error", "message": "Agent 工具数据不足，请先抓取"}

    def _run():
        import asyncio
        from app.database import SessionLocal
        from app.reports.generator import generate_agent_survey_report
        session = SessionLocal()
        try:
            all_tools = session.query(AgentTool).all()
            report = asyncio.run(generate_agent_survey_report(all_tools))
            session.add(report)
            session.commit()
        finally:
            session.close()

    background_tasks.add_task(_run)
    return {"status": "queued", "message": f"正在生成 Agent 全景调研报告（共 {len(tools)} 个工具）", "seeded": seeded}


@app.get("/api/sources")
def api_sources():
    return [s.model_dump() for s in load_sources()]


@app.post("/api/crawl/trigger")
async def trigger_crawl(async_mode: bool = True, db: Session = Depends(get_db)):
    if async_mode:
        from tasks.crawl_tasks import run_crawl_pipeline
        task = run_crawl_pipeline.delay()
        return {"status": "queued", "task_id": task.id}
    result = await run_full_pipeline(db)
    return {"status": "completed", "result": result}
