import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { HistoryResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { ReliabilityBadge } from "@/components/viz/ReliabilityBadge";

/** Prediction history (ROADMAP-054). */
export function HistoryPage() {
  const q = useQuery({
    queryKey: ["history"],
    queryFn: () => getJson<HistoryResponse>("/api/v1/history"),
    refetchInterval: 4000,
  });
  return (
    <section className="space-y-8">
      <header className="max-w-2xl space-y-3">
        <h1 className="font-[family-name:var(--font-display)] text-4xl tracking-tight md:text-5xl">
          History
        </h1>
        <p className="text-lg text-[var(--fg-muted)]">
          Every detection from this session - uploads and microphone recordings.
        </p>
      </header>
      <QueryStatus
        isPending={q.isPending}
        isError={q.isError}
        error={q.error ?? undefined}
        empty={(q.data?.items.length ?? 0) === 0}
        emptyMessage="No predictions yet."
      >
        <ul className="divide-y divide-[var(--border)] overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)]/70">
          {(q.data?.items ?? []).map((item) => (
            <li
              key={item.prediction_id}
              className="flex flex-wrap items-center gap-3 px-4 py-4 text-sm"
            >
              <span className="text-[var(--fg-muted)]">{item.created_at}</span>
              <span className="font-[family-name:var(--font-display)] text-lg capitalize">
                {item.label}
              </span>
              <span className="tabular-nums">{item.confidence.toFixed(2)}</span>
              <ReliabilityBadge level={item.reliability} />
              <span className="rounded-full bg-[var(--bg)] px-2 py-0.5 text-[var(--fg-muted)]">
                {item.language}
              </span>
            </li>
          ))}
        </ul>
      </QueryStatus>
    </section>
  );
}
