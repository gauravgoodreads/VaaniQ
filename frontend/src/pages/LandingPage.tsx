import { Link } from "react-router-dom";

import { useHealth } from "@/hooks/useHealth";
import { LANGUAGES } from "@/types/language";

/** Marketing/home surface — brand-first with live API health (REQ-134). */
export function LandingPage() {
  const health = useHealth();

  return (
    <section className="flex min-h-[70vh] flex-col justify-center gap-8">
      <div className="max-w-2xl space-y-4">
        <p className="text-sm uppercase tracking-[0.2em] text-[var(--fg-muted)]">
          Capstone research system
        </p>
        <h1 className="font-[family-name:var(--font-display)] text-5xl leading-tight md:text-6xl">
          VaaniQ
        </h1>
        <p className="max-w-xl text-lg text-[var(--fg-muted)]">
          Cross-lingual, compression-robust detection of AI-generated voice for Hindi, Marathi,
          and Tamil — with calibrated confidence.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link
            to="/upload"
            className="inline-flex h-11 items-center rounded-md bg-[var(--accent)] px-5 text-[var(--accent-fg)]"
          >
            Open upload
          </Link>
          <Link
            to="/docs"
            className="inline-flex h-11 items-center rounded-md border border-[var(--border)] px-5"
          >
            Read docs
          </Link>
        </div>
      </div>

      <dl className="grid gap-4 sm:grid-cols-2">
        <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
          <dt className="text-sm text-[var(--fg-muted)]">Languages</dt>
          <dd className="mt-1 font-medium">{LANGUAGES.join(" · ")}</dd>
        </div>
        <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
          <dt className="text-sm text-[var(--fg-muted)]">Backend health</dt>
          <dd className="mt-1 font-medium" data-testid="landing-health">
            {health.isPending && "Checking…"}
            {health.isSuccess && `Connected (${health.data.status})`}
            {health.isError && "Unreachable — start the API on VITE_API_BASE_URL"}
          </dd>
        </div>
      </dl>
    </section>
  );
}
