"""Human-readable clip preview for scripts (ROADMAP-018)."""

from __future__ import annotations

from collections.abc import Sequence

from vaaniq.core.domain.entities import ClipMetadata


def format_preview(clips: Sequence[ClipMetadata], n: int) -> str:
    """Format the first ``n`` clips as a tab-separated preview string.

    Args:
        clips: Clip metadata sequence.
        n: Maximum number of rows to include.

    Returns:
        Multi-line string suitable for CLI / script stdout.

    Serves:
        ROADMAP-018 (dataset report / preview helpers).
    """
    if n < 0:
        n = 0
    header = "clip_id\tlanguage\tlabel\tsource\tsplit\tduration_sec"
    lines = [header]
    for clip in list(clips)[:n]:
        lines.append(
            "\t".join(
                [
                    clip.clip_id,
                    clip.language.value,
                    clip.label.value,
                    clip.source.value,
                    clip.split.value,
                    f"{clip.duration_sec:.3f}",
                ]
            )
        )
    return "\n".join(lines)
