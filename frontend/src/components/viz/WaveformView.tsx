type WaveformViewProps = {
  samples: number[];
};

/** SVG waveform preview (REQ-087). */
export function WaveformView({ samples }: WaveformViewProps) {
  if (samples.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No waveform samples.</p>;
  }
  const w = 640;
  const h = 96;
  const mid = h / 2;
  const step = Math.max(1, Math.floor(samples.length / w));
  const pts = samples.filter((_, i) => i % step === 0);
  const points = pts.map((v, i) => `${i},${mid - v * mid * 0.92}`).join(" ");
  const area = `0,${h} ${points} ${pts.length - 1},${h}`;

  return (
    <div>
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-[var(--fg-muted)]">Waveform</p>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="w-full max-w-3xl rounded-xl border border-[var(--border)] bg-[linear-gradient(180deg,color-mix(in_oklab,var(--accent)_8%,transparent),transparent)]"
        role="img"
        aria-label="Waveform"
      >
        <polygon fill="color-mix(in oklab, var(--accent) 18%, transparent)" points={area} />
        <polyline
          fill="none"
          stroke="var(--accent)"
          strokeWidth="1.5"
          points={points}
        />
      </svg>
    </div>
  );
}
