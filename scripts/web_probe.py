from __future__ import annotations

from report_generator.skills import fetch_web_page, search_web


if __name__ == "__main__":
    result = search_web("江苏 生态产品 价值实现")
    print(result)
    if result.get("status") == "ok" and result.get("results"):
        page = fetch_web_page(result["results"][0]["url"])
        print(page.get("title", ""))
        print(page.get("text", "")[:500])
