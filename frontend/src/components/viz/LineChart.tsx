type LineChartProps = {
  points: { x: number; y: number }[];
  xlabel: string;
  ylabel: string;
  title: string;
};

const TICKS = [0, 0.2, 0.4, 0.6, 0.8, 1];

/** Lightweight SVG line chart for ECE / reliability diagrams. */
export function LineChart({ points, xlabel, ylabel, title }: LineChartProps) {
  const w = 420;
  const h = 240;
  const pad = 44;
  if (points.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No chart data.</p>;
  }
  const px = (x: number) => pad + x * (w - 2 * pad);
  const py = (y: number) => h - pad - y * (h - 2 * pad);
  const d = points.map((p, i) => `${i === 0 ? "M" : "L"} ${px(p.x)} ${py(p.y)}`).join(" ");
  const perfect = `M ${px(0)} ${py(0)} L ${px(1)} ${py(1)}`;
  return (
    <figure className="rounded border border-[var(--border)] bg-[var(--bg-elevated)] p-3">
      <figcaption className="mb-2 text-sm font-medium">{title}</figcaption>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label={title}>
        {TICKS.map((tick) => (
          <g key={`grid-${tick}`}>
            <line
              x1={px(tick)}
              y1={pad}
              x2={px(tick)}
              y2={h - pad}
              stroke="var(--border)"
              strokeWidth="1"
            />
            <line
              x1={pad}
              y1={py(tick)}
              x2={w - pad}
              y2={py(tick)}
              stroke="var(--border)"
              strokeWidth="1"
            />
            <text x={px(tick)} y={h - 18} textAnchor="middle" className="fill-[var(--fg-muted)] text-[9px]">
              {tick.toFixed(1)}
            </text>
            <text x={16} y={py(tick) + 3} textAnchor="end" className="fill-[var(--fg-muted)] text-[9px]">
              {tick.toFixed(1)}
            </text>
          </g>
        ))}
        <path d={perfect} fill="none" stroke="var(--fg-muted)" strokeWidth="1.5" strokeDasharray="4 4" />
        <path d={d} fill="none" stroke="var(--accent)" strokeWidth="2.5" />
        {points.map((p, index) => (
          <circle
            key={`point-${index}`}
            cx={px(p.x)}
            cy={py(p.y)}
            r="3.5"
            fill="var(--accent)"
          />
        ))}
        <text x={w / 2} y={h - 4} textAnchor="middle" className="fill-[var(--fg-muted)] text-[10px]">
          {xlabel}
        </text>
        <text
          x="14"
          y={h / 2}
          className="fill-[var(--fg-muted)] text-[10px]"
          transform={`rotate(-90 14 ${h / 2})`}
        >
          {ylabel}
        </text>
      </svg>
    </figure>
  );
}
