import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { getJson } from "@/api/client";
import type { ExperimentsResponse, ReportResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { Button } from "@/components/ui/button";

type Compare = {
  metric: string;
  rows: Record<string, unknown>[];
};

type Search = { items: Record<string, unknown>[] };

function cellText(value: unknown): string {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(4);
  }
  if (value == null) {
    return "—";
  }
  return String(value);
}

/** Experiment browser, compare, and report download (RQ1–RQ5). */
export function ExperimentsPage() {
  const [rq, setRq] = useState("RQ3");
  const experiments = useQuery({
    queryKey: ["experiments"],
    queryFn: () => getJson<ExperimentsResponse>("/api/v1/experiments"),
  });
  const compare = useQuery({
    queryKey: ["compare"],
    queryFn: () => getJson<Compare>("/api/v1/experiments/compare?metric=eer"),
  });
  const search = useQuery({
    queryKey: ["search", rq],
    queryFn: () => getJson<Search>(`/api/v1/experiments/search?rq_id=${rq}`),
  });
  const report = useQuery({
    queryKey: ["report"],
    queryFn: () => getJson<ReportResponse>("/api/v1/experiments/report?experiment_id=demo"),
    enabled: false,
  });

  const compareRows = compare.data?.rows ?? [];
  const compareKeys = compareRows[0] ? Object.keys(compareRows[0]) : [];
  const searchItems = search.data?.items ?? [];
  const searchKeys = searchItems[0] ? Object.keys(searchItems[0]).slice(0, 6) : [];

  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Experiments</h1>
      <label className="grid max-w-xs gap-1 text-sm">
        Filter by RQ
        <select
          className="rounded border border-[var(--border)] bg-transparent px-2 py-1"
          value={rq}
          onChange={(e) => setRq(e.target.value)}
          aria-label="Research question filter"
        >
          {["RQ1", "RQ2", "RQ3", "RQ4", "RQ5"].map((id) => (
            <option key={id} value={id}>
              {id}
            </option>
          ))}
        </select>
      </label>
      <QueryStatus
        isPending={experiments.isPending}
        isError={experiments.isError}
        error={experiments.error ?? undefined}
        empty={(experiments.data?.items.length ?? 0) === 0}
        emptyMessage="No experiment directories yet. Run python -m vaaniq.research.cli."
      >
        <ul className="space-y-1 text-sm">
          {(experiments.data?.items ?? []).map((item) => (
            <li key={item.experiment_id}>
              <code>{item.experiment_id}</code> — {item.path}
            </li>
          ))}
        </ul>
      </QueryStatus>
      <h2 className="text-lg">Compare (EER)</h2>
      <QueryStatus
        isPending={compare.isPending}
        isError={compare.isError}
        error={compare.error ?? undefined}
        empty={compareRows.length === 0}
        emptyMessage="No comparable runs stored."
      >
        <div className="overflow-x-auto rounded border border-[var(--border)]">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">Experiment EER comparison</caption>
            <thead>
              <tr>
                {compareKeys.map((key) => (
                  <th key={key} className="px-3 py-2 font-medium">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {compareRows.map((row, i) => (
                <tr key={i} className="border-t border-[var(--border)]">
                  {compareKeys.map((key) => (
                    <td key={key} className="px-3 py-2">
                      {cellText(row[key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </QueryStatus>
      <h2 className="text-lg">Search</h2>
      <QueryStatus
        isPending={search.isPending}
        isError={search.isError}
        error={search.error ?? undefined}
        empty={searchItems.length === 0}
        emptyMessage={`No stored runs tagged ${rq}.`}
      >
        <div className="overflow-x-auto rounded border border-[var(--border)]">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">Experiment search results</caption>
            <thead>
              <tr>
                {searchKeys.map((key) => (
                  <th key={key} className="px-3 py-2 font-medium">
                    {key}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {searchItems.map((row, i) => (
                <tr key={i} className="border-t border-[var(--border)]">
                  {searchKeys.map((key) => (
                    <td key={key} className="px-3 py-2">
                      {cellText(row[key])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </QueryStatus>
      <Button type="button" onClick={() => void report.refetch()}>
        Generate report
      </Button>
      {report.isFetching ? <p className="text-sm text-[var(--fg-muted)]">Generating…</p> : null}
      {report.data ? (
        <pre className="max-h-96 overflow-auto whitespace-pre-wrap rounded border border-[var(--border)] p-3 text-xs">
          {report.data.report_markdown}
        </pre>
      ) : null}
    </section>
  );
}
