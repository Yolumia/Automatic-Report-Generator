from __future__ import annotations

import argparse
from pathlib import Path

from report_generator.config import AppConfig
from report_generator.docx_export import export_markdown_file_to_docx
from report_generator.pipeline import project_root_from_file, run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="自动报告生成器")
    parser.add_argument("--topic", required=False, help="报告主题")
    parser.add_argument("--sources-dir", type=Path, default=None, help="参考资料目录")
    parser.add_argument("--output-dir", type=Path, default=None, help="输出目录")
    parser.add_argument("--from-markdown", type=Path, default=None, help="从现有 Markdown 文件导出 Word")
    parser.add_argument("--docx-output", type=Path, default=None, help="导出的 Word 文件路径")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.from_markdown:
        output_path = export_markdown_file_to_docx(args.from_markdown, args.docx_output)
        print(f"Word 文档已生成: {output_path}")
        return

    if not args.topic:
        parser.error("未指定 --topic，或请使用 --from-markdown 直接导出 Word")

    root = project_root_from_file(Path(__file__))
    config = AppConfig.from_base_dir(
        base_dir=root,
        sources_dir=args.sources_dir,
        output_dir=args.output_dir,
    )
    artifacts = run_pipeline(topic=args.topic, config=config)

    print(f"已处理资料数量: {len(artifacts.extracted_documents)}")
    print(f"证据摘录数量: {len(artifacts.evidence_snippets)}")
    print(f"输出目录: {artifacts.output_dir}")


if __name__ == "__main__":
    main()
