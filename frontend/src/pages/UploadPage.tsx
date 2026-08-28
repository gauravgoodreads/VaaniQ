import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Upload as UploadIcon } from "lucide-react";

import { apiBaseUrl, ApiError } from "@/api/client";
import type { PredictionResponse } from "@/api/types";
import { VoiceRecorder } from "@/components/audio/VoiceRecorder";
import { Button } from "@/components/ui/button";
import { ConfidenceGauge } from "@/components/viz/ConfidenceGauge";
import { ReliabilityBadge } from "@/components/viz/ReliabilityBadge";
import { SpectrogramView } from "@/components/viz/SpectrogramView";
import { WaveformView } from "@/components/viz/WaveformView";
import { useVoiceRecorder } from "@/hooks/useVoiceRecorder";
import { cn } from "@/lib/utils";

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
    let detail = "Inference failed";
    try {
      const problem = (await response.json()) as { detail?: string | { msg?: string }[] };
      if (typeof problem.detail === "string") detail = problem.detail;
    } catch {
      /* keep default */
    }
    throw new ApiError(detail, response.status);
  }
  return (await response.json()) as PredictionResponse;
}

/** Upload + mic recording + inference with waveform/spectrogram (ROADMAP-054). */
export function UploadPage() {
  const [language, setLanguage] = useState("hi");
  const [file, setFile] = useState<File | null>(null);
  const [source, setSource] = useState<"file" | "mic">("mic");
  const recorder = useVoiceRecorder({ maxDurationSec: 120 });
  const activeFile = source === "mic" ? recorder.recording?.file ?? null : file;

  const mutation = useMutation({
    mutationFn: () => {
      if (!activeFile) throw new Error("No audio selected");
      return postInference(activeFile, language);
    },
  });

  return (
    <section className="space-y-8">
      <header className="max-w-2xl space-y-3">
        <h1 className="font-[family-name:var(--font-display)] text-4xl tracking-tight md:text-5xl">
          Upload
        </h1>
        <p className="text-lg text-[var(--fg-muted)]">
          Record up to two minutes of speech, or drop an existing clip - then run Opus-aware
          deepfake detection with calibrated reliability.
        </p>
      </header>

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Audio source">
        {(
          [
            { id: "mic" as const, label: "Record voice" },
            { id: "file" as const, label: "Upload file" },
          ] as const
        ).map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={source === tab.id}
            className={cn(
              "rounded-full px-4 py-2 text-sm transition-colors",
              source === tab.id
                ? "bg-[var(--accent)] text-[var(--accent-fg)]"
                : "border border-[var(--border)] text-[var(--fg-muted)] hover:text-[var(--fg)]",
            )}
            onClick={() => setSource(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {source === "mic" ? <VoiceRecorder recorder={recorder} /> : null}

      {source === "file" ? (
        <label className="group flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border border-dashed border-[var(--border)] bg-[var(--bg-elevated)]/60 px-6 py-14 transition hover:border-[var(--accent)]">
          <UploadIcon className="h-8 w-8 text-[var(--accent)]" aria-hidden />
          <span className="font-medium">Drop audio or click to browse</span>
          <span className="text-sm text-[var(--fg-muted)]">
            WAV, FLAC, OGG, Opus, MP3 · up to 120 s · max 25 MB
          </span>
          <input
            type="file"
            accept="audio/*,.wav,.flac,.ogg,.opus,.mp3"
            aria-label="Audio file"
            className="sr-only"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
          {file ? (
            <span className="text-sm text-[var(--accent)]">
              {file.name} · {(file.size / 1024).toFixed(0)} KB
            </span>
          ) : null}
        </label>
      ) : null}

      <div className="flex flex-wrap items-end gap-4">
        <label className="grid gap-1 text-sm">
          Language
          <select
            className="h-10 rounded-lg border border-[var(--border)] bg-[var(--bg-elevated)] px-3"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            aria-label="Language"
          >
            <option value="hi">Hindi</option>
            <option value="mr">Marathi</option>
            <option value="ta">Tamil</option>
          </select>
        </label>
        <Button
          type="button"
          disabled={!activeFile || mutation.isPending}
          onClick={() => mutation.mutate()}
          className="h-11 min-w-[8rem] px-6"
        >
          {mutation.isPending ? "Running…" : "Detect"}
        </Button>
      </div>

      {mutation.data ? <PredictionPanel data={mutation.data} /> : null}
      {mutation.error ? (
        <p className="text-sm text-[var(--danger)]">{(mutation.error as Error).message}</p>
      ) : null}
    </section>
  );
}

export function PredictionPanel({ data }: { data: PredictionResponse }) {
  const verdictTone =
    data.label === "fake" || data.label === "ai" || data.label === "spoof"
      ? "text-[var(--danger)]"
      : "text-[var(--success)]";

  return (
    <div className="vaaniq-enter space-y-6 rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)]/70 p-6 text-[var(--fg)]">
      <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          <p className="text-xs uppercase tracking-[0.18em] text-[var(--fg-muted)]">Verdict</p>
          <p
            className={cn(
              "font-[family-name:var(--font-display)] text-4xl capitalize tracking-tight",
              verdictTone,
            )}
          >
            {data.label}
          </p>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Language" value={data.language} />
            <div>
              <p className="text-xs uppercase tracking-wide text-[var(--fg-muted)]">Reliability</p>
              <div className="mt-1">
                <ReliabilityBadge level={data.reliability} />
              </div>
            </div>
            <Stat label="Compression" value={data.compression_status} />
          </div>
        </div>
        <ConfidenceGauge value={data.confidence} />
      </div>

      {(data.analysis_summary || data.transcript || data.accent_notes) && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 p-4">
            <p className="text-xs uppercase tracking-[0.16em] text-[var(--fg-muted)]">Analysis</p>
            <p className="mt-2 text-sm leading-relaxed">{data.analysis_summary || "-"}</p>
            <p className="mt-3 text-xs text-[var(--fg-muted)]">
              Whisper: {data.whisper_backend || "-"} · LLM: {data.enrichment_backend || "-"}
            </p>
          </div>
          <div className="rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 p-4 space-y-2 text-sm">
            <p>
              <span className="text-[var(--fg-muted)]">Detected lang:</span>{" "}
              {data.detected_language ?? "-"}
            </p>
            <p>
              <span className="text-[var(--fg-muted)]">Accent:</span> {data.accent_notes || "-"}
            </p>
            <p>
              <span className="text-[var(--fg-muted)]">Language notes:</span>{" "}
              {data.language_notes || "-"}
            </p>
            <p>
              <span className="text-[var(--fg-muted)]">Risk:</span> {data.risk_notes || "-"}
            </p>
          </div>
        </div>
      )}

      {data.transcript ? (
        <div className="rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 p-4">
          <p className="text-xs uppercase tracking-[0.16em] text-[var(--fg-muted)]">Transcript</p>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed">{data.transcript}</p>
        </div>
      ) : null}

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
