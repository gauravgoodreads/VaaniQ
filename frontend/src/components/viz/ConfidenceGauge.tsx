type ConfidenceGaugeProps = {
  value: number;
  label?: string;
};

/** Circular confidence gauge for calibrated scores (RQ4 / O7). */
export function ConfidenceGauge({ value, label = "Confidence" }: ConfidenceGaugeProps) {
  const clamped = Math.min(1, Math.max(0, value));
  const r = 42;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - clamped);
  return (
    <div className="flex items-center gap-3" aria-label={`${label} ${clamped.toFixed(2)}`}>
      <svg width="112" height="112" viewBox="0 0 112 112" role="img">
        <circle cx="56" cy="56" r={r} fill="none" stroke="var(--border)" strokeWidth="10" />
        <circle
          cx="56"
          cy="56"
          r={r}
          fill="none"
          stroke="var(--accent)"
          strokeWidth="10"
          strokeDasharray={c}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform="rotate(-90 56 56)"
          className="transition-all duration-500"
        />
        <text x="56" y="62" textAnchor="middle" className="fill-[var(--fg)] text-lg font-medium">
          {clamped.toFixed(2)}
        </text>
      </svg>
      <p className="text-sm text-[var(--fg-muted)]">{label}</p>
    </div>
  );
}
