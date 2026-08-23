import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import { QueryStatus } from "@/components/QueryStatus";

type Explorer = {
  total_clips: number;
  total_hours: number;
  counts_by_language: Record<string, number>;
  hours_by_language: Record<string, number>;
  counts_by_label: Record<string, number>;
  hours_by_label: Record<string, number>;
  languages: string[];
  note: string;
};

/** Dataset explorer for language x label hours (O1 / REQ-034). */
export function DatasetPage() {
  const q = useQuery({
    queryKey: ["datasets"],
    queryFn: () => getJson<Explorer>("/api/v1/datasets/explorer"),
  });
  const data = q.data;
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Dataset explorer</h1>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <p className="text-sm text-[var(--fg-muted)]">{data?.note}</p>
        <p className="text-lg">
          {data?.total_clips ?? "—"} clips · {(data?.total_hours ?? 0).toFixed(4)} hours
        </p>
        <table className="w-full max-w-xl text-left text-sm">
          <caption className="sr-only">Counts by language</caption>
          <thead>
            <tr>
              <th>Language</th>
              <th>Clips</th>
              <th>Hours</th>
            </tr>
          </thead>
          <tbody>
            {(data?.languages ?? ["hi", "mr", "ta"]).map((lang) => (
              <tr key={lang} className="border-t border-[var(--border)]">
                <td>{lang}</td>
                <td>{data?.counts_by_language[lang] ?? 0}</td>
                <td>{(data?.hours_by_language[lang] ?? 0).toFixed(4)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </QueryStatus>
    </section>
  );
}
