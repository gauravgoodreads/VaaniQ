# Known limitations

Honest constraints for the dissertation §18 analogue. Do not hide these in RQ tables.

1. **NumPy AASIST-style head** is not clovaai graph-attention parity (OQ-014). GPU swap is future work.
2. **Fixture / demo scores** in CI are not curated-hour results (OQ-002).
3. **Gated Hugging Face corpora** are not downloaded in this environment.
4. **ffmpeg Opus twins** skip when the host blocks process spawn (observed on some Windows Application Control setups).
5. **Human study N** is below the proposal floor until volunteers are recruited (REQ-123).
6. **English-only baseline** uses the ASVspoof 2019 LA *protocol* default (OQ-015); domain shift vs Indic test audio must be disclosed.
7. **Packet loss and bitrate ladder** are SHOULD ablations, not the primary WhatsApp cell (OQ-007, OQ-012, OQ-037).
8. **Grad-CAM** is spectrogram-energy aligned (OQ-034), not backprop through a graph AASIST.
9. **Node.js BFF** is not deployed (OQ-026 / ROADMAP-058).
10. **IndicSynth CC BY-NC** may block a full public audio dump (OQ-035).
11. **Tamil-fluent listeners** may be unavailable (OQ-025).
12. **WhatsApp Opus args** are a documented simulation, not a byte-identical WhatsApp encoder (proposal §18; OQ-007).
13. **Live MediaRecorder** ingest is not decoded WebM→PCM; labels are a session-path check.
14. **`/api/v1/admin/status`** is unauthenticated (lab compose only).
15. **Empty history metrics** may return toy scores — never cite them as RQ results.
