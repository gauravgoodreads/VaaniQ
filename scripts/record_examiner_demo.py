#!/usr/bin/env python3
"""Record one labeled examiner demo MP4 with audible HUMAN and AI speech."""

from __future__ import annotations

import json
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
FRONTEND = "http://127.0.0.1:5173"
API = "http://127.0.0.1:8001"
HUMAN_CLIP = REPO / "data/publication_corpus/audio/hi/real/hi-real-dc1d927e3f9f02cf.flac"
AI_CLIP = REPO / "data/publication_corpus/audio/hi/fake/hi-fake-2710dee28900583a.flac"
FINAL_MP4 = OUT_DIR / "VaaniQ_Examiner_Demo.mp4"

SET_OVERLAY_JS = """
({ title, subtitle }) => {
  const css = [
    "position:fixed","left:0","right:0","bottom:0","z-index:2147483647",
    "display:flex","flex-direction:column","gap:4px","padding:14px 22px 16px",
    "background:linear-gradient(90deg,#04120f,#0d2a28 55%,#163a38)",
    "color:#e8f2f0","font-family:Segoe UI,system-ui,sans-serif",
    "box-shadow:0 -12px 40px rgba(0,0,0,0.35)","pointer-events:none"
  ].join(";");
  let bar = document.getElementById("vaaniq-demo-overlay");
  if (!bar) {
    bar = document.createElement("div");
    bar.id = "vaaniq-demo-overlay";
    document.body.appendChild(bar);
  }
  bar.style.cssText = css;
  document.body.style.paddingBottom = "120px";
  bar.innerHTML = (
    "<div style='font-size:11px;letter-spacing:0.18em;text-transform:uppercase;color:#7dffd4'>"
    + "VAANIQ EXAMINER DEMO  |  Hindi + Marathi + Tamil  |  LIVE APP + AUDIO"
    + "</div>"
    + "<div style='font-size:22px;font-weight:700;line-height:1.2'>" + title + "</div>"
    + "<div style='font-size:14px;color:#c5ddd8'>" + subtitle + "</div>"
  );
}
"""

