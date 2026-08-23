import { useQuery } from "@tanstack/react-query";

import { getJson } from "@/api/client";
import type { HistoryResponse, PredictionResponse } from "@/api/types";
import { QueryStatus } from "@/components/QueryStatus";
import { PredictionPanel } from "@/pages/UploadPage";

/** Detailed inference view for the latest prediction (ROADMAP-054). */
export function InferencePage() {
  const q = useQuery({
    queryKey: ["history"],
    queryFn: () => getJson<HistoryResponse>("/api/v1/history"),
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
    <section className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Inference</h1>
      <p className="text-[var(--fg-muted)]">Latest verdict, confidence, and reliability badge.</p>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        {stub ? (
          <PredictionPanel data={stub} />
        ) : (
          <p className="text-sm">No predictions yet — use Upload.</p>
        )}
      </QueryStatus>
    </section>
  );
}
