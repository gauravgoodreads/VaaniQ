import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { CalibrationResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { HonestyBanner, PageHeader, StatTile, Surface } from "@/components/layout/PageChrome";
import { LineChart } from "@/components/viz/LineChart";

/** Calibration / reliability page (RQ4). */
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
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Calibration"
        subtitle="Temperature-scaled confidence quality: ECE, Brier, reliability diagrams (RQ4)."
      />
      <HonestyBanner>
        Charts reflect the current API session (or demo fallbacks when history is empty). They are not
        dissertation RQ4 tables until temperature scaling is fit on curated validation logits.
      </HonestyBanner>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <div className="grid gap-4 sm:grid-cols-2">
          <StatTile label="ECE" value={q.data ? q.data.ece.toFixed(4) : "-"} />
          <StatTile label="Brier" value={q.data ? q.data.brier.toFixed(4) : "-"} />
        </div>
        <div className="mt-6 grid gap-5 md:grid-cols-2">
          <Surface>
            <LineChart
              title="Reliability diagram"
              xlabel="Confidence"
              ylabel="Accuracy"
              points={reliability}
            />
          </Surface>
          <Surface>
            <LineChart
              title="Coverage curve"
              xlabel="Coverage"
              ylabel="Accuracy"
              points={coverage}
            />
          </Surface>
        </div>
      </QueryStatus>
    </section>
  );
}
