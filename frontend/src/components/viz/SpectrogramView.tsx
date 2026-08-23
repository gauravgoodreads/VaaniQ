type SpectrogramViewProps = {
  matrix: number[][];
};

/** Interactive spectrogram grid (REQ-077). */
export function SpectrogramView({ matrix }: SpectrogramViewProps) {
  if (matrix.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No spectrogram.</p>;
  }
  const flat = matrix.flat();
  const max = Math.max(...flat, 1e-6);
  const rows = matrix.length;
  const cols = matrix[0]?.length ?? 0;
  return (
    <div>
      <p className="mb-1 text-sm text-[var(--fg-muted)]">Spectrogram</p>
      <div
        className="grid max-w-3xl overflow-hidden rounded border border-[var(--border)]"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
        role="img"
        aria-label="Spectrogram"
      >
        {matrix.map((row, r) =>
          row.map((v, c) => (
            <div
              key={`${r}-${c}`}
              title={`${r},${c}: ${v.toFixed(3)}`}
              style={{
                backgroundColor: `rgba(31, 111, 106, ${0.15 + 0.85 * (v / max)})`,
                aspectRatio: "1",
              }}
            />
          )),
        )}
        <span className="sr-only">
          {rows} by {cols} spectrogram cells
        </span>
      </div>
    </div>
  );
}
