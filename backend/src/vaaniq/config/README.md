# config

Layered pydantic config loader: defaults → YAML → env → CLI (ROADMAP-004).

Domain experiment YAMLs under repo ``configs/{data,audio,model,train,eval,calibration}/``
are validated by ``vaaniq.config.domains`` via ``load_all_domain_configs`` (Phase 1 step 9).
They are **not** merged into ``AppConfig``.

**REQs:** REQ-001, REQ-132, REQ-135, REQ-136, REQ-139

Unknown keys fail validation (`extra='forbid'`). Language codes for the app must equal
`list(Language)` — never hardcode `hi/mr/ta` in application code.
