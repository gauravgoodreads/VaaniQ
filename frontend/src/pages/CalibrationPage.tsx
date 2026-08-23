import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { CalibrationResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { LineChart } from "@/components/viz/LineChart";

/** Calibration / reliability page (RQ4 / ROADMAP-043+). */
export function CalibrationPage() {
  const q = useQuery({
    queryKey: ["calibration"],
    queryFn: () => getJson<CalibrationResponse>("/api/v1/calibration"),
  });
  const reliability = (q.data?.reliability_diagram ?? []).map((d) => ({
    x: Number(d["confidence"] ?? 0),
    y: Number(d["accuracy"] ?? 0),
  }));
  const coverage = (q.data?.coverage_curve ?? []).map((d) => ({
    x: Number(d["coverage"] ?? 0),
    y: Number(d["accuracy"] ?? 0),
  }));
  return (
    <section className="vaaniq-enter space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Calibration</h1>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        {q.data ? (
          <div className="grid gap-2 sm:grid-cols-2">
            <p>ECE: {q.data.ece.toFixed(4)}</p>
            <p>Brier: {q.data.brier.toFixed(4)}</p>
          </div>
        ) : null}
        <div className="grid gap-4 md:grid-cols-2">
          <LineChart
            title="Reliability diagram"
            xlabel="Confidence"
            ylabel="Accuracy"
            points={reliability}
          />
          <LineChart title="Coverage curve" xlabel="Coverage" ylabel="Accuracy" points={coverage} />
        </div>
      </QueryStatus>
    </section>
  );
}
