from __future__ import annotations

from report_generator.models import EvidenceSnippet, ExtractedDocument


def build_evidence_snippets(
    extracted_documents: list[ExtractedDocument],
    *,
    max_snippets_per_doc: int = 3,
    snippet_length: int = 280,
) -> list[EvidenceSnippet]:
    snippets: list[EvidenceSnippet] = []

    for document in extracted_documents:
        if document.status != "ok" or not document.text.strip():
            continue

        paragraphs = [segment.strip() for segment in document.text.split("\n") if segment.strip()]
        selected = paragraphs[:max_snippets_per_doc] or [document.text.strip()[:snippet_length]]

        for segment in selected:
            snippet = segment[:snippet_length]
            snippets.append(
                EvidenceSnippet(
                    source_path=document.source_path,
                    file_name=document.file_name,
                    parser_name=document.parser_name,
                    snippet=snippet,
                    metadata=document.metadata,
                )
            )

    return snippets
