import math
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models import RawArticle, SignalScore, SignalStatus
from app.yaml_config import ScoringConfig, load_scoring_config

AI_ENTITIES = {
    "gpt", "claude", "gemini", "llama", "deepseek", "qwen", "mistral",
    "openai", "anthropic", "google", "meta", "huggingface",
    "langchain", "llamaindex", "rag", "agent", "transformer", "embedding",
    "fine-tuning", "lora", "vllm", "ollama", "mcp", "dify", "coze",
    "pytorch", "tensorflow", "cuda", "gpu", "inference", "multimodal",
    "ai", "llm", "machine learning", "deep learning", "nlp",
}


def normalize_title(title: str) -> str:
    title = title.lower()
    title = re.sub(r"[^\w\s]", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def title_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def compute_time_decay(published_at: datetime | None, lambda_val: float = 0.01) -> float:
    if not published_at:
        return 0.5
    hours = max(0, (datetime.utcnow() - published_at).total_seconds() / 3600)
    return math.exp(-lambda_val * hours)


def compute_entity_density(text: str) -> float:
    if not text:
        return 0.0
    lower = text.lower()
    words = set(re.findall(r"[a-zA-Z0-9\-]+", lower))
    matches = sum(1 for e in AI_ENTITIES if e in words or e in lower)
    normalized_len = max(len(text) / 500, 1)
    return min(matches / normalized_len, 1.0)


def count_cross_validation(
    db: Session,
    title: str,
    source_id: str,
    window_hours: int = 72,
    max_sources: int = 5,
) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)
    recent = (
        db.query(RawArticle)
        .filter(RawArticle.fetched_at >= cutoff)
        .filter(RawArticle.source_id != source_id)
        .all()
    )
    count = 0
    seen_sources: set[str] = set()
    for article in recent:
        if title_similarity(title, article.title) >= 0.6:
            if article.source_id not in seen_sources:
                seen_sources.add(article.source_id)
                count += 1
    return min(count, max_sources)


def compute_score_points(
    source_weight: int,
    cross_count: int,
    cross_max: int,
    entity: float,
    time_decay: float,
    config: ScoringConfig | None = None,
) -> tuple[float, float, float, float, float]:
    """Return (total_0_100, source_pts, cross_pts, entity_pts, time_pts)."""
    config = config or load_scoring_config()
    w = config.weights
    source_pts = source_weight * w.source
    cross_pts = (cross_count / cross_max) * 100 * w.cross_validation
    entity_pts = entity * 100 * w.entity_density
    time_pts = time_decay * 100 * w.time_decay
    total = min(source_pts + cross_pts + entity_pts + time_pts, 100.0)
    return total, source_pts, cross_pts, entity_pts, time_pts


def estimate_preliminary_score(article: RawArticle, config: ScoringConfig | None = None) -> float:
    """Quality gate before save (no cross-validation yet)."""
    config = config or load_scoring_config()
    lambda_val = config.time_decay.get("lambda", 0.01)
    text = f"{article.title} {article.summary or ''}"
    entity = compute_entity_density(text)
    time_c = compute_time_decay(article.published_at, lambda_val)
    total, _, _, _, _ = compute_score_points(
        article.source_weight, 0, 1, entity, time_c, config
    )
    return total


def passes_quality_gate(article: RawArticle, config: ScoringConfig | None = None) -> bool:
    config = config or load_scoring_config()
    gate = config.quality_gate
    title = article.title or ""
    if len(title.strip()) < gate.min_title_length:
        return False
    text = f"{title} {article.summary or ''}"
    if compute_entity_density(text) < gate.min_entity_density:
        return False
    if estimate_preliminary_score(article, config) < gate.min_save_score:
        return False
    return True


def is_duplicate_title(
    db: Session,
    title: str,
    threshold: float = 0.85,
    window_hours: int = 48,
) -> bool:
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)
    recent = db.query(RawArticle.title, RawArticle.title_zh).filter(RawArticle.fetched_at >= cutoff).all()
    for existing_title, existing_zh in recent:
        for t in (existing_title, existing_zh):
            if t and title_similarity(title, t) >= threshold:
                return True
    return False


def compute_signal_score(
    db: Session,
    article: RawArticle,
    config: ScoringConfig | None = None,
) -> SignalScore:
    config = config or load_scoring_config()
    lambda_val = config.time_decay.get("lambda", 0.01)
    cv_window = config.cross_validation.get("window_hours", 72)
    cv_max = config.cross_validation.get("max_sources", 5)

    cross_count = count_cross_validation(db, article.title, article.source_id, cv_window, cv_max)
    text = f"{article.title} {article.summary or ''} {article.content or ''}"
    entity = compute_entity_density(text)
    time_c = compute_time_decay(article.published_at, lambda_val)

    total, source_pts, cross_pts, entity_pts, time_pts = compute_score_points(
        article.source_weight, cross_count, cv_max, entity, time_c, config
    )

    if total >= config.thresholds.high:
        status = SignalStatus.HIGH
    elif total >= config.thresholds.medium:
        status = SignalStatus.MEDIUM
    else:
        status = SignalStatus.LOW

    return SignalScore(
        article_id=article.id,
        score=round(total, 1),
        source_component=round(source_pts, 2),
        cross_validation_component=round(cross_pts, 2),
        entity_density_component=round(entity_pts, 2),
        time_decay_component=round(time_pts, 2),
        cross_validation_count=cross_count,
        status=status,
    )


def upsert_signal_score(db: Session, article: RawArticle, config: ScoringConfig | None = None) -> SignalScore:
    existing = db.query(SignalScore).filter(SignalScore.article_id == article.id).first()
    signal = compute_signal_score(db, article, config)
    if existing:
        existing.score = signal.score
        existing.source_component = signal.source_component
        existing.cross_validation_component = signal.cross_validation_component
        existing.entity_density_component = signal.entity_density_component
        existing.time_decay_component = signal.time_decay_component
        existing.cross_validation_count = signal.cross_validation_count
        existing.status = signal.status
        return existing
    db.add(signal)
    return signal


def rescore_recent_articles(db: Session, window_hours: int = 72) -> int:
    """Recalculate scores (cross-validation changes as new articles arrive)."""
    cutoff = datetime.utcnow() - timedelta(hours=window_hours)
    articles = db.query(RawArticle).filter(RawArticle.fetched_at >= cutoff).all()
    for article in articles:
        upsert_signal_score(db, article)
    db.commit()
    return len(articles)


def classify_report_type(article: RawArticle) -> str:
    if article.category == "agent":
        return "agent"
    text = f"{article.title} {article.summary or ''}".lower()
    tool_keywords = ["github.com", "trending", "release", "tool", "framework", "library", "open source", "repo"]
    if any(kw in text for kw in tool_keywords) or "github" in article.url:
        return "tool"
    if article.source_id.startswith("arxiv"):
        return "trend"
    product_keywords = ["launch", "product", "api", "pricing", "startup"]
    if any(kw in text for kw in product_keywords):
        return "tool"
    return "trend"
