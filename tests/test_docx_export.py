from __future__ import annotations

from pathlib import Path

from docx import Document

from report_generator.docx_export import export_markdown_file_to_docx


SAMPLE_MARKDOWN = """# 主标题

## 二级标题

普通段落，包含**重点内容**和更多说明。

- 列表项A
- 列表项B

1. 来源一
2. 来源二
"""


def test_export_markdown_file_to_docx(tmp_path: Path) -> None:
    markdown_path = tmp_path / "sample.md"
    docx_path = tmp_path / "sample.docx"
    markdown_path.write_text(SAMPLE_MARKDOWN, encoding="utf-8")

    output = export_markdown_file_to_docx(markdown_path, docx_path)

    assert output.exists()
    document = Document(output)
    texts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]

    assert texts[0] == "主标题"
    assert "二级标题" in texts
    assert any("重点内容" in text for text in texts)
    assert any("列表项A" in text for text in texts)
    assert any("来源一" in text for text in texts)
