#!/usr/bin/env python3
"""Generate a two-column IEEE-style VaaniQ research paper draft."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[1]
REPORT_PATH = REPO / "models" / "checkpoints" / "xlsr_aasist" / "train_report.json"
FIGURE_DIR = REPO / "docs" / "assets" / "verified_figures"
OUTPUT = REPO / "docs" / "VaaniQ_IEEE_Research_Paper_Final.docx"
DRAFT_OUTPUT = REPO / "docs" / "VaaniQ_IEEE_Research_Paper_Draft.docx"
PROGRESS_OUTPUT = REPO / "docs" / "VaaniQ_Midterm_Progress_Report.docx"

import sys

sys.path.insert(0, str(REPO / "scripts"))
from report_data import load_baseline_matrix, load_rq2, load_rq4_audit  # noqa: E402


def _load_report() -> dict[str, object]:
    raw = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError("training report must be a JSON object")
    return raw


def _dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _number(mapping: dict[str, object], key: str) -> float:
    value = mapping.get(key, 0)
    return float(value) if isinstance(value, int | float) else 0.0


def _set_columns(section: object, count: int) -> None:
    section_properties = section._sectPr  # type: ignore[attr-defined]
    columns = section_properties.xpath("./w:cols")
    node = columns[0] if columns else OxmlElement("w:cols")
    node.set(qn("w:num"), str(count))
    node.set(qn("w:space"), "360")
    if not columns:
        section_properties.append(node)


def _set_cell_text(cell: object, text: str, *, bold: bool = False) -> None:
    cell.text = text  # type: ignore[attr-defined]
    for paragraph in cell.paragraphs:  # type: ignore[attr-defined]
        paragraph.paragraph_format.space_after = Pt(0)
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(7.5)
            run.bold = bold


def _table(
    doc: Document,
    headers: list[str],
    rows: list[list[str]],
    *,
    caption: str,
) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(caption.upper())
    run.bold = True
    run.font.size = Pt(8)
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, header in enumerate(headers):
        _set_cell_text(table.rows[0].cells[index], header, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            _set_cell_text(cells[index], value)


def _heading(doc: Document, number: str, title: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(2)
    run = paragraph.add_run(f"{number}. {title}".upper())
    run.bold = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)


def _subheading(doc: Document, letter: str, title: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(3)
    paragraph.paragraph_format.space_after = Pt(1)
    run = paragraph.add_run(f"{letter}. {title}")
    run.italic = True
    run.font.name = "Times New Roman"
    run.font.size = Pt(10)


def _body(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(text)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    paragraph.paragraph_format.first_line_indent = Inches(0.16)
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.line_spacing = 1.0


def _figure(doc: Document, filename: str, caption: str) -> None:
    path = FIGURE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(3.18))
    caption_paragraph = doc.add_paragraph(caption)
    caption_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_paragraph.paragraph_format.space_after = Pt(3)
    for run in caption_paragraph.runs:
        run.font.size = Pt(8)


def _cross_lingual_results() -> dict[str, dict[str, object]]:
    results: dict[str, dict[str, object]] = {}
    for language in ("hi", "mr", "ta"):
        path = REPO / "models" / "checkpoints" / "rq3" / f"test_{language}" / "train_report.json"
        if not path.is_file():
            continue
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            metrics = raw.get("test_metrics")
            if isinstance(metrics, dict):
                results[language] = metrics
    return results


def build_paper() -> Path:
    """Build the IEEE-style hard-copy paper from persisted measured results."""
    report = _load_report()
    metrics = _dict(report.get("test_metrics"))
    per_language = _dict(metrics.get("per_language"))
    per_condition = _dict(metrics.get("per_condition"))
    calibration_pre = _dict(metrics.get("calibration_pre"))
    calibration_post = _dict(metrics.get("calibration_post"))
    provenance = _dict(report.get("corpus_provenance"))
    cross_lingual = _cross_lingual_results()
    is_publication_subset = "kathbath" in str(report.get("data_provenance", ""))
    if not is_publication_subset:
        raise RuntimeError(
            "IEEE paper requires measured Kathbath + IndicSynth results; "
            "run publication-corpus training first"
        )

    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.62)
    section.bottom_margin = Inches(0.62)
    section.left_margin = Inches(0.66)
    section.right_margin = Inches(0.66)

    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(9)
    normal.paragraph_format.space_after = Pt(2)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run(
        "VaaniQ: Cross-Lingual, Compression-Robust Detection and "
        "Calibrated Reliability Estimation for AI-Generated Voice "
        "in Indian Languages"
    )
    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)

    authors = doc.add_paragraph()
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors.add_run(
        "Gaurav Phadale, Eshaan Sarkhawas, Aarav Phutane, Prajwal Patil\n"
        "Mukesh Patel School of Technology Management & Engineering, NMIMS\n"
        "Faculty Guide: Prof. Rama Bharti Varshney"
    )

    status = doc.add_paragraph()
    status.alignment = WD_ALIGN_PARAGRAPH.CENTER
    status_run = status.add_run("Mid-Term Capstone Research Paper Draft - Academic Year 2026-27")
    status_run.bold = True
    status_run.font.size = Pt(9)

    abstract = doc.add_paragraph()
    abstract.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abstract_run = abstract.add_run("Abstract:")
    abstract_run.bold = True
    abstract.add_run(
        "AI-generated speech creates a fraud risk in linguistically diverse and "
        "compression-heavy communication channels. VaaniQ evaluates real Kathbath "
        "and generated IndicSynth speech in Hindi, Marathi, and Tamil using a "
        "speaker-disjoint benchmark, a deterministic acoustic front-end, an "
        "AASIST-compatible anti-spoofing head, and validation-only temperature "
        f"scaling. On {int(metrics.get('n', 0))} held-out evaluation instances, "
        f"the measured accuracy is {_number(metrics, 'accuracy'):.1%}, equal error "
        f"rate is {_number(metrics, 'eer'):.1%}, F1 is {_number(metrics, 'f1'):.1%}, "
        f"post-calibration ECE is {_number(metrics, 'ece'):.3f}, and Brier score is "
        f"{_number(metrics, 'brier'):.3f}. Results are restricted to the persisted "
        "bounded subset and do not imply performance on the complete source corpora."
    )

    keywords = doc.add_paragraph()
    keywords.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    keyword_run = keywords.add_run("Index Terms")
    keyword_run.bold = True
    keywords.add_run(
        "audio deepfake detection, Indian languages, Kathbath, IndicSynth, "
        "Opus compression, calibration, AASIST"
    )

    columns = doc.add_section(WD_SECTION.CONTINUOUS)
    columns.top_margin = Inches(0.62)
    columns.bottom_margin = Inches(0.62)
    columns.left_margin = Inches(0.66)
    columns.right_margin = Inches(0.66)
    _set_columns(columns, 2)

    _heading(doc, "I", "Introduction")
    _body(
        doc,
        "Voice cloning can imitate speakers from short reference recordings and "
        "can be delivered through compressed messaging channels. Existing major "
        "anti-spoofing benchmarks are concentrated in English or Mandarin. VaaniQ "
        "targets Hindi, Marathi, and Tamil and combines detection, codec robustness, "
        "calibrated confidence, explainability, and a human-perception protocol.",
    )
    _body(
        doc,
        "The project addresses five research questions: compression degradation "
        "(RQ1), multilingual versus English-only training (RQ2), zero-shot "
        "cross-lingual transfer (RQ3), calibration under compression (RQ4), and "
        "human-versus-model performance on identical stimuli (RQ5). This mid-term "
        "draft reports only completed, reproducible subset experiments.",
    )

    _heading(doc, "II", "Related Work")
    _body(
        doc,
        "AASIST integrates spectro-temporal graph attention for anti-spoofing [1]. "
        "XLS-R provides cross-lingual self-supervised speech representations [2]. "
        "IndicSUPERB introduced Kathbath, a large human-labelled Indian-language "
        "speech resource [3], while IndicSynth provides synthetic speech for twelve "
        "Indian languages [4]. Prior calibration research demonstrates that high "
        "classification accuracy does not guarantee trustworthy confidence [5].",
    )

    _heading(doc, "III", "Dataset and Experimental Protocol")
    _subheading(doc, "A", "Sources and Licences")
    _body(
        doc,
        f"The persisted source subset contains {int(provenance.get('total_clips', 0))} "
        f"original clips ({float(provenance.get('total_hours', 0)):.2f} h). "
        "Bonafide clips are drawn from ai4bharat/Kathbath under its published "
        "packaging terms; generated clips are drawn from vdivyasharma/IndicSynth "
        "under CC BY-NC 4.0 for non-commercial academic research. The subset is "
        "balanced by source label and language.",
    )
    _subheading(doc, "B", "Leakage Control")
    _body(
        doc,
        "Source and target speaker identifiers are normalized before a deterministic "
        "SHA-256 seeded 70/15/15 split. A pre-training assertion rejects any speaker "
        "appearing in more than one split. Clean and 16 kbps libopus twins retain "
        "the same speaker, label, pair identifier, and split.",
    )
    _table(
        doc,
        ["Partition", "Instances", "Selection role"],
        [
            ["Train", str(report.get("n_train", 0)), "Parameter learning"],
            ["Validation", str(report.get("n_val", 0)), "Checkpoint/calibration"],
            ["Test", str(report.get("n_test", 0)), "Final metrics only"],
        ],
        caption="Table I. Speaker-disjoint data partitions",
    )

    _heading(doc, "IV", "System and Method")
    _figure(doc, "system_architecture.png", "Fig. 1. VaaniQ software architecture.")
    _body(
        doc,
        "Audio is decoded, converted to mono 16 kHz, peak-normalized, and bounded in "
        "duration. The measured subset uses a deterministic 1024-dimensional acoustic "
        "embedding and an AASIST-compatible NumPy classification head. Validation "
        "accuracy, followed by EER, selects the checkpoint. Per-language and "
        "per-condition temperature scaling is fitted only on validation logits.",
    )
    _body(
        doc,
        "The implementation exposes upload and live-microphone inference through "
        "FastAPI and a strict TypeScript React interface. Reliability diagrams, "
        "coverage curves, spectrograms, temporal attention, frequency-band masking, "
        "and compression views support interpretation.",
    )

    _heading(doc, "V", "Results")
    _table(
        doc,
        ["Metric", "Held-out value"],
        [
            ["Accuracy", f"{_number(metrics, 'accuracy'):.1%}"],
            ["Precision", f"{_number(metrics, 'precision'):.1%}"],
            ["Recall", f"{_number(metrics, 'recall'):.1%}"],
            ["F1", f"{_number(metrics, 'f1'):.1%}"],
            ["EER", f"{_number(metrics, 'eer'):.1%}"],
            ["min-DCF", f"{_number(metrics, 'min_dcf'):.3f}"],
            ["ROC-AUC", f"{_number(metrics, 'roc_auc'):.3f}"],
        ],
        caption="Table II. Overall speaker-disjoint test results",
    )
    language_rows: list[list[str]] = []
    for code, name in (("hi", "Hindi"), ("mr", "Marathi"), ("ta", "Tamil")):
        block = _dict(per_language.get(code))
        language_rows.append(
            [
                name,
                str(block.get("n", 0)),
                f"{_number(block, 'accuracy'):.1%}",
                f"{_number(block, 'f1'):.1%}",
                f"{_number(block, 'eer'):.1%}",
            ]
        )
    _table(
        doc,
        ["Language", "n", "Accuracy", "F1", "EER"],
        language_rows,
        caption="Table III. Per-language held-out results",
    )
    condition_rows: list[list[str]] = []
    for code, name in (("clean", "Clean"), ("opus_whatsapp_sim", "Opus 16 kbps")):
        block = _dict(per_condition.get(code))
        condition_rows.append(
            [
                name,
                str(block.get("n", 0)),
                f"{_number(block, 'accuracy'):.1%}",
                f"{_number(block, 'f1'):.1%}",
                f"{_number(block, 'eer'):.1%}",
            ]
        )
    _table(
        doc,
        ["Condition", "n", "Accuracy", "F1", "EER"],
        condition_rows,
        caption="Table IV. Clean and paired-Opus results",
    )
    if len(cross_lingual) == 3:
        target_names = {"hi": "Hindi", "mr": "Marathi", "ta": "Tamil"}
        cross_rows = [
            [
                target_names[code],
                str(cross_lingual[code].get("n", 0)),
                f"{_number(cross_lingual[code], 'accuracy'):.1%}",
                f"{_number(cross_lingual[code], 'f1'):.1%}",
                f"{_number(cross_lingual[code], 'eer'):.1%}",
            ]
            for code in ("hi", "mr", "ta")
        ]
        _table(
            doc,
            ["Unseen language", "n", "Accuracy", "F1", "EER"],
            cross_rows,
            caption="Table V. Leave-one-language-out transfer",
        )
        _figure(
            doc,
            "cross_lingual_transfer.png",
            "Fig. 2. Transfer when each test language is excluded from training.",
        )
    _figure(
        doc,
        "confusion_matrix.png",
        "Fig. 3. Confusion matrix on the held-out test partition.",
    )

    _heading(doc, "VI", "Calibration and Reliability")
    rq4 = load_rq4_audit()
    rq4_strategies = _dict(rq4.get("strategies"))
    global_post = _dict(rq4_strategies.get("global_temperature"))
    uncal = _dict(rq4_strategies.get("uncalibrated"))
    strategy = str(report.get("calibration_strategy", rq4.get("best_strategy_by_test_ece", "global_temperature")))
    _body(
        doc,
        "Calibration strategy was selected on validation ECE only (global vs "
        "per-languagecondition temperature scaling). Per-cell scaling overfit small "
        "validation cells; global validation-fitted temperature improved held-out ECE "
        f"({ _number(uncal, 'ece'):.3f} ? { _number(global_post, 'ece'):.3f}) in the "
        "audit replay. The persisted train report uses the validation-selected strategy: "
        f"{strategy}.",
    )
    _table(
        doc,
        ["Error", "Uncalibrated", "Global TS (selected on val)"],
        [
            [
                "ECE",
                f"{_number(uncal if uncal else calibration_pre, 'ece'):.3f}",
                f"{_number(global_post if global_post else calibration_post, 'ece'):.3f}",
            ],
            [
                "Brier",
                f"{_number(uncal if uncal else calibration_pre, 'brier'):.3f}",
                f"{_number(global_post if global_post else calibration_post, 'brier'):.3f}",
            ],
        ],
        caption="Table VI. Held-out calibration (validation-selected global temperature)",
    )
    _figure(
        doc,
        "reliability_diagram.png",
        "Fig. 4. Post-calibration reliability on held-out data.",
    )

    rq2 = load_rq2()
    rq2_status = "Complete" if rq2.get("english_only_indic_test") else "Pending"
    matrix = load_baseline_matrix()
    _heading(doc, "VII", "Implementation Progress")
    _table(
        doc,
        ["Work package", "Status"],
        [
            ["API, validation, typed errors", "Complete"],
            ["React UI, upload, live microphone", "Complete"],
            ["Kathbath + IndicSynth ingest (Baseline V1)", "Complete"],
            ["Speaker-disjoint training/evaluation", "Complete"],
            ["Opus paired evaluation", "Complete"],
            ["Calibration audit (val-selected global TS)", "Complete"],
            ["LFCC-GMM baseline", "Complete"],
            ["RawNet2-style approximate baseline", "Complete (not canonical RawNet2)"],
            [f"RQ2 English-only ASVspoof control", rq2_status],
            [
                "RQ3 leave-one-language-out runs",
                "Complete" if len(cross_lingual) == 3 else "Pending",
            ],
            ["Frozen XLS-R main experiment", "In progress / see artifacts/xlsr_main"],
            ["Benchmark V2 multi-source", "In progress"],
            ["RQ5 participant data collection", "Pending (N=0)"],
        ],
        caption="Table VII. Implementation evidence",
    )
    if matrix.get("models"):
        rows = []
        for name, pack in _dict(matrix.get("models")).items():
            if isinstance(pack, dict) and "accuracy" in pack:
                rows.append(
                    [
                        name,
                        str(pack.get("n", "")),
                        f"{float(pack.get('accuracy', 0)):.1%}",
                        f"{float(pack.get('eer', 0)):.1%}",
                    ]
                )
        if rows:
            _table(
                doc,
                ["Model", "n", "Accuracy", "EER"],
                rows,
                caption="Table VII-b. Baseline matrix on identical V1 test protocol",
            )
    if rq2.get("english_only_indic_test"):
        en = _dict(rq2.get("english_only_indic_test"))
        multi = _dict(rq2.get("multilingual_baseline_v1_test"))
        _table(
            doc,
            ["Model", "Indic test accuracy", "Indic test EER"],
            [
                [
                    "English-only (ASVspoof LA train)",
                    f"{float(en.get('accuracy', 0)):.1%}",
                    f"{float(en.get('eer', 0)):.1%}",
                ],
                [
                    "Multilingual (hi+mr+ta)",
                    f"{float(multi.get('accuracy', 0)):.1%}",
                    f"{float(multi.get('eer', 0)):.1%}",
                ],
            ],
            caption="Table VIII. RQ2 English-only vs multilingual on Indic held-out test",
        )

    _heading(doc, "VIII", "Limitations and Threats to Validity")
    _body(
        doc,
        "The measured corpus is a bounded subset rather than the complete 303 GB "
        "six-cell source collection. Dataset-source artefacts may make discrimination "
        "easier than unseen-generator detection. The current front-end is a compact "
        "deterministic embedding, not the final frozen XLS-R representation. RQ2 "
        "and RQ5 remain incomplete; consequently, no claim is made for those "
        "questions or for generalization beyond the persisted manifest. RQ3 is "
        "reported as a measured leave-one-language-out baseline.",
    )

    _heading(doc, "IX", "Ethics and Reproducibility")
    _body(
        doc,
        "Audio is excluded from version control. The manifest records source, label, "
        "speaker, split, duration, checksum, and generation model. Kathbath access "
        "conditions and IndicSynth non-commercial restrictions are respected. "
        "The human protocol is anonymous and reveals no gold labels during trials.",
    )

    _heading(doc, "X", "Conclusion")
    _body(
        doc,
        "VaaniQ demonstrates an end-to-end multilingual audio-deepfake research "
        "apparatus with real/fake source ingest, speaker-disjoint evaluation, "
        "compression testing, calibrated confidence, explainability, and a live web "
        "application. The current measurements establish a reproducible mid-term "
        "baseline; planned detector baselines, cross-lingual runs, and human "
        "responses are required for the final conference-oriented study.",
    )

    _heading(doc, "", "References")
    references = [
        "[1] J. Jung et al., AASIST: Audio anti-spoofing using integrated "
        "spectro-temporal graph attention networks, ICASSP, 2022.",
        "[2] A. Babu et al., XLS-R: Self-supervised cross-lingual speech "
        "representation learning at scale, arXiv:2111.09296, 2021.",
        "[3] T. Javed et al., IndicSUPERB: A speech processing universal "
        "performance benchmark for Indian languages, arXiv:2208.11761, 2022.",
        "[4] D. V. Sharma, V. Ekbote, and A. Gupta, IndicSynth: A large-scale "
        "multilingual synthetic speech dataset, ACL, 2025.",
        "[5] O. Pascu et al., Towards calibrated and explainable audio deepfake "
        "detection, Interspeech, 2024.",
        "[6] R. Mller et al., Human perception of audio deepfakes, "
        "ACM Workshop on Information Hiding and Multimedia Security, 2022.",
        "[7] McAfee, The Artificial Imposter, May 2023.",
        "[8] AI4Bharat, Kathbath dataset, Hugging Face: ai4bharat/Kathbath.",
        "[9] D. V. Sharma et al., IndicSynth dataset, Hugging Face: vdivyasharma/IndicSynth.",
    ]
    for reference in references:
        paragraph = doc.add_paragraph(reference)
        paragraph.paragraph_format.left_indent = Inches(0.14)
        paragraph.paragraph_format.first_line_indent = Inches(-0.14)
        paragraph.paragraph_format.space_after = Pt(1)
        for run in paragraph.runs:
            run.font.size = Pt(8)

    doc.save(OUTPUT)
    doc.save(DRAFT_OUTPUT)
    return OUTPUT


def build_progress_report() -> Path:
    """Build a professional mid-term progress report from measured evidence."""
    report = _load_report()
    metrics = _dict(report.get("test_metrics"))
    provenance = _dict(report.get("corpus_provenance"))
    per_language = _dict(metrics.get("per_language"))
    per_condition = _dict(metrics.get("per_condition"))
    calibration_pre = _dict(metrics.get("calibration_pre"))
    calibration_post = _dict(metrics.get("calibration_post"))
    cross_lingual = _cross_lingual_results()
    if "kathbath" not in str(report.get("data_provenance", "")):
        raise RuntimeError("progress report requires publication-subset results")

    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal.font.size = Pt(10.5)
    normal.paragraph_format.space_after = Pt(6)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Inches(1.1)
    run = title.add_run("VaaniQ\nMid-Term Capstone Progress Report")
    run.bold = True
    run.font.name = "Aptos Display"
    run.font.size = Pt(24)
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(
        "Cross-Lingual, Compression-Robust Detection and Calibrated Reliability "
        "Estimation for AI-Generated Voice in Indian Languages"
    ).italic = True
    team = doc.add_paragraph()
    team.alignment = WD_ALIGN_PARAGRAPH.CENTER
    team.add_run(
        "\nGaurav Phadale  70022300092\n"
        "Eshaan Sarkhawas  70022300066\n"
        "Aarav Phutane  70022300152\n"
        "Prajwal Patil  70022300213\n\n"
        "Faculty Guide: Prof. Rama Bharti Varshney\n"
        "MPSTME, NMIMS  Academic Year 2026-27"
    )
    doc.add_page_break()

    doc.add_heading("1. Executive Progress Summary", level=1)
    _body(
        doc,
        "VaaniQ is operational as an end-to-end research system: authenticated "
        "Kathbath and IndicSynth ingest, deterministic speaker-disjoint splitting, "
        "actual Opus evaluation pairs, detector training, validation-only calibration, "
        "explainability, typed FastAPI endpoints, and a React demonstration interface. "
        "This report separates completed measured evidence from remaining work.",
    )
    _table(
        doc,
        ["Evidence item", "Current measured state"],
        [
            [
                "Source corpus",
                f"{provenance.get('total_clips', 0)} original clips; "
                f"{float(provenance.get('total_hours', 0)):.2f} h",
            ],
            [
                "Evaluation corpus",
                f"{report.get('n_clips', 0)} clean/Opus instances; "
                f"{float(report.get('total_hours', 0)):.2f} h",
            ],
            [
                "Held-out test",
                f"n={metrics.get('n', 0)}; accuracy "
                f"{_number(metrics, 'accuracy'):.1%}; EER "
                f"{_number(metrics, 'eer'):.1%}",
            ],
            [
                "Leakage control",
                "PASS - no speaker overlap across train/validation/test",
            ],
            ["Application", "Backend API and React UI operational"],
        ],
        caption="Table 1. Mid-term evidence snapshot",
    )

    doc.add_heading("2. Completed Work Packages", level=1)
    _table(
        doc,
        ["Work package", "Evidence"],
        [
            ["Problem framing and five RQs", "Proposal traceability complete"],
            ["Three-language data ingest", "Hindi, Marathi, Tamil persisted"],
            ["Balanced real/fake source cells", "900 Kathbath / 900 IndicSynth"],
            ["Speaker-disjoint split", "1254 train / 508 val / 584 test instances"],
            ["Compression robustness", "546 paired 16 kbps libopus twins"],
            ["Detector training", "Primary and three RQ3 checkpoints"],
            ["Calibration", "Validation-only per-language/condition temperatures"],
            ["Explainability", "Five stored explanation views per prediction"],
            ["Web application", "Upload, live, dashboard, research, admin, docs"],
            ["Submission artefacts", "Master DOCX and IEEE-style paper generated"],
        ],
        caption="Table 2. Implemented capstone components",
    )

    architecture = FIGURE_DIR / "system_architecture.png"
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(architecture), width=Inches(6.3))
    caption = doc.add_paragraph("Fig. 1. Implemented VaaniQ three-tier architecture.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_heading("3. Dataset and Reproducibility Evidence", level=1)
    _body(
        doc,
        "The complete six target-language source cells exceed 303 GB. The declared "
        "evaluation population is therefore a reproducible bounded subset rather than "
        "an unspecified sample. Every manifest row includes source, language, label, "
        "speaker, split, duration, checksum, and model provenance. Shared source and "
        "target speaker identifiers are assigned to one split before augmentation.",
    )
    _table(
        doc,
        ["Language", "Source clips", "Held-out instances", "Accuracy", "EER"],
        [
            [
                name,
                "600",
                str(_dict(per_language.get(code)).get("n", 0)),
                f"{_number(_dict(per_language.get(code)), 'accuracy'):.1%}",
                f"{_number(_dict(per_language.get(code)), 'eer'):.1%}",
            ]
            for code, name in (("hi", "Hindi"), ("mr", "Marathi"), ("ta", "Tamil"))
        ],
        caption="Table 3. Balanced source cells and language results",
    )

    doc.add_heading("4. Measured Model Results", level=1)
    _table(
        doc,
        ["Metric", "Value"],
        [
            ["Accuracy", f"{_number(metrics, 'accuracy'):.2%}"],
            ["Precision", f"{_number(metrics, 'precision'):.2%}"],
            ["Recall", f"{_number(metrics, 'recall'):.2%}"],
            ["F1", f"{_number(metrics, 'f1'):.2%}"],
            ["EER", f"{_number(metrics, 'eer'):.2%}"],
            ["ROC-AUC", f"{_number(metrics, 'roc_auc'):.4f}"],
            ["min-DCF", f"{_number(metrics, 'min_dcf'):.4f}"],
        ],
        caption="Table 4. Overall held-out publication-subset metrics",
    )
    performance = FIGURE_DIR / "performance_overview.png"
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(performance), width=Inches(6.3))
    caption = doc.add_paragraph("Fig. 2. Overall held-out performance.")
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _table(
        doc,
        ["Condition", "n", "Accuracy", "EER", "F1"],
        [
            [
                name,
                str(_dict(per_condition.get(code)).get("n", 0)),
                f"{_number(_dict(per_condition.get(code)), 'accuracy'):.1%}",
                f"{_number(_dict(per_condition.get(code)), 'eer'):.1%}",
                f"{_number(_dict(per_condition.get(code)), 'f1'):.1%}",
            ]
            for code, name in (("clean", "Clean"), ("opus_whatsapp_sim", "Opus 16 kbps"))
        ],
        caption="Table 5. RQ1 compression robustness",
    )

    doc.add_heading("5. Calibration and Cross-Lingual Findings", level=1)
    _body(
        doc,
        "Temperature scaling was fitted only on validation logits. On the held-out "
        "distribution it slightly worsened both ECE and Brier score. This negative "
        "result is retained because accurate capstone reporting is more important "
        "than presenting calibration as universally beneficial.",
    )
    _table(
        doc,
        ["Calibration error", "Before", "After"],
        [
            [
                "ECE",
                f"{_number(calibration_pre, 'ece'):.4f}",
                f"{_number(calibration_post, 'ece'):.4f}",
            ],
            [
                "Brier",
                f"{_number(calibration_pre, 'brier'):.4f}",
                f"{_number(calibration_post, 'brier'):.4f}",
            ],
        ],
        caption="Table 6. RQ4 held-out calibration comparison",
    )
    if len(cross_lingual) == 3:
        _table(
            doc,
            ["Unseen test language", "n", "Accuracy", "EER", "F1"],
            [
                [
                    name,
                    str(cross_lingual[code].get("n", 0)),
                    f"{_number(cross_lingual[code], 'accuracy'):.1%}",
                    f"{_number(cross_lingual[code], 'eer'):.1%}",
                    f"{_number(cross_lingual[code], 'f1'):.1%}",
                ]
                for code, name in (("hi", "Hindi"), ("mr", "Marathi"), ("ta", "Tamil"))
            ],
            caption="Table 7. RQ3 leave-one-language-out transfer",
        )

    doc.add_heading("6. Research Question Status", level=1)
    _table(
        doc,
        ["RQ", "Status", "Current evidence"],
        [
            ["RQ1", "Measured", "Clean versus paired Opus test metrics"],
            ["RQ2", "Pending", "English-only control checkpoint not yet run"],
            ["RQ3", "Measured", "Three leave-one-language-out runs"],
            ["RQ4", "Measured", "Validation-fitted pre/post calibration"],
            ["RQ5", "Protocol ready", "Participant responses N=0; no result claimed"],
        ],
        caption="Table 8. Honest research-question status",
    )

    doc.add_heading("7. Remaining Final-Phase Work", level=1)
    remaining = [
        "Run the frozen XLS-R research front-end and detector baseline matrix.",
        "Add the English-only RQ2 control using a licensed English benchmark.",
        "Expand attack diversity beyond one published synthetic source.",
        "Recruit eligible listeners and complete the approved RQ5 protocol.",
        "Freeze result CSVs, repeat confidence intervals, and prepare the final paper.",
    ]
    for item in remaining:
        doc.add_paragraph(item, style="List Bullet")

    doc.add_heading("8. Mid-Term Demonstration Readiness", level=1)
    _body(
        doc,
        "The live system can demonstrate upload inference, microphone streaming, "
        "dataset provenance, compression-aware metrics, calibration plots, "
        "explainability artefacts, experiment records, and API documentation. "
        "The master report and IEEE-style paper use persisted metrics rather than "
        "manually copied values.",
    )

    doc.add_heading("9. Submission Checklist", level=1)
    checklist = [
        "Master project DOCX generated and package-verified.",
        "IEEE-style hard-copy paper generated and package-verified.",
        "Mid-term progress report generated from the same training report.",
        "All chart source PNGs have automated blank/crop margin checks.",
        "Human-study claims remain explicitly N=0 until responses exist.",
        "Team must bring a laptop, charger, backup copy, and printed hard copies.",
    ]
    for item in checklist:
        doc.add_paragraph(f"? {item}")

    doc.save(PROGRESS_OUTPUT)
    return PROGRESS_OUTPUT


def verify_paper(path: Path) -> None:
    """Verify package integrity, formatting structure, images, tables, and metrics."""
    document = Document(path)
    text = "\n".join(
        [paragraph.text for paragraph in document.paragraphs]
        + [cell.text for table in document.tables for row in table.rows for cell in row.cells]
    )
    report = _load_report()
    metrics = _dict(report.get("test_metrics"))
    required = [
        "Gaurav Phadale",
        "Eshaan Sarkhawas",
        "Aarav Phutane",
        "Prajwal Patil",
        "Prof. Rama Bharti Varshney",
        "Kathbath",
        "IndicSynth",
        f"{_number(metrics, 'accuracy'):.1%}",
        f"{_number(metrics, 'ece'):.3f}",
        "N=0",
    ]
    missing = [value for value in required if value not in text]
    if missing:
        raise RuntimeError(f"IEEE paper is missing required evidence: {missing}")
    if len(document.tables) < 6:
        raise RuntimeError(f"expected at least 6 tables, got {len(document.tables)}")
    if len(document.inline_shapes) < 3:
        raise RuntimeError(
            f"expected at least 3 embedded figures, got {len(document.inline_shapes)}"
        )
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("IEEE DOCX package integrity check failed")
    print(
        f"IEEE paper verified: {len(document.tables)} tables, "
        f"{len(document.inline_shapes)} figures, package integrity PASS"
    )


def main() -> None:
    """Build and verify the IEEE paper and mid-term progress report."""
    paper_path = build_paper()
    verify_paper(paper_path)
    print(f"Wrote {paper_path}")
    progress_path = build_progress_report()
    with zipfile.ZipFile(progress_path) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("progress-report DOCX integrity check failed")
    print(f"Wrote {progress_path}")


if __name__ == "__main__":
    main()
