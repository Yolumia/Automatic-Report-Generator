from __future__ import annotations

from pathlib import Path

from report_generator.config import SUPPORTED_EXTENSIONS


def scan_source_files(sources_dir: Path) -> list[Path]:
    if not sources_dir.exists():
        return []

    files = [
        path for path in sources_dir.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files, key=lambda item: str(item).lower())
