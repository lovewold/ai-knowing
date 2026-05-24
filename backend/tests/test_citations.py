"""Tests for citation helpers."""
from app.reports.citations import Citation, citations_from_json, citations_to_json, clean_report_content, ensure_references_in_content


def test_citations_roundtrip():
    items = [
        Citation(id=1, title="A", url="https://a.com", snippet="s", source_type="web"),
        Citation(id=2, title="B", url="https://b.com", snippet="t", source_type="article", article_id=9),
    ]
    raw = citations_to_json(items)
    restored = citations_from_json(raw)
    assert len(restored) == 2
    assert restored[1].article_id == 9


def test_clean_report_content():
    content = "# Title\n\nBody with claim [1] and [2-3].\n\n## 参考来源\n\n[1] foo"
    out = clean_report_content(content)
    assert "[1]" not in out
    assert "参考来源" not in out
    assert "Body with claim" in out


def test_ensure_references_strips_only():
    content = "# T\n\nText [1]."
    out = ensure_references_in_content(content, [])
    assert "[1]" not in out
