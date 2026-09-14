#!/usr/bin/env python3
"""One complete VaaniQ demo: hear human then AI, then results, all three languages."""

from __future__ import annotations

import base64
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf
from playwright.sync_api import Page, sync_playwright

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "assets" / "demo"
WAV_DIR = OUT_DIR / "_wavs"
FRONTEND = "http://127.0.0.1:5173"
API = "http://127.0.0.1:8001"
AUDIO = REPO / "data" / "publication_corpus" / "audio"
FINAL_MP4 = OUT_DIR / "VaaniQ_Examiner_Demo.mp4"
LISTEN_JS = (REPO / "scripts" / "_demo_listen.js").read_text(encoding="utf-8")

CLIPS: list[tuple[str, str, str, Path]] = [
    ("hi", "human", "real", AUDIO / "hi" / "real" / "hi-real-dc1d927e3f9f02cf.flac"),
    ("hi", "ai", "fake", AUDIO / "hi" / "fake" / "hi-fake-2710dee28900583a.flac"),
    ("mr", "human", "real", AUDIO / "mr" / "real" / "mr-real-162797030213c858.flac"),
    ("mr", "ai", "fake", AUDIO / "mr" / "fake" / "mr-fake-db5e91655ec51d63.flac"),
    ("ta", "human", "real", AUDIO / "ta" / "real" / "ta-real-a4250b6b638f16fd.flac"),
    ("ta", "ai", "fake", AUDIO / "ta" / "fake" / "ta-fake-85ccb5a546dc634c.flac"),
]
LANG_NAME = {"hi": "Hindi", "mr": "Marathi", "ta": "Tamil"}
KIND_NAME = {"human": "HUMAN Kathbath REAL", "ai": "AI IndicSynth FAKE"}

OVERLAY_JS = """
(payload) => {
  const title = payload.title;
  const subtitle = payload.subtitle;
  let bar = document.getElementById("vaaniq-demo-overlay");
  if (!bar) {
    bar = document.createElement("div");
    bar.id = "vaaniq-demo-overlay";
    document.body.appendChild(bar);
  }
  bar.style.cssText = [
    "position:fixed", "left:0", "right:0", "bottom:0", "z-index:2147483647",
    "padding:16px 22px 18px", "background:#04120fcc", "color:#e8f2f0",
    "font-family:Segoe UI,system-ui,sans-serif", "pointer-events:none"
  ].join(";");
  document.body.style.paddingBottom = "120px";
  bar.innerHTML =
    "<div style='font-size:11px;letter-spacing:0.16em;color:#7dffd4'>VAANIQ COMPLETE DEMO  |  Hindi + Marathi + Tamil</div>"
    + "<div style='font-size:22px;font-weight:700'>" + title + "</div>"
    + "<div style='font-size:15px;color:#c5ddd8'>" + subtitle + "</div>";
}
"""


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def to_wav(src: Path, dest: Path) -> float:
    samples, rate = sf.read(str(src), always_2d=True)
    target = 48000
    if rate != target:
        n_out = int(round(samples.shape[0] * target / rate))
        old_t = np.linspace(0.0, 1.0, samples.shape[0], endpoint=False)
        new_t = np.linspace(0.0, 1.0, n_out, endpoint=False)
        samples = np.column_stack(
            [np.interp(new_t, old_t, samples[:, ch]) for ch in range(samples.shape[1])]
        )
        rate = target
    if samples.shape[1] == 1:
        samples = np.repeat(samples, 2, axis=1)
    peak = float(np.max(np.abs(samples))) or 1.0
    samples = samples * (0.92 / peak)
    dest.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dest), samples, rate, subtype="PCM_16")
    return float(samples.shape[0] / rate)


def wav_for(lang: str, kind: str) -> Path:
    return WAV_DIR / f"{lang}_{kind}.wav"


def prepare_wavs() -> dict[str, float]:
    durations: dict[str, float] = {}
    for lang, kind, _expected, clip in CLIPS:
        durations[f"{lang}_{kind}"] = to_wav(clip, wav_for(lang, kind))
    return durations


