import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";

import { apiBaseUrl } from "@/api/client";
import { HonestyBanner, PageHeader, Surface } from "@/components/layout/PageChrome";
import { Button } from "@/components/ui/button";

type Participant = {
  participant_id: string;
  fluency_self_report: string;
  clip_ids: string[];
};

type Report = {
  n_responses: number;
  stats: Record<string, unknown>;
};

type ClipMeta = {
  clip_id: string;
  language: string;
  label: string;
  compression_status: string;
  duration_sec: number;
  has_audio: boolean;
};

/** Human listening-test UI with audio playback (RQ5 / O6). */
export function HumanStudyPage() {
  const [fluency, setFluency] = useState("hi+mr+ta");
  const [choice, setChoice] = useState("real");
  const [confidence, setConfidence] = useState(3);
  const [index, setIndex] = useState(0);
  const started = useRef(0);

  const register = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fluency_self_report: fluency }),
      });
      if (!res.ok) throw new Error("register failed");
      started.current = Date.now();
      setIndex(0);
      return (await res.json()) as Participant;
    },
  });

  const report = useQuery({
    queryKey: ["human-report"],
    queryFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/report`);
      if (!res.ok) throw new Error("report failed");
      return (await res.json()) as Report;
    },
  });

  const session = register.data;
  const clipId = session?.clip_ids[index] ?? "";

  const clipMeta = useQuery({
    queryKey: ["clip-meta", clipId],
    enabled: Boolean(clipId),
    queryFn: async () => {
      const res = await fetch(`${apiBaseUrl()}/api/v1/datasets/clips/${clipId}`);
      if (!res.ok) throw new Error("clip meta failed");
      return (await res.json()) as ClipMeta;
    },
  });

  useEffect(() => {
    started.current = Date.now();
  }, [clipId]);

  async function submitTrial() {
    if (!session || !clipId) return;
    const body = {
      participant_id: session.participant_id,
      clip_id: clipId,
      choice,
      confidence_1_5: confidence,
      response_ms: Date.now() - started.current,
      language: clipMeta.data?.language ?? clipId.split("-")[0] ?? "hi",
      compression_status: clipMeta.data?.compression_status ?? "clean",
    };
    const res = await fetch(`${apiBaseUrl()}/api/v1/human-study/response`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error("response failed");
    setIndex((i) => Math.min(i + 1, (session.clip_ids.length || 1) - 1));
    await report.refetch();
  }

  return (
    <section className="vaaniq-enter space-y-8">
      <PageHeader
        title="Human study"
        subtitle="Anonymous listening protocol (RQ5): play each clip, choose real or fake, rate confidence 1-5."
      />
      <HonestyBanner>
        Gold labels stay hidden during the trial. Model comparison numbers are demo-session stats -
        not a published human-perception paper result until recruitment completes.
      </HonestyBanner>

      <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
        <Surface title="Registration">
          <label className="grid gap-1 text-sm text-[var(--fg)]">
            Fluency self-report
            <input
              className="rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-2 text-[var(--fg)]"
              value={fluency}
              onChange={(e) => setFluency(e.target.value)}
              aria-label="Fluency self-report"
            />
          </label>
          <Button
            className="mt-4"
            type="button"
            onClick={() => register.mutate()}
            disabled={register.isPending}
          >
            Register anonymous ID
          </Button>
          {session ? (
            <p className="mt-3 text-sm text-[var(--fg-muted)]">
              Participant <code className="text-[var(--fg)]">{session.participant_id.slice(0, 8)}…</code>{" "}
              · {session.clip_ids.length} clips assigned
            </p>
          ) : null}
        </Surface>

        <Surface title="Trial">
          {session && clipId ? (
            <div className="space-y-4">
              <p className="text-sm text-[var(--fg-muted)]">
                Clip {index + 1} / {session.clip_ids.length} · <code>{clipId}</code>
                {clipMeta.data
                  ? ` · ${clipMeta.data.language} · ${clipMeta.data.compression_status} · ${clipMeta.data.duration_sec}s`
                  : null}
              </p>
              {clipMeta.data?.has_audio ? (
                <audio
                  key={clipId}
                  controls
                  className="w-full"
                  src={`${apiBaseUrl()}/api/v1/datasets/clips/${clipId}/audio`}
                />
              ) : (
                <p className="text-sm text-[var(--danger)]">
                  Audio missing for this clip. Generate the demo corpus first.
                </p>
              )}
              <div className="flex flex-wrap gap-4">
                <label className="grid gap-1 text-sm">
                  Choice
                  <select
                    className="h-10 rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 text-[var(--fg)]"
                    value={choice}
                    onChange={(e) => setChoice(e.target.value)}
                    aria-label="Real or fake choice"
                  >
                    <option value="real">Real</option>
                    <option value="fake">Fake</option>
                  </select>
                </label>
                <label className="grid gap-1 text-sm">
                  Confidence (1-5)
                  <input
                    type="range"
                    min={1}
                    max={5}
                    value={confidence}
                    onChange={(e) => setConfidence(Number(e.target.value))}
                    aria-label="Confidence 1 to 5"
                  />
                  <span className="tabular-nums">{confidence}</span>
                </label>
              </div>
              <Button type="button" onClick={() => void submitTrial()}>
                Submit & next
              </Button>
            </div>
          ) : (
            <p className="text-sm text-[var(--fg-muted)]">Register to start the listening protocol.</p>
          )}
        </Surface>
      </div>

      <Surface title="Session report">
        <p className="text-sm text-[var(--fg-muted)]">
          Responses recorded: {report.data?.n_responses ?? 0}
        </p>
        {report.data && Object.keys(report.data.stats).length > 0 ? (
          <pre className="mt-3 max-h-64 overflow-auto rounded-xl bg-[var(--bg)] p-4 text-xs text-[var(--fg)]">
            {JSON.stringify(report.data.stats, null, 2)}
          </pre>
        ) : (
          <p className="mt-2 text-sm text-[var(--fg-muted)]">Submit trials to populate comparison stats.</p>
        )}
      </Surface>
    </section>
  );
}
