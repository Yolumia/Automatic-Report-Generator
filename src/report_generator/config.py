from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".pptx", ".xlsx"}
TEXT_EXTENSIONS = {".txt", ".md"}


@dataclass(slots=True)
class AppConfig:
    base_dir: Path
    sources_dir: Path
    processed_dir: Path
    output_dir: Path
    prompts_dir: Path
    docs_dir: Path

    @classmethod
    def from_base_dir(
        cls,
        base_dir: Path,
        sources_dir: Path | None = None,
        output_dir: Path | None = None,
    ) -> "AppConfig":
        return cls(
            base_dir=base_dir,
            sources_dir=(sources_dir or base_dir / "data" / "sources").resolve(),
            processed_dir=(base_dir / "data" / "processed").resolve(),
            output_dir=(output_dir or base_dir / "outputs").resolve(),
            prompts_dir=(base_dir / "prompts").resolve(),
            docs_dir=(base_dir / "docs").resolve(),
        )
