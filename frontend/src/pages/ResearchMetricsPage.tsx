import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { MetricsResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { HonestyBanner, PageHeader, StatTile, Surface } from "@/components/layout/PageChrome";
import { LineChart } from "@/components/viz/LineChart";

function formatValue(value: unknown): string {
  if (typeof value === "number") return value.toFixed(4);
  return String(value);
}

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

/** Research metrics page (ROADMAP-036+). */
export function ResearchMetricsPage() {
  const q = useQuery({
    queryKey: ["metrics"],
    queryFn: () => getJson<MetricsResponse>("/api/v1/metrics"),
  });
  const pipe = useQuery({
    queryKey: ["pipeline"],
    queryFn: () => getJson<Pipeline>("/api/v1/metrics/pipeline"),
  });
  const metrics = q.data?.metrics ?? {};
  const matrices = q.data?.matrices ?? {};
  const tempPoints = Object.entries(pipe.data?.temperatures ?? {}).map(([k, v], i) => ({
    x: i + 1,
    y: Number(v),
    label: k,
  }));

  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Research metrics"
        subtitle="Session detection scalars, trained pipeline status, and calibration temperatures."
      />
      <HonestyBanner>
        Values here track the running API demo / fixture path. Curated RQ1-RQ5 CSV results stay under{" "}
        <code>research/results/</code> and remain PENDING until real experiment runs complete.
      </HonestyBanner>
      <QueryStatus
        isPending={q.isPending || pipe.isPending}
        isError={q.isError || pipe.isError}
        error={q.error ?? pipe.error ?? undefined}
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile label="Pipeline" value={String(pipe.data?.status ?? "-")} />
          <StatTile
            label="Val accuracy"
            value={
              pipe.data?.val_accuracy != null
                ? Number(pipe.data.val_accuracy).toFixed(3)
                : "-"
            }
          />
          <StatTile
            label="Checkpoint"
            value={pipe.data?.checkpoint_loaded ? "loaded" : "missing"}
          />
          <StatTile
            label="Calibrated"
            value={pipe.data?.calibrated ? "yes" : "no"}
          />
        </div>

        <Surface title="Detection pipeline" className="mt-6">
          <p className="text-sm text-[var(--fg)]">{pipe.data?.pipeline}</p>
          <p className="mt-2 text-sm text-[var(--fg-muted)]">
            Languages: {(pipe.data?.languages ?? []).join(", ") || "-"} · Experiments:{" "}
            {pipe.data?.n_experiments ?? 0} · GPU:{" "}
            {pipe.data?.gpu ?? (pipe.data?.cuda_available ? "CUDA" : "CPU")}
          </p>
          <p className="mt-2 text-xs text-[var(--fg-muted)]">{pipe.data?.note}</p>
        </Surface>

        {tempPoints.length > 0 ? (
          <div className="mt-6 grid gap-5 md:grid-cols-2">
            <Surface title="Temperature table (T)">
              <ul className="space-y-2 text-sm">
                {Object.entries(pipe.data?.temperatures ?? {}).map(([k, v]) => (
                  <li key={k} className="flex justify-between border-t border-[var(--border)] pt-2">
                    <span className="text-[var(--fg-muted)]">{k}</span>
                    <span className="tabular-nums">{Number(v).toFixed(3)}</span>
                  </li>
                ))}
              </ul>
            </Surface>
            <Surface>
              <LineChart
                title="Temperature by condition"
                xlabel="Condition index"
                ylabel="T"
                points={tempPoints.map((p) => ({ x: p.x, y: p.y }))}
              />
            </Surface>
          </div>
        ) : null}

        <Surface title="Scalar metrics" className="mt-6">
          <table className="w-full text-left text-sm">
            <caption className="sr-only">Scalar metrics</caption>
            <tbody>
              {Object.entries(metrics).map(([k, v]) => (
                <tr key={k} className="border-t border-[var(--border)]">
                  <th className="py-3 font-medium text-[var(--fg)]">{k}</th>
                  <td className="py-3 tabular-nums text-[var(--fg)]">{formatValue(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Surface>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {Object.entries(matrices).map(([name, matrix]) => (
            <Surface key={name} title={name.replaceAll("_", " ")}>
              <p className="text-sm text-[var(--fg-muted)]">
                {typeof matrix === "object" && matrix !== null
                  ? `${Object.keys(matrix as object).length} entries`
                  : "-"}
              </p>
            </Surface>
          ))}
        </div>
      </QueryStatus>
    </section>
  );
}
