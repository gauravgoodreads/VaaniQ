import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { MetricsResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";

function formatValue(value: unknown): string {
  if (typeof value === "number") {
    return value.toFixed(4);
  }
  return String(value);
}

/** Research metrics page (ROADMAP-036+). */
export function ResearchMetricsPage() {
  const q = useQuery({
    queryKey: ["metrics"],
    queryFn: () => getJson<MetricsResponse>("/api/v1/metrics"),
  });
  const metrics = q.data?.metrics ?? {};
  const matrices = q.data?.matrices ?? {};
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Research metrics</h1>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <table className="w-full max-w-xl text-left text-sm">
          <caption className="sr-only">Scalar metrics</caption>
          <tbody>
            {Object.entries(metrics).map(([k, v]) => (
              <tr key={k} className="border-t border-[var(--border)]">
                <th className="py-1 font-medium">{k}</th>
                <td>{formatValue(v)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {Object.entries(matrices).map(([name, matrix]) => (
          <article key={name} className="space-y-2">
            <h2 className="text-lg capitalize">{name.replaceAll("_", " ")}</h2>
            <p className="text-sm text-[var(--fg-muted)]">
              {typeof matrix === "object" && matrix !== null
                ? `${Object.keys(matrix as object).length} train rows`
                : "—"}
            </p>
          </article>
        ))}
      </QueryStatus>
    </section>
  );
}
