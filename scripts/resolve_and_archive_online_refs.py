from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from report_generator.skills import DEFAULT_USER_AGENT, _extract_web_page_text

BASE_DIR = Path(r"E:\Personal Project\自动报告生成器")
REF_DIR = BASE_DIR / "data" / "sources" / "网络在线参考资料"
INDEX_FILE = REF_DIR / "网络在线参考资料.md"
TIMEOUT = 20


@dataclass
class RefItem:
    heading: str
    lines: list[str]


def slugify_filename(text: str, limit: int = 50) -> str:
    text = re.sub(r"[\\/:*?\"<>|]", "_", text)
    text = re.sub(r"\s+", "_", text).strip("._ ")
    return text[:limit] or "untitled"


def read_sections(content: str) -> tuple[list[str], list[RefItem]]:
    pattern = re.compile(r"(^##\s+.+?)(?=^##\s+|\Z)", re.MULTILINE | re.DOTALL)
    matches = list(pattern.finditer(content))
    header = content[: matches[0].start()].strip().splitlines() if matches else content.splitlines()
    items: list[RefItem] = []
    for match in matches:
        block = match.group(1).strip().splitlines()
        heading = block[0][3:].strip()
        items.append(RefItem(heading=heading, lines=block))
    return header, items


def get_field(lines: list[str], prefix: str) -> str:
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return ""


def replace_or_append(lines: list[str], prefix: str, value: str, *, after_prefix: str | None = None) -> list[str]:
    updated = []
    replaced = False
    for line in lines:
        if line.startswith(prefix):
            updated.append(f"{prefix}{value}")
            replaced = True
        else:
            updated.append(line)
    if replaced:
        return updated
    if after_prefix:
        result = []
        inserted = False
        for line in updated:
            result.append(line)
            if (not inserted) and line.startswith(after_prefix):
                result.append(f"{prefix}{value}")
                inserted = True
        if inserted:
            return result
    updated.append(f"{prefix}{value}")
    return updated


def resolve_baidu_url(url: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    try:
        response = requests.get(
            url,
            timeout=TIMEOUT,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            allow_redirects=True,
        )
        final_url = response.url
        if final_url and "baidu.com" not in urlparse(final_url).netloc:
            return final_url, warnings

        html = response.text
        meta_match = re.search(r'url=(https?://[^\"\'> ]+)', html, re.IGNORECASE)
        if meta_match:
            final_url = meta_match.group(1)
            return final_url, warnings

        href_match = re.search(r'(https?://[^\"\'> ]+)', html)
        if href_match and "baidu.com" not in urlparse(href_match.group(1)).netloc:
            return href_match.group(1), warnings

        warnings.append("未能从百度跳转页解析出原始链接")
        return url, warnings
    except requests.RequestException as exc:
        warnings.append(f"解析跳转链接失败: {exc}")
        return url, warnings


def fetch_page(url: str) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    try:
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": DEFAULT_USER_AGENT})
        response.raise_for_status()
    except requests.RequestException as exc:
        return "", "", [f"抓取网页失败: {exc}"]

    response.encoding = response.apparent_encoding or response.encoding
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""

    candidates = []
    for selector in ["article", "main", ".article", ".content", ".article-content", ".detail-content", "#content"]:
        node = soup.select_one(selector)
        if node:
            text = _extract_web_page_text(str(node))
            if len(text) > 120:
                candidates.append(text)
                break

    text = candidates[0] if candidates else _extract_web_page_text(html)
    if len(text) < 120:
        warnings.append("正文内容较短，可能存在反爬、跳转页或正文抽取失败")
    return title, text, warnings


def archive_item(index: int, title: str, resolved_url: str, text: str, warnings: list[str]) -> str:
    domain = urlparse(resolved_url).netloc or "unknown"
    safe_title = slugify_filename(title or f"ref_{index:02d}")
    file_name = f"{index:02d}_{slugify_filename(domain, 30)}_{safe_title}.md"
    output_file = REF_DIR / file_name
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = [
        f"# {title or f'参考资料 {index}'}",
        "",
        f"- 原始链接：{resolved_url}",
        f"- 抓取时间：{generated_at}",
        f"- 来源域名：{domain}",
        f"- 状态：{'ok' if text else 'error'}",
    ]
    if warnings:
        content.append(f"- 告警：{'；'.join(warnings)}")
    content.extend(["", "## 网页正文", "", text or "（抓取失败或正文为空）", ""])
    output_file.write_text("\n".join(content), encoding="utf-8")
    return file_name


def main() -> None:
    original = INDEX_FILE.read_text(encoding="utf-8")
    header, items = read_sections(original)
    new_parts = ["\n".join(header)]

    for index, item in enumerate(items, start=1):
        lines = item.lines[:]
        baidu_url = get_field(lines, "- 链接：")
        resolved_url, resolve_warnings = resolve_baidu_url(baidu_url)
        title, text, fetch_warnings = fetch_page(resolved_url)
        warnings = resolve_warnings + fetch_warnings
        local_file = archive_item(index, item.heading.split(". ", 1)[-1], resolved_url, text, warnings)

        lines = replace_or_append(lines, "- 原始链接：", resolved_url, after_prefix="- 链接：")
        lines = replace_or_append(lines, "- 本地归档：", f"`{local_file}`", after_prefix="- 原始链接：")
        lines = replace_or_append(lines, "- 抓取状态：", "成功" if text else "失败", after_prefix="- 本地归档：")
        if warnings:
            lines = replace_or_append(lines, "- 归档告警：", "；".join(warnings), after_prefix="- 抓取状态：")
        new_parts.append("\n".join(lines))

    resolved_file = REF_DIR / "网络在线参考资料_已解析.md"
    resolved_file.write_text("\n\n".join(new_parts) + "\n", encoding="utf-8")
    INDEX_FILE.write_text("\n\n".join(new_parts) + "\n", encoding="utf-8")
    print(resolved_file)


if __name__ == "__main__":
    main()
