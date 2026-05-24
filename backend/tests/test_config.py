from app.yaml_config import SourceConfig, load_sources


def test_source_config_model():
    source = SourceConfig(
        id="test-rss",
        name="Test RSS",
        type="rss",
        url="https://example.com/feed",
        weight=50,
    )
    assert source.enabled is True
    assert source.type == "rss"


def test_load_sources_has_entries():
    sources = load_sources()
    assert len(sources) >= 5
    types = {s.type for s in sources}
    assert "rss" in types
    assert "arxiv" in types
