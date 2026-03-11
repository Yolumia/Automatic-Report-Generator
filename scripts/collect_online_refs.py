from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from report_generator.skills import fetch_web_page, search_web

BASE_DIR = Path(r"E:\Personal Project\自动报告生成器")
OUTPUT_DIR = BASE_DIR / "data" / "sources" / "网络在线参考资料"

QUERIES = [
    "江苏 生态产品 价值实现",
    "江苏省 生态产品 价值实现 机制",
    "江苏 GEP 核算 生态产品",
    "江苏 自然资源 生态产品 典型案例",
    "江苏 林业碳汇 水权 生态产品",
    "江苏 生态产品 价值实现 平台",
]

KEYWORDS = [
    "江苏", "生态产品", "价值实现", "机制", "平台", "GEP", "林业碳汇", "水权", "典型案例", "自然资源"
]
TRUSTED_HINTS = [
    "gov.cn", "jiangsu.gov.cn", "js.gov.cn", "nr.gov.cn", "ndrc.gov.cn", "mee.gov.cn", "mnr.gov.cn", "news.cn"
]
MAX_ITEMS = 12
EXCLUDED_HINTS = ["百度资讯", "百度百科", "网络不给力", "贴吧", "论坛", "博客"]


def score_result(item: dict[str, Any], page: dict[str, Any]) -> int:
    text = " ".join(
        [
            item.get("title", ""),
            item.get("url", ""),
            page.get("title", ""),
            page.get("text", "")[:1500],
        ]
    )
    score = sum(3 for kw in KEYWORDS if kw in text)
    url = item.get("url", "")
    if any(domain in url for domain in TRUSTED_HINTS):
        score += 6
    if "江苏" in text and "生态产品" in text:
        score += 5
    if "价值实现" in text or "GEP" in text:
        score += 4
    return score


def compact(text: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit] + ("..." if len(text) > limit else "")


def choose_relevance_reason(item: dict[str, Any], page: dict[str, Any]) -> str:
    text = " ".join([item.get("title", ""), page.get("title", ""), page.get("text", "")[:1200]])
    reasons = []
    if "江苏" in text:
        reasons.append("直接涉及江苏")
    if "生态产品" in text and "价值实现" in text:
        reasons.append("直接涉及生态产品价值实现")
    if "平台" in text:
        reasons.append("涉及平台建设或平台化机制")
    if "林业碳汇" in text or "水权" in text:
        reasons.append("涉及林业碳汇/水权等关键交易品种")
    if "GEP" in text:
        reasons.append("涉及 GEP 核算或价值评估")
    return "；".join(reasons[:3]) or "与报告主题存在直接关联"


def looks_garbled(text: str) -> bool:
    bad_tokens = ["ÖÐ", "×", "ç¾", "å", "ï¼"]
    return any(token in text for token in bad_tokens)


def is_reliable_enough(item: dict[str, Any], page: dict[str, Any]) -> bool:
    title = item.get("title", "") + page.get("title", "")
    text = page.get("text", "")[:2000]
    url = item.get("url", "")
    if any(hint in title or hint in text for hint in EXCLUDED_HINTS):
        return False
    if looks_garbled(title) or looks_garbled(text):
        return False
    if len(text.strip()) < 120:
        return False
    if "江苏" not in (title + text):
        return False
    if "生态产品" not in (title + text) and "GEP" not in (title + text):
        return False
    if any(domain in url for domain in TRUSTED_HINTS):
        return True
    return "发布时间" in text or "来源" in text or "发布日期" in text


def main() -> None:
    if os.getenv("REPORT_GENERATOR_ENABLE_WEB") != "1":
        raise SystemExit("请先设置 REPORT_GENERATOR_ENABLE_WEB=1")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    collected: list[tuple[int, dict[str, Any], dict[str, Any], str]] = []
    seen_urls: set[str] = set()

    for query in QUERIES:
        search_result = search_web(query, limit=8)
        if search_result.get("status") != "ok":
            continue
        for item in search_result.get("results", []):
            url = item.get("url", "")
            if not url or url in seen_urls:
                continue
            page = fetch_web_page(url)
            if page.get("status") != "ok":
                continue
            score = score_result(item, page)
            if score < 12:
                continue
            if not is_reliable_enough(item, page):
                continue
            seen_urls.add(url)
            collected.append((score, item, page, query))

    collected.sort(key=lambda x: x[0], reverse=True)
    selected = collected[:MAX_ITEMS]

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# 网络在线参考资料（自动筛选）",
        "",
        f"- 生成时间：{generated_at}",
        f"- 检索范围：{', '.join(QUERIES)}",
        f"- 收录数量：{len(selected)}",
        "- 说明：本文件基于联网搜索与网页正文抓取自动整理，仅保留与“江苏生态产品价值实现”高度相关、正文可读且具备进一步核验条件的公开资料；正式写入报告前，仍需回到权威原始来源二次核验。",
        "",
    ]

    for index, (score, item, page, query) in enumerate(selected, start=1):
        lines.extend(
            [
                f"## {index}. {item.get('title', '').strip() or page.get('title', '').strip() or '未命名页面'}",
                "",
                f"- 检索词：`{query}`",
                f"- 链接：{item.get('url', '')}",
                f"- 来源页：{item.get('source', '')}",
                f"- 相关性：{choose_relevance_reason(item, page)}",
                f"- 摘要：{compact(page.get('text', '') or item.get('snippet', ''))}",
                f"- 评分：{score}",
                "- 核验提示：优先核对发文机关、发布日期、正文原文及附件；如为转载页，应继续追溯至原始官网页面。",
                "",
            ]
        )

    output_file = OUTPUT_DIR / "网络在线参考资料.md"
    output_file.write_text("\n".join(lines), encoding="utf-8")
    print(output_file)


if __name__ == "__main__":
    main()
