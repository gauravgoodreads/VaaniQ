import { useCallback, useEffect, useRef, useState } from "react";

import { concatFloat32, encodeWavMono, LIVE_MIC_CONSTRAINTS } from "@/lib/audio/wav";

export type RecorderStatus = "idle" | "recording" | "processing" | "ready" | "error";

export type VoiceRecording = {
  file: File;
  durationSec: number;
  objectUrl: string;
};

type UseVoiceRecorderOptions = {
  /** Hard cap in seconds (aligned with API max audio duration). */
  maxDurationSec?: number;
};

type UseVoiceRecorderResult = {
  status: RecorderStatus;
  elapsedSec: number;
  level: number;
  error: string | null;
  recording: VoiceRecording | null;
  maxDurationSec: number;
  isSupported: boolean;
  start: () => Promise<void>;
  stop: () => Promise<void>;
  reset: () => void;
};

const DEFAULT_MAX = 120;

/** Long-form microphone capture → uncompressed WAV (no Opus). */
export function useVoiceRecorder(
  options: UseVoiceRecorderOptions = {},
): UseVoiceRecorderResult {
  const maxDurationSec = options.maxDurationSec ?? DEFAULT_MAX;
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [elapsedSec, setElapsedSec] = useState(0);
  const [level, setLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState<VoiceRecording | null>(null);

  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const chunksRef = useRef<Float32Array[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const sampleRateRef = useRef(16000);
  const tickRef = useRef<number | null>(null);
  const startedAtRef = useRef<number>(0);
  const recordingRef = useRef<VoiceRecording | null>(null);

  const isSupported =
    typeof window !== "undefined" &&
    typeof navigator !== "undefined" &&
    Boolean(navigator.mediaDevices?.getUserMedia) &&
    typeof AudioContext !== "undefined";

  const cleanupTick = useCallback(() => {
    if (tickRef.current != null) {
      window.clearInterval(tickRef.current);
      tickRef.current = null;
    }
    setLevel(0);
  }, []);

  const releaseStream = useCallback(async () => {
    cleanupTick();
    processorRef.current?.disconnect();
    processorRef.current = null;
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    if (audioCtxRef.current) {
      await audioCtxRef.current.close().catch(() => undefined);
      audioCtxRef.current = null;
    }
  }, [cleanupTick]);

  const reset = useCallback(() => {
    void releaseStream();
    if (recordingRef.current?.objectUrl) URL.revokeObjectURL(recordingRef.current.objectUrl);
    recordingRef.current = null;
    setRecording(null);
    setElapsedSec(0);
    setError(null);
    setStatus("idle");
  }, [releaseStream]);

  useEffect(() => {
    return () => {
      void releaseStream();
      if (recordingRef.current?.objectUrl) URL.revokeObjectURL(recordingRef.current.objectUrl);
    };
  }, [releaseStream]);

  const stop = useCallback(async () => {
    if (!processorRef.current) return;
    setStatus("processing");
    const durationSec = Math.max(0.1, (Date.now() - startedAtRef.current) / 1000);
    const samples = concatFloat32(chunksRef.current);
    const rate = sampleRateRef.current;
    await releaseStream();
    try {
      const wav = encodeWavMono(samples, rate);
      const file = new File([wav], `vaaniq-recording-${Date.now()}.wav`, {
        type: "audio/wav",
      });
      const objectUrl = URL.createObjectURL(file);
      const next = { file, durationSec, objectUrl };
      recordingRef.current = next;
      setRecording(next);
      setElapsedSec(durationSec);
      setStatus("ready");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not encode recording");
      setStatus("error");
    }
  }, [releaseStream]);

  const start = useCallback(async () => {
    if (!isSupported) {
      setError("Microphone recording is not supported in this browser.");
      setStatus("error");
      return;
    }
    setError(null);
    if (recordingRef.current?.objectUrl) URL.revokeObjectURL(recordingRef.current.objectUrl);
    recordingRef.current = null;
    setRecording(null);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: LIVE_MIC_CONSTRAINTS,
      });
      streamRef.current = stream;
      const ctx = new AudioContext({ sampleRate: 16000 });
      audioCtxRef.current = ctx;
      sampleRateRef.current = ctx.sampleRate;
      const source = ctx.createMediaStreamSource(stream);
      const processor = ctx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      processor.onaudioprocess = (ev) => {
        const input = ev.inputBuffer.getChannelData(0);
        chunksRef.current.push(new Float32Array(input));
        let sum = 0;
        for (let i = 0; i < input.length; i += 1) {
          const s = input[i] ?? 0;
          sum += s * s;
        }
        setLevel(Math.min(1, Math.sqrt(sum / input.length) * 3));
      };
      const mute = ctx.createGain();
      mute.gain.value = 0;
      source.connect(processor);
      processor.connect(mute);
      mute.connect(ctx.destination);

      startedAtRef.current = Date.now();
      setElapsedSec(0);
      setStatus("recording");
      tickRef.current = window.setInterval(() => {
        const elapsed = (Date.now() - startedAtRef.current) / 1000;
        setElapsedSec(elapsed);
        if (elapsed >= maxDurationSec) {
          void stop();
        }
      }, 200);
    } catch (err) {
      await releaseStream();
      setError(
        err instanceof Error ? err.message : "Microphone permission denied or unavailable.",
      );
      setStatus("error");
    }
  }, [isSupported, maxDurationSec, releaseStream, stop]);

  return {
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
  };
}