SHOW_PLAYER_JS = """
({ label, repeats }) => {
  const input = document.querySelector("input[type=file]");
  const file = input && input.files && input.files[0];
  if (!file) return false;
  const url = URL.createObjectURL(file);
  let wrap = document.getElementById("vaaniq-audio-play");
  if (wrap) wrap.remove();
  wrap = document.createElement("div");
  wrap.id = "vaaniq-audio-play";
  wrap.style.cssText = [
    "position:fixed","top:78px","left:50%","transform:translateX(-50%)",
    "z-index:2147483646","background:#04120f","padding:14px 18px",
    "border-radius:16px","border:2px solid #7dffd4","min-width:520px",
    "box-shadow:0 16px 40px rgba(0,0,0,0.45)"
  ].join(";");
  wrap.innerHTML = (
    "<div style='color:#7dffd4;font:700 13px Segoe UI;letter-spacing:0.16em'>"
    + "NOW PLAYING  |  TURN SPEAKERS ON</div>"
    + "<div style='color:#e8f2f0;font:20px Segoe UI;margin-top:6px'>" + label + "</div>"
    + "<audio id='vaaniq-clip' controls autoplay style='width:100%;margin-top:10px'></audio>"
  );
  document.body.appendChild(wrap);
  const audio = wrap.querySelector("audio");
  audio.src = url;
  audio.volume = 1;
  let left = repeats;
  audio.addEventListener("ended", () => {
    left -= 1;
    if (left > 0) {
      audio.currentTime = 0;
      audio.play();
    }
  });
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
    if not HUMAN_CLIP.is_file() or not AI_CLIP.is_file():
        raise FileNotFoundError("publication corpus clips missing")


def overlay(page: Page, title: str, subtitle: str) -> None:
    page.evaluate(SET_OVERLAY_JS, {"title": title, "subtitle": subtitle})


def hold(page: Page, ms: int) -> None:
    page.wait_for_timeout(ms)


def title_card(page: Page, heading: str, lines: list[str], ms: int = 5000) -> None:
    items = "".join(f"<li>{line}</li>" for line in lines)
    page.set_content(
        f"""
        <html><body style="margin:0;background:#04120f;color:#e8f2f0;
        font-family:Segoe UI,system-ui,sans-serif">
        <div style="min-height:100vh;display:flex;flex-direction:column;
        justify-content:center;padding:72px 80px;
        background:radial-gradient(ellipse at 70% 20%,#163a38, #04120f 60%)">
          <p style="letter-spacing:0.22em;text-transform:uppercase;color:#7dffd4;
          font-size:14px">VaaniQ capstone demonstration</p>
          <h1 style="font-size:64px;margin:16px 0 24px;letter-spacing:-0.03em">{heading}</h1>
          <ul style="font-size:22px;line-height:1.55;max-width:980px;color:#c5ddd8">{items}</ul>
        </div></body></html>
        """
    )
    hold(page, ms)


def open_app(page: Page, route: str, title: str, subtitle: str, ms: int) -> None:
    page.goto(f"{FRONTEND}{route}", wait_until="networkidle")
    overlay(page, title, subtitle)
    hold(page, ms)


def play_clip(page: Page, *, label: str, seconds: float, repeats: int = 2) -> None:
    started = page.evaluate(SHOW_PLAYER_JS, {"label": label, "repeats": repeats})
    if not started:
        raise RuntimeError(f"audio autoplay failed: {label}")
    hold(page, int((seconds * repeats + 0.8) * 1000))


def upload_detect_and_listen(
    page: Page,
    clip: Path,
    expected: str,
    listen_label: str,
    t0: float,
    marks: dict[str, float],
    mark_key: str,
) -> None:
    page.get_by_role("tab", name="Upload file").click()
    page.locator("input[type='file']").set_input_files(str(clip))
    hold(page, 1200)
    marks[mark_key] = time.perf_counter() - t0
    play_clip(page, label=listen_label, seconds=clip_seconds(clip), repeats=2)
    page.get_by_role("button", name="Detect").click()
    page.get_by_text("Verdict").wait_for(timeout=90000)
    page.get_by_text("Verdict").scroll_into_view_if_needed()
    page.get_by_text(expected, exact=True).first.wait_for(timeout=15000)
    hold(page, 6000)


def write_doubled_wav(src: Path, dest: Path) -> None:
    samples, rate = sf.read(str(src))
    doubled = np.concatenate([samples, samples])
    dest.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(dest), doubled, rate)


def mux_audio(webm: Path, mp4: Path, marks: dict[str, float]) -> None:
    human_ms = max(0, int(marks["human"] * 1000))
    ai_ms = max(0, int(marks["ai"] * 1000))
    human_wav = OUT_DIR / "_human_x2.wav"
    ai_wav = OUT_DIR / "_ai_x2.wav"
    write_doubled_wav(HUMAN_CLIP, human_wav)
    write_doubled_wav(AI_CLIP, ai_wav)
    ff = ffmpeg_bin()
    cmd = [
        ff,
        "-y",
        "-i",
        str(webm),
        "-i",
        str(human_wav),
        "-i",
        str(ai_wav),
        "-filter_complex",
        (
            f"[1:a]aformat=channel_layouts=stereo,volume=5,adelay={human_ms}:all=1[h];"
            f"[2:a]aformat=channel_layouts=stereo,volume=5,adelay={ai_ms}:all=1[a];"
            "[h][a]amix=inputs=2:duration=longest:normalize=0,apad[aout]"
        ),
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
        "-shortest",
        "-movflags",
        "+faststart",
        str(mp4),
    ]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True)
    human_wav.unlink(missing_ok=True)
    ai_wav.unlink(missing_ok=True)
    if completed.returncode != 0 or not mp4.is_file():
        raise RuntimeError(completed.stderr[-2000:] if completed.stderr else "ffmpeg mux failed")


def record() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
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
            "VaaniQ live system demo",
            [
                "One complete walkthrough of the running React + FastAPI stack",
                "HUMAN audio = Kathbath real Hindi speech (you will hear it)",
                "AI audio = IndicSynth generated Hindi speech (you will hear it)",
                "Frozen result: 91.61% accuracy, 6.56% EER, n=584, speaker-disjoint",
                "Languages: Hindi, Marathi, Tamil. Telugu is not in this project.",
            ],
            6500,
        )
        title_card(
            page,
            "Full demonstration map",
            [
                "Home, dashboard, datasets",
                "Upload HUMAN speech -> listen twice -> detect REAL",
                "Upload AI speech -> listen twice -> detect FAKE",
                "Inference, history, calibration, explainability",
                "Metrics, experiments, human-study protocol (N=0), live, admin, API docs",
            ],
            5500,
        )
        open_app(
            page, "/", "Home",
            "Calibrated detection of AI-generated voice in Indian languages.", 4000,
        )
        open_app(
            page, "/dashboard", "Dashboard  |  Frozen Baseline V1",
            "n=584  |  91.61% acc  |  6.56% EER  |  ROC-AUC 0.9729  |  speaker-disjoint", 7000,
        )
        open_app(
            page, "/datasets", "Datasets  |  Kathbath real + IndicSynth fake",
            "2,346 evaluation instances. Hindi, Marathi, Tamil. Bounded V1 subset.", 5000,
        )
        open_app(
            page, "/upload", "UPLOAD 1 of 2  |  HUMAN audio  |  speakers on",
            "Ground truth REAL  |  Kathbath  |  Hindi  |  hi-real-dc1d927e3f9f02cf", 2000,
        )
        upload_detect_and_listen(
            page,
            HUMAN_CLIP,
            "real",
            "HUMAN SPEECH  |  Kathbath REAL  |  Hindi",
            t0,
            marks,
            "human",
        )
        overlay(
            page,
            "RESULT  |  HUMAN clip labeled REAL",
            "You just heard bona fide Kathbath speech. Verdict, confidence, reliability badge.",
        )
        hold(page, 4000)

        open_app(
            page, "/upload", "UPLOAD 2 of 2  |  AI audio  |  speakers on",
            "Ground truth FAKE  |  IndicSynth  |  Hindi  |  hi-fake-2710dee28900583a", 2000,
        )
        upload_detect_and_listen(
            page,
            AI_CLIP,
            "fake",
            "AI-GENERATED SPEECH  |  IndicSynth FAKE  |  Hindi",
            t0,
            marks,
            "ai",
        )
        overlay(
            page,
            "RESULT  |  AI clip labeled FAKE",
            "Same detector, threshold 0.5. FAKE is the positive class.",
        )
        hold(page, 4000)

        open_app(page, "/inference", "Inference", "Latest live verdict from the AI clip.", 4000)
        open_app(page, "/history", "History", "HUMAN vs AI detections in this session.", 4500)
        open_app(
            page, "/calibration", "RQ4 Calibration",
            "Temperature scaling, ECE, Brier, reliability diagram. Fit on validation only.", 5000,
        )
        open_app(
            page, "/explainability", "Explainability",
            "Grad-CAM proxy, spectrogram, attention, compression artefacts.", 5000,
        )
        open_app(
            page, "/research-metrics", "Live metrics panel",
            "Session view. Canonical numbers: artifacts/final_results_manifest.json", 4500,
        )
        open_app(
            page, "/experiments", "Experiments",
            "RQ1 Opus, RQ2 English-only, RQ3 leave-one-language, RQ4 calibration.", 5000,
        )
        open_app(
            page, "/human-study", "RQ5 Human study  |  protocol ready, N=0",
            "No listener data was fabricated.", 5000,
        )
        open_app(
            page, "/live", "Live microphone",
            "In viva: click Start and speak. This recording uses file uploads with audible clips.", 3500,
        )
        open_app(
            page, "/admin", "Admin health",
            "Local stack, git SHA, hardware snapshot.", 3500,
        )
        open_app(
            page, "/docs", "In-app documentation",
            "Proposal, architecture, datasets, known limitations.", 3500,
        )
        page.goto(f"{API}/docs", wait_until="networkidle")
        overlay(
            page,
            "FastAPI OpenAPI  |  http://127.0.0.1:8001/docs",
            "Upload, infer, calibrate, explain, human-study are typed API routes.",
        )
        hold(page, 4500)
        title_card(
            page,
            "Honest close",
            [
                "RQ1-RQ4 COMPLETE on bounded V1; Baseline 91.61% / 6.56% EER",
                "Frozen XLS-R: 92.12% accuracy, 0.9828 ROC-AUC",
                "Limit: V1 source correlates with label (Kathbath=real, IndicSynth=fake)",
                "PENDING/PILOT: faithful RawNet2, generator-disjoint, FLEURS n=9, RQ5 N=0",
                "Research prototype for Hindi, Marathi, Tamil. Not a production scam detector.",
            ],
            7000,
        )

        page.close()
        context.close()
        browser.close()

    videos = list(raw_dir.glob("*.webm"))
    if not videos:
        raise FileNotFoundError("Playwright did not write a webm")
    webm = videos[0]
    (OUT_DIR / "audio_cues.json").write_text(json.dumps(marks, indent=2), encoding="utf-8")
    mux_audio(webm, FINAL_MP4, marks)
    shutil.rmtree(raw_dir, ignore_errors=True)
    extra_webm = OUT_DIR / "VaaniQ_Examiner_Demo.webm"
    if extra_webm.is_file():
        extra_webm.unlink()
    return FINAL_MP4


def main() -> int:
    require_stack()
    path = record()
    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"DEMO_VIDEO={path}")
    print(f"SIZE_MB={size_mb:.1f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
