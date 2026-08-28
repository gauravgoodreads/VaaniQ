import { useMutation } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { Radio } from "lucide-react";

import { apiBaseUrl, ApiError } from "@/api/client";
import type { PredictionResponse } from "@/api/types";
import { HonestyBanner, PageHeader, Surface } from "@/components/layout/PageChrome";
import { Button } from "@/components/ui/button";
import { PredictionPanel } from "@/pages/UploadPage";

type LivePred = { label: string; confidence: number; at: string };

/** Real-time microphone streaming → PCM16 live ingest + final detect. */
export function LivePage() {
  const [language, setLanguage] = useState("hi");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [streaming, setStreaming] = useState(false);
  const [level, setLevel] = useState(0);
  const [timeline, setTimeline] = useState<LivePred[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [finalResult, setFinalResult] = useState<PredictionResponse | null>(null);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const sessionRef = useRef<string | null>(null);
  const pcmChunksRef = useRef<Int16Array[]>([]);

  const startSession = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/live/session`, { method: "POST" });
      if (!res.ok) throw new Error("Could not start live session");
      return (await res.json()) as { session_id: string };
    },
    onSuccess: (data) => {
      setSessionId(data.session_id);
      sessionRef.current = data.session_id;
    },
  });

  async function stopStreaming() {
    setStreaming(false);
    processorRef.current?.disconnect();
    processorRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (audioCtxRef.current) {
      await audioCtxRef.current.close().catch(() => undefined);
      audioCtxRef.current = null;
    }
    setLevel(0);
  }

  async function startStreaming() {
    setError(null);
    setTimeline([]);
    setFinalResult(null);
    pcmChunksRef.current = [];
    let sid = sessionRef.current;
    if (!sid) {
      const data = await startSession.mutateAsync();
      sid = data.session_id;
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
    });
    streamRef.current = stream;
    const ctx = new AudioContext({ sampleRate: 16000 });
    audioCtxRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const processor = ctx.createScriptProcessor(4096, 1, 1);
    processorRef.current = processor;

    processor.onaudioprocess = (ev) => {
      const input = ev.inputBuffer.getChannelData(0);
      let sum = 0;
      const pcm = new Int16Array(input.length);
      for (let i = 0; i < input.length; i += 1) {
        const s = Math.max(-1, Math.min(1, input[i] ?? 0));
        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        sum += s * s;
      }
      setLevel(Math.min(1, Math.sqrt(sum / input.length) * 3));
      pcmChunksRef.current.push(pcm);
      void sendPcm(sid!, pcm);
    };

    source.connect(processor);
    processor.connect(ctx.destination);
    setStreaming(true);
  }

  async function sendPcm(sid: string, pcm: Int16Array) {
    try {
      const body = new FormData();
      body.append("session_id", sid);
      body.append(
        "chunk",
        new Blob([pcm.buffer], { type: "application/octet-stream" }),
        "chunk.pcm",
      );
      const res = await fetch(`${apiBaseUrl()}/api/v1/live/ingest`, { method: "POST", body });
      if (!res.ok) return;
      const data = (await res.json()) as {
        predictions: { label: string; confidence: number }[];
      };
      if (data.predictions?.length) {
        setTimeline((prev) => [
          ...data.predictions.map((p) => ({
            label: p.label,
            confidence: p.confidence,
            at: new Date().toLocaleTimeString(),
          })),
          ...prev,
        ].slice(0, 40));
      }
    } catch {
      /* keep streaming */
    }
  }

  async function finalizeDetect() {
    await stopStreaming();
    const parts = pcmChunksRef.current;
    if (!parts.length) {
      setError("No audio captured");
      return;
    }
    const total = parts.reduce((n, p) => n + p.length, 0);
    const merged = new Int16Array(total);
    let o = 0;
    for (const p of parts) {
      merged.set(p, o);
      o += p.length;
    }
    // Build WAV for full inference + Whisper/Groq enrichment
    const wav = encodeWav(merged, 16000);
    const file = new File([wav], `live-${Date.now()}.wav`, { type: "audio/wav" });
    const body = new FormData();
    body.append("file", file);
    body.append("language", language);
    body.append("model_id", "aasist-v1");
    const res = await fetch(`${apiBaseUrl()}/api/v1/inference`, { method: "POST", body });
    if (!res.ok) throw new ApiError("Inference failed", res.status);
    setFinalResult((await res.json()) as PredictionResponse);
  }

  useEffect(() => {
    return () => {
      void stopStreaming();
    };
  }, []);

  return (
    <section className="space-y-8">
      <PageHeader
        title="Live"
        subtitle="Speak into the mic for sliding-window detection, then run a full Whisper + calibrated pass."
      />
      <HonestyBanner>
        Live windows (~3s) skip silence and need stronger fake evidence before labeling FAKE. Your
        voice should read as real. Final detect adds Whisper (Groq or local) and optional Groq LLM
        notes when <code>GROQ_API_KEY</code> is set.
      </HonestyBanner>

      <Surface title="Stream">
        <div className="flex flex-wrap items-end gap-4">
          <label className="grid gap-1 text-sm text-[var(--fg)]">
            Language
            <select
              className="h-10 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              aria-label="Language"
            >
              <option value="hi">Hindi</option>
              <option value="mr">Marathi</option>
              <option value="ta">Tamil</option>
            </select>
          </label>
          {!streaming ? (
            <Button type="button" onClick={() => void startStreaming()}>
              <Radio className="h-4 w-4" aria-hidden />
              Start live mic
            </Button>
          ) : (
            <>
              <Button type="button" variant="outline" onClick={() => void stopStreaming()}>
                Pause stream
              </Button>
              <Button type="button" onClick={() => void finalizeDetect()}>
                Stop & full detect
              </Button>
            </>
          )}
          {sessionId ? (
            <p className="text-sm text-[var(--fg-muted)]">
              Session <code>{sessionId.slice(0, 8)}…</code>
            </p>
          ) : null}
        </div>
        <div className="mt-5 h-3 overflow-hidden rounded-full bg-[var(--border)]">
          <div
            className="h-full rounded-full bg-[var(--accent)] transition-[width] duration-100"
            style={{ width: `${Math.round(level * 100)}%` }}
          />
        </div>
      </Surface>

      <Surface title="Live prediction timeline">
        {timeline.length === 0 ? (
          <p className="text-sm text-[var(--fg-muted)]">
            Speak clearly for a few seconds. Windows (~3s) appear here; silence is ignored.
          </p>
        ) : (
          <ol className="space-y-2">
            {timeline.map((p, i) => (
              <li
                key={`${p.at}-${i}`}
                className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 px-3 py-2 text-sm text-[var(--fg)]"
              >
                <span
                  className={`font-medium capitalize ${
                    p.label === "fake" ? "text-[var(--danger)]" : "text-[var(--accent)]"
                  }`}
                >
                  {p.label}
                </span>
                <span className="tabular-nums text-[var(--fg-muted)]">
                  {p.confidence.toFixed(2)} · {p.at}
                </span>
              </li>
            ))}
          </ol>
        )}
      </Surface>

      {error ? <p className="text-sm text-[var(--danger)]">{error}</p> : null}
      {finalResult ? <PredictionPanel data={finalResult} /> : null}
    </section>
  );
}

function encodeWav(samples: Int16Array, sampleRate: number): Blob {
  const dataSize = samples.length * 2;
  const buffer = new ArrayBuffer(44 + dataSize);
  const view = new DataView(buffer);
  const write = (offset: number, s: string) => {
    for (let i = 0; i < s.length; i += 1) view.setUint8(offset + i, s.charCodeAt(i));
  };
  write(0, "RIFF");
  view.setUint32(4, 36 + dataSize, true);
  write(8, "WAVE");
  write(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  write(36, "data");
  view.setUint32(40, dataSize, true);
  let o = 44;
  for (let i = 0; i < samples.length; i += 1) {
    view.setInt16(o, samples[i] ?? 0, true);
    o += 2;
  }
  return new Blob([buffer], { type: "audio/wav" });
}
