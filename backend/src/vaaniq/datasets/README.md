# datasets

Dataset source adapters, manifests, splits, offline download/cache helpers,
validators, parsers, loaders, stats, and preview (ROADMAP-011–018).

Offline-first: unit tests use `MockDownloader`, fixture manifests under
`backend/tests/fixtures/datasets/`, and adapter `manifest_path` / `rows` —
no network in the default path.
