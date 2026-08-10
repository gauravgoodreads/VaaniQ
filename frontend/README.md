# VaaniQ frontend

Vite + React 18 + TypeScript (strict) + Tailwind v4 + TanStack Query.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Vite dev server (default `:5173`) |
| `npm run build` | `tsc -b` + production bundle |
| `npm run typecheck` | TypeScript project references |
| `npm run test` | Vitest |
| `npm run lint` | ESLint |

## Env

Copy `.env.example` to `.env`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

The shell polls `GET /health` to prove the frontend↔backend loop (ROADMAP-007 / REQ-134).

## Pages

Landing, dashboard, upload, live, inference, history, research-metrics, experiments,
calibration, explainability, admin, docs — stubs cite ROADMAP ids until P9.
