import { useEffect, useRef } from "react";

type SpectrogramViewProps = {
  matrix: number[][];
};

/** Canvas spectrogram (REQ-077). */
export function SpectrogramView({ matrix }: SpectrogramViewProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || matrix.length === 0) return;
    const rows = matrix.length;
    const cols = matrix[0]?.length ?? 0;
    if (cols === 0) return;
    const width = 720;
    const height = 220;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    const flat = matrix.flat();
    const max = Math.max(...flat, 1e-6);
    const cellW = width / cols;
    const cellH = height / rows;
    for (let r = 0; r < rows; r += 1) {
      const row = matrix[r] ?? [];
      for (let c = 0; c < cols; c += 1) {
        const v = (row[c] ?? 0) / max;
        const g = Math.round(40 + v * 180);
        const a = Math.round(80 + v * 175);
        ctx.fillStyle = `rgb(10, ${g}, ${Math.round(90 + v * 80)})`;
        ctx.globalAlpha = a / 255;
        ctx.fillRect(c * cellW, height - (r + 1) * cellH, cellW + 0.5, cellH + 0.5);
      }
    }
    ctx.globalAlpha = 1;
  }, [matrix]);

  if (matrix.length === 0) {
    return <p className="text-sm text-[var(--fg-muted)]">No spectrogram.</p>;
  }

  return (
    <div>
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-[var(--fg-muted)]">
        Spectrogram
      </p>
      <canvas
        ref={canvasRef}
        className="w-full max-w-3xl rounded-xl border border-[var(--border)] bg-[#04120f]"
        role="img"
        aria-label="Spectrogram"
      />
    </div>
  );
}
