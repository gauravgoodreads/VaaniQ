import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiBaseUrl, getJson } from "@/api/client";
import { QueryStatus } from "@/components/QueryStatus";
import { HonestyBanner, PageHeader, StatTile, Surface } from "@/components/layout/PageChrome";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type Sample = {
  clip_id: string;
  language: string;
  label: string;
  compression_status: string;
  duration_sec: number;
  has_audio: boolean;
};

type Explorer = {
  total_clips: number;
  total_hours: number;
  counts_by_language: Record<string, number>;
  hours_by_language: Record<string, number>;
  counts_by_label: Record<string, number>;
  hours_by_label: Record<string, number>;
  languages: string[];
  note: string;
  playable_clips?: number;
  samples?: Sample[];
};

const LANG_LABEL: Record<string, string> = {
  hi: "Hindi",
  mr: "Marathi",
  ta: "Tamil",
};

/** Dataset explorer for language × label hours with playable samples (O1). */
export function DatasetPage() {
  const [filter, setFilter] = useState<"all" | "hi" | "mr" | "ta">("all");
  const [active, setActive] = useState<Sample | null>(null);
  const q = useQuery({
    queryKey: ["datasets"],
    queryFn: () => getJson<Explorer>("/api/v1/datasets/explorer"),
  });
  const data = q.data;
  const samples = useMemo(() => {
    const all = data?.samples ?? [];
    if (filter === "all") return all;
    return all.filter((s) => s.language === filter);
  }, [data?.samples, filter]);

  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Dataset explorer"
        subtitle="Hindi, Marathi, and Tamil inventory for the active VaaniQ corpus - browse, filter, and listen."
      />
      <HonestyBanner>{data?.note ?? "Loading corpus note…"}</HonestyBanner>
      <QueryStatus isPending={q.isPending} isError={q.isError} error={q.error ?? undefined}>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile label="Total clips" value={String(data?.total_clips ?? "-")} />
          <StatTile
            label="Total hours"
            value={(data?.total_hours ?? 0).toFixed(3)}
            hint="Active corpus duration"
          />
          <StatTile
            label="Playable audio"
            value={String(data?.playable_clips ?? 0)}
            hint="On-disk audio files"
          />
          <StatTile
            label="Languages"
            value={(data?.languages ?? []).map((l) => LANG_LABEL[l] ?? l).join(" · ")}
          />
        </div>

        <div className="mt-6 grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <Surface title="Hours by language">
            <table className="w-full text-left text-sm">
              <caption className="sr-only">Counts by language</caption>
              <thead>
                <tr className="text-[var(--fg-muted)]">
                  <th className="pb-3 font-medium">Language</th>
                  <th className="pb-3 font-medium">Clips</th>
                  <th className="pb-3 font-medium">Hours</th>
                  <th className="pb-3 font-medium">Share</th>
                </tr>
              </thead>
              <tbody>
                {(data?.languages ?? ["hi", "mr", "ta"]).map((lang) => {
                  const hours = data?.hours_by_language[lang] ?? 0;
                  const total = data?.total_hours || 1;
                  const pct = Math.round((hours / total) * 100);
                  return (
                    <tr key={lang} className="border-t border-[var(--border)]">
                      <td className="py-3 font-medium text-[var(--fg)]">
                        {LANG_LABEL[lang] ?? lang}{" "}
                        <span className="text-[var(--fg-muted)]">({lang})</span>
                      </td>
                      <td className="py-3 text-[var(--fg)]">{data?.counts_by_language[lang] ?? 0}</td>
                      <td className="py-3 tabular-nums text-[var(--fg)]">{hours.toFixed(4)}</td>
                      <td className="py-3">
                        <div className="flex items-center gap-2">
                          <div className="h-2 flex-1 overflow-hidden rounded-full bg-[var(--border)]">
                            <div
                              className="h-full rounded-full bg-[var(--accent)]"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                          <span className="w-10 text-right text-xs text-[var(--fg-muted)]">{pct}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              {Object.entries(data?.counts_by_label ?? {}).map(([label, n]) => (
                <div
                  key={label}
                  className="rounded-xl border border-[var(--border)] bg-[var(--bg)]/60 px-4 py-3"
                >
                  <p className="text-xs uppercase tracking-wide text-[var(--fg-muted)]">{label}</p>
                  <p className="mt-1 text-xl font-medium text-[var(--fg)]">
                    {n} clips · {(data?.hours_by_label[label] ?? 0).toFixed(3)} h
                  </p>
                </div>
              ))}
            </div>
          </Surface>

          <Surface title="Listen to samples">
            <div className="mb-4 flex flex-wrap gap-2">
              {(["all", "hi", "mr", "ta"] as const).map((id) => (
                <button
                  key={id}
                  type="button"
                  className={cn(
                    "rounded-full px-3 py-1.5 text-xs font-medium transition",
                    filter === id
                      ? "bg-[var(--accent)] text-[var(--accent-fg)]"
                      : "border border-[var(--border)] text-[var(--fg-muted)] hover:text-[var(--fg)]",
                  )}
                  onClick={() => setFilter(id)}
                >
                  {id === "all" ? "All" : LANG_LABEL[id]}
                </button>
              ))}
            </div>
            <ul className="max-h-[28rem] space-y-2 overflow-y-auto pr-1">
              {samples.map((s) => (
                <li key={s.clip_id}>
                  <button
                    type="button"
                    onClick={() => setActive(s)}
                    className={cn(
                      "flex w-full items-center justify-between gap-3 rounded-xl border px-3 py-3 text-left transition",
                      active?.clip_id === s.clip_id
                        ? "border-[var(--accent)] bg-[color-mix(in_oklab,var(--accent)_12%,var(--bg-elevated))]"
                        : "border-[var(--border)] hover:border-[var(--accent)]/50",
                    )}
                  >
                    <span>
                      <span className="block font-medium text-[var(--fg)]">{s.clip_id}</span>
                      <span className="text-xs text-[var(--fg-muted)]">
                        {LANG_LABEL[s.language] ?? s.language} · {s.label} · {s.compression_status} ·{" "}
                        {s.duration_sec.toFixed(0)}s
                      </span>
                    </span>
                    <span
                      className={cn(
                        "rounded-full px-2 py-0.5 text-[10px] uppercase tracking-wide",
                        s.has_audio
                          ? "bg-[color-mix(in_oklab,var(--success)_18%,transparent)] text-[var(--success)]"
                          : "bg-[var(--bg)] text-[var(--fg-muted)]",
                      )}
                    >
                      {s.has_audio ? "WAV" : "meta"}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
            {active?.has_audio ? (
              <div className="mt-4 space-y-2 rounded-xl border border-[var(--border)] bg-[var(--bg)]/50 p-4">
                <p className="text-sm font-medium text-[var(--fg)]">Now playing · {active.clip_id}</p>
                <audio
                  key={active.clip_id}
                  controls
                  autoPlay
                  className="w-full"
                  src={`${apiBaseUrl()}/api/v1/datasets/clips/${active.clip_id}/audio`}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setActive(null)}
                >
                  Close player
                </Button>
              </div>
            ) : active ? (
              <p className="mt-4 text-sm text-[var(--fg-muted)]">
                No WAV on disk for {active.clip_id}. Regenerate the demo corpus.
              </p>
            ) : null}
          </Surface>
        </div>
      </QueryStatus>
    </section>
  );
}
