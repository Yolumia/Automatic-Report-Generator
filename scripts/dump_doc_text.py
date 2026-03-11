from __future__ import annotations

import argparse
from pathlib import Path

from report_generator.skills import parse_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    parsed = parse_file(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(parsed.text, encoding="utf-8")
    print(args.output)
