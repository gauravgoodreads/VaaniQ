type ReliabilityBin = Record<string, number | string | undefined>;

/** Map API reliability bins to chart points, skipping empty bins. */
export function reliabilityChartPoints(diagram: ReliabilityBin[] | undefined): { x: number; y: number }[] {
  return (diagram ?? [])
    .filter((row) => Number(row.count ?? 0) > 0)
    .map((row) => {
      const lo = Number(row.bin_lo ?? row.confidence ?? 0);
      const hi = Number(row.bin_hi ?? row.confidence ?? lo);
      return {
        x: (lo + hi) / 2,
        y: Number(row.accuracy ?? 0),
      };
    });
}
