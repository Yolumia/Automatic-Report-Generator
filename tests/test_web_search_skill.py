from __future__ import annotations

from report_generator.skills import fetch_web_page, search_web


def test_search_web_returns_disabled_without_config(monkeypatch) -> None:
    monkeypatch.delenv("REPORT_GENERATOR_ENABLE_WEB", raising=False)
    monkeypatch.delenv("REPORT_GENERATOR_WEB_SEARCH_API", raising=False)
    monkeypatch.delenv("REPORT_GENERATOR_WEB_SEARCH_API_KEY", raising=False)

    result = search_web("江苏 生态产品 价值实现")

    assert result["status"] == "disabled"
    assert result["results"] == []
    assert result["warnings"]


def test_fetch_web_page_returns_disabled_without_config(monkeypatch) -> None:
    monkeypatch.delenv("REPORT_GENERATOR_ENABLE_WEB", raising=False)

    result = fetch_web_page("https://example.com")

    assert result["status"] == "disabled"
    assert result["text"] == ""
    assert result["warnings"]
