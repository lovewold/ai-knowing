import os
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SourceConfig(BaseModel):
    id: str
    name: str
    type: str
    weight: int = 50
    language: str = "en"
    enabled: bool = True
    url: str | None = None
    category: str | None = None
    filter: str | None = None
    query: str | None = None


class ScoringWeights(BaseModel):
    source: float = 0.4
    cross_validation: float = 0.25
    entity_density: float = 0.2
    time_decay: float = 0.15


class ScoringThresholds(BaseModel):
    high: float = 70.0
    medium: float = 45.0


class QualityGate(BaseModel):
    min_entity_density: float = 0.06
    min_title_length: int = 10
    min_save_score: float = 32.0


class ScoringConfig(BaseModel):
    weights: ScoringWeights = Field(default_factory=ScoringWeights)
    thresholds: ScoringThresholds = Field(default_factory=ScoringThresholds)
    quality_gate: QualityGate = Field(default_factory=QualityGate)
    time_decay: dict = Field(default_factory=lambda: {"lambda": 0.01})
    cross_validation: dict = Field(default_factory=lambda: {"window_hours": 72, "max_sources": 5})
    dedup: dict = Field(default_factory=lambda: {"title_similarity_threshold": 0.85, "window_hours": 48})


def get_config_dir() -> Path:
    return Path(os.environ.get("CONFIG_DIR", "../config"))


def load_sources() -> list[SourceConfig]:
    path = get_config_dir() / "sources.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [SourceConfig(**s) for s in data.get("sources", []) if s.get("enabled", True)]


def load_all_sources() -> list[SourceConfig]:
    path = get_config_dir() / "sources.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [SourceConfig(**s) for s in data.get("sources", [])]


def load_scoring_config() -> ScoringConfig:
    path = get_config_dir() / "scoring.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return ScoringConfig(**data)


class DailyBriefingConfig(BaseModel):
    window_hours: int = 24
    max_articles: int = 12
    min_score: float = 68.0
    include_high_signal: bool = True
    include_medium_zh: bool = True
    medium_zh_min_score: float = 52.0
    prefer_localized: bool = True
    overview_max_tokens: int = 280


class DouyinCreator(BaseModel):
    name: str
    profile_url: str
    focus: str
    reason: str


def load_daily_briefing_config() -> DailyBriefingConfig:
    path = get_config_dir() / "daily_briefing.yaml"
    if not path.exists():
        return DailyBriefingConfig()
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return DailyBriefingConfig(**data)


def load_douyin_creators() -> list[DouyinCreator]:
    path = get_config_dir() / "douyin_creators.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [DouyinCreator(**c) for c in data.get("creators", [])]


def save_sources_yaml(sources: list[dict]) -> None:
    path = get_config_dir() / "sources.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump({"sources": sources}, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def save_douyin_creators_yaml(creators: list[dict]) -> None:
    path = get_config_dir() / "douyin_creators.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump({"creators": creators}, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def save_daily_briefing_yaml(config: dict) -> None:
    path = get_config_dir() / "daily_briefing.yaml"
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def load_daily_briefing_yaml() -> dict:
    path = get_config_dir() / "daily_briefing.yaml"
    if not path.exists():
        return DailyBriefingConfig().model_dump()
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}
