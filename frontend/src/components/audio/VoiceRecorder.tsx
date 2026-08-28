import { Mic, Square, RotateCcw, AudioWaveform } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { useVoiceRecorder } from "@/hooks/useVoiceRecorder";
import { cn } from "@/lib/utils";

type VoiceRecorderApi = ReturnType<typeof useVoiceRecorder>;

type VoiceRecorderProps = {
  recorder: VoiceRecorderApi;
  className?: string;
};

function formatTime(sec: number): string {
  const s = Math.max(0, Math.floor(sec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${r.toString().padStart(2, "0")}`;
}

/** Polished long-form mic capture with live level meter and playback. */
export function VoiceRecorder({ recorder, className }: VoiceRecorderProps) {
  const {
    status,
    elapsedSec,
    level,
    error,
    recording,
    maxDurationSec,
    isSupported,
    start,
    stop,
    reset,
  } = recorder;

  const progress = Math.min(1, elapsedSec / maxDurationSec);
  const recordingActive = status === "recording";

  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--bg-elevated)]/80 p-6 backdrop-blur-sm",
        className,
      )}
    >
      <div
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          background: `radial-gradient(ellipse 70% 60% at 50% 0%, color-mix(in oklab, var(--accent) ${12 + level * 40}%, transparent), transparent)`,
        }}
        aria-hidden
      />

      <div className="relative space-y-5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="flex items-center gap-2 text-sm font-medium text-[var(--fg)]">
              <AudioWaveform className="h-4 w-4 text-[var(--accent)]" aria-hidden />
              Voice recording
            </p>
            <p className="mt-1 text-sm text-[var(--fg-muted)]">
              Capture up to {Math.round(maxDurationSec / 60)} minutes. Encoded as WAV for
              detection.
            </p>
          </div>
          <p
            className={cn(
              "font-[family-name:var(--font-display)] text-3xl tabular-nums tracking-tight",
              recordingActive && "text-[var(--ember)]",
            )}
            aria-live="polite"
          >
            {formatTime(elapsedSec)}
            <span className="ml-1 text-sm text-[var(--fg-muted)]">
              / {formatTime(maxDurationSec)}
            </span>
          </p>
        </div>

        <div
          className="flex h-16 items-end justify-center gap-1"
          role="img"
          aria-label={`Microphone level ${Math.round(level * 100)} percent`}
        >
          {Array.from({ length: 32 }, (_, i) => {
            const threshold = i / 32;
            const active = level > threshold;
            const h = 8 + ((i % 7) + 1) * 6;
            return (
              <span
                key={i}
                className={cn(
                  "w-1.5 rounded-full transition-all duration-100",
                  active
                    ? "bg-[var(--accent)]"
                    : "bg-[var(--border)]",
                  recordingActive && active && "shadow-[0_0_12px_color-mix(in_oklab,var(--accent)_50%,transparent)]",
                )}
                style={{
                  height: recordingActive && active ? `${h + level * 28}px` : `${h * 0.45}px`,
                }}
              />
            );
          })}
        </div>

        <div className="h-1.5 overflow-hidden rounded-full bg-[var(--border)]/60">
          <div
            className={cn(
              "h-full rounded-full bg-[var(--accent)] transition-[width] duration-200",
              recordingActive && "vaaniq-pulse-bar",
            )}
            style={{ width: `${progress * 100}%` }}
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {!recordingActive && status !== "processing" ? (
            <Button
              type="button"
              onClick={() => void start()}
              disabled={!isSupported}
              className="min-w-[9rem]"
            >
              <Mic className="h-4 w-4" aria-hidden />
              {recording ? "Record again" : "Start recording"}
            </Button>
          ) : null}
          {recordingActive ? (
            <Button
              type="button"
              variant="outline"
              onClick={() => void stop()}
              className="min-w-[9rem] border-[var(--ember)] text-[var(--ember)]"
            >
              <Square className="h-4 w-4 fill-current" aria-hidden />
              Stop
            </Button>
          ) : null}
          {status === "processing" ? (
            <Button type="button" disabled>
              Encoding WAV…
            </Button>
          ) : null}
          {recording ? (
            <Button type="button" variant="ghost" onClick={reset}>
              <RotateCcw className="h-4 w-4" aria-hidden />
              Clear
            </Button>
          ) : null}
        </div>

        {recording ? (
          <div className="space-y-2 rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 p-4">
            <p className="text-sm font-medium">
              Ready · {recording.file.name} · {formatTime(recording.durationSec)} ·{" "}
              {(recording.file.size / 1024).toFixed(0)} KB
            </p>
            <audio
              controls
              src={recording.objectUrl}
              className="w-full"
              preload="metadata"
            >
              Your browser does not support audio playback.
            </audio>
          </div>
        ) : null}

        {error ? (
          <p className="text-sm text-[var(--danger)]" role="alert">
            {error}
          </p>
        ) : null}
        {!isSupported ? (
          <p className="text-sm text-[var(--fg-muted)]">
            This browser cannot access the microphone. Use Chrome or Edge, or upload a file
            instead.
          </p>
        ) : null}
      </div>
    </div>
  );
}
