# Automated validation report

Validation date: 2026-09-12  
Environment: Windows, Python 3.11.16, Node.js 22 toolchain

## Result

The software and frozen-artifact checks below pass in the current worktree.
This report records automated evidence only. It is not a substitute for research
participants, independent replication, peer review, or journal acceptance.

| Gate | Result |
|---|---|
| Backend unit/API/integration tests | PASS: 195 passed, 3 environment skips |
| Backend branch coverage | PASS: 82.72% (threshold 80%) |
| Ruff lint and format | PASS |
| Mypy strict type checking | PASS: 179 source files |
| Frontend tests | PASS: 20 passed after retiring the out-of-scope human-study route |
| TypeScript type checking | PASS |
| ESLint | PASS |
| Vite production build | PASS |
| OpenAPI client drift | PASS |
| Project-language guard | PASS |
| Research artifact integrity | PASS: 2,346 manifest clips, 0 blocking issues |
| Browser smoke test | PASS: desktop and 390 px mobile, no console/page errors |
| Mobile layout overflow | PASS: no horizontal overflow |
| Master DOCX structural audit | PASS: 32 images, 15 tables, 10 verified figures |
| Master DOCX visual render | PASS: 41 pages inspected |
| IEEE paper visual render | PASS: 4 pages inspected; no clipping or overflow |
| Examiner demo media | PASS: 6:35.86, H.264 1600x900 at 25 fps, AAC stereo |

The three skipped backend tests require an executable FFmpeg binary on `PATH`.
They cover Opus compression integration; the rest of the suite passes without it.

## Inference disclosure

Uploaded-file decisions use the calibrated model at threshold 0.5. Browser microphone
decisions currently apply a separate, unvalidated domain heuristic because the training
domain does not represent laptop microphones. The API returns both the displayed decision
probabilities and `model_probabilities`, plus `decision_policy` and `limitations`, so this
post-processing cannot be mistaken for a frozen benchmark result.

## Research status

The integrity audit reports one non-blocking negative result: held-out ECE changed from
0.0245 to 0.026 after calibration. This is reported as measured. The paper is scoped to
RQ1-RQ4 machine evaluation and does not claim a human-subject experiment. Benchmark V2
remains partial, the generator-disjoint cell remains N=0, and a faithful RawNet2
implementation remains pending.

## Reproduction

Run from the repository root:

```powershell
powershell -File scripts/check_all.ps1
backend\.venv\Scripts\python.exe scripts\verify_research_integrity.py
```

Canonical research values remain frozen in
`artifacts/final_results_manifest.json`; this validation does not rewrite them.

## Live API smoke matrix

The following packaged demo files were posted to the running API on 2026-09-11 with
optional cloud enrichment disabled. All six used the calibrated uploaded-file policy.

| Language | Input | Expected | Actual | Confidence |
|---|---|---|---|---:|
| Hindi | Human | REAL | REAL | 0.9881 |
| Hindi | AI | FAKE | FAKE | 0.9961 |
| Marathi | Human | REAL | REAL | 1.0000 |
| Marathi | AI | FAKE | FAKE | 0.9973 |
| Tamil | Human | REAL | REAL | 0.9107 |
| Tamil | AI | FAKE | FAKE | 0.9367 |

The Marathi human file was also submitted through the microphone route. It returned
REAL and identified `live_microphone_heuristic_unvalidated` as its decision policy,
while returning the independent raw model probability and limitation notice.

Cloud-enrichment smoke testing also passed for a Hindi REAL sample: Groq Whisper and the
LLM explanation path both returned successfully in 3.3 seconds.

## Publication artifact QA

`docs/VaaniQ_Master_Presentation_FINAL_v2.docx` passed its structural verifier and was
rendered with LibreOffice/Poppler for page-by-page inspection. All publication figures were
regenerated at 300 dpi with non-overlapping labels, legends, nodes, and routed connectors.
The machine-evaluation-only
IEEE paper was regenerated from the frozen manifest, rendered to four pages, and inspected
for clipped tables, missing figures, overflow, and stray pages. A matching PDF is included
in `docs/IEEE_final_VaaniQ/`.

The examiner demo was regenerated after the machine-evaluation scope cleanup. Sampled
frames confirm the opening RQ1-RQ4 scope, cleaned navigation, multilingual demonstrations,
waveforms, spectrograms, result panels, and limitations close.
