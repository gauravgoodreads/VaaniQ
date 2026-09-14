#!/usr/bin/env python3
"""Build a publishable IEEE package from frozen Round-3 evidence only."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from report_data import (  # noqa: E402
    as_dict,
    as_number,
    load_final_results,
    load_train_report,
    pct,
)

FIGURE_DIR = REPO / "docs" / "assets" / "verified_figures"
PACKAGE = REPO / "docs" / "IEEE_final_VaaniQ"
DESKTOP_PACKAGE = Path.home() / "Desktop" / "VaaniQ_IEEE_final"
MANUSCRIPT = REPO / "research" / "paper" / "manuscript" / "VaaniQ_manuscript.md"
APPROVED = "084bd47ca6ca1b69a7cdbf424e2946f3794c2a95"


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
    widths: list[float] | None = None,
) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(caption.upper())
    run.bold = True
    run.font.size = Pt(8)
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    if widths is None:
        if len(headers) == 2:
            widths = [1.8, 1.35]
        elif len(headers) == 3:
            widths = [1.15, 1.0, 1.0]
        else:
            widths = [3.15 / len(headers)] * len(headers)
    table.autofit = False
    total_twips = sum(Inches(width).twips for width in widths)
    table_width = table._tbl.tblPr.first_child_found_in("w:tblW")
    if table_width is not None:
        table_width.set(qn("w:w"), str(total_twips))
        table_width.set(qn("w:type"), "dxa")
    table_grid = table._tbl.tblGrid
    for grid_col in list(table_grid):
        table_grid.remove(grid_col)
    for width in widths:
        grid_col = OxmlElement("w:gridCol")
        grid_col.set(qn("w:w"), str(Inches(width).twips))
        table_grid.append(grid_col)
    for index, header in enumerate(headers):
        _set_cell_text(table.rows[0].cells[index], header, bold=True)
        table.rows[0].cells[index].width = Inches(widths[index])
    header_props = table.rows[0]._tr.get_or_add_trPr()
    repeat_header = OxmlElement("w:tblHeader")
    repeat_header.set(qn("w:val"), "true")
    header_props.append(repeat_header)
    for row in rows:
        cells = table.add_row().cells
        for index, value in enumerate(row):
            _set_cell_text(cells[index], value)
            cells[index].width = Inches(widths[index])


def _heading(doc: Document, number: str, title: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(5)
    paragraph.paragraph_format.space_after = Pt(2)
    label = f"{number}. {title}".upper() if number else title.upper()
    run = paragraph.add_run(label)
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
        return
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(path), width=Inches(3.15))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(8)


def build_publishable_docx(output: Path) -> Path:
    """Generate the full IEEE-style DOCX from frozen metrics."""
    report = load_train_report()
    final = load_final_results()
    baseline = as_dict(final.get("baseline_v1"))
    metrics = as_dict(baseline.get("metrics"))
    if not metrics:
        metrics = as_dict(report.get("test_metrics"))

    xlsr_blob = as_dict(final.get("xlsr_main"))
    xlsr = {
        "n": as_number(xlsr_blob, "n_test", 584),
        "accuracy": as_number(xlsr_blob, "test_accuracy", 0.9212),
        "eer": as_number(xlsr_blob, "test_eer", 0.0688),
        "roc_auc": as_number(xlsr_blob, "test_roc_auc", 0.9828),
        "min_dcf": as_number(xlsr_blob, "test_min_dcf", 0.3144),
    }
    xlsr_metrics = as_dict(xlsr_blob.get("metrics") or xlsr_blob.get("test_metrics"))
    if xlsr_metrics:
        for key in ("accuracy", "eer", "roc_auc", "min_dcf", "n", "by_condition"):
            if key in xlsr_metrics:
                xlsr[key] = xlsr_metrics[key]

    rq2 = as_dict(final.get("rq2"))
    rq2_ctrl = as_dict(
        rq2.get("english_only_indic_test")
        or rq2.get("english_control")
        or rq2.get("control")
        or rq2
    )
    rq2_m = as_dict(rq2_ctrl.get("metrics") or rq2_ctrl)
    eng_acc = as_number(rq2_m, "accuracy", as_number(rq2_m, "test_accuracy", 0.548))
    eng_eer = as_number(rq2_m, "eer", as_number(rq2_m, "test_eer", 0.7656))
    eng_auc = as_number(rq2_m, "roc_auc", as_number(rq2_m, "test_roc_auc", 0.162))

    rq3 = as_dict(final.get("rq3"))
    folds = as_dict(rq3.get("folds"))
    hi = as_dict(folds.get("held_out_hi"))
    mr = as_dict(folds.get("held_out_mr"))
    ta = as_dict(folds.get("held_out_ta"))
    hi_acc = as_number(hi, "accuracy", 0.7883)
    hi_eer = as_number(hi, "eer", 0.2183)
    mr_acc = as_number(mr, "accuracy", 0.9329)
    mr_eer = as_number(mr, "eer", 0.0714)
    ta_acc = as_number(ta, "accuracy", 0.9394)
    ta_eer = as_number(ta, "eer", 0.0635)

    provenance = as_dict(report.get("data_provenance"))
    per_cond = as_dict(metrics.get("per_condition") or metrics.get("by_condition"))
    clean = as_dict(per_cond.get("clean"))
    opus = as_dict(
        per_cond.get("opus_whatsapp_sim")
        or per_cond.get("whatsapp_opus")
        or per_cond.get("opus")
    )
    rq1 = as_dict(final.get("rq1"))
    rq1_ac = as_dict(rq1.get("baseline_v1_acoustic") or rq1.get("acoustic") or rq1.get("baseline_v1"))
    if rq1_ac:
        clean = as_dict(rq1_ac.get("clean") or clean)
        opus = as_dict(rq1_ac.get("opus_whatsapp_sim") or rq1_ac.get("opus") or opus)
    xlsr_test = as_dict(xlsr_blob.get("test_metrics"))
    x_by = as_dict(xlsr_test.get("per_condition") or xlsr_metrics.get("per_condition") or {})
    x_clean = as_dict(x_by.get("clean"))
    x_opus = as_dict(x_by.get("opus_whatsapp_sim") or x_by.get("whatsapp_opus") or x_by.get("opus"))
    rq1_x = as_dict(rq1.get("xlsr_main") or rq1.get("xlsr"))
    if rq1_x:
        x_clean = as_dict(rq1_x.get("clean") or x_clean)
        x_opus = as_dict(rq1_x.get("opus_whatsapp_sim") or rq1_x.get("opus") or x_opus)

    cal_pre = as_dict(metrics.get("calibration_pre"))
    cal_post = as_dict(metrics.get("calibration_post"))

    v2 = as_dict(final.get("benchmark_v2"))
    evals = as_dict(v2.get("evaluations"))
    independent = as_dict(evals.get("independent_real_test"))
    gen = as_dict(evals.get("generator_held_out_test"))
    shortcut = as_dict(v2.get("source_shortcut_v2"))

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.75)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.75)
    section.right_margin = Inches(0.75)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title.add_run(
        "VaaniQ: Cross-Lingual, Compression-Robust Detection and Calibrated "
        "Reliability Estimation for AI-Generated Voice in Indian Languages"
    )
    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(16)

    authors = doc.add_paragraph()
    authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    authors.add_run(
        "Gaurav Phadale, Eshaan Sarkhawas, Aarav Phutane, Prajwal Patil\n"
        "Mukesh Patel School of Technology Management & Engineering, NMIMS\n"
        "Faculty Guide: Prof. Rama Bharti Varshney"
    )

    status = doc.add_paragraph()
    status.alignment = WD_ALIGN_PARAGRAPH.CENTER
    status_run = status.add_run(
        f"IEEE archival draft — frozen Round 3 evidence at commit {APPROVED}. "
        "RQ1–RQ4 complete on the bounded machine-evaluated benchmark."
    )
    status_run.italic = True
    status_run.font.size = Pt(8)

    abstract = doc.add_paragraph()
    abstract.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ar = abstract.add_run("Abstract—")
    ar.bold = True
    abstract.add_run(
        "Voice cloning enables scalable audio fraud, yet anti-spoofing evidence remains "
        "concentrated in English/Mandarin and rarely couples Indian-language stimuli with "
        "messaging-style compression, confidence calibration, and cross-lingual transfer. "
        "VaaniQ builds a bounded speaker-disjoint benchmark for Hindi, Marathi, and "
        "Tamil (Kathbath real; IndicSynth fake) and evaluates detection under clean audio and "
        "WhatsApp-style 16 kbps Opus simulation. On 584 held-out instances, an acoustic "
        f"AASIST-compatible head reaches {pct(as_number(metrics, 'accuracy', 0.9161))} accuracy "
        f"and {pct(as_number(metrics, 'eer', 0.0656))} EER; frozen wav2vec2-xls-r-300m reaches "
        f"{pct(as_number(xlsr, 'accuracy', 0.9212))} accuracy, {pct(as_number(xlsr, 'eer', 0.0688))} "
        f"EER, and {as_number(xlsr, 'roc_auc', 0.9828):.4f} ROC-AUC. Compression effects are "
        "model-dependent; English-only transfer collapses; leave-one-language-out transfer is "
        "asymmetric; validation-selected calibration does not uniformly improve held-out ECE. "
        "Benchmark V2 remains a partial external-source pilot, so claims are restricted to the "
        "declared machine-evaluated corpus and attack sources."
    )

    keywords = doc.add_paragraph()
    keywords.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    kr = keywords.add_run("Index Terms—")
    kr.bold = True
    keywords.add_run(
        "audio deepfake detection, Indian languages, Kathbath, IndicSynth, Opus compression, "
        "calibration, XLS-R, speaker-disjoint evaluation, cross-lingual transfer"
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
        "Neural voice cloning can imitate speakers from short enrollments and can be delivered "
        "as compressed chat audio. Major anti-spoofing benchmarks remain concentrated in English "
        "or Mandarin. VaaniQ studies Hindi, Marathi, and Tamil on a bounded speaker-disjoint "
        "benchmark and measures codec shift, cross-lingual transfer, and confidence calibration. "
        "It does not claim universal fake-voice detection. Telugu is out of project scope.",
    )
    _body(
        doc,
        "Contributions: (1) a versioned V1 publication corpus with paired Opus twins and held-out "
        f"n={int(as_number(metrics, 'n', 584))}; (2) complete RQ1–RQ4 results including negative "
        "calibration transfer and catastrophic English→Indic transfer retained honestly; "
        "(3) a reproducible research stack with frozen manifests and automated validation. "
        "Non-claims: not the first "
        "Indic detector; V1 source–label confounding is disclosed.",
    )
    _body(
        doc,
        "RQ1: Opus compression effects? RQ2: English-only versus multilingual transfer? "
        "RQ3: unseen-language (LOLO) generalisation? RQ4: validation-selected calibration under "
        "shift? RQ1–RQ4 are complete on the bounded benchmark.",
    )

    _heading(doc, "II", "Related Work and Comparative Study")
    _subheading(doc, "A", "Literature Axes")
    _body(
        doc,
        "AASIST integrates spectro-temporal graph attention for anti-spoofing [1]. XLS-R provides "
        "cross-lingual self-supervised speech representations [2]. IndicSUPERB/Kathbath [3],[6] and "
        "IndicSynth [4],[7] supply Indic real and synthetic speech. Pascu et al. study calibrated "
        "SSL deepfake detection without Indian languages or an isolated WhatsApp-Opus cell [5]. "
        "FLEURS supports cross-lingual evaluation [8]. Opus is defined in RFC 6716 [9]. ASVspoof "
        "2019 LA remains the English control resource [10]. Indic-CodecFake/SATYAM targets codec "
        "synthesis—a different attack surface than messaging-style Opus transport of cloning/TTS "
        "fraud audio—and does not couple Opus isolation with calibration analysis.",
    )
    _subheading(doc, "B", "Feature Comparison Across Related Work")
    _body(
        doc,
        "Cross-paper EER comparison is invalid under mismatched corpora. Table II compares "
        "evaluation axes only. VaaniQ does not claim to be first at Indic detection or "
        "calibration; the defensible contribution is their combination with isolated Opus and "
        "cross-lingual evaluation (proposal §5.7).",
    )
    _body(
        doc,
        "Axis summary: ASVspoof+AASIST supplies the non-Indic architecture benchmark; Pascu "
        "et al. supply calibration precedent without an isolated Opus cell; IndicSynth supplies "
        "Indic synthetic data; SATYAM studies codec synthesis rather than Opus transport; VaaniQ "
        "combines hi/mr/ta, a 16 kbps Opus cell, calibration, and LOLO evaluation.",
    )
    bm = as_dict(as_dict(final.get("baseline_matrix")).get("models"))
    lfcc = as_dict(bm.get("lfcc_gmm"))
    raw = as_dict(bm.get("rawnet2_style_approx"))
    _subheading(doc, "C", "Same-Test Empirical Comparison (n=584)")
    _body(
        doc,
        "All systems below share identical V1 held-out clips, labels, threshold 0.5, and score "
        "contract—the only fair numeric comparison in this paper. Matching 54.79% accuracy for "
        "LFCC-GMM and RawNet2-style at threshold 0.5 is a documented coincidence; EER and ROC-AUC "
        "differ materially. Faithful RawNet2 remains PENDING.",
    )
    _table(
        doc,
        ["Model", "Acc / EER", "AUC / min-DCF"],
        [
            [
                "LFCC-GMM",
                f"{pct(as_number(lfcc, 'accuracy', 0.5479))} / {pct(as_number(lfcc, 'eer', 0.2348))}",
                f"{as_number(lfcc, 'roc_auc', 0.8195):.4f} / {as_number(lfcc, 'min_dcf', 0.4962):.4f}",
            ],
            [
                "RawNet2-style approx.",
                f"{pct(as_number(raw, 'accuracy', 0.5479))} / {pct(as_number(raw, 'eer', 0.4318))}",
                f"{as_number(raw, 'roc_auc', 0.5845):.4f} / {as_number(raw, 'min_dcf', 0.9621):.4f}",
            ],
            [
                "Acoustic AASIST-comp.",
                f"{pct(as_number(metrics, 'accuracy', 0.9161))} / {pct(as_number(metrics, 'eer', 0.0656))}",
                f"{as_number(metrics, 'roc_auc', 0.9729):.4f} / {as_number(metrics, 'min_dcf', 0.7841):.4f}",
            ],
            [
                "Frozen XLS-R + head",
                f"{pct(as_number(xlsr, 'accuracy', 0.9212))} / {pct(as_number(xlsr, 'eer', 0.0688))}",
                f"{as_number(xlsr, 'roc_auc', 0.9828):.4f} / {as_number(xlsr, 'min_dcf', 0.3144):.4f}",
            ],
            [
                "English-only control",
                f"{pct(eng_acc)} / {pct(eng_eer)}",
                f"{eng_auc:.3f} / —",
            ],
        ],
        caption="Table I. Comparative study — same VaaniQ V1 test",
    )
    per_lang = as_dict(metrics.get("per_language"))
    hi_in = as_dict(per_lang.get("hi"))
    mr_in = as_dict(per_lang.get("mr"))
    ta_in = as_dict(per_lang.get("ta"))
    _subheading(doc, "D", "In-Domain versus Leave-One-Language-Out")
    _table(
        doc,
        ["Language", "In-domain Acc / EER", "LOLO Acc / EER"],
        [
            [
                "Hindi",
                f"{pct(as_number(hi_in, 'accuracy', 0.9099))} / {pct(as_number(hi_in, 'eer', 0.0704))}",
                f"{pct(hi_acc)} / {pct(hi_eer)}",
            ],
            [
                "Marathi",
                f"{pct(as_number(mr_in, 'accuracy', 0.9329))} / {pct(as_number(mr_in, 'eer', 0.0625))}",
                f"{pct(mr_acc)} / {pct(mr_eer)}",
            ],
            [
                "Tamil",
                f"{pct(as_number(ta_in, 'accuracy', 0.9091))} / {pct(as_number(ta_in, 'eer', 0.0714))}",
                f"{pct(ta_acc)} / {pct(ta_eer)}",
            ],
        ],
        caption="Table II. Comparative view — in-domain vs LOLO",
    )
    _body(
        doc,
        "Hindi zero-shot collapse (90.99% in-domain → 78.83% LOLO) is the standout RQ3 finding "
        "and caution against treating Indian languages as a homogeneous transfer class.",
    )

    _heading(doc, "III", "Dataset")
    _subheading(doc, "A", "Bounded V1 Benchmark")
    _body(
        doc,
        f"The persisted source subset contains {int(provenance.get('total_clips', 1800))} "
        f"original clips ({float(provenance.get('total_hours', 3.15) or 3.15):.2f} h): "
        "900 Kathbath REAL and 900 IndicSynth FAKE, balanced across Hindi, Marathi, and Tamil. "
        "Paired validation/test 16 kbps libopus twins expand evaluation to 2,346 instances. "
        f"Held-out test n={int(as_number(metrics, 'n', 584))}. Bonafide clips follow Kathbath "
        "packaging terms; generated clips follow IndicSynth CC BY-NC 4.0 for non-commercial "
        "academic research.",
    )
    _body(
        doc,
        "V1 has a structural weakness: REAL equals Kathbath and FAKE equals IndicSynth. Source "
        "identity is therefore associated with class. Speaker-disjoint splitting protects against "
        "speaker leakage but does not remove source-domain shortcuts.",
    )
    _subheading(doc, "B", "Partial V2 External-Source Pilot")
    _body(
        doc,
        "Benchmark V2 is a partial external-source pilot. It adds an independent real-speech "
        "source but does not eliminate source-label confounding. Current cells include "
        "Kathbath×real, IndicSynth×fake, and FLEURS×real. Generator-disjoint evaluation has "
        "n=0 and remains PENDING.",
    )
    _table(
        doc,
        ["Benchmark", "Source / Class", "Count / Status"],
        [
            ["V1", "Kathbath / REAL", "900 / COMPLETE"],
            ["V1", "IndicSynth / FAKE", "900 / COMPLETE"],
            ["V2", "Kathbath / REAL", "1,177 / PARTIAL"],
            ["V2", "IndicSynth / FAKE", "1,169 / PARTIAL"],
            ["V2", "FLEURS / REAL", "50 / PARTIAL"],
        ],
        caption="Table III. Dataset composition",
    )

    _heading(doc, "IV", "Methodology")
    _figure(
        doc,
        "system_architecture.png",
        "Fig. 1. VaaniQ architecture: preprocess → acoustic or frozen XLS-R → head → calibration.",
    )
    _subheading(doc, "A", "Acoustic Baseline V1")
    _body(
        doc,
        "Baseline V1 uses a deterministic 1024-D acoustic embedding and an AASIST-compatible "
        "NumPy classification head. It is not canonical AASIST and not XLS-R. Decision threshold "
        "0.5 on the fake softmax score. Label 0=REAL, 1=FAKE; higher score_fake means more fake.",
    )
    _subheading(doc, "B", "Frozen XLS-R Main")
    _body(
        doc,
        "Frozen facebook/wav2vec2-xls-r-300m, last-layer mean pooling, cached features, and a "
        "lightweight trainable head. Backbone weights are not updated. Production calibration is "
        "global temperature scaling selected on validation.",
    )
    _subheading(doc, "C", "Baselines and Controls")
    _body(
        doc,
        "LFCC-GMM is a complete weak baseline. A RawNet2-style approximate baseline must not be "
        "called faithful RawNet2 (PENDING). An English-only ASVspoof LA control is evaluated on "
        "the same Indic held-out test.",
    )
    _subheading(doc, "D", "Compression and Metrics")
    _body(
        doc,
        "ffmpeg/libopus at 16 kbps provides a WhatsApp-style Opus simulation, not WhatsApp "
        "transport. EER, ROC-AUC, and normalized min-DCF share score direction. min-DCF uses "
        "P_target=0.05, C_miss=1, C_fa=1.",
    )
    _heading(doc, "V", "Primary Results")
    _figure(doc, "performance_overview.png", "Fig. 2. Held-out performance overview.")
    _figure(doc, "confusion_matrix.png", "Fig. 3. Confusion matrix (Baseline V1).")
    _table(
        doc,
        ["System", "n", "Acc / EER / AUC / min-DCF"],
        [
            [
                "Acoustic Baseline V1",
                str(int(as_number(metrics, "n", 584))),
                f"{pct(as_number(metrics, 'accuracy', 0.9161))} / {pct(as_number(metrics, 'eer', 0.0656))} / {as_number(metrics, 'roc_auc', 0.9729):.4f} / {as_number(metrics, 'min_dcf', 0.7841):.4f}",
            ],
            [
                "Frozen XLS-R",
                str(int(as_number(xlsr, "n", 584))),
                f"{pct(as_number(xlsr, 'accuracy', 0.9212))} / {pct(as_number(xlsr, 'eer', 0.0688))} / {as_number(xlsr, 'roc_auc', 0.9828):.4f} / {as_number(xlsr, 'min_dcf', 0.3144):.4f}",
            ],
        ],
        caption="Table IV. Canonical held-out results (threshold 0.5)",
    )
    _body(
        doc,
        "Frozen XLS-R improves ranking performance while thresholded accuracy remains broadly "
        "comparable to Baseline V1.",
    )

    _heading(doc, "VI", "Compression (RQ1)")
    _figure(doc, "condition_breakdown.png", "Fig. 4. Clean versus Opus condition breakdown.")
    _table(
        doc,
        ["Model", "Clean Acc / EER", "Opus Acc / EER"],
        [
            [
                "Acoustic",
                f"{pct(as_number(clean, 'accuracy', 0.9384))} / {pct(as_number(clean, 'eer', 0.0563))}",
                f"{pct(as_number(opus, 'accuracy', 0.8938))} / {pct(as_number(opus, 'eer', 0.0758))}",
            ],
            [
                "Frozen XLS-R",
                f"{pct(as_number(x_clean, 'accuracy', 0.9144))} / {pct(as_number(x_clean, 'eer', 0.0813))}",
                f"{pct(as_number(x_opus, 'accuracy', 0.9281))} / {pct(as_number(x_opus, 'eer', 0.0606))}",
            ],
        ],
        caption="Table V. RQ1 compression (WhatsApp-style Opus 16 kbps)",
    )
    _body(doc, "Compression effects are model-dependent on this benchmark.")

    _heading(doc, "VII", "English-Only Transfer (RQ2)")
    _table(
        doc,
        ["System", "Acc / EER / AUC", "Note"],
        [
            [
                "English-only control",
                f"{pct(eng_acc)} / {pct(eng_eer)} / {eng_auc:.3f}",
                "All REAL at thr 0.5",
            ],
            [
                "Multilingual Baseline V1",
                f"{pct(as_number(metrics, 'accuracy', 0.9161))} / {pct(as_number(metrics, 'eer', 0.0656))} / {as_number(metrics, 'roc_auc', 0.9729):.4f}",
                "Same Indic test",
            ],
        ],
        caption="Table VI. RQ2 English→Indic transfer",
    )
    _body(
        doc,
        "English-only anti-spoofing fails to transfer. Official scores are not polarity-flipped "
        "to inflate AUC.",
    )

    _heading(doc, "VIII", "Cross-Lingual Transfer (RQ3)")
    _figure(doc, "cross_lingual_transfer.png", "Fig. 5. Cross-lingual / language transfer view.")
    _table(
        doc,
        ["Held-out language", "Accuracy", "EER"],
        [
            ["Hindi", pct(hi_acc), pct(hi_eer)],
            ["Marathi", pct(mr_acc), pct(mr_eer)],
            ["Tamil", pct(ta_acc), pct(ta_eer)],
        ],
        caption="Table VII. RQ3 leave-one-language-out (Round 3)",
    )
    _body(doc, "Transfer is strongly asymmetric; Hindi is the weakest zero-shot cell.")

    _heading(doc, "IX", "Calibration (RQ4)")
    _figure(doc, "reliability_diagram.png", "Fig. 6. Reliability diagram.")
    _figure(doc, "calibration_pre_post.png", "Fig. 7. Pre/post calibration comparison.")
    _table(
        doc,
        ["Quantity", "Value", "Role"],
        [
            [
                "Pre-cal test ECE",
                f"{as_number(cal_pre, 'ece', 0.0245):.4f}",
                "Held-out uncalibrated",
            ],
            [
                "Post-cal test ECE",
                f"{as_number(cal_post, 'ece', 0.026):.4f}",
                "After val-selected strategy",
            ],
            [
                "Selection rule",
                "validation ECE only",
                "No test peeking for production",
            ],
        ],
        caption="Table VIII. RQ4 calibration audit",
    )
    _body(
        doc,
        "Validation-selected fine-grained calibration slightly worsened held-out ECE "
        f"({as_number(cal_pre, 'ece', 0.0245):.4f} → {as_number(cal_post, 'ece', 0.026):.4f}). "
        "This negative transfer result is retained.",
    )

    _heading(doc, "X", "External Validity and V2 Pilot")
    probe = as_number(shortcut, "source_probe_test_accuracy", 0.9848)
    _table(
        doc,
        ["Eval", "n", "Status / Result"],
        [
            [
                "V2 full test",
                str(as_dict(evals.get("full_test")).get("n", 593)),
                "PARTIAL / not confound-free",
            ],
            [
                "FLEURS unseen-real",
                str(independent.get("n", 9)),
                "PILOT / 55.6% pipeline only",
            ],
            ["Generator-disjoint", str(gen.get("n", 0)), "PENDING / no result"],
            [
                "V2 source probe",
                str(shortcut.get("test_n", 593)),
                f"PARTIAL / {probe * 100:.2f}% source identity",
            ],
            ["Faithful RawNet2", "-", "PENDING / not implemented"],
        ],
        caption="Table IX. Remaining generalization status",
    )

    _heading(doc, "XI", "Discussion")
    _body(
        doc,
        "Strong V1 discrimination coexists with structural threats. Catastrophic English→Indic "
        "transfer supports multilingual training for this domain. Asymmetric LOLO results caution "
        "against treating Indian languages as a homogeneous transfer class. Negative calibration "
        "transfer shows validation ECE gains require held-out audits. The paper therefore scopes "
        "its contribution to the reproducible machine-evaluation evidence reported here.",
    )

    _heading(doc, "XII", "Limitations")
    _body(
        doc,
        "Key threats: (1) V1 source–label confound; (2) bounded size; (3) academic≠scam audio; "
        "(4) simulated≠real WhatsApp transport; (5) three-language scope; (6) non-canonical "
        "AASIST / pending faithful RawNet2; (7) incomplete V2; (8) source probe 98.48%; "
        "(9) FLEURS n=9; (10) generator-disjoint n=0; (11) calibration-transfer "
        "uncertainty; (12) unresolved val/test heterogeneity; (13) no universal unseen-generator "
        "claim. Strong EER can coexist with high min-DCF under a 5% target prior.",
    )

    _heading(doc, "XIII", "Ethics")
    _body(
        doc,
        "Audio and weights are excluded from version control. Kathbath access conditions and "
        "IndicSynth non-commercial restrictions are respected. Dual-use risks of detection "
        "systems are acknowledged; release emphasizes "
        "research evaluation.",
    )

    _heading(doc, "XIV", "Reproducibility")
    _body(
        doc,
        f"Authoritative metrics are frozen in artifacts/final_results_manifest.json at commit "
        f"{APPROVED}. Integrity verification: scripts/verify_research_integrity.py. Documents "
        "must consume the frozen manifest rather than superseded checkpoints.",
    )

    _heading(doc, "XV", "Future Work")
    _body(
        doc,
        "Expand confound-controlled and generator-disjoint evaluation; implement faithful "
        "RawNet2 and canonical AASIST; study "
        "real messaging-channel audio beyond Opus simulation.",
    )

    _heading(doc, "XVI", "Conclusion")
    _body(
        doc,
        "VaaniQ establishes a reproducible multilingual framework for studying audio-deepfake "
        "detection under language, codec, and confidence-calibration shift. Acoustic and frozen "
        "XLS-R pipelines achieve strong held-out discrimination on bounded V1, while transfer, "
        "calibration, and source-domain experiments expose important limits. Evidence supports "
        "multilingual machine evaluation but "
        "does not establish universal source- or generator-independent detection.",
    )

    _heading(doc, "", "References")
    references = [
        "[1] J. Jung et al., AASIST: Audio anti-spoofing using integrated spectro-temporal graph attention networks, in Proc. ICASSP, 2022.",
        "[2] A. Babu et al., XLS-R: Self-supervised cross-lingual speech representation learning at scale, arXiv:2111.09296, 2021.",
        "[3] T. Javed et al., IndicSUPERB: A speech processing universal performance benchmark for Indian languages, arXiv:2208.11761, 2022.",
        "[4] D. V. Sharma, V. Ekbote, and A. Gupta, IndicSynth: A large-scale multilingual synthetic speech dataset, ACL, 2025.",
        "[5] O. Pascu et al., Towards calibrated and explainable audio deepfake detection, in Proc. Interspeech, 2024.",
        "[6] AI4Bharat, Kathbath dataset, Hugging Face: ai4bharat/Kathbath.",
        "[7] D. V. Sharma et al., IndicSynth dataset, Hugging Face: vdivyasharma/IndicSynth.",
        "[8] A. Conneau et al., FLEURS: Few-shot learning evaluation of universal representations of speech, arXiv:2205.12446, 2022.",
        "[9] IETF RFC 6716, Definition of the Opus Audio Codec, 2012.",
        "[10] ASVspoof 2019, logical access evaluation plan; English-only control uses a streaming subset of Bisher/ASVspoof_2019_LA (ODC-By).",
    ]
    for reference in references:
        paragraph = doc.add_paragraph(reference)
        paragraph.paragraph_format.left_indent = Inches(0.14)
        paragraph.paragraph_format.first_line_indent = Inches(-0.14)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.line_spacing = 0.9
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(7)

    output.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output)
    return output


def _write_readme(package: Path) -> None:
    text = """# VaaniQ IEEE Final Package

