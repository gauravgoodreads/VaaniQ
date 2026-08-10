# config

Layered pydantic config loader: defaults → YAML → env → CLI (ROADMAP-004).

**REQs:** REQ-001, REQ-132, REQ-135, REQ-136, REQ-139

Unknown keys fail validation (`extra='forbid'`). Language codes must equal
`list(Language)` — never hardcode `hi/mr/ta` in application code.
