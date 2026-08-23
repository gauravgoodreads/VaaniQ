import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getJson } from "@/api/client";
import type { CalibrationResponse, HistoryResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { ConfidenceGauge } from "@/components/viz/ConfidenceGauge";
import { ReliabilityBadge } from "@/components/viz/ReliabilityBadge";

type Explorer = {
  total_clips: number;
  languages: string[];
};

/** Research dashboard: latest verdict, calibration, dataset, model compare. */
export function DashboardPage() {
  const history = useQuery({
    queryKey: ["history"],
    queryFn: () => getJson<HistoryResponse>("/api/v1/history"),
  });
  const calib = useQuery({
    queryKey: ["calibration"],
    queryFn: () => getJson<CalibrationResponse>("/api/v1/calibration"),
  });
  const explorer = useQuery({
    queryKey: ["datasets"],
    queryFn: () => getJson<Explorer>("/api/v1/datasets/explorer"),
  });
  const latest = history.data?.items[0];
  const loading = history.isPending || calib.isPending || explorer.isPending;
  const error = history.error ?? calib.error ?? explorer.error;

  return (
    <section className="vaaniq-enter space-y-6">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Dashboard</h1>
      <p className="max-w-2xl text-[var(--fg-muted)]">
        Calibrated detection overview for Hindi, Marathi, and Tamil (O7).
      </p>
      <QueryStatus isPending={loading} isError={Boolean(error)} error={error ?? undefined}>
        <div className="grid gap-4 md:grid-cols-3">
          <article className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
            <h2 className="text-sm uppercase tracking-wide text-[var(--fg-muted)]">Latest verdict</h2>
            {latest ? (
              <div className="mt-3 space-y-2">
                <p className="text-2xl font-medium">{latest.label}</p>
                <ReliabilityBadge level={latest.reliability} />
                <ConfidenceGauge value={latest.confidence} />
              </div>
            ) : (
              <p className="mt-3 text-sm">
                No predictions yet. <Link to="/upload">Upload a clip</Link>.
              </p>
            )}
          </article>
          <article className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
            <h2 className="text-sm uppercase tracking-wide text-[var(--fg-muted)]">Calibration (RQ4)</h2>
            <p className="mt-3 text-lg">ECE {calib.data ? calib.data.ece.toFixed(4) : "—"}</p>
            <p className="text-sm text-[var(--fg-muted)]">
              Brier {calib.data ? calib.data.brier.toFixed(4) : "—"}
            </p>
            <Link className="mt-3 inline-block text-sm underline" to="/calibration">
              Reliability diagrams
            </Link>
          </article>
          <article className="rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] p-4">
            <h2 className="text-sm uppercase tracking-wide text-[var(--fg-muted)]">Dataset (O1)</h2>
            <p className="mt-3 text-lg">{explorer.data?.total_clips ?? "—"} clips</p>
            <p className="text-sm text-[var(--fg-muted)]">
              {(explorer.data?.languages ?? []).join(" · ")}
            </p>
            <Link className="mt-3 inline-block text-sm underline" to="/datasets">
              Explorer
            </Link>
          </article>
        </div>
      </QueryStatus>
    </section>
  );
}
