import enum
from datetime import date, datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SignalStatus(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReportType(str, enum.Enum):
    TREND = "trend"
    TOOL = "tool"
    SCENARIO = "scenario"
    AGENT_SURVEY = "agent_survey"
    CUSTOM = "custom"
    DAILY_BRIEFING = "daily_briefing"


class ArticleCategory(str, enum.Enum):
    NEWS = "news"
    AGENT = "agent"
    TOOL = "tool"
    PAPER = "paper"


class RawArticle(Base):
    __tablename__ = "raw_articles"
    __table_args__ = (UniqueConstraint("url", name="uq_raw_articles_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(100), index=True)
    source_name: Mapped[str] = mapped_column(String(200))
    source_weight: Mapped[int] = mapped_column(Integer, default=50)
    title: Mapped[str] = mapped_column(String(500))
    title_zh: Mapped[str | None] = mapped_column(String(500), nullable=True)
    title_original: Mapped[str | None] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(String(1000))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_original: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en")
    category: Mapped[str] = mapped_column(String(50), default=ArticleCategory.NEWS.value, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    external_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    localized: Mapped[bool] = mapped_column(Boolean, default=False)

    signal: Mapped["SignalScore | None"] = relationship(back_populates="article", uselist=False)
    reports: Mapped[list["Report"]] = relationship(back_populates="article")


class SignalScore(Base):
    __tablename__ = "signal_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("raw_articles.id"), unique=True)
    score: Mapped[float] = mapped_column(Float)
    source_component: Mapped[float] = mapped_column(Float)
    cross_validation_component: Mapped[float] = mapped_column(Float)
    entity_density_component: Mapped[float] = mapped_column(Float)
    time_decay_component: Mapped[float] = mapped_column(Float)
    cross_validation_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[SignalStatus] = mapped_column(Enum(SignalStatus))

    article: Mapped["RawArticle"] = relationship(back_populates="signal")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("raw_articles.id"), index=True, nullable=True)
    report_type: Mapped[ReportType] = mapped_column(
        Enum(ReportType, values_callable=lambda x: [e.value for e in x])
    )
    title: Mapped[str] = mapped_column(String(500))
    content_md: Mapped[str] = mapped_column(Text)
    user_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_label: Mapped[str] = mapped_column(String(50), default="AI初稿")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["RawArticle | None"] = relationship(back_populates="reports")


class AgentTool(Base):
    __tablename__ = "agent_tools"
    __table_args__ = (UniqueConstraint("url", name="uq_agent_tools_url"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    name_zh: Mapped[str | None] = mapped_column(String(200), nullable=True)
    url: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tool_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    article_id: Mapped[int | None] = mapped_column(ForeignKey("raw_articles.id"), nullable=True)
    report_id: Mapped[int | None] = mapped_column(ForeignKey("reports.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DailyBriefing(Base):
    __tablename__ = "daily_briefings"
    __table_args__ = (UniqueConstraint("briefing_date", name="uq_daily_briefings_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    briefing_date: Mapped[date] = mapped_column(Date, index=True)
    title: Mapped[str] = mapped_column(String(200))
    overview: Mapped[str] = mapped_column(Text)
    theme_tags: Mapped[str | None] = mapped_column(String(500), nullable=True)
    article_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    items: Mapped[list["DailyBriefingItem"]] = relationship(
        back_populates="briefing", order_by="DailyBriefingItem.sort_order"
    )


class DailyBriefingItem(Base):
    __tablename__ = "daily_briefing_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    briefing_id: Mapped[int] = mapped_column(ForeignKey("daily_briefings.id"), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    item_type: Mapped[str] = mapped_column(String(20), default="article")  # article | creator
    article_id: Mapped[int | None] = mapped_column(ForeignKey("raw_articles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str] = mapped_column(String(1000))
    source_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    signal_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    creator_focus: Mapped[str | None] = mapped_column(String(200), nullable=True)

    briefing: Mapped["DailyBriefing"] = relationship(back_populates="items")


class LlmModelConfig(Base):
    __tablename__ = "llm_model_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    provider: Mapped[str] = mapped_column(String(50))  # deepseek | openai | anthropic | openai_compatible
    model_id: Mapped[str] = mapped_column(String(100))
    base_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    api_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    # 逗号分隔任务标签: report, localize, briefing, custom, agent
    task_tags: Mapped[str] = mapped_column(String(200), default="report,custom,briefing,localize")
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    temperature: Mapped[float] = mapped_column(Float, default=0.3)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AgentCombo(Base):
    __tablename__ = "agent_combos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    workflow_type: Mapped[str] = mapped_column(String(50), default="sequential")  # sequential | parallel | router
    llm_model_id: Mapped[int | None] = mapped_column(ForeignKey("llm_model_configs.id"), nullable=True)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    llm_model: Mapped["LlmModelConfig | None"] = relationship()
    members: Mapped[list["AgentComboMember"]] = relationship(
        back_populates="combo", order_by="AgentComboMember.sort_order", cascade="all, delete-orphan"
    )


class AgentComboMember(Base):
    __tablename__ = "agent_combo_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    combo_id: Mapped[int] = mapped_column(ForeignKey("agent_combos.id"), index=True)
    agent_tool_id: Mapped[int | None] = mapped_column(ForeignKey("agent_tools.id"), nullable=True)
    role_name: Mapped[str] = mapped_column(String(100))
    role_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    combo: Mapped["AgentCombo"] = relationship(back_populates="members")
    agent_tool: Mapped["AgentTool | None"] = relationship()
