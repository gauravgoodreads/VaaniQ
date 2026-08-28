"""Groq LLM enrichment — accent / dialect / fraud-pattern notes for the demo."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import structlog

from vaaniq.integrations.settings import IntegrationSettings, get_integration_settings

log = structlog.get_logger(__name__)


@dataclass(slots=True)
class EnrichmentResult:
    """LLM-assisted analysis of a clip transcript + detector verdict."""

    summary: str
    accent_notes: str
    language_notes: str
    risk_notes: str
    backend: str


_SYSTEM = (
    "You are VaaniQ, an Indic-language AI-voice fraud detection assistant. "
    "Languages in scope: Hindi (hi), Marathi (mr), Tamil (ta). Never mention Telugu. "
    "Be concise, practical, and honest when uncertain. "
    "Focus on accent/dialect cues, urgency/fraud-pattern language, and compression artefacts."
)


def enrich_with_groq(
    *,
    transcript: str,
    language: str,
    label: str,
    confidence: float,
    reliability: str,
    settings: IntegrationSettings | None = None,
) -> EnrichmentResult | None:
    """Call Groq chat completions for human-readable enrichment.

    Returns ``None`` when Groq is not configured or the call fails.
    """
    cfg = settings or get_integration_settings()
    if not cfg.groq_enabled or not cfg.enable_llm_enrichment:
        return None

    user = (
        f"Detector verdict: {label} (confidence={confidence:.3f}, reliability={reliability}).\n"
        f"Declared/hint language: {language}.\n"
        f"Transcript (may be empty or noisy):\n'''{transcript[:2500]}'''\n\n"
        "Reply in exactly 4 short lines with these prefixes:\n"
        "SUMMARY:\n"
        "ACCENT:\n"
        "LANGUAGE:\n"
        "RISK:\n"
    )
    try:
        with httpx.Client(timeout=60.0) as client:
            res = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {cfg.groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": cfg.groq_llm_model,
                    "temperature": 0.2,
                    "messages": [
                        {"role": "system", "content": _SYSTEM},
                        {"role": "user", "content": user},
                    ],
                },
            )
            res.raise_for_status()
            content = res.json()["choices"][0]["message"]["content"]
    except Exception as exc:
        log.warning("groq_llm_failed", error=str(exc))
        return None

    parsed = {"SUMMARY": "", "ACCENT": "", "LANGUAGE": "", "RISK": ""}
    current = None
    for line in str(content).splitlines():
        raw = line.strip()
        upper = raw.upper()
        for key in parsed:
            if upper.startswith(f"{key}:"):
                current = key
                parsed[key] = raw.split(":", 1)[-1].strip()
                break
        else:
            if current and raw:
                parsed[current] = f"{parsed[current]} {raw}".strip()

    return EnrichmentResult(
        summary=parsed["SUMMARY"] or str(content).strip()[:400],
        accent_notes=parsed["ACCENT"] or "Accent cues inconclusive from transcript alone.",
        language_notes=parsed["LANGUAGE"] or f"Treating clip as {language}.",
        risk_notes=parsed["RISK"] or "No clear fraud-pattern language detected.",
        backend=f"groq:{cfg.groq_llm_model}",
    )


def heuristic_enrichment(
    *,
    transcript: str,
    language: str,
    label: str,
    confidence: float,
) -> EnrichmentResult:
    """Offline enrichment when Groq is unavailable."""
    text = transcript.lower()
    fraud_hits = [
        w
        for w in (
            "arrest",
            "police",
            "otp",
            "urgent",
            "transfer",
            "account",
            "emergency",
            "hospital",
            "bail",
            "fine",
        )
        if w in text
    ]
    risk = (
        f"Possible urgency/fraud lexicon: {', '.join(fraud_hits)}."
        if fraud_hits
        else "No obvious English fraud keywords in transcript (Indic script may still carry risk)."
    )
    return EnrichmentResult(
        summary=(
            f"Local detector labelled this clip **{label}** at {confidence:.0%} confidence "
            f"for language `{language}`."
        ),
        accent_notes=(
            "Set GROQ_API_KEY for LLM accent/dialect notes. "
            "Acoustic path still scores real vs AI voice independently of transcript."
        ),
        language_notes=f"Active language channel: {language} (hi / mr / ta).",
        risk_notes=risk,
        backend="heuristic-offline",
    )
