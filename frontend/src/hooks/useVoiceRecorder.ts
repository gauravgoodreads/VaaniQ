import { useCallback, useEffect, useRef, useState } from "react";

import { blobToWavFile, preferredRecorderMime } from "@/lib/audio/wav";

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

/** Long-form microphone capture → WAV file for VaaniQ upload/inference. */
export function useVoiceRecorder(
  options: UseVoiceRecorderOptions = {},
): UseVoiceRecorderResult {
  const maxDurationSec = options.maxDurationSec ?? DEFAULT_MAX;
  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [elapsedSec, setElapsedSec] = useState(0);
  const [level, setLevel] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState<VoiceRecording | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const rafRef = useRef<number | null>(null);
  const tickRef = useRef<number | null>(null);
  const startedAtRef = useRef<number>(0);
  const stopPromiseRef = useRef<((blob: Blob) => void) | null>(null);

  const isSupported =
    typeof window !== "undefined" &&
    typeof navigator !== "undefined" &&
    Boolean(navigator.mediaDevices?.getUserMedia) &&
    typeof MediaRecorder !== "undefined";

  const cleanupMeters = useCallback(() => {
    if (rafRef.current != null) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    if (tickRef.current != null) {
      window.clearInterval(tickRef.current);
      tickRef.current = null;
    }
    setLevel(0);
  }, []);

  const releaseStream = useCallback(async () => {
    cleanupMeters();
    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    mediaRecorderRef.current = null;
    if (audioCtxRef.current) {
      await audioCtxRef.current.close().catch(() => undefined);
      audioCtxRef.current = null;
      analyserRef.current = null;
    }
  }, [cleanupMeters]);

  const reset = useCallback(() => {
    void releaseStream();
    if (recording?.objectUrl) URL.revokeObjectURL(recording.objectUrl);
    setRecording(null);
    setElapsedSec(0);
    setError(null);
    setStatus("idle");
  }, [recording, releaseStream]);

  useEffect(() => {
    return () => {
      void releaseStream();
      if (recording?.objectUrl) URL.revokeObjectURL(recording.objectUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- unmount only
  }, []);

  const startMeter = useCallback((stream: MediaStream) => {
    const ctx = new AudioContext();
    audioCtxRef.current = ctx;
    const source = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 256;
    source.connect(analyser);
    analyserRef.current = analyser;
    const data = new Uint8Array(analyser.frequencyBinCount);

    const loop = () => {
      analyser.getByteTimeDomainData(data);
      let sum = 0;
      for (let i = 0; i < data.length; i += 1) {
        const v = ((data[i] ?? 128) - 128) / 128;
        sum += v * v;
      }
      setLevel(Math.min(1, Math.sqrt(sum / data.length) * 3));
      rafRef.current = requestAnimationFrame(loop);
    };
    rafRef.current = requestAnimationFrame(loop);
  }, []);

  const stop = useCallback(async () => {
    const recorder = mediaRecorderRef.current;
    if (!recorder || recorder.state === "inactive") return;

    setStatus("processing");
    const blob = await new Promise<Blob>((resolve) => {
      stopPromiseRef.current = resolve;
      recorder.stop();
    });
    const durationSec = Math.max(0.1, (Date.now() - startedAtRef.current) / 1000);
    await releaseStream();

    try {
      const file = await blobToWavFile(blob, `vaaniq-recording-${Date.now()}.wav`);
      const objectUrl = URL.createObjectURL(file);
      setRecording({ file, durationSec, objectUrl });
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
    if (recording?.objectUrl) URL.revokeObjectURL(recording.objectUrl);
    setRecording(null);
    chunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          channelCount: 1,
        },
      });
      streamRef.current = stream;
      const mime = preferredRecorderMime();
      const recorder = mime
        ? new MediaRecorder(stream, { mimeType: mime })
        : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = () => {
        const type = recorder.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type });
        stopPromiseRef.current?.(blob);
        stopPromiseRef.current = null;
      };

      startedAtRef.current = Date.now();
      setElapsedSec(0);
      setStatus("recording");
      recorder.start(250);
      startMeter(stream);

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
        err instanceof Error
          ? err.message
          : "Microphone permission denied or unavailable.",
      );
      setStatus("error");
    }
  }, [isSupported, maxDurationSec, recording, releaseStream, startMeter, stop]);

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
