import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getJson } from "@/api/client";
import type { CalibrationResponse, HistoryResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { HonestyBanner, PageHeader, Surface } from "@/components/layout/PageChrome";
import { ConfidenceGauge } from "@/components/viz/ConfidenceGauge";
import { LineChart } from "@/components/viz/LineChart";
import { ReliabilityBadge } from "@/components/viz/ReliabilityBadge";

type Explorer = {
  total_clips: number;
  languages: string[];
  total_hours?: number;
  playable_clips?: number;
};

type Pipeline = {
  status: string;
  checkpoint_loaded: boolean;
  calibrated: boolean;
  val_accuracy?: number;
  n_train?: number;
  n_val?: number;
  languages?: string[];
  gpu?: string;
  cuda_available?: boolean;
  pipeline?: string;
  temperatures?: Record<string, number>;
  n_experiments?: number;
  note?: string;
};

/** Research dashboard: latest verdict, calibration, dataset, pipeline. */
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
  const pipeline = useQuery({
    queryKey: ["pipeline"],
    queryFn: () => getJson<Pipeline>("/api/v1/metrics/pipeline"),
  });
  const latest = history.data?.items[0];
  const loading =
    history.isPending || calib.isPending || explorer.isPending || pipeline.isPending;
  const error = history.error ?? calib.error ?? explorer.error ?? pipeline.error;
  const reliability = (calib.data?.reliability_diagram ?? []).map((d) => ({
    x: Number(d["confidence"] ?? 0),
    y: Number(d["accuracy"] ?? 0),
  }));

  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Dashboard"
        subtitle="Calibrated detection overview for Hindi, Marathi, and Tamil. Live pulse of the demo stack."
      />
      <HonestyBanner>
        Dataset hours and ECE shown here are from the local demo corpus / session, not curated
        dissertation RQ tables until research data is ingested and trained.
      </HonestyBanner>
      <QueryStatus isPending={loading} isError={Boolean(error)} error={error ?? undefined}>
        <div className="grid gap-5 md:grid-cols-3">
          <article className="rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-5 text-[var(--fg)] shadow-[0_20px_60px_-40px_rgba(15,28,36,0.45)]">
            <h2 className="text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">
              Latest verdict
            </h2>
            {latest ? (
              <div className="mt-4 space-y-3">
                <p className="font-[family-name:var(--font-display)] text-3xl capitalize">
                  {latest.label}
                </p>
                <ReliabilityBadge level={latest.reliability} />
                <ConfidenceGauge value={latest.confidence} />
              </div>
            ) : (
              <p className="mt-4 text-sm text-[var(--fg-muted)]">
                No predictions yet.{" "}
                <Link className="text-[var(--accent)] underline" to="/upload">
                  Record or upload a clip
                </Link>
                .
              </p>
            )}
          </article>
          <article className="rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-5 text-[var(--fg)]">
            <h2 className="text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">
              Calibration (RQ4)
            </h2>
            <p className="mt-4 font-[family-name:var(--font-display)] text-3xl">
              ECE {calib.data ? calib.data.ece.toFixed(4) : "-"}
            </p>
            <p className="text-sm text-[var(--fg-muted)]">
              Brier {calib.data ? calib.data.brier.toFixed(4) : "-"}
            </p>
            <Link className="mt-4 inline-block text-sm text-[var(--accent)] underline" to="/calibration">
              Reliability diagrams
            </Link>
          </article>
          <article className="rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)] p-5 text-[var(--fg)]">
            <h2 className="text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">
              Dataset (O1)
            </h2>
            <p className="mt-4 font-[family-name:var(--font-display)] text-3xl">
              {explorer.data?.total_clips ?? "-"}{" "}
              <span className="text-lg text-[var(--fg-muted)]">clips</span>
            </p>
            <p className="text-sm text-[var(--fg-muted)]">
              {(explorer.data?.total_hours ?? 0).toFixed(3)} h ·{" "}
              {explorer.data?.playable_clips ?? 0} playable ·{" "}
              {(explorer.data?.languages ?? []).join(" · ")}
            </p>
            <Link className="mt-4 inline-block text-sm text-[var(--accent)] underline" to="/datasets">
              Explorer
            </Link>
          </article>
        </div>

        <Surface title="Trained pipeline" className="mt-6">
          <p className="text-sm text-[var(--fg-muted)]">
            {pipeline.data?.pipeline ?? "preprocess -> acoustic embedding -> AASIST -> temperature"}
          </p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            <p className="text-sm">
              <span className="text-[var(--fg-muted)]">Status:</span>{" "}
              {pipeline.data?.status ?? "-"}
            </p>
            <p className="text-sm">
              <span className="text-[var(--fg-muted)]">Val acc:</span>{" "}
              {pipeline.data?.val_accuracy != null
                ? Number(pipeline.data.val_accuracy).toFixed(3)
                : "-"}
            </p>
            <p className="text-sm">
              <span className="text-[var(--fg-muted)]">Train / val:</span>{" "}
              {pipeline.data?.n_train ?? "-"} / {pipeline.data?.n_val ?? "-"}
            </p>
            <p className="text-sm">
              <span className="text-[var(--fg-muted)]">GPU:</span>{" "}
              {pipeline.data?.gpu ?? (pipeline.data?.cuda_available ? "CUDA" : "CPU")}
            </p>
          </div>
          <p className="mt-3 text-xs text-[var(--fg-muted)]">{pipeline.data?.note}</p>
        </Surface>

        {reliability.length > 0 ? (
          <div className="mt-6">
            <Surface title="Reliability snapshot">
              <LineChart
                title="Confidence vs accuracy"
                xlabel="Confidence"
                ylabel="Accuracy"
                points={reliability}
              />
            </Surface>
          </div>
        ) : null}
      </QueryStatus>
    </section>
  );
}
