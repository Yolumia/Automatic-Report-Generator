from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class ExtractedDocument:
    source_path: str
    file_name: str
    extension: str
    parser_name: str
    status: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    error_code: str | None = None
    error_message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class EvidenceSnippet:
    source_path: str
    file_name: str
    parser_name: str
    snippet: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class ReportArtifacts:
    topic: str
    sources_dir: Path
    output_dir: Path
    extracted_documents: list[ExtractedDocument]
    evidence_snippets: list[EvidenceSnippet]
    report_markdown: str
    ai_prompt_package: str
