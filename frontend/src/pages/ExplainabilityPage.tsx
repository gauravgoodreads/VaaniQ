import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { ExplainResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";

/** Explainability viewer (Grad-CAM, bands, artifacts, explorer). */
export function ExplainabilityPage() {
  const q = useQuery({
    queryKey: ["explain"],
    queryFn: () => getJson<ExplainResponse>("/api/v1/explain"),
  });
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Explainability</h1>
      <p className="text-[var(--fg-muted)]">
        Grad-CAM proxy, attention maps, frequency-band masking, spectrogram, and compression
        artifacts (proposal §7.7).
      </p>
      <QueryStatus
        isPending={q.isPending}
        isError={q.isError}
        error={q.error ?? undefined}
        empty={(q.data?.artefacts.length ?? 0) === 0}
        emptyMessage="No explainability artefacts yet. Run inference first."
      >
        <ul className="space-y-2 text-sm">
          {(q.data?.artefacts ?? []).map((a) => (
            <li key={`${a.kind}-${a.uri}`} className="rounded border border-[var(--border)] p-3">
              <strong>{a.kind}</strong>
              <p>{a.summary}</p>
              <code className="text-xs">{a.uri}</code>
            </li>
          ))}
        </ul>
      </QueryStatus>
    </section>
  );
}
