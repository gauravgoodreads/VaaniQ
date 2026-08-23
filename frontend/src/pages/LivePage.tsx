import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { apiBaseUrl } from "@/api/client";
import { Button } from "@/components/ui/button";

type LiveSession = { session_id: string };

/** Live microphone / sliding-window inference (ROADMAP-055 / OQ-019). */
export function LivePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [log, setLog] = useState<string[]>([]);

  const start = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/live/session`, { method: "POST" });
      if (!res.ok) throw new Error("session failed");
      return (await res.json()) as LiveSession;
    },
    onSuccess: (data) => setSessionId(data.session_id),
  });

  async function recordBurst() {
    if (!sessionId) return;
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const recorder = new MediaRecorder(stream);
    const chunks: BlobPart[] = [];
    recorder.ondataavailable = (e) => {
      chunks.push(e.data);
    };
    recorder.start();
    await new Promise((r) => setTimeout(r, 1500));
    recorder.stop();
    await new Promise((r) => {
      recorder.onstop = () => r(null);
    });
    stream.getTracks().forEach((t) => t.stop());
    const blob = new Blob(chunks, { type: "audio/webm" });
    const buf = new Uint8Array(await blob.arrayBuffer());
    const pcm = new Int16Array(Math.max(8000, Math.floor(buf.length / 2)));
    const body = new FormData();
    body.append("session_id", sessionId);
    body.append(
      "chunk",
      new Blob([pcm.buffer], { type: "application/octet-stream" }),
      "chunk.pcm",
    );
    const res = await fetch(`${apiBaseUrl()}/api/v1/live/ingest`, { method: "POST", body });
    if (!res.ok) throw new Error("ingest failed");
    const data = (await res.json()) as {
      session_id: string;
      predictions: { label: string; confidence: number }[];
    };
    setLog((prev) => [
      ...prev,
      ...data.predictions.map((p) => `${p.label} @ ${p.confidence.toFixed(2)}`),
    ]);
  }

  return (
    <section className="space-y-4">
      <h1 className="font-[family-name:var(--font-display)] text-3xl">Live</h1>
      <p className="text-[var(--fg-muted)]">
        Sliding-window microphone mode (2.0 s window / 0.5 s hop — ASSUMPTION OQ-019).
      </p>
      <p className="max-w-2xl text-sm text-[var(--fg-muted)]" role="note">
        Browser MediaRecorder output is WebM/Opus. This demo currently sends a PCM-shaped buffer
        derived from the recorded bytes, not a decoded linear PCM waveform. Treat live labels as
        a session-path check, not as a published detection result.
      </p>
      <div className="flex gap-3">
        <Button type="button" onClick={() => start.mutate()} disabled={!!sessionId}>
          Start session
        </Button>
        <Button type="button" onClick={() => void recordBurst()} disabled={!sessionId}>
          Record burst
        </Button>
      </div>
      {sessionId ? <p className="text-sm">Session: {sessionId}</p> : null}
      <h2 className="text-lg">Prediction timeline</h2>
      <ol className="space-y-1 text-sm">
        {log.map((line, i) => (
          <li key={`${line}-${i}`} className="border-l-2 border-[var(--accent)] pl-3">
            {line}
          </li>
        ))}
      </ol>
    </section>
  );
}
