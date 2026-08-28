#!/usr/bin/env python3
"""One complete VaaniQ demo: hi/mr/ta, listen then results, transcript, calibration."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import soundfile as sf
from playwright.sync_api import Page, sync_playwright

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "docs" / "assets" / "demo"
FRONTEND = "http://127.0.0.1:5173"
API = "http://127.0.0.1:8001"
AUDIO = REPO / "data" / "publication_corpus" / "audio"
FINAL_MP4 = OUT_DIR / "VaaniQ_Examiner_Demo.mp4"

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

SET_OVERLAY_JS = """
({ title, subtitle }) => {
  let bar = document.getElementById("vaaniq-demo-overlay");
  if (!bar) {
    bar = document.createElement("div");
    bar.id = "vaaniq-demo-overlay";
    document.body.appendChild(bar);
  }
  bar.style.cssText = "position:fixed;left:0;right:0;bottom:0;z-index:2147483647;padding:16px 22px 18px;background:#04120f;color:#e8f2f0;font-family:Segoe UI,sans-serif;pointer-events:none";
  document.body.style.paddingBottom = "130px";
  bar.innerHTML = "<div style='font-size:11px;letter-spacing:0.16em;color:#7dffd4'>VAANIQ COMPLETE DEMO | HINDI + MARATHI + TAMIL</div><div style='font-size:22px;font-weight:700'>" + title + "</div><div style='font-size:15px;color:#c5ddd8'>" + subtitle + "</div>";
}
"""

SHOW_PLAYER_JS = """
({ label }) => {
  const input = document.querySelector("input[type=file]");
  const file = input && input.files && input.files[0];
  if (!file) return false;
  const url = URL.createObjectURL(file);
  let wrap = document.getElementById("vaaniq-audio-play");
  if (wrap) wrap.remove();
  wrap = document.createElement("div");
  wrap.id = "vaaniq-audio-play";
  wrap.style.cssText = "position:fixed;top:78px;left:50%;transform:translateX(-50%);z-index:2147483646;background:#04120f;padding:16px 20px;border-radius:16px;border:2px solid #7dffd4;min-width:560px";
  wrap.innerHTML = "<div style='color:#7dffd4;font-weight:700'>LISTEN FIRST | RESULT AFTER AUDIO</div><div style='color:#e8f2f0;font-size:22px;margin-top:8px'>" + label + "</div><audio id='vaaniq-clip' controls autoplay style='width:100%;margin-top:10px'></audio>";
  document.body.appendChild(wrap);
  const audio = wrap.querySelector("audio");
  audio.src = url;
  audio.volume = 1;
  return audio.play().then(() => true).catch(() => false);
}
"""


def ffmpeg_bin() -> str:
    found = shutil.which("ffmpeg")
    if found:
        return found
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def clip_seconds(path: Path) -> float:
    return float(sf.info(str(path)).duration)


def require_stack() -> None:
    for url in (f"{API}/health", FRONTEND):
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(f"not ready: {url}")
    missing = [str(path) for *_, path in CLIPS if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing clips")


def overlay(page: Page, title: str, subtitle: str) -> None:
    page.evaluate(SET_OVERLAY_JS, {"title": title, "subtitle": subtitle})


def hold(page: Page, ms: int) -> None:
    page.wait_for_timeout(ms)


def title_card(page: Page, heading: str, lines: list[str], ms: int) -> None:
    items = "".join(f"<li>{line}</li>" for line in lines)
    page.set_content(
        "<html><body style='margin:0;background:#04120f;color:#e8f2f0;font-family:Segoe UI,sans-serif'>"
        "<div style='min-height:100vh;display:flex;flex-direction:column;justify-content:center;padding:72px 80px'>"
        "<p style='letter-spacing:0.2em;color:#7dffd4'>VAANIQ COMPLETE PROJECT DEMO</p>"
        f"<h1 style='font-size:52px'>{heading}</h1>"
        f"<ul style='font-size:22px;line-height:1.55;color:#c5ddd8'>{items}</ul>"
        "</div></body></html>"
    )
    hold(page, ms)


def open_app(page: Page, route: str, title: str, subtitle: str, ms: int) -> None:
    page.goto(f"{FRONTEND}{route}", wait_until="networkidle")
    overlay(page, title, subtitle)
    hold(page, ms)


def show_text(page: Page, text: str, ms: int) -> None:
    loc = page.get_by_text(text, exact=False)
    if loc.count() == 0:
        hold(page, 800)
        return
    loc.first.scroll_into_view_if_needed()
    hold(page, ms)


def listen_then_result(
    page: Page,
    lang: str,
    kind: str,
    expected: str,
    clip: Path,
    t0: float,
    marks: dict[str, float],
) -> None:
    lang_name = LANG_NAME[lang]
    kind_name = KIND_NAME[kind]
    key = f"{lang}_{kind}"
    page.goto(f"{FRONTEND}/upload", wait_until="networkidle")
    overlay(page, f"{lang_name} | {kind_name} | LISTEN", "Audio first. Result, transcript, and graphs after the clip.")
    page.get_by_label("Language").select_option(lang)
    page.get_by_role("tab", name="Upload file").click()
    page.locator("input[type='file']").set_input_files(str(clip))
    hold(page, 800)
    marks[key] = time.perf_counter() - t0
    ok = page.evaluate(SHOW_PLAYER_JS, {"label": f"{lang_name} | {kind_name}"})
    if not ok:
        raise RuntimeError("autoplay failed " + key)
    hold(page, int((clip_seconds(clip) + 1.4) * 1000))
    page.evaluate("() => { const w = document.getElementById('vaaniq-audio-play'); if (w) w.remove(); }")
    hold(page, 600)
    overlay(page, f"DETECTING {lang_name} {kind.upper()}", "Running VaaniQ. Then we show verdict, confidence, transcript, waveform.")
    page.get_by_role("button", name="Detect").click()
    page.get_by_text("Verdict", exact=True).wait_for(timeout=90000)
    page.get_by_text(expected, exact=True).first.wait_for(timeout=15000)
    overlay(
        page,
        f"{lang_name} RESULT | {expected.upper()}",
        "Confidence, transcript, analysis, waveform, and spectrogram are below.",
    )
    page.get_by_text("Verdict", exact=True).scroll_into_view_if_needed()
    hold(page, 4500)
    show_text(page, "Transcript", 5500)
    show_text(page, "Analysis", 3500)
    show_text(page, "Detected lang", 2500)
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    overlay(page, f"{lang_name} | waveform + spectrogram", "Visual evidence for the clip you just heard.")
    hold(page, 3500)


def mux_audio(webm: Path, mp4: Path, marks: dict[str, float]) -> None:
    ff = ffmpeg_bin()
    cmd: list[str] = [ff, "-y", "-i", str(webm)]
    for _lang, _kind, _exp, clip in CLIPS:
        cmd.extend(["-i", str(clip)])
    parts: list[str] = []
    aliases: list[str] = []
    for i, (lang, kind, _exp, _clip) in enumerate(CLIPS, start=1):
        delay = max(0, int(marks[f"{lang}_{kind}"] * 1000))
        alias = f"a{i}"
        parts.append(
            f"[{i}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=5,adelay={delay}:all=1[{alias}]"
        )
        aliases.append(f"[{alias}]")
    parts.append("".join(aliases) + f"amix=inputs={len(CLIPS)}:duration=longest:normalize=0,apad[aout]")
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
        raise RuntimeError(done.stderr[-2500:] if done.stderr else "mux failed")


def record() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    raw_dir = OUT_DIR / "_raw"
    if raw_dir.exists():
        shutil.rmtree(raw_dir)
    raw_dir.mkdir(parents=True)
    marks: dict[str, float] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
        context = browser.new_context(
            viewport={"width": 1600, "height": 900},
            record_video_dir=str(raw_dir),
            record_video_size={"width": 1600, "height": 900},
        )
        page = context.new_page()
        page.set_default_timeout(60000)
        t0 = time.perf_counter()

        title_card(page, "VaaniQ", [
            "AI-voice detection for Hindi, Marathi, and Tamil",
            "One complete video: live app, all 3 languages, transcripts, calibration graphs",
            "For each language: hear HUMAN then see REAL result; hear AI then see FAKE result",
        ], 6500)
        title_card(page, "Frozen numbers", [
            "Baseline V1: 91.61% accuracy, 6.56% EER, ROC-AUC 0.9729, n=584",
            "Frozen XLS-R: 92.12% accuracy, ROC-AUC 0.9828",
            "RQ1-RQ4 complete on bounded V1. RQ5 human study N=0",
            "Telugu is not a project language",
        ], 7000)

        open_app(page, "/", "Home", "Calibrated detection of AI-generated voice in Indian languages.", 3500)
        open_app(page, "/dashboard", "Dashboard", "91.61% acc | 6.56% EER | n=584 | speaker-disjoint Kathbath + IndicSynth", 6500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        overlay(page, "Dashboard | full metrics", "Pipeline status, calibration snapshot, dataset counts.")
        hold(page, 4000)
        open_app(page, "/datasets", "Datasets", "Hindi, Marathi, Tamil. REAL=Kathbath. FAKE=IndicSynth. 2346 instances.", 5000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 3000)

        for lang, kind, expected, clip in CLIPS:
            who = "HUMAN Kathbath REAL" if kind == "human" else "AI IndicSynth FAKE"
            title_card(page, f"{LANG_NAME[lang]} | {who}", [
                f"You will hear {LANG_NAME[lang]} speech",
                "Listen to the full clip first",
                "Then VaaniQ shows verdict, confidence, transcript, waveform, spectrogram",
            ], 4000)
            listen_then_result(page, lang, kind, expected, clip, t0, marks)

        open_app(page, "/history", "History", "Six live runs: HUMAN=REAL and AI=FAKE for Hindi, Marathi, Tamil.", 5000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 3000)
        open_app(page, "/inference", "Inference", "Latest verdict plus confidence from the last clip.", 4000)

        title_card(page, "Research questions", [
            "RQ1 Opus compression robustness",
            "RQ2 English-only transfer fails: 54.8% acc, 76.56% EER",
            "RQ3 leave-one-language: Hindi 78.83%, Marathi 93.29%, Tamil 93.94%",
            "RQ4 calibration graphs next. RQ5 listeners N=0",
        ], 6500)

        open_app(page, "/calibration", "RQ4 Calibration graphs", "ECE and Brier first, then reliability and coverage curves.", 4000)
        show_text(page, "ECE", 3000)
        show_text(page, "Brier", 2500)
        show_text(page, "Reliability diagram", 6000)
        show_text(page, "Coverage", 5000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        overlay(page, "Calibration | full charts", "Reliability diagram and coverage/accuracy curve for RQ4.")
        hold(page, 4500)

        open_app(page, "/explainability", "Explainability", "Grad-CAM, spectrogram, attention, compression artefacts.", 3500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 4500)
        open_app(page, "/research-metrics", "Research metrics", "Live session scalars. Canonical numbers stay in the frozen manifest.", 4500)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        hold(page, 3000)
        open_app(page, "/experiments", "Experiments", "RQ catalogue.", 3000)
        for rq, note in (("RQ1", "Opus compression"), ("RQ2", "English-only control"), ("RQ3", "Leave-one-language"), ("RQ4", "Calibration")):
            page.locator("select").first.select_option(rq)
            overlay(page, f"Experiments | {rq}", note)
            hold(page, 2800)
        open_app(page, "/human-study", "RQ5 Human study", "Protocol ready. N=0. No answers were invented.", 4500)
        open_app(page, "/live", "Live microphone", "Viva option: Start and speak. This video used files so all 3 languages are audible.", 3500)
        open_app(page, "/admin", "Admin", "Stack health and git SHA.", 3000)
        open_app(page, "/docs", "Documentation", "Proposal, architecture, datasets, limitations.", 3000)
        page.goto(f"{API}/docs", wait_until="networkidle")
        overlay(page, "FastAPI /docs", "Typed API: upload, infer, calibrate, explain, human-study.")
        hold(page, 4000)
        title_card(page, "Honest close", [
            "Shown live: Hindi, Marathi, Tamil HUMAN then AI, with transcripts",
            "RQ1-RQ4 complete on bounded V1. 91.61% / 6.56% EER",
            "Limit: V1 source correlates with label. RQ5 N=0. FLEURS n=9 PILOT",
            "Research prototype for three languages. Not a production scam detector",
        ], 7000)

        page.close()
        context.close()
        browser.close()

    videos = list(raw_dir.glob("*.webm"))
    if not videos:
        raise FileNotFoundError("no webm")
    mux_audio(videos[0], FINAL_MP4, marks)
    shutil.rmtree(raw_dir, ignore_errors=True)
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
