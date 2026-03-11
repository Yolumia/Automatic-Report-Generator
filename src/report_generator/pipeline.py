from __future__ import annotations

import json
from pathlib import Path

from report_generator.config import AppConfig
from report_generator.evidence import build_evidence_snippets
from report_generator.ingest import scan_source_files
from report_generator.models import ReportArtifacts
from report_generator.prompting import render_ai_prompt_package, render_report_markdown
from report_generator.skills import parse_file


def ensure_directories(config: AppConfig) -> None:
    config.sources_dir.mkdir(parents=True, exist_ok=True)
    config.processed_dir.mkdir(parents=True, exist_ok=True)
    config.output_dir.mkdir(parents=True, exist_ok=True)


def run_pipeline(topic: str, config: AppConfig) -> ReportArtifacts:
    ensure_directories(config)
    source_files = scan_source_files(config.sources_dir)
    extracted_documents = [parse_file(path) for path in source_files]
    evidence_snippets = build_evidence_snippets(extracted_documents)

    report_markdown = render_report_markdown(topic, evidence_snippets, extracted_documents)
    ai_prompt_package = render_ai_prompt_package(
        topic=topic,
        prompts_dir=config.prompts_dir,
        docs_dir=config.docs_dir,
        extracted_documents=extracted_documents,
        evidence_snippets=evidence_snippets,
    )

    evidence_payload = {
        "topic": topic,
        "sources_dir": str(config.sources_dir),
        "documents": [item.to_dict() for item in extracted_documents],
        "evidence_snippets": [item.to_dict() for item in evidence_snippets],
    }

    (config.output_dir / "evidence.json").write_text(
        json.dumps(evidence_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (config.output_dir / "report.md").write_text(report_markdown, encoding="utf-8")
    (config.output_dir / "ai_prompt_package.md").write_text(ai_prompt_package, encoding="utf-8")

    return ReportArtifacts(
        topic=topic,
        sources_dir=config.sources_dir,
        output_dir=config.output_dir,
        extracted_documents=extracted_documents,
        evidence_snippets=evidence_snippets,
        report_markdown=report_markdown,
        ai_prompt_package=ai_prompt_package,
    )


def project_root_from_file(current_file: Path) -> Path:
    return current_file.resolve().parents[2]
