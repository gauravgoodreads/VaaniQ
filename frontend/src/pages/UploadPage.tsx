import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { apiBaseUrl, ApiError } from "@/api/client";
import type { PredictionResponse } from "@/api/types";
import { Button } from "@/components/ui/button";
import { ConfidenceGauge } from "@/components/viz/ConfidenceGauge";
import { ReliabilityBadge } from "@/components/viz/ReliabilityBadge";
import { SpectrogramView } from "@/components/viz/SpectrogramView";
import { WaveformView } from "@/components/viz/WaveformView";

async function postInference(file: File, language: string): Promise<PredictionResponse> {
  const body = new FormData();
  body.append("file", file);
  body.append("language", language);
  body.append("model_id", "aasist-v1");
  const response = await fetch(`${apiBaseUrl()}/api/v1/inference`, {
    method: "POST",
    body,
  });
  if (!response.ok) {
    throw new ApiError("Inference failed", response.status);
  }
  return (await response.json()) as PredictionResponse;
}

/** Upload + inference UI with waveform/spectrogram previews (ROADMAP-054). */
export function UploadPage() {
  const [language, setLanguage] = useState("hi");
  const [file, setFile] = useState<File | null>(null);
  const mutation = useMutation({ mutationFn: () => postInference(file as File, language) });

  return (
    <section className="space-y-6">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Upload</h1>
      <p className="max-w-2xl text-[var(--fg-muted)]">
        Upload a clip for Opus-aware deepfake detection with calibrated reliability.
      </p>
      <div className="flex flex-wrap items-end gap-4">
        <label className="grid gap-1 text-sm">
          Language
          <select
            className="rounded border border-[var(--border)] bg-transparent px-2 py-1"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            aria-label="Language"
          >
            <option value="hi">Hindi</option>
            <option value="mr">Marathi</option>
            <option value="ta">Tamil</option>
          </select>
        </label>
        <label className="grid gap-1 text-sm">
          Audio file
          <input
            type="file"
            accept="audio/*"
            aria-label="Audio file"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <Button
          type="button"
          disabled={!file || mutation.isPending}
          onClick={() => mutation.mutate()}
        >
          {mutation.isPending ? "Running…" : "Detect"}
        </Button>
      </div>
      {mutation.data ? <PredictionPanel data={mutation.data} /> : null}
      {mutation.error ? (
        <p className="text-sm text-red-600">{(mutation.error as Error).message}</p>
      ) : null}
    </section>
  );
}

export function PredictionPanel({ data }: { data: PredictionResponse }) {
  return (
    <div className="vaaniq-enter space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="grid gap-2 sm:grid-cols-2">
          <Stat label="Verdict" value={data.label} />
          <Stat label="Language" value={data.language} />
          <div>
            <p className="text-xs uppercase tracking-wide text-[var(--fg-muted)]">Reliability</p>
            <ReliabilityBadge level={data.reliability} />
          </div>
          <Stat label="Compression" value={data.compression_status} />
        </div>
        <ConfidenceGauge value={data.confidence} />
      </div>
      <WaveformView samples={data.waveform ?? []} />
      <SpectrogramView matrix={data.spectrogram ?? []} />
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs uppercase tracking-wide text-[var(--fg-muted)]">{label}</p>
      <p className="text-lg font-medium">{value}</p>
    </div>
  );
}
