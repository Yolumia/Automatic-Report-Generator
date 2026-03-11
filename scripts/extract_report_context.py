from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Iterable

from report_generator.skills import parse_file

BASE = Path(r"E:\Personal Project\自动报告生成器")
TARGETS = [
    BASE / "data" / "sources" / "江苏省生态产品价值实现平台建设可行性研究报告详细大纲.docx",
    BASE / "data" / "sources" / "生态产品价值实现" / "总结.docx",
    BASE / "data" / "sources" / "生态产品价值实现" / "姜-江苏省产权交易所生态资源产品平台建设调研方案.docx",
    BASE / "data" / "sources" / "生态产品价值实现" / "马-江苏省产权交易所关于生态产品价值实现平台建设专题调研方案.docx",
    BASE / "data" / "sources" / "生态产品价值实现" / "政策文件" / "整理.xlsx",
    BASE / "data" / "sources" / "生态产品价值实现" / "经典案例" / "18 江苏省自然资源领域生态产品价值实现典型案例（第一批）.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "经典案例" / "19 江苏省自然资源领域生态产品价值实现典型案例（第二批）.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "经典案例" / "23 自然资源部《生态产品价值实现典型案例》（第四批）.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "经典案例" / "24 自然资源部《生态产品价值实现典型案例》（第五批）.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "适用政策文件" / "8 江苏印发《江苏省建立健全生态产品价值实现机制实施方案》_中共江苏省委新闻网.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "适用政策文件" / "1 中共中央办公厅 国务院办公厅印发《关于建立健全生态产品价值实现机制的意见》.pdf",
    BASE / "data" / "sources" / "生态产品价值实现" / "适用政策文件" / "3 加快完善生态产品价值实现机制 拓宽绿水青山转化金山银山路径-国家发展和改革委员会.pdf",
]

KEYWORDS = [
    "江苏", "生态产品", "平台", "交易", "成交", "案例", "GEP", "碳汇", "水权", "运营", "收益", "机制", "确权", "金融", "丽水", "抚州", "南平", "福建", "浙江", "福建"
]

number_pattern = re.compile(r"(?:\d+[\d,.]*\s*(?:万元|亿元|元|宗|笔|个|亩|吨|年|%))")


def score_line(line: str) -> int:
    return sum(1 for keyword in KEYWORDS if keyword in line)


def pick_lines(text: str, limit: int = 20) -> list[str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    ranked = sorted(lines, key=lambda item: (score_line(item), len(number_pattern.findall(item))), reverse=True)
    selected: list[str] = []
    seen = set()
    for line in ranked:
        if score_line(line) == 0 and not number_pattern.search(line):
            continue
        normalized = re.sub(r"\s+", " ", line)
        if normalized in seen:
            continue
        seen.add(normalized)
        selected.append(line)
        if len(selected) >= limit:
            break
    return selected


def extract() -> list[dict]:
    payload = []
    for path in TARGETS:
        if not path.exists():
            payload.append({"file": str(path), "status": "missing"})
            continue
        parsed = parse_file(path)
        payload.append(
            {
                "file": str(path),
                "status": parsed.status,
                "warnings": parsed.warnings,
                "metadata": parsed.metadata,
                "selected_lines": pick_lines(parsed.text),
            }
        )
    return payload


if __name__ == "__main__":
    out = BASE / "outputs" / "report_context.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(extract(), ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)