def require_stack() -> None:
    for url in (f"{API}/health", FRONTEND):
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(f"not ready: {url}")
    missing = [str(path) for _, _, _, path in CLIPS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing clips: " + ", ".join(missing))


def overlay(page: Page, title: str, subtitle: str) -> None:
    page.evaluate(OVERLAY_JS, {"title": title, "subtitle": subtitle})


def hold(page: Page, ms: int) -> None:
    page.wait_for_timeout(ms)


def title_card(page: Page, heading: str, lines: list[str], ms: int = 5000) -> None:
    items = "".join(f"<li>{line}</li>" for line in lines)
    page.set_content(
        "<html><body style='margin:0;background:#04120f;color:#e8f2f0;font-family:Segoe UI,sans-serif'>"
        "<div style='min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:72px 80px'>"
        "<p style='letter-spacing:0.2em;color:#7dffd4'>VAANIQ COMPLETE DEMO</p>"
        f"<h1 style='font-size:52px;margin:16px 0 24px'>{heading}</h1>"
        f"<ul style='font-size:22px;line-height:1.55;color:#c5ddd8'>{items}</ul>"
        "</div></body></html>"
    )
    hold(page, ms)


def listen_visualizer(
    page: Page,
    *,
    lang: str,
    kind: str,
    wav: Path,
    duration: float,
    t0: float,
    marks: dict[str, float],
) -> None:
    lang_name = LANG_NAME[lang]
    is_human = kind == "human"
    badge = "LIVE HUMAN SPEECH  |  BEING SPOKEN NOW" if is_human else "AI AUDIO  |  PLAYING NOW"
    truth = "Ground truth: REAL human (Kathbath)" if is_human else "Ground truth: FAKE AI (IndicSynth)"
    title = f"{lang_name}  |  {KIND_NAME[kind]}"
    subtitle = f"{truth}. Watch the live waveform and spectrogram while you hear the clip."
    badge_bg = "#7dffd4" if is_human else "#ff6b6b"
    badge_fg = "#04120f"
    page.set_content(
        "<html><body style='margin:0;background:#04120f;color:#e8f2f0;font-family:Segoe UI,sans-serif'>"
        "<div style='min-height:100vh;padding:36px 56px;background:radial-gradient(ellipse at 78% 8%,#1a4a44,#04120f 58%)'>"
        f"<div style='display:inline-block;padding:8px 16px;border-radius:999px;letter-spacing:0.16em;"
        f"font-size:13px;font-weight:700;background:{badge_bg};color:{badge_fg}'>{badge}</div>"
        f"<h1 style='font-size:52px;margin:18px 0 8px'>{title}</h1>"
        f"<p style='font-size:22px;color:#c5ddd8;max-width:980px'>{subtitle}</p>"
        "<canvas id='wave' width='1400' height='160' style='width:100%;height:160px;margin-top:24px;"
        "border-radius:16px;border:1px solid #2a5a54;background:#020807'></canvas>"
        "<canvas id='spec' width='1400' height='220' style='width:100%;height:220px;margin-top:14px;"
        "border-radius:16px;border:1px solid #2a5a54;background:#020807'></canvas>"
        "<p style='margin-top:18px;color:#9ec9c2'>Turn speakers on. Detection, transcript, and calculated spectrogram follow.</p>"
        "</div></body></html>"
    )
    b64 = base64.b64encode(wav.read_bytes()).decode("ascii")
    marks[f"{lang}_{kind}"] = time.perf_counter() - t0
    started = page.evaluate(LISTEN_JS, {"b64": b64, "isHuman": is_human})
    if not started:
        raise RuntimeError(f"autoplay failed {lang}_{kind}")
    hold(page, int((duration + 0.8) * 1000))


def show_detection(
    page: Page,
    *,
    lang: str,
    kind: str,
    expected: str,
    clip: Path,
) -> None:
    lang_name = LANG_NAME[lang]
    page.goto(f"{FRONTEND}/upload", wait_until="networkidle")
    overlay(
        page,
        f"DETECTING {lang_name.upper()}  |  {KIND_NAME[kind]}",
        "Same clip you just heard. Calculated score, transcript, English translation, spectrogram.",
    )
    page.get_by_label("Language").select_option(lang)
    page.get_by_role("tab", name="Upload file").click()
    page.locator("input[type='file']").set_input_files(str(clip))
    hold(page, 700)
    page.get_by_role("button", name="Detect").click()
    page.get_by_text("Verdict", exact=True).wait_for(timeout=120000)
    page.get_by_text(expected, exact=True).first.wait_for(timeout=15000)
    if page.get_by_text("No spectrogram.").count():
        raise RuntimeError(f"empty spectrogram for {lang}_{kind}")
    page.locator("canvas[aria-label='Spectrogram']").wait_for(timeout=15000)
    overlay(
        page,
        f"{lang_name.upper()} RESULT  |  {expected.upper()}",
        "P(real), P(fake), analysis, native transcript, English translation, waveform, spectrogram.",
    )
    page.get_by_text("P(real)", exact=True).scroll_into_view_if_needed()
    hold(page, 2200)
    page.get_by_text("P(fake)", exact=True).scroll_into_view_if_needed()
    hold(page, 2000)
    page.get_by_text("Analysis", exact=True).scroll_into_view_if_needed()
    hold(page, 3200)
    page.get_by_text("Transcript", exact=True).scroll_into_view_if_needed()
    hold(page, 4000)
    page.get_by_text("Translation (English)", exact=True).scroll_into_view_if_needed()
    hold(page, 4500)
    page.get_by_text("Waveform", exact=True).scroll_into_view_if_needed()
    hold(page, 2200)
    page.get_by_text("Spectrogram", exact=True).scroll_into_view_if_needed()
    hold(page, 3500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    hold(page, 1800)


def open_app(page: Page, route: str, title: str, subtitle: str, ms: int) -> None:
    page.goto(f"{FRONTEND}{route}", wait_until="networkidle")
    overlay(page, title, subtitle)
    hold(page, ms)


def mux_audio(webm: Path, mp4: Path, marks: dict[str, float]) -> None:
    ff = ffmpeg_bin()
    cmd: list[str] = [ff, "-y", "-i", str(webm)]
    for lang, kind, _expected, _clip in CLIPS:
        cmd.extend(["-i", str(wav_for(lang, kind))])
    parts: list[str] = []
    labels: list[str] = []
    for index, (lang, kind, _expected, _clip) in enumerate(CLIPS, start=1):
        delay = max(0, int(marks[f"{lang}_{kind}"] * 1000))
        alias = f"a{index}"
        parts.append(
            f"[{index}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
            f"volume=3.5,adelay={delay}:all=1[{alias}]"
        )
        labels.append(f"[{alias}]")
    parts.append("".join(labels) + f"amix=inputs={len(CLIPS)}:duration=longest:normalize=0,apad[aout]")
    cmd.extend(
        [
            "-filter_complex",
            ";".join(parts),
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-shortest",
            "-movflags",
            "+faststart",
            str(mp4),
        ]
    )
    done = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if done.returncode != 0 or not mp4.is_file():
        raise RuntimeError(done.stderr[-2500:] if done.stderr else "ffmpeg mux failed")


def record() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    durations = prepare_wavs()
    raw_dir = OUT_DIR / "_raw"
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    raw_dir.mkdir(parents=True)
    marks: dict[str, float] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required"],
        )
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            record_video_dir=str(raw_dir),
            record_video_size={"width": 1600, "height": 900},
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        t0 = time.perf_counter()

        title_card(
            page,
            "VaaniQ live demonstration",
            [
                "AI-generated voice detection for Hindi, Marathi, and Tamil",
                "Speakers on: you will hear HUMAN speech, then AI speech, for every language",
                "After each clip: calculated REAL/FAKE, native transcript, English translation, spectrogram",
                "Then the full stack: dashboard, calibration graphs, experiments, API",
            ],
            7000,
        )
        title_card(
            page,
            "Frozen research numbers",
            [
                "Baseline V1: 91.61% accuracy, 6.56% EER, ROC-AUC 0.9729, n=584",
                "Frozen XLS-R: 92.12% accuracy, ROC-AUC 0.9828",
                "RQ1-RQ4 COMPLETE on the bounded machine-evaluated V1 benchmark",
                "Tamil is the third language. Telugu is not in this project.",
            ],
            7000,
        )

        open_app(page, "/", "Home", "Cross-lingual calibrated detection of AI-generated voice.", 3200)
        open_app(
            page,
            "/dashboard",
            "Dashboard | full metrics",
            "91.61% acc | 6.56% EER | n=584 | speaker-disjoint Kathbath + IndicSynth",
            6500,
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 2500)
        open_app(
            page,
            "/datasets",
            "Datasets",
            "Hindi, Marathi, Tamil. REAL=Kathbath. FAKE=IndicSynth.",
            4000,
        )

        for lang, kind, expected, clip in CLIPS:
            lang_name = LANG_NAME[lang]
            if kind == "human":
                title_card(
                    page,
                    f"Now hear {lang_name} HUMAN speech",
                    [
                        "This is a real Kathbath speaker. Ground truth: REAL",
                        "You will hear the spoken clip with a live spectrogram",
                        "After it ends, VaaniQ shows REAL, transcript, English translation, and spectrogram",
                    ],
                    4500,
                )
            else:
                title_card(
                    page,
                    f"Now hear {lang_name} AI speech",
                    [
                        "This is IndicSynth AI audio. Ground truth: FAKE",
                        "You will hear the generated clip with a live spectrogram",
                        "After it ends, VaaniQ shows FAKE, transcript, English translation, and spectrogram",
                    ],
                    4500,
                )
            listen_visualizer(
                page,
                lang=lang,
                kind=kind,
                wav=wav_for(lang, kind),
                duration=durations[f"{lang}_{kind}"],
                t0=t0,
                marks=marks,
            )
            show_detection(page, lang=lang, kind=kind, expected=expected, clip=clip)

        open_app(
            page,
            "/history",
            "History | six live detections",
            "Hindi, Marathi, Tamil: HUMAN=REAL and AI=FAKE",
            5000,
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 2000)
        open_app(page, "/inference", "Inference", "Latest clip verdict plus confidence.", 3500)

        title_card(
            page,
            "Research questions and calculations",
            [
                "RQ1: WhatsApp-style Opus compression robustness",
                "RQ2: English-only transfer fails (54.8% acc, 76.56% EER)",
                "RQ3: Leave-one-language: Hindi 78.83%, Marathi 93.29%, Tamil 93.94%",
                "RQ4 next: ECE, Brier, reliability diagram, coverage curve",
            ],
            6500,
        )
        open_app(
            page,
            "/calibration",
            "RQ4 Calibration graphs",
            "ECE and Brier first, then reliability diagram and coverage/accuracy curve",
            2500,
        )
        page.get_by_text("ECE", exact=True).scroll_into_view_if_needed()
        hold(page, 2800)
        page.get_by_text("Brier", exact=True).scroll_into_view_if_needed()
        hold(page, 2500)
        page.get_by_text("Reliability diagram", exact=True).scroll_into_view_if_needed()
        hold(page, 5000)
        page.get_by_text("Coverage curve", exact=True).scroll_into_view_if_needed()
        hold(page, 5000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        overlay(page, "Calibration | full calculation", "Temperature scaling. T fit on validation, not test.")
        hold(page, 2500)

        open_app(
            page,
            "/explainability",
            "Explainability",
            "Grad-CAM proxy, spectrogram, attention, compression artefacts",
            4500,
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 2500)
        open_app(
            page,
            "/research-metrics",
            "Research metrics",
            "Canonical numbers stay in artifacts/final_results_manifest.json",
            4500,
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 2500)
        open_app(page, "/experiments", "Experiments", "RQ catalogue on the frozen V1 split.", 2800)
        for rq, note in (
            ("RQ1", "Opus compression robustness"),
            ("RQ2", "English-only transfer control"),
            ("RQ3", "Leave-one-language-out Hindi / Marathi / Tamil"),
            ("RQ4", "Calibration: ECE, Brier, reliability"),
        ):
            page.locator("select").first.select_option(rq)
            overlay(page, f"Experiments | {rq}", note)
            hold(page, 2800)

        open_app(
            page,
            "/live",
            "Live microphone",
            "In viva you can click Start and speak. This video used files so Hindi, Marathi, and Tamil are all audible.",
            3500,
        )
        open_app(page, "/admin", "Admin", "Local stack health and git SHA.", 3000)
        open_app(page, "/docs", "Documentation", "Proposal, architecture, datasets, limitations.", 3000)
        page.goto(f"{API}/docs", wait_until="networkidle")
        overlay(page, "FastAPI /docs", "Upload, infer, calibrate, explain, and research metrics.")
        hold(page, 4000)
        title_card(
            page,
            "Honest close",
            [
                "Heard live: Hindi, Marathi, Tamil HUMAN then AI, with transcripts, translations, spectrograms",
                "RQ1-RQ4 COMPLETE on bounded V1. 91.61% accuracy / 6.56% EER",
                "Limits: V1 source correlates with label; FLEURS n=9 remains a pilot",
                "Research prototype, not a production scam detector",
            ],
            7000,
        )

        page.close()
        context.close()
        browser.close()

    videos = list(raw_dir.glob("*.webm"))
    if not videos:
        raise FileNotFoundError("Playwright did not write a webm")
    mux_audio(videos[0], FINAL_MP4, marks)
    shutil.rmtree(raw_dir, ignore_errors=True)
    shutil.rmtree(WAV_DIR, ignore_errors=True)
    for extra in (OUT_DIR / "VaaniQ_Examiner_Demo.webm", OUT_DIR / "audio_cues.json", OUT_DIR / "_tmp.mp4"):
        if extra.is_file():
            extra.unlink()
    return FINAL_MP4


def main() -> int:
    require_stack()
    path = record()
    print(f"DEMO_VIDEO={path}")
    print(f"SIZE_MB={path.stat().st_size / (1024 * 1024):.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
