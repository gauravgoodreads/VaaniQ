# models/

Trained checkpoints and exported ONNX/weights live here locally.

**Never commit `*.pt` / `*.pth` / `*.onnx` / `*.ckpt`** (vaaniq-core.mdc).

Track model cards via `registry.json` only until ROADMAP-035.

| Field (registry) | Meaning |
|------------------|---------|
| `name` | Logical model id |
| `uri` | Local or remote path |
| `req_ids` | Covered requirements |

Stub registry committed in ROADMAP-001; real entries from P5.
