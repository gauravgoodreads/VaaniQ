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
  });
  return (
    <section className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">History</h1>
      <QueryStatus
        isPending={q.isPending}
        isError={q.isError}
        error={q.error ?? undefined}
        empty={(q.data?.items.length ?? 0) === 0}
        emptyMessage="No predictions yet."
      >
        <ul className="space-y-2">
          {(q.data?.items ?? []).map((item) => (
            <li
              key={item.prediction_id}
              className="flex flex-wrap items-center gap-3 border-b border-[var(--border)] py-2 text-sm"
            >
              <span className="text-[var(--fg-muted)]">{item.created_at}</span>
              <span className="font-medium">{item.label}</span>
              <span>{item.confidence.toFixed(2)}</span>
              <ReliabilityBadge level={item.reliability} />
              <span className="text-[var(--fg-muted)]">lang={item.language}</span>
            </li>
          ))}
        </ul>
      </QueryStatus>
    </section>
  );
}
