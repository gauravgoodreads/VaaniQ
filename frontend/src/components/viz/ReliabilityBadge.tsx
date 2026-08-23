type ReliabilityBadgeProps = {
  level: string;
};

/** Reliability flag from calibration / compression (REQ-062 / OQ-010). */
export function ReliabilityBadge({ level }: ReliabilityBadgeProps) {
  const tone =
    level.toLowerCase() === "high"
      ? "bg-[var(--success)]/15 text-[var(--success)]"
      : level.toLowerCase() === "low"
        ? "bg-[var(--danger)]/15 text-[var(--danger)]"
        : "bg-[var(--accent)]/15 text-[var(--accent)]";
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium uppercase ${tone}`}>
      {level}
    </span>
  );
}
