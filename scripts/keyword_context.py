from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from report_generator.skills import parse_file


def find_context(text: str, keywords: list[str], window: int = 120, limit: int = 20) -> list[dict[str, str]]:
    text = re.sub(r"\s+", " ", text)
    results: list[dict[str, str]] = []
    seen = set()
    for keyword in keywords:
        start = 0
        while True:
            idx = text.find(keyword, start)
            if idx == -1:
                break
            left = max(0, idx - window)
            right = min(len(text), idx + window)
            snippet = text[left:right].strip()
            start = idx + len(keyword)
            normalized = re.sub(r"\s+", " ", snippet)
            if normalized in seen:
                continue
            seen.add(normalized)
            results.append({"keyword": keyword, "snippet": snippet})
            if len(results) >= limit:
                return results
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    parser.add_argument("keywords", nargs="+")
    parser.add_argument("--window", type=int, default=160)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    parsed = parse_file(args.file)
    payload = {
        "file": str(args.file),
        "status": parsed.status,
        "warnings": parsed.warnings,
        "metadata": parsed.metadata,
        "matches": find_context(parsed.text, args.keywords, window=args.window, limit=args.limit),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
