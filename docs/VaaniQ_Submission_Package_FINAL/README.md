# VaaniQ Final Submission Package

VaaniQ is a multilingual synthetic-speech detection capstone evaluated on Hindi, Marathi, and Tamil audio. This package contains the examiner-facing manuscript, technical report, reproducible results, figures, and recorded demonstration.

## Deliverables

- `VaaniQ_Master_Presentation_FINAL_v2.docx` - complete capstone report and presentation document.
- `VaaniQ_Master_Presentation_FINAL_v2.pdf` - fixed-layout rendering of the master document.
- `VaaniQ_IEEE_Research_Paper_Publishable.docx` - editable IEEE-style manuscript.
- `VaaniQ_IEEE_Research_Paper_Publishable.pdf` - fixed-layout IEEE-style manuscript.
- `VaaniQ_Examiner_Demo.mp4` - end-to-end recorded application demonstration.
- `AUTOMATED_VALIDATION_REPORT.md` - consolidated engineering and artifact checks.
- `AUDIO_PREPROCESSING_COMPLETE.md` - complete corpus, normalization, codec, feature, split, and calibration preprocessing record.
- `VIVA_DEMO_WALKTHROUGH.md` - examiner demonstration sequence and talking points.
- `final_results_manifest.json` - machine-readable source of reported metrics.
- `verified_figures/` - ten regenerated publication figures sourced from the results manifest.

## Verified Result Snapshot

- Evaluation corpus: 2,346 clips.
- Languages: Hindi, Marathi, and Tamil.
- Overall accuracy: 91.6%.
- Equal error rate: 6.6%.
- Expected calibration error: 0.026 after calibration.
- Reported research scope: RQ1-RQ4, evaluated using reproducible machine experiments.

## Evidence Boundary

The live microphone path and uploaded-file path are demonstrated as product behavior. Formal claims are limited to the documented datasets, protocols, and machine-evaluation results. No human-subject study or external clinical/forensic validation is claimed. The system is a research prototype and its output should not be treated as sole evidence in consequential decisions.

## Reproduction Entry Points

From the repository root, use the commands and environment described in the master document and validation report. The application entry point used in the demo is `/upload`; the API exposes health, detection, explanation, and model-card endpoints. Figures and documents are generated from versioned scripts and the results manifest.

## Package Status

The source code, tests, type checks, lint checks, builds, API behavior, document structure, figure layout, and demo media were checked before packaging. See `AUTOMATED_VALIDATION_REPORT.md` for the recorded validation details and stated limitations.