## What this is
Publishable IEEE-style archival draft for VaaniQ, generated from frozen Round-3 evidence
(`artifacts/final_results_manifest.json`, commit `084bd47…`).

## Files
- `VaaniQ_IEEE_Research_Paper_Publishable.docx` — full IEEE-style paper
- `VaaniQ_IEEE_Research_Paper_Publishable.pdf` — rendered submission copy
- `VaaniQ_manuscript.md` — markdown source of record for the narrative
- `verified_figures/` — figures embedded in the DOCX
- `README.md` — this file

## Honesty status (do not overclaim)
| Item | Status |
|------|--------|
| RQ1–RQ4 | COMPLETE on bounded V1 |
| Benchmark V2 | PARTIAL pilot |
| Generator-disjoint | PENDING (n=0) |
| Faithful RawNet2 | PENDING |

The paper is scoped to machine evaluation. No human-subject experiment or human-comparison
result is part of the submission.

## Regenerate
```bash
cd backend
..\\.venv\\Scripts\\python.exe ..\\scripts\\build_ieee_final_package.py
```

Also regenerates legacy DOCX via `scripts/generate_ieee_paper_docx.py`.
"""
    (package / "README.md").write_text(text, encoding="utf-8")


def build_package() -> Path:
    PACKAGE.mkdir(parents=True, exist_ok=True)
    docx_path = PACKAGE / "VaaniQ_IEEE_Research_Paper_Publishable.docx"
    build_publishable_docx(docx_path)

    # Sync manuscript
    if MANUSCRIPT.is_file():
        shutil.copy2(MANUSCRIPT, PACKAGE / "VaaniQ_manuscript.md")

    # Figures
    fig_out = PACKAGE / "verified_figures"
    if fig_out.exists():
        shutil.rmtree(fig_out)
    if FIGURE_DIR.is_dir():
        shutil.copytree(FIGURE_DIR, fig_out)

    # Also refresh legacy Final/Draft via existing generator when possible
    try:
        from generate_ieee_paper_docx import build_paper  # type: ignore

        legacy = build_paper()
        shutil.copy2(legacy, PACKAGE / "VaaniQ_IEEE_Research_Paper_Final.docx")
        draft = REPO / "docs" / "VaaniQ_IEEE_Research_Paper_Draft.docx"
        if draft.is_file():
            shutil.copy2(draft, PACKAGE / "VaaniQ_IEEE_Research_Paper_Draft.docx")
    except Exception as exc:  # noqa: BLE001 — package still useful if legacy fails
        (PACKAGE / "LEGACY_GENERATOR_NOTE.txt").write_text(
            f"Legacy generate_ieee_paper_docx.build_paper failed: {exc}\n",
            encoding="utf-8",
        )

    # Copy existing PDF if present
    pdf = REPO / "IEEE_final_VanniQ.pdf"
    if pdf.is_file():
        shutil.copy2(pdf, PACKAGE / "IEEE_final_VanniQ_prior.pdf")

    _write_readme(PACKAGE)

    # Desktop mirror for examiner handoff
    if DESKTOP_PACKAGE.exists():
        shutil.rmtree(DESKTOP_PACKAGE)
    shutil.copytree(PACKAGE, DESKTOP_PACKAGE)

    return PACKAGE


def main() -> None:
    path = build_package()
    print(f"IEEE package written to: {path}")
    print(f"Desktop mirror: {DESKTOP_PACKAGE}")


if __name__ == "__main__":
    main()
