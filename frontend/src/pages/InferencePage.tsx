import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

import { getJson } from "@/api/client";
import type { HistoryResponse, PredictionResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { PredictionPanel } from "@/pages/UploadPage";

/** Detailed inference view for the latest prediction (ROADMAP-054). */
export function InferencePage() {
  const q = useQuery({
    queryKey: ["history"],
    queryFn: () => getJson<HistoryResponse>("/api/v1/history"),
    refetchInterval: 4000,
  });
  const latest = q.data?.items[0];
  const stub: PredictionResponse | null = latest
    ? {
        prediction_id: latest.prediction_id,
        label: latest.label,
        confidence: latest.confidence,
        reliability: latest.reliability,
        language: latest.language,
        compression_status: "clean",
        probabilities: { [latest.label]: latest.confidence },
        waveform: [],
        spectrogram: [],
      }
    : null;

  return (
    <section className="space-y-8">
      <header className="max-w-2xl space-y-3">
        <h1 className="font-[family-name:var(--font-display)] text-4xl tracking-tight md:text-5xl">
          Inference
        </h1>
        <p className="text-lg text-[var(--fg-muted)]">
          Latest verdict, calibrated confidence, and reliability badge from your recordings.
        </p>
      </header>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        {stub ? (
          <PredictionPanel data={stub} />
        ) : (
          <p className="text-sm text-[var(--fg-muted)]">
            No predictions yet -{" "}
            <Link className="text-[var(--accent)] underline" to="/upload">
              record or upload
            </Link>{" "}
            a clip.
          </p>
        )}
      </QueryStatus>
    </section>
  );
}
