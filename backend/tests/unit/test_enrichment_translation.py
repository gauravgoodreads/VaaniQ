"""Unit tests for demo enrichment translation field."""

from __future__ import annotations

from vaaniq.integrations.groq_llm import heuristic_enrichment


def test_heuristic_enrichment_does_not_invent_translation() -> None:
    result = heuristic_enrichment(
        transcript="नमस्ते",
        language="hi",
        label="real",
        confidence=0.91,
    )
    assert result.translation == ""
    assert "hi" in result.language_notes
