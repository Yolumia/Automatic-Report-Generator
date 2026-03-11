from __future__ import annotations

from pathlib import Path

from report_generator.models import EvidenceSnippet, ExtractedDocument


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def render_ai_prompt_package(
    topic: str,
    prompts_dir: Path,
    docs_dir: Path,
    extracted_documents: list[ExtractedDocument],
    evidence_snippets: list[EvidenceSnippet],
) -> str:
    system_prompt = load_text(prompts_dir / "system" / "report_system_prompt.md")
    report_prompt = load_text(prompts_dir / "tasks" / "report_generation_prompt.md")
    checklist_prompt = load_text(prompts_dir / "checklists" / "quality_checklist.md")
    skills_reference = load_text(docs_dir / "skills_reference.md")

    document_lines = []
    for doc in extracted_documents:
        line = (
            f"- 文件: {doc.file_name} | 状态: {doc.status} | 解析器: {doc.parser_name}"
            f" | 字数: {len(doc.text)} | 警告: {', '.join(doc.warnings) if doc.warnings else '无'}"
        )
        document_lines.append(line)

    evidence_lines = []
    for index, snippet in enumerate(evidence_snippets, start=1):
        evidence_lines.append(
            f"{index}. [{snippet.file_name}] {snippet.snippet}"
        )

    process_guide = load_text(docs_dir / "process_guide.md")

    return "\n\n".join(
        [
            f"# AI 报告生成提示词包\n\n主题：{topic}",
            "## 一、System Prompt\n" + system_prompt,
            "## 二、任务提示词\n" + report_prompt,
            "## 三、质量检查清单\n" + checklist_prompt,
            "## 四、可用 Skills\n" + skills_reference,
            "## 五、资料清单\n" + ("\n".join(document_lines) or "- 当前未发现可解析资料"),
            "## 六、证据摘录\n" + ("\n".join(evidence_lines) or "暂无可用证据摘录"),
            "## 七、执行流程指导\n" + process_guide,
        ]
    )


def render_report_markdown(topic: str, evidence_snippets: list[EvidenceSnippet], extracted_documents: list[ExtractedDocument]) -> str:
    if evidence_snippets:
        findings = "\n".join(
            f"- 依据 `{item.file_name}`：{item.snippet}" for item in evidence_snippets[:8]
        )
    else:
        findings = "- 当前资料中未提取到足够证据，请补充原始材料。"

    source_summary = "\n".join(
        f"- `{doc.file_name}`：状态={doc.status}，解析器={doc.parser_name}，文本长度={len(doc.text)}"
        for doc in extracted_documents
    ) or "- 未发现任何可解析的资料文件。"

    return f"""# {topic}\n\n## 1. 报告结论摘要\n- 本草稿由本地资料自动整理而来，正式结论需由 AI 按证据进一步归纳。\n- 只建议输出有来源支撑的结论；缺少依据的部分应明确标记为待确认。\n\n## 2. 核心依据摘录\n{findings}\n\n## 3. 风险与不确定性\n- 解析成功不等于事实已经充分验证，仍需按来源交叉校验。\n- 对缺页、扫描件、表格合并单元格等情况，可能存在抽取偏差。\n- 若关键数字仅出现一次且无第二来源印证，应标记为低置信度。\n\n## 4. 建议的正式写作要求\n- 每个重要判断至少附一个来源文件名。\n- 对推断性表述使用“可能”“初步判断”“待确认”等词。\n- 对行动建议应区分短期、中期、长期。\n\n## 5. 资料处理概况\n{source_summary}\n"""
