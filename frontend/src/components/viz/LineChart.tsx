type LineChartProps = {
  points: { x: number; y: number }[];
  xlabel: string;
  ylabel: string;
  title: string;
};

/** Lightweight SVG line chart for ECE / reliability diagrams. */
export function LineChart({ points, xlabel, ylabel, title }: LineChartProps) {
  const w = 420;
  const h = 220;
  const pad = 36;
  if (points.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No chart data.</p>;
  }
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const xmin = Math.min(...xs);
  const xmax = Math.max(...xs, xmin + 1e-6);
  const ymin = Math.min(...ys);
  const ymax = Math.max(...ys, ymin + 1e-6);
  const px = (x: number) => pad + ((x - xmin) / (xmax - xmin)) * (w - 2 * pad);
  const py = (y: number) => h - pad - ((y - ymin) / (ymax - ymin)) * (h - 2 * pad);
  const d = points.map((p, i) => `${i === 0 ? "M" : "L"} ${px(p.x)} ${py(p.y)}`).join(" ");
  return (
    <figure className="rounded border border-[var(--border)] bg-[var(--bg-elevated)] p-3">
      <figcaption className="mb-2 text-sm font-medium">{title}</figcaption>
      <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label={title}>
        <path d={d} fill="none" stroke="var(--accent)" strokeWidth="2" />
        <text x={w / 2} y={h - 8} textAnchor="middle" className="fill-[var(--fg-muted)] text-[10px]">
          {xlabel}
        </text>
        <text
          x="12"
          y={h / 2}
          className="fill-[var(--fg-muted)] text-[10px]"
          transform={`rotate(-90 12 ${h / 2})`}
        >
          {ylabel}
        </text>
      </svg>
    </figure>
  );
}
