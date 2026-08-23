type WaveformViewProps = {
  samples: number[];
};

/** SVG waveform preview (REQ-087). */
export function WaveformView({ samples }: WaveformViewProps) {
  if (samples.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No waveform samples.</p>;
  }
  const w = 640;
  const h = 80;
  const mid = h / 2;
  const step = Math.max(1, Math.floor(samples.length / w));
  const points = samples
    .filter((_, i) => i % step === 0)
    .map((v, i) => `${i},${mid - v * mid}`)
    .join(" ");
  return (
    <div>
      <p className="mb-1 text-sm text-[var(--fg-muted)]">Waveform</p>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="w-full max-w-3xl rounded border border-[var(--border)] bg-[var(--bg-elevated)]"
        role="img"
        aria-label="Waveform"
      >
        <polyline fill="none" stroke="currentColor" strokeWidth="1" points={points} />
      </svg>
    </div>
  );
}
