# data/

Local audio, embeddings, and object-store blobs live here.

**Never commit audio or weights** (`.gitignore`; REQ-111).

| Path | Purpose | REQ |
|------|---------|-----|
| `object_store/` | Uploaded clips and artefacts | REQ-135 |
| `embedding_cache/` | Frozen XLS-R embeddings | REQ-037 |
| manifests (elsewhere) | Versioned split manifests in repo under `backend/.../datasets/manifests` | REQ-099 |

Created empty in ROADMAP-001. Population begins ROADMAP-011+ (P2).
