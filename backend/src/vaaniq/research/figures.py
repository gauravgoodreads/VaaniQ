"""Publication SVG/CSV figures (vector-quality, no matplotlib required)."""

from __future__ import annotations

import csv
from collections.abc import Sequence
from pathlib import Path


def write_csv(path: Path, headers: Sequence[str], rows: Sequence[Sequence[object]]) -> Path:
    """Write a UTF-8 CSV table."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(list(headers))
        for row in rows:
            writer.writerow(list(row))
    return path


def write_line_svg(
    path: Path,
    *,
    xs: Sequence[float],
    ys: Sequence[float],
    title: str,
    xlabel: str,
    ylabel: str,
    caption: str,
) -> Path:
    """Write a simple SVG line chart (dissertation-ready vector)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    w, h, pad = 640.0, 360.0, 48.0
    if not xs or not ys:
        xs, ys = [0.0, 1.0], [0.0, 0.0]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmax <= xmin:
        xmax = xmin + 1.0
    if ymax <= ymin:
        ymax = ymin + 1.0

    def px(x: float) -> float:
        return pad + (x - xmin) / (xmax - xmin) * (w - 2 * pad)

    def py(y: float) -> float:
        return h - pad - (y - ymin) / (ymax - ymin) * (h - 2 * pad)

    pts = " ".join(f"{px(x):.1f},{py(y):.1f}" for x, y in zip(xs, ys, strict=True))
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{w / 2:.0f}" y="24" text-anchor="middle" font-size="14">{title}</text>
  <polyline fill="none" stroke="#1d4ed8" stroke-width="2" points="{pts}"/>
  <text x="{w / 2:.0f}" y="{h - 8:.0f}" text-anchor="middle" font-size="11">{xlabel}</text>
  <text x="14" y="{h / 2:.0f}" font-size="11" transform="rotate(-90 14 {h / 2:.0f})">{ylabel}</text>
  <text x="{pad}" y="{h - 20:.0f}" font-size="10" fill="#444">{caption}</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    path.with_suffix(".caption.txt").write_text(caption, encoding="utf-8")
    return path


def write_heatmap_svg(
    path: Path,
    *,
    matrix: dict[str, dict[str, float]],
    title: str,
    caption: str,
) -> Path:
    """Write a categorical heatmap SVG (cross-language / cross-condition)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(matrix.keys())
    cols = list(next(iter(matrix.values())).keys()) if matrix else []
    n_r = max(1, len(rows))
    n_c = max(1, len(cols))
    cell = 48
    left, top = 80, 40
    w = left + n_c * cell + 24
    h = top + n_r * cell + 48
    rects: list[str] = []
    vals = [v for row in matrix.values() for v in row.values() if v == v]
    vmax = max(vals) if vals else 1.0
    vmin = min(vals) if vals else 0.0
    span = vmax - vmin if vmax > vmin else 1.0
    for i, r in enumerate(rows):
        rects.append(f'<text x="8" y="{top + i * cell + 28}" font-size="11">{r}</text>')
        for j, c in enumerate(cols):
            val = float(matrix[r].get(c, float("nan")))
            t = 0.0 if val != val else (val - vmin) / span
            blue = int(255 * (1.0 - t))
            color = f"rgb({blue},{blue},255)"
            x = left + j * cell
            y = top + i * cell
            label = "nan" if val != val else f"{val:.3f}"
            rects.append(
                f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" '
                f'fill="{color}" stroke="#ccc"/>'
                f'<text x="{x + cell / 2:.0f}" y="{y + 28}" text-anchor="middle" '
                f'font-size="10">{label}</text>'
            )
    headers = " ".join(
        f'<text x="{left + j * cell + cell / 2:.0f}" y="{top - 8}" '
        f'text-anchor="middle" font-size="11">{c}</text>'
        for j, c in enumerate(cols)
    )
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{w / 2:.0f}" y="18" text-anchor="middle" font-size="14">{title}</text>
  {headers}
  {"".join(rects)}
  <text x="8" y="{h - 10}" font-size="10" fill="#444">{caption}</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")
    path.with_suffix(".caption.txt").write_text(caption, encoding="utf-8")
    return path


def write_confusion_svg(
    path: Path,
    matrix: Sequence[Sequence[int]],
    *,
    title: str,
    caption: str,
) -> Path:
    """Write a 2x2 confusion-matrix SVG (TN/FP/FN/TP)."""
    tn = int(matrix[0][0]) if matrix and matrix[0] else 0
    fp = int(matrix[0][1]) if matrix and len(matrix[0]) > 1 else 0
    fn = int(matrix[1][0]) if len(matrix) > 1 and matrix[1] else 0
    tp = int(matrix[1][1]) if len(matrix) > 1 and len(matrix[1]) > 1 else 0
    grid = {
        "real": {"real": float(tn), "fake": float(fp)},
        "fake": {"real": float(fn), "fake": float(tp)},
    }
    return write_heatmap_svg(path, matrix=grid, title=title, caption=caption)


def write_roc_svg(
    path: Path,
    *,
    fpr: Sequence[float],
    tpr: Sequence[float],
    auc: float,
    caption: str,
) -> Path:
    """Write an ROC curve SVG with AUC in the title."""
    return write_line_svg(
        path,
        xs=list(fpr),
        ys=list(tpr),
        title=f"ROC (AUC={auc:.3f})",
        xlabel="False positive rate",
        ylabel="True positive rate",
        caption=caption,
    )
