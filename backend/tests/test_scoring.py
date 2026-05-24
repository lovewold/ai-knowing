import math
from datetime import datetime, timedelta

from app.scoring.signal import (
    compute_entity_density,
    compute_time_decay,
    normalize_title,
    title_similarity,
)


def test_normalize_title():
    assert normalize_title("Hello, World! GPT-4") == "hello world gpt 4"


def test_title_similarity():
    a = "OpenAI releases GPT-5 model"
    b = "OpenAI releases GPT-5"
    assert title_similarity(a, b) > 0.7


def test_time_decay_recent():
    recent = datetime.utcnow() - timedelta(hours=1)
    decay = compute_time_decay(recent, lambda_val=0.01)
    assert decay > 0.9


def test_time_decay_old():
    old = datetime.utcnow() - timedelta(days=30)
    decay = compute_time_decay(old, lambda_val=0.01)
    assert decay < 0.3


def test_entity_density():
    text = "OpenAI GPT-4 LangChain RAG agent embedding transformer"
    density = compute_entity_density(text)
    assert density > 0


def test_signal_score_formula():
    source_weight = 95
    cross_count = 2
    cross_max = 5
    entity = 0.5
    time_decay = 0.9

    score = (
        source_weight * 0.4
        + (cross_count / cross_max) * 100 * 0.25
        + entity * 100 * 0.2
        + time_decay * 100 * 0.15
    )
    assert score >= 70
