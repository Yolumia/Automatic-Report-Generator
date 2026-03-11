from __future__ import annotations

import json
from pathlib import Path

from report_generator.config import AppConfig
from report_generator.evidence import build_evidence_snippets
from report_generator.pipeline import run_pipeline
from report_generator.skills import parse_text_file


def test_parse_text_file_reads_utf8(tmp_path: Path) -> None:
    file_path = tmp_path / "notes.txt"
    file_path.write_text("第一行\n第二行", encoding="utf-8")

    result = parse_text_file(file_path)

    assert result.status == "ok"
    assert "第一行" in result.text
    assert result.metadata["encoding"] == "utf-8"


def test_build_evidence_snippets_returns_content() -> None:
    document = parse_text_file(Path(__file__))
    snippets = build_evidence_snippets([document], max_snippets_per_doc=2, snippet_length=50)

    assert snippets
    assert len(snippets) <= 2


def test_run_pipeline_generates_outputs(tmp_path: Path) -> None:
    base_dir = tmp_path
    sources_dir = base_dir / "data" / "sources"
    prompts_dir = base_dir / "prompts"
    docs_dir = base_dir / "docs"
    output_dir = base_dir / "outputs"

    sources_dir.mkdir(parents=True)
    (prompts_dir / "system").mkdir(parents=True)
    (prompts_dir / "tasks").mkdir(parents=True)
    (prompts_dir / "checklists").mkdir(parents=True)
    docs_dir.mkdir(parents=True)

    (sources_dir / "input.txt").write_text("可作为依据的内容\n第二段", encoding="utf-8")
    (prompts_dir / "system" / "report_system_prompt.md").write_text("system", encoding="utf-8")
    (prompts_dir / "tasks" / "report_generation_prompt.md").write_text("task", encoding="utf-8")
    (prompts_dir / "checklists" / "quality_checklist.md").write_text("check", encoding="utf-8")
    (docs_dir / "skills_reference.md").write_text("skills", encoding="utf-8")
    (docs_dir / "process_guide.md").write_text("guide", encoding="utf-8")

    config = AppConfig.from_base_dir(base_dir=base_dir, sources_dir=sources_dir, output_dir=output_dir)
    artifacts = run_pipeline(topic="测试主题", config=config)

    assert len(artifacts.extracted_documents) == 1
    assert (output_dir / "evidence.json").exists()
    assert (output_dir / "report.md").exists()
    assert (output_dir / "ai_prompt_package.md").exists()

    payload = json.loads((output_dir / "evidence.json").read_text(encoding="utf-8"))
    assert payload["topic"] == "测试主题"
    assert payload["documents"][0]["file_name"] == "input.txt"
